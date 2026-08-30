# Multilingual Speech Design — 5 MVP Languages + Mixed/Bilingual

**Date:** 2026-08-29
**Status:** Approved design (pending implementation plan)
**Target languages:** English (`en`), Hindi (`hi`), Gujarati (`gu`), Marathi (`mr`), Bengali (`bn`)

## 1. Scope & non-negotiables

This design fixes speech *input* (STT) and *output* (TTS/read-aloud) for the 5 MVP
languages and adds mixed/bilingual query handling. It does **not** touch the RAG
core, corpus, embeddings, or the evidence/citation gates.

Hard constraints (from the brief, carried unchanged):

- One RAG core, one grounding/evidence path, one citation-verification path.
- One generic speech-preparation layer (`speech_text` / `speech_segments`).
- Language-specific configuration is allowed **only** for legitimate locale/voice
  selection (config-driven `language → locale → voice`).
- Never: modify corpus, re-ingest, re-chunk, re-embed, change Jina v3 / 768d,
  weaken the evidence gate, weaken citation verification, remove citations from
  the API response, hardcode chunk IDs, hardcode document/query/language-specific
  answers or citation-removal hacks, or create a separate RAG per language.

## 2. Current pipeline (traced, pre-design)

- **Read-aloud** (`frontend/src/components/chat/MessageBubble.tsx`): calls
  `speech.speak(resp.speech_text ?? resp.answer, resp.language)` → **browser
  `speechSynthesis`**, single locale = answer language.
- **Mic input** (`frontend/src/components/ChatWindow.tsx` `toggleMic`): calls
  `speech.listen(lang, …)` → **browser Web Speech STT** → transcript appended to
  the text box → sent to `POST /chat` (text). Single language = UI-selected.
- **Backend `/voice`** (`backend/app/routes/voice.py`): full Azure STT → RAG →
  Azure TTS. Exists and is unit-tested but **no UI button currently calls it**
  (dormant path). This is the route that will serve the Azure TTS fallback.

**Observed root causes of the reported failures:**

1. **Chunk-ID speech** — TTS received the raw `answer` containing `[chunk:ID]`
   markers. *Already fixed earlier in this session* via `speech_text`
   (post-verification) emitted by `chat.py` and consumed by both read-aloud and
   `/voice`. This design preserves that fix.
2. **Gujarati/Marathi/Bengali read-aloud "incorrect"** — most likely the browser
   `speechSynthesis` has **no Indic voice** on the user's OS, so it silently
   falls back to an English voice that mispronounces the text. This design fixes
   it with a browser→Azure TTS fallback (never an English substitution).

## 3. Locked decisions

| # | Decision | Choice |
|---|----------|--------|
| 1 | Read-aloud TTS engine | **Hybrid**: browser voice → Azure `/voice/speak` fallback per missing language |
| 2 | Mixed-TTS segmentation | **Server emits `speech_segments`** (`[{language, text}]`) via generic script-run detection |
| 3 | STT path | **Browser Web Speech primary**; mixed handling via server-side language ID + English retrieval representation |
| 4 | Response-language resolution | **One backend `resolve_response_language()` with session memory** |

## 4. Architecture / data flow

**Path A — Read-aloud (per message, user-facing):**

```
MessageBubble
  → speech.speakSegments(resp.speech_segments
        ?? [{language: resp.language, text: resp.speech_text}])
  → partition into ordered CONTIGUOUS RUNS of the same TTS source:
        browser run  (every segment in the run has a local voice)
        azure run    (no segment in the run has a local voice)
  → for each run, in order:
        browser run → speak sequentially via speechSynthesis
        azure run   → one POST /voice/speak {segments: run}
              → backend builds Azure SSML, one <voice> per segment, in order
              → returns a single WAV for that run → play
  → text answer always remains visible
```

Example: `[en browser] → [gu Azure] → [en browser] → [mr Azure]` becomes two
contiguous Azure runs (`[gu]` and `[mr]`), so **2 Azure calls**, each played in
its correct sequential position. No splicing of one WAV into two positions.

**Path B — Mic → answer:**

```
browser speech.listen(uiLang) → transcript → input box → POST /chat (text)
  server: detect_query_languages → resolve_response_language
        → existing RAG → verified answer
        → speech_text + speech_segments → ChatResponse
```

Backend `/voice` full pipeline remains available and tested but is **not** the
primary UI path (per decision 3).

## 5. Backend components

### 5a. `app/speech_text.py`

- `prepare_speech_text(answer) -> str` (exists): strips `[chunk:ID]` / `【ID】` /
  `[ID]`, markdown links, URLs, tidies punctuation. Runs **after** verification.
- NEW `segment_speech(answer, answer_language) -> list[dict]`:
  - Splits on **script runs**, mapping:
    - Gujarati `U+0A80–U+0AFF` → `gu`
    - Bengali `U+0980–U+09FF` → `bn`
    - Devanagari `U+0900–U+097F` → **`answer_language`** (already resolved; no
      guessing) — see §10 for why this is answer-side only.
    - Latin → `en`
  - Numbers, dates, percentages, clause numbers, scheme names, abbreviations,
    official terminology preserved verbatim.
  - Returns `[{language, text}, …]`. Generic — **no `if lang == "hi"` branches**.
- `chat.py` emits both `speech_text` (concatenated, backward-compat) and
  `speech_segments` (from `segment_speech(answer, answer_language)`).

### 5b. `app/language.py` (input side — NOT Devanagari-only)

- `detect_query_languages(text) -> {languages: set, dominant: str, explicit_request: str|None}`:
  - Detects **explicit response-language request** in the query
    ("respond in Hindi", "explain in Marathi", "Marathi म्हणजे काय? explain in Marathi")
    → `explicit_request`.
  - Per-script run identification for Latin + Indic code-switching.
  - **Hindi vs Marathi remain distinguishable via the existing stopword-bias
    logic** — Devanagari is *not* mapped to Hindi for input detection.
- `english_retrieval_query(text, detected) -> str`:
  - Preserves scheme names / acronyms / legal terms / numbers / dates / clause
    numbers (e.g. `PMFBY`, `premium`, `PACS`, `Threshold Yield`).
  - Translates the semantic Indic runs to English for retrieval.
  - Original query is **never** mutated (kept for logging/display/response-language
    selection).

### 5c. `app/services/lang_memory.py` (new)

- In-memory `dict[session_id, language]`. *(MVP single-instance; note: swap to
  Supabase/Redis if multi-instance deployment.)*
- `get_session_language(session_id) -> str | None`
- `set_session_language(session_id, language)` — called **only** when the
  resolved language is intentional/clear (see §7).

### 5d. `app/resolve_response_language.py` (new, single source of truth)

```
resolve(req_lang, ui_language_explicit, detected, session_lang, explicit_request)
  → explicit user request          (parsed from query)
  → explicit UI language selection/change   (only when user actively chose; ui_language_explicit=true)
  → existing session language      (from lang_memory)
  → detected dominant input language
  → "en"
```

- Used by `chat.py` **and** `voice.py`. Updates `lang_memory` **only** when the
  winning source is an explicit request or an explicit UI selection/change (so a
  one-off detected query never poisons the session).
- Frontend sends `ui_language_explicit: bool` (true only when the user actively
  changes the language selector; default/unchanged = false), so a default `en`
  UI language does **not** override an existing Hindi session.

### 5e. `app/routes/chat.py`

- Calls `detect_query_languages(question)` and `resolve_response_language(...)`
  using `req.language`, `req.ui_language_explicit`, detected langs, `session_id`.
- Sets `answer_language` on the response.
- Response gains `speech_segments` (from `segment_speech(answer, answer_language)`);
  `speech_text` unchanged.

### 5f. `app/routes/voice.py` `/voice/speak`

- `SpeakRequest` gains optional `segments: list[{language, text}] | None`.
- If `segments` provided: build **Azure SSML with one `<voice name=…>` per
  segment, in order**, synthesize once, return concatenated audio.
- Else: single-voice behavior (today) is preserved.

### 5g. `app/config.py`

- `tts_voices` / `speech_locales` for `en/hi/gu/mr/bn` (defaults already set).
- **Phase 8 verification:** attempt to list voices from Azure with the configured
  key; if a configured voice name is invalid, surface the exact error and fix the
  config string. **Never substitute a random voice.**

## 6. Frontend components

- **`lib/speech.ts`**:
  - `hasVoice(lang) -> bool` (checks `speechSynthesis.getVoices()`).
  - `speakSegments(segments)` (replaces single `speak` for read-aloud):
    partition into ordered contiguous runs (browser vs Azure source); for each
    run in order, speak browser runs via `speechSynthesis` and send each Azure
    run as one `POST /voice/speak`; play returned WAV in its sequential position.
  - Handle `voiceschanged` (voices load asynchronously).
  - `stopSpeaking()` cancels the whole queue.
- **`lib/api.ts`**: add `speakSegments`/`fetchVoiceSpeak(segments)` client for
  `POST /voice/speak`.
- **`chat/MessageBubble.tsx`**:
  - `handleSpeak` uses `resp.speech_segments ?? [{language: resp.language, text: resp.speech_text}]`.
  - **Remove the read-aloud control from the abstained (`Alert`) branch** (see §12).
- **`ChatWindow.tsx`**: send `ui_language_explicit` (true on user language-change
  event), pass through existing `session_id`.

## 7. Response-language resolution (corrected priority + memory)

```
explicit user request
→ explicit UI language selection/change
→ existing session language
→ detected dominant input language
→ en
```

- Session memory is updated **only** from an explicit request or explicit UI
  selection/change — never from detected dominant or the default — so a stray
  English query in a Hindi session will not flip the session to English.
- Example: session memory = `hi`; user asks "What is PMFBY premium?" → no explicit
  request, UI unchanged (`ui_language_explicit=false`), session = `hi` → answer in
  Hindi. User then switches UI to English → `ui_language_explicit=true` → `en`,
  memory updated to `en`.

## 8. TTS fallback chain (corrected — NO English fallback)

For a target language `L` (answer language, or a segment's language):

```
1. browser voice matching L        → speak
2. else Azure matching voice for L  → POST /voice/speak, play
3. else → "audio unavailable" for L
```

**Never** silently substitute an English (or any other) voice for
Hindi/Gujarati/Marathi/Bengali. If the requested language cannot be spoken, the
UI shows an explicit "audio unavailable in <lang>" note and the text remains.

## 9. Mixed-TTS segmentation & batching (contiguous-run approach)

- `speech_segments` is the single source for both browser and Azure paths.
- Client partitions the segments into **ordered contiguous runs** by TTS source
  (a run is a maximal sequence of adjacent segments that all share the same
  source: browser-eligible, or Azure-needed).
- For each run, in segment order:
  - **Browser run** → spoken sequentially via `speechSynthesis`.
  - **Azure run** → sent as **one** `POST /voice/speak` with that run's segments
    (backend returns a single WAV for the run, multi-voice SSML in order).
- This minimizes Azure HTTP calls (one per contiguous Azure run, not per
  segment) **and** preserves order trivially, because runs are contiguous and
  played sequentially. A single Azure WAV is never required to appear in two
  separate browser positions.
- **Non-overlap is mandatory:** playback is driven by one sequential queue; runs
  play one-at-a-time in segment order; browser and Azure audio must never overlap
  or reorder.

## 10. Input-language detection (corrected — Devanagari NOT used for input)

- `detect_query_languages` uses script + **stopword bias** to keep Hindi and
  Marathi distinguishable. It does **not** map Devanagari → Hindi for input.
- The `Devanagari → answer_language` rule is used **only** for *answer-side*
  segmentation (§5a), where the answer language is already resolved and therefore
  unambiguous.

## 11. Mixed-language STT limitation (explicit)

```
browser STT → transcript → server language identification → mixed-language processing
```

Browser Web Speech is the primary recognizer. **Server-side language ID cannot
recover text that the browser recognizer never transcribed correctly.** The design
therefore does *not* claim that server-side ID guarantees correct mixed-language
STT. For the MVP this is acceptable; Azure STT with automatic language
identification is noted as a future upgrade (already available via `/voice` if
wired later).

## 12. Abstention & TTS (corrected)

```
grounded answer → TTS available
abstention      → no factual answer → no read-aloud
```

- Abstained responses get **no read-aloud control** by default (the speak button
  is removed from the abstained `Alert` branch in `MessageBubble`).
- If a future product decision wants the controlled abstention message read
  aloud, it must be an **explicit, opted-in** behavior (e.g. a product flag) —
  never accidental.

## 13. Error handling

- **TTS failure** (browser or Azure) → text answer remains; read-aloud shows a
  small "audio unavailable" note; never fabricates speech.
- **STT failure / empty transcript** → clear message, no fabricated query.
- **Azure voice missing** → reported via app state; "audio unavailable" per §8;
  never a wrong-language substitution.
- **Abstention** → no TTS of a factual answer (§12).

## 14. Testing matrix

Single-language (each: text → answer → TTS): `en, hi, gu, mr, bn`.
Voice (each: speech → STT → RAG → TTS): `en, hi, gu, mr, bn`.

Extend suites:

- `test_speech_text.py`: `segment_speech` preserves all 5 scripts; Devanagari
  segmented as `answer_language`; markers/URLs/markdown removed; no Unicode
  corruption; no `if lang ==` branches.
- `test_language.py`: mixed-query detection (`hi+en`, `gu+en`, `mr+en`, `bn+en`);
  dominant + explicit-request parsing; `english_retrieval_query` preserves
  `PMFBY`/`premium`/numbers/dates; hi vs mr distinguishable.
- `test_resolve_response_language.py`: priority order; session memory updates
  only from explicit sources; default `en` UI does not override existing session.
- `test_chat_route.py`: response includes `speech_segments`; marker-free; abstain
  path unchanged; `ui_language_explicit` honored.
- `test_voice_routes.py`: `/voice/speak` with `segments` builds multi-voice SSML
  (mocked); single-voice still works; Azure calls are batched per **contiguous
  run** (e.g. `[en][gu][en][mr]` → 2 Azure calls, not 1, not 4).
- Regression: citation verifier still fail-closed; `speech_text`/`speech_segments`
  derived only from verified answer.

## 15. RAG regression guard

After speech changes, confirm (existing eval):

- corpus unchanged (2,188 chunks), Jina v3 unchanged, 768d unchanged
- `retrieval.query` / `retrieval.passage` unchanged
- evidence gate unchanged, citation verifier active, reranker OFF
- domain/jurisdiction filters unchanged

Expected baseline: Recall@1=0.800, Recall@3=0.900, Recall@5=0.925, MRR=0.856,
contamination=0. Do not modify retrieval to move numbers.

## 16. Live validation plan & limitations

- Where `AZURE_SPEECH_KEY` is available, install `azure-cognitiveservices.speech`
  and attempt **real** TTS + STT for the 5 languages; produce a
  `Language | STT | Answer | TTS | Voice/Locale | Result` table.
- **Live results are labeled explicitly as live; boundary/mocked tests are
  labeled as such** (per brief — never report mocked as live).
- If SDK/keys are unavailable in the build environment, those rows are marked
  **"not verified live"** with the exact missing stage noted.
- Browser `speechSynthesis` Indic voice availability is OS-dependent; the hybrid
  Azure fallback covers it.
- Hindi↔Marathi input STT/ID may occasionally mis-tag (shared Devanagari); answer
  segmentation is unaffected (uses resolved answer language).
- Session memory is in-memory (MVP single-instance); noted for multi-instance.

## 17. Files changed (summary)

Backend: `app/speech_text.py` (segment), `app/language.py` (detect/retrieval),
`app/services/lang_memory.py` (new), `app/resolve_response_language.py` (new),
`app/routes/chat.py`, `app/routes/voice.py`, `app/config.py`.
Frontend: `lib/speech.ts`, `lib/api.ts`, `components/chat/MessageBubble.tsx`,
`components/ChatWindow.tsx`.
Tests: `test_speech_text.py`, `test_language.py`, `test_resolve_response_language.py` (new),
`test_chat_route.py`, `test_voice_routes.py`.

## 18. Success criteria (from brief)

- [ ] English/Hindi/Gujarati/Marathi/Bengali TTS works (hybrid, no English substitution)
- [ ] English/Hindi/Gujarati/Marathi/Bengali STT works
- [ ] citation IDs never reach TTS; citation verification remains fail-closed
- [ ] TTS receives `speech_text` / `speech_segments` only
- [ ] `speech_text`/`speech_segments` preserve all five languages
- [ ] mixed-language queries are understood; mixed answers use correct response language
- [ ] multilingual answer segments use appropriate voices; Azure requests are batched per contiguous run and played in order
- [ ] TTS does not depend on rendered DOM
- [ ] TTS failure does not destroy text answer; abstention prevents read-aloud
- [ ] no document/query/language-specific hardcoding; corpus & RAG unchanged
- [ ] frontend build passes; backend tests pass; RAG regression passes
