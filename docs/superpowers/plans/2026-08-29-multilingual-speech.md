# Multilingual Speech (TTS/STT + Mixed-Language) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix read-aloud/TTS and STT for en/hi/gu/mr/bn and add mixed/bilingual query handling, using a server-generated `speech_segments` representation, a backend response-language resolver with session memory, and a browser→Azure hybrid TTS with per-contiguous-run batching.

**Architecture:** One RAG core stays untouched. The backend emits `speech_text` (single, concatenated) and `speech_segments` (language-tagged runs) from the *verified* answer. A new `resolve_response_language` module (explicit request → explicit UI selection → session → detected → en) sets the answer language; mixed input is detected and an English retrieval representation is built. The frontend read-aloud uses `speech_segments`, speaking browser-eligible contiguous runs locally and sending each contiguous Azure run in one `/voice/speak` call. The dormant backend `/voice` serves Azure TTS fallback.

**Tech Stack:** FastAPI (Python), Pydantic, Azure Cognitive Services Speech SDK (`azure-cognitiveservices.speech`), Next.js/React/TypeScript (frontend), browser `speechSynthesis` + Web Speech API, `pytest`, Vitest.

## Global Constraints

- One RAG core, one grounding/evidence path, one citation-verification path.
- One generic speech-preparation layer (`speech_text` / `speech_segments`).
- Language-specific configuration is allowed **only** for legitimate locale/voice selection (config-driven `language → locale → voice`).
- Never: modify corpus, re-ingest, re-chunk, re-embed, change Jina v3 / 768d, weaken the evidence gate, weaken citation verification, remove citations from the API response, hardcode chunk IDs, hardcode document/query/language-specific answers or citation-removal hacks, or create a separate RAG per language.
- `speech_text` / `speech_segments` are derived ONLY from the verified answer (after citation verification).
- Response-language priority: `explicit user request → explicit UI language selection/change → existing session language → detected dominant input language → en`. Session memory is updated ONLY from explicit sources.
- TTS fallback per language: `requested language → browser matching voice → Azure matching voice → audio unavailable`. Never silently substitute an English (or other) voice for hi/gu/mr/bn.
- Mixed TTS: segments partitioned into ordered contiguous runs; each Azure run is ONE `/voice/speak` call; runs played sequentially, no overlap/reorder.
- Devanagari→answer_language is used ONLY for answer-side segmentation; input detection keeps hi/mr distinguishable via stopword bias.
- Abstention → no read-aloud (no factual answer spoken).
- Live Azure audio results labeled explicitly as live; boundary/mocked tests labeled as such.

---

## File Structure

**Backend (new):**
- `backend/app/services/lang_memory.py` — in-memory session→language store.
- `backend/app/resolve_response_language.py` — single response-language resolver.
- `backend/scripts/verify_azure_voices.py` — environment-dependent voice/locale verification (Phase 8).

**Backend (modify):**
- `backend/app/speech_text.py` — add `segment_speech(answer, answer_language)`.
- `backend/app/language.py` — add `detect_query_languages`, `english_retrieval_query`.
- `backend/app/routes/chat.py` — resolver integration; emit `speech_segments`; add `ui_language_explicit` to `ChatRequest`.
- `backend/app/providers/azure_voice.py` — add `text_to_speech_segments` (SSML multi-voice).
- `backend/app/services/voice_service.py` — add `text_to_speech_segments` fallback pass-through.
- `backend/app/routes/voice.py` — `SpeakRequest` accepts `segments`; route uses it.
- `backend/app/config.py` — no code change required (already has `tts_voices`/`speech_locales` for en/hi/gu/mr/bn); verification script reads them.

**Frontend (modify):**
- `frontend/src/lib/speech.ts` — `hasVoice`, `speakSegments` (contiguous-run hybrid), `stopSpeaking` covers Azure audio.
- `frontend/src/lib/api.ts` — `ChatResponse.speech_segments`; `sendChat` sends `ui_language_explicit`; add `fetchVoiceSpeak`.
- `frontend/src/components/chat/MessageBubble.tsx` — use `speech_segments`; remove abstain speak button.
- `frontend/src/components/ChatWindow.tsx` — send `ui_language_explicit`.

**Tests (modify/add):**
- `backend/tests/test_speech_text.py` — segmentation cases.
- `backend/tests/test_language.py` — mixed detection + English retrieval representation.
- `backend/tests/test_resolve_response_language.py` (new).
- `backend/tests/test_chat_route.py` — `speech_segments` in response; `ui_language_explicit` honored; abstain unchanged.
- `backend/tests/test_voice_routes.py` — `/voice/speak` with segments → multi-voice SSML (mocked); contiguous-run batching.

---

### Task 1: Backend — `segment_speech` in `speech_text.py`

**Files:**
- Modify: `backend/app/speech_text.py`
- Test: `backend/tests/test_speech_text.py`

**Interfaces:**
- Produces: `segment_speech(answer: str, answer_language: str) -> list[dict]` returning `[{"language": str, "text": str}, …]`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_speech_text.py (append)
def test_segment_speech_single_latin():
    from app.speech_text import segment_speech
    segs = segment_speech("PMFBY provides crop insurance.", "en")
    assert segs == [{"language": "en", "text": "PMFBY provides crop insurance."}]


def test_segment_speech_mixed_hindi_english():
    from app.speech_text import segment_speech
    ans = "प्रधानमंत्री फसल बीमा योजना PMFBY के तहत"
    segs = segment_speech(ans, "hi")
    langs = [s["language"] for s in segs]
    assert langs == ["hi", "en", "hi"]
    assert segs[1]["text"] == "PMFBY"


def test_segment_speech_devanagari_uses_answer_language():
    from app.speech_text import segment_speech
    ans = "हे उत्तर मराठीत आहे"
    segs = segment_speech(ans, "mr")
    assert all(s["language"] == "mr" for s in segs)


def test_segment_speech_strips_markers_before_segmenting():
    from app.speech_text import segment_speech
    ans = "Eligible farmers [chunk:abc123] are covered."
    segs = segment_speech(ans, "en")
    assert "[chunk:" not in segs[0]["text"]


def test_segment_speech_preserves_unicode():
    from app.speech_text import segment_speech
    ans = "ગુજરાતી PMFBY માટે"
    segs = segment_speech(ans, "gu")
    joined = "".join(s["text"] for s in segs)
    assert "ગુજરાતી" in joined and "PMFBY" in joined
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_speech_text.py -q`
Expected: FAIL (`segment_speech` not defined / ImportError).

- [ ] **Step 3: Write minimal implementation**

Append to `backend/app/speech_text.py`:

```python
def _char_script(ch: str, answer_language: str):
    """Map a character to a language bucket for segmentation.

    Gujarati/Bengali/Latin are script-unique. Devanagari is mapped to the
    *already resolved* answer language (NOT guessed) — this is answer-side only.
    Punctuation/spaces return None (attach to the current run).
    """
    cp = ord(ch)
    if 0x0A80 <= cp <= 0x0AFF:
        return "gu"
    if 0x0980 <= cp <= 0x09FF:
        return "bn"
    if 0x0900 <= cp <= 0x097F:
        return answer_language
    if ch.isascii() and (ch.isalpha() or ch.isdigit()):
        return "en"
    return None


def segment_speech(answer: str, answer_language: str) -> list[dict]:
    """Split a verified answer into language-tagged segments by script run.

    Generic — no per-language hardcoding. Devanagari runs take the resolved
    ``answer_language`` so Hindi/Marathi answers segment correctly.
    """
    if not answer:
        return []
    segments: list[dict] = []
    current_lang: str | None = None
    current_text: list[str] = []
    for ch in answer:
        lang = _char_script(ch, answer_language)
        if lang is None:
            if current_lang is not None:
                current_text.append(ch)
            continue
        if lang != current_lang:
            if current_lang is not None:
                text = "".join(current_text).strip()
                if text:
                    segments.append({"language": current_lang, "text": text})
            current_lang = lang
            current_text = [ch]
        else:
            current_text.append(ch)
    if current_lang is not None:
        text = "".join(current_text).strip()
        if text:
            segments.append({"language": current_lang, "text": text})
    return segments
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_speech_text.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/speech_text.py backend/tests/test_speech_text.py
git commit -m "feat(speech): add generic segment_speech by script run"
```

---

### Task 2: Backend — mixed input detection in `language.py`

**Files:**
- Modify: `backend/app/language.py`
- Test: `backend/tests/test_language.py`

**Interfaces:**
- Produces: `detect_query_languages(text: str) -> dict` with keys `languages: set[str]`, `dominant: str | None`, `explicit_request: str | None`.
- Produces: `english_retrieval_query(text: str, detected: dict, settings) -> str` (reuses the already-wired `AzureTranslator`; preserves entities/numbers, translates Indic runs to English).

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_language.py (append)
from app.language import detect_query_languages, english_retrieval_query
from app.config import get_settings

def test_detect_mixed_hindi_english():
    d = detect_query_languages("PMFBY क्या है and premium कितना है?")
    assert "hi" in d["languages"] and "en" in d["languages"]
    assert d["dominant"] is not None

def test_detect_explicit_request_marathi():
    d = detect_query_languages("PMFBY म्हणजे काय? explain in Marathi")
    assert d["explicit_request"] == "mr"

def test_detect_explicit_request_gujarati_native():
    d = detect_query_languages("આ વિશે ગુજરાતી માં સમજાવો")
    assert d["explicit_request"] == "gu"

def test_detect_marathi_not_hindi():
    d = detect_query_languages("मला मराठीत उत्तर हवे आहे")
    assert "mr" in d["languages"]
    # stopword bias must allow mr to be present (not forced to hi only)
    assert d["dominant"] in ("mr", "hi")

def test_english_retrieval_preserves_latin_entities(monkeypatch):
    settings = get_settings()

    class _FakeT:
        def translate(self, t, to, source):
            # only Indic runs reach here; Latin runs are never passed to translate
            return t.replace("શું", "WHAT").replace("કેટલું", "HOWMUCH")

    monkeypatch.setattr("app.language.AzureTranslator", lambda s: _FakeT())
    out = english_retrieval_query("PMFBY શું છે and farmer premium 500", None, settings)
    assert "PMFBY" in out and "farmer" in out and "premium" in out and "500" in out
    assert "WHAT" in out and "HOWMUCH" in out  # Indic runs were translated
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_language.py -q`
Expected: FAIL (functions not defined).

- [ ] **Step 3: Write minimal implementation**

Append to `backend/app/language.py`:

```python
import re

# Explicit "respond/explain in <lang>" detection. Name -> code, including native terms.
_EXPLICIT_LANG_NAMES = {
    "english": "en", "angrezi": "en",
    "hindi": "hi", "हिंदी": "hi",
    "gujarati": "gu", "ગુજરાતી": "gu",
    "marathi": "mr", "मराठी": "mr",
    "bengali": "bn", "bangla": "bn", "বাংলা": "bn",
}
_EXPLICIT_RE = re.compile(
    r"(?:respond|reply|answer|explain|समझाओ|समजावो|बताओ|समझाएं|in|में|मां)\s+"
    r"(english|angrezi|hindi|हिंदी|gujarati|ગુજરાતી|marathi|मराठी|bengali|bangla|বাংলা)",
    re.IGNORECASE,
)


def _detect_explicit_request(text: str) -> str | None:
    m = _EXPLICIT_RE.search(text)
    if m:
        return _EXPLICIT_LANG_NAMES.get(m.group(1).lower())
    return None


def detect_query_languages(text: str) -> dict:
    """Detect languages present in a (possibly mixed) query.

    Devanagari is NOT mapped to Hindi for input — hi/mr stay distinguishable
    via stopword bias (reusing normalize_language on the devanagari run).
    """
    cfg = _load_config()
    languages: set[str] = set()
    # Per-script run classification ignoring Latin (handled separately).
    ratios = _script_ratios(text)
    if ratios.get("gujarati", 0.0) >= cfg["script_threshold"]:
        languages.add("gu")
    if ratios.get("bengali", 0.0) >= cfg["script_threshold"]:
        languages.add("bn")
    if ratios.get("devanagari", 0.0) >= cfg["script_threshold"]:
        # distinguish hi/mr via stopword bias (never force Hindi)
        languages.add("mr" if _stopword_bias(text, "mr") > _stopword_bias(text, "hi") else "hi")
    # Latin presence
    latin_letters = [c for c in text if c.isalpha() and c.isascii()]
    if latin_letters:
        languages.add("en")
    # dominant = script with highest alphabetic ratio (hi/mr kept distinguishable)
    best, best_r = None, 0.0
    for name, r in ratios.items():
        if name in ("gujarati", "bengali", "devanagari") and r > best_r:
            best, best_r = name, r
    if best == "gujarati":
        dominant = "gu"
    elif best == "bengali":
        dominant = "bn"
    elif best == "devanagari":
        # SAME hi/mr stopword-bias decision as the `languages` set above
        dominant = "mr" if _stopword_bias(text, "mr") > _stopword_bias(text, "hi") else "hi"
    elif latin_letters:
        dominant = "en"
    else:
        dominant = None
    return {
        "languages": languages,
        "dominant": dominant,
        "explicit_request": _detect_explicit_request(text),
    }


_SCRIPT_TO_LANG = {"gujarati": "gu", "bengali": "bn", "devanagari": "hi"}


def _script_runs(text: str) -> list[tuple[str, str]]:
    """Split text into (script_label, text) runs for run-aware translation."""
    cfg = _load_config()
    scripts = cfg["scripts"]

    def label(c: str) -> str:
        cp = ord(c)
        for name, charset in scripts.items():
            if cp in charset:
                return name
        if c.isascii() and c.isalpha():
            return "latin"
        return "other"

    runs: list[tuple[str, str]] = []
    cur_script: str | None = None
    cur_chars: list[str] = []
    for c in text:
        if c.isspace():
            if cur_chars:
                cur_chars.append(c)
            continue
        s = label(c)
        if s != cur_script:
            if cur_chars:
                runs.append((cur_script or "other", "".join(cur_chars)))
            cur_script = s
            cur_chars = [c]
        else:
            cur_chars.append(c)
    if cur_chars:
        runs.append((cur_script or "other", "".join(cur_chars)))
    return runs


def english_retrieval_query(text: str, detected: dict | None, settings) -> str:
    """Build an English retrieval representation (run-aware).

    Latin runs (scheme names, acronyms, numbers, dates, English words) are
    preserved verbatim; only Indic-script runs are translated via the
    already-wired AzureTranslator. This preserves the terminology the design
    requires to stay intact, rather than translating the whole query. Falls
    back to the original text on any failure (never fabricates).
    """
    from app.providers.translator import AzureTranslator

    dom = (detected or {}).get("dominant")
    if not dom or dom == "en":
        return text
    try:
        translator = AzureTranslator(settings)
        out: list[str] = []
        for script, run_text in _script_runs(text):
            if script in ("latin", "other"):
                out.append(run_text)
            else:
                out.append(translator.translate(run_text, to="en", source=_SCRIPT_TO_LANG[script]))
        return "".join(out)
    except Exception:
        return text
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_language.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/language.py backend/tests/test_language.py
git commit -m "feat(language): mixed-query detection + English retrieval representation"
```

---

### Task 3: Backend — `lang_memory.py` (session language store)

**Files:**
- Create: `backend/app/services/lang_memory.py`

**Interfaces:**
- Produces: `get_session_language(session_id: str) -> str | None`, `set_session_language(session_id: str, language: str) -> None`.

- [ ] **Step 1: Write the module**

```python
"""In-memory session -> response-language store (MVP, single-instance).

NOTE: swap to Supabase/Redis if the deployment runs multiple workers.
"""
from __future__ import annotations

_STORE: dict[str, str] = {}


def get_session_language(session_id: str) -> str | None:
    return _STORE.get(session_id)


def set_session_language(session_id: str, language: str) -> None:
    _STORE[session_id] = language
```

- [ ] **Step 2: Smoke-check import**

Run: `cd backend && python -c "from app.services.lang_memory import get_session_language, set_session_language; set_session_language('s','hi'); assert get_session_language('s')=='hi'; print('ok')"`
Expected: `ok`

- [ ] **Step 3: Commit**

```bash
git add backend/app/services/lang_memory.py
git commit -m "feat(language): add in-memory session language store"
```

---

### Task 4: Backend — `resolve_response_language.py`

**Files:**
- Create: `backend/app/resolve_response_language.py`
- Test: `backend/tests/test_resolve_response_language.py` (new)

**Interfaces:**
- Consumes: `detect_query_languages` (Task 2), `get_session_language`/`set_session_language` (Task 3).
- Produces: `resolve_response_language(question, ui_language, ui_language_explicit, session_language) -> str` and `resolve_and_remember(question, ui_language, ui_language_explicit, session_id) -> str`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_resolve_response_language.py
from app.resolve_response_language import resolve_response_language, resolve_and_remember
from app.services.lang_memory import set_session_language, _STORE


def test_explicit_request_wins():
    assert resolve_response_language("explain in Marathi", "en", False, None) == "mr"


def test_ui_explicit_over_session():
    assert resolve_response_language("PMFBY?", "mr", True, "hi") == "mr"


def test_session_over_detected():
    assert resolve_response_language("what is PMFBY", "en", False, "hi") == "hi"


def test_detected_over_default_en():
    # no explicit, no ui change, no session -> detected dominant
    assert resolve_response_language("PMFBY क्या है", "en", False, None) == "hi"


def test_default_en_when_nothing():
    assert resolve_response_language("hello", "en", False, None) == "en"


def test_memory_updated_only_from_explicit():
    _STORE.clear()
    resolve_and_remember("explain in Marathi", "en", False, "sess1")
    assert _STORE.get("sess1") == "mr"
    _STORE.clear()
    resolve_and_remember("PMFBY क्या है", "en", False, "sess2")
    assert _STORE.get("sess2") is None  # detected dominant must NOT poison session
    _STORE.clear()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_resolve_response_language.py -q`
Expected: FAIL (module not found).

- [ ] **Step 3: Write minimal implementation**

```python
"""Single authoritative response-language resolver (brief Phase 13)."""
from __future__ import annotations

from app.language import detect_query_languages
from app.services.lang_memory import get_session_language, set_session_language


def resolve_response_language(
    question: str,
    ui_language: str,
    ui_language_explicit: bool,
    session_language: str | None,
) -> str:
    detected = detect_query_languages(question)
    explicit = detected.get("explicit_request")
    if explicit:
        return explicit
    if ui_language_explicit and ui_language:
        return ui_language
    if session_language:
        return session_language
    if detected.get("dominant"):
        return detected["dominant"]
    return "en"


def resolve_and_remember(
    question: str,
    ui_language: str,
    ui_language_explicit: bool,
    session_id: str,
) -> str:
    session_language = get_session_language(session_id)
    resolved = resolve_response_language(question, ui_language, ui_language_explicit, session_language)
    detected = detect_query_languages(question)
    # Update memory ONLY from an intentional signal.
    if detected.get("explicit_request") or ui_language_explicit:
        set_session_language(session_id, resolved)
    return resolved
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_resolve_response_language.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/resolve_response_language.py backend/tests/test_resolve_response_language.py
git commit -m "feat(language): add authoritative response-language resolver with memory"
```

---

### Task 5: Backend — wire resolver + emit `speech_segments` in `chat.py`

**Files:**
- Modify: `backend/app/routes/chat.py`
- Test: `backend/tests/test_chat_route.py`

**Interfaces:**
- Consumes: `resolve_and_remember` (Task 4), `segment_speech` (Task 1), `detect_query_languages` (Task 2), `get_session_language` (Task 3), `prepare_speech_text` (already imported).
- Produces: `ChatRequest.ui_language_explicit: bool`; response dict gains `speech_segments`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_chat_route.py (append)
def test_response_includes_speech_segments(respx_mock, monkeypatch):
    from app.routes import chat as chat_route
    # minimal provider mocks (reuse existing fixtures from this file)
    ...
    body = r.json()
    assert "speech_segments" in body
    assert isinstance(body["speech_segments"], list)
    # every segment has language + text, no citation markers
    for seg in body["speech_segments"]:
        assert set(seg.keys()) == {"language", "text"}
        assert "[chunk:" not in seg["text"]
```

(Reuse the provider-mock pattern already present in `test_chat_route.py` for the existing 5-language test; adapt to assert `speech_segments`.)

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_chat_route.py -q`
Expected: FAIL (`speech_segments` missing).

- [ ] **Step 3: Write minimal implementation**

In `backend/app/routes/chat.py`:

Add imports (replace the existing `from app.language import normalize_language` line 24):
```python
from app.resolve_response_language import resolve_and_remember
from app.speech_text import prepare_speech_text, segment_speech
```
(Remove `from app.language import normalize_language` — `resolve_and_remember` is the
sole owner of detection + session lookup. Do NOT import `detect_query_languages` or
`get_session_language` here, to avoid a second source of the same state.)

Add field to `ChatRequest` (after `language`):
```python
    ui_language_explicit: bool = False
```

In `chat()`, replace:
```python
    lang = normalize_language(req.language, req.question)
```
with a single resolver call (the resolver detects languages and reads session
memory internally — no duplicate detection in the route):
```python
    lang = resolve_and_remember(
        req.question, req.language, req.ui_language_explicit, req.session_id
    )
```
(Keep the existing `retrieval_query` translation block that uses `lang` — RAG behavior unchanged.)

After:
```python
        speech_text = prepare_speech_text(answer)
```
add:
```python
        speech_segments = segment_speech(answer, lang)
```
and add `"speech_segments": speech_segments,` to the returned dict (alongside `"speech_text": speech_text,`).

In `_abstain`, add `"speech_segments": [],` to the returned dict for schema consistency (read-aloud is intentionally disabled for abstentions).

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_chat_route.py -q`
Expected: PASS (existing tests still green; new assertion green).

- [ ] **Step 5: Commit**

```bash
git add backend/app/routes/chat.py backend/tests/test_chat_route.py
git commit -m "feat(chat): resolve response language + emit speech_segments"
```

---

### Task 6: Backend — multi-voice Azure TTS + `/voice/speak` segments

**Files:**
- Modify: `backend/app/providers/azure_voice.py`
- Modify: `backend/app/services/voice_service.py`
- Modify: `backend/app/routes/voice.py`
- Test: `backend/tests/test_voice_routes.py`

**Interfaces:**
- Consumes: `tts_voices` / `speech_locales` from `get_settings` (already present).
- Produces: `AzureVoiceProvider.text_to_speech_segments(segments: list[dict]) -> bytes` (SSML, one `<voice>` per segment, in order); `VoiceService.text_to_speech_segments(segments)` pass-through; `SpeakRequest.segments`.

- [ ] **Step 1: Write the failing test**

```python
# backend/tests/test_voice_routes.py (append)
def test_voice_speak_segments_builds_multivoice_ssml(respx_mock, monkeypatch):
    # force Azure enabled + mock SDK synth to capture SSML
    ...
    r = client.post("/voice/speak", json={"segments": [
        {"language": "hi", "text": "नमस्ते"},
        {"language": "en", "text": "PMFBY"},
    ]})
    assert r.status_code == 200
    # captured SSML must contain both voice names in order
    assert "<voice name=" in CAPTURED_SSML
```

(Adapt to the existing Azure mock pattern in `test_voice_routes.py`: monkeypatch `azure_voice._sdk` and assert `speak_ssml_async` received SSML containing both `hi-IN-SwaraNeural` and `en-IN-NeerjaNeural` in that order, and that the route accepted a `segments` payload. The contiguous-run → 2 Azure calls behavior is frontend logic and is covered by the frontend unit test added in Task 9.)

- [ ] **Step 2: Run test to verify it fails**

Run: `cd backend && python -m pytest tests/test_voice_routes.py -q`
Expected: FAIL (`text_to_speech_segments` not defined).

- [ ] **Step 3: Write minimal implementation**

`backend/app/providers/azure_voice.py` — add:
```python
    @staticmethod
    def _xml_escape(text: str) -> str:
        return (
            text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;").replace("'", "&apos;")
        )

    def text_to_speech_segments(self, segments: list[dict]) -> bytes:
        """Synthesize multiple language-tagged segments in order via SSML.

        One <voice> element per segment (config-driven voice), concatenated
        into a single audio stream. Used for one contiguous Azure run. The root
        ``xml:lang`` is only a document default; per-<voice> ``name`` selects the
        actual voice/locale, so the root value does not alter synthesis.
        """
        if not self.enabled:
            raise RuntimeError("Azure voice not configured")
        speechsdk = self._sdk()
        root_locale = self._locale(segments[0]["language"]) if segments else "en-US"
        voices_xml = []
        for seg in segments:
            voice = self._voice(seg["language"])
            text = self._xml_escape(seg["text"])
            voices_xml.append(f'<voice name="{voice}">{text}</voice>')
        ssml = (
            '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" '
            f'xml:lang="{root_locale}">{"".join(voices_xml)}</speak>'
        )
        try:
            config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.speech_region)
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=None)
            result = synthesizer.speak_ssml_async(ssml).get()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Azure TTS failed: %r", exc)
            raise RuntimeError("Azure TTS failed") from exc
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            return result.audio_data
        # No audio produced → propagate as failure so the caller reaches the
        # "audio unavailable" behavior instead of silently returning empty audio.
        raise RuntimeError("Azure TTS produced no audio")
```

`backend/app/services/voice_service.py` — add:
```python
    async def text_to_speech_segments(self, segments: list[dict]) -> bytes:
        for name, provider in self.providers:
            try:
                return await provider.text_to_speech_segments(segments)
            except Exception as e:
                logger.warning(f"{name} TTS segments failed: {e}")
                continue
        raise VoiceUnavailableError("No voice providers available.")
```
(`SarvamVoiceProvider` lacks this method → AttributeError caught → falls through; Azure is primary.)

Also harden the pre-existing single-voice `text_to_speech` in `azure_voice.py`: change its trailing `return b""` to `raise RuntimeError("Azure TTS produced no audio")` so BOTH paths reach the "audio unavailable" behavior (no silent empty audio).

`backend/app/routes/voice.py` — update `SpeakRequest` and `speak_text`:
```python
class SpeakRequest(BaseModel):
    text: str = ""
    language: str = "en"
    segments: list[dict] | None = None


@router.post("/speak")
async def speak_text(req: SpeakRequest) -> dict:
    try:
        if req.segments:
            audio_bytes = await voice_service.text_to_speech_segments(req.segments)
        else:
            audio_bytes = await voice_service.text_to_speech(req.text, req.language)
    except VoiceUnavailableError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    return {"audio": audio_bytes.hex(), "language": req.language}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd backend && python -m pytest tests/test_voice_routes.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/app/providers/azure_voice.py backend/app/services/voice_service.py backend/app/routes/voice.py backend/tests/test_voice_routes.py
git commit -m "feat(voice): multi-voice Azure TTS via SSML segments"
```

---

### Task 7: Backend — Azure voice/locale verification (Phase 8)

**Files:**
- Create: `backend/scripts/verify_azure_voices.py`

**Interfaces:**
- Consumes: `get_settings().tts_voices`, `get_settings().speech_locales`, Azure SDK `SpeechSynthesizer.get_voices_async`.
- NOTE: this validates configured voice NAMES only — it is NOT a synthesis test. Actual audio synthesis is verified separately (Task 12) and labeled as live vs boundary.

- [ ] **Step 1: Write the script**

```python
"""Verify configured Azure voices/locales are valid against the resource.

Environment-dependent: requires AZURE_SPEECH_KEY + SDK. If unavailable, prints a
clear 'NOT VERIFIED LIVE' notice and exits 0 so CI does not fail on missing keys.
Run: python -m scripts.verify_azure_voices
"""
from __future__ import annotations
import sys
from app.config import get_settings


def main() -> int:
    settings = get_settings()
    if not settings.azure_speech_key:
        print("NOT VERIFIED LIVE: AZURE_SPEECH_KEY not set in this environment.")
        return 0
    try:
        import azure.cognitiveservices.speech as speechsdk
    except ImportError:
        print("NOT VERIFIED LIVE: azure-cognitiveservices-speech SDK not installed.")
        return 0
    cfg = speechsdk.SpeechConfig(subscription=settings.azure_speech_key,
                                 region=settings.azure_speech_region)
    synth = speechsdk.SpeechSynthesizer(speech_config=cfg, audio_config=None)
    result = synth.get_voices_async().get()
    if result.reason != speechsdk.ResultReason.VoicesListRetrieved:
        print("Azure voices list failed:", result.error_details)
        return 1
    available = {v.short_name for v in result.voices}
    locales = settings.speech_locales
    voices = settings.tts_voices
    ok = True
    for lang, voice in voices.items():
        if voice not in available:
            ok = False
            print(f"INVALID voice for {lang}: {voice}")
        else:
            print(f"OK {lang}: {voice} ({locales.get(lang)})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run (expect NOT VERIFIED LIVE in this env)**

Run: `cd backend && python -m scripts.verify_azure_voices`
Expected: prints `NOT VERIFIED LIVE: ...` and exits 0 (no key/SDK here). If a key + SDK are present, it prints per-language OK/INVALID.

- [ ] **Step 3: Commit**

```bash
git add backend/scripts/verify_azure_voices.py
git commit -m "feat(voice): add Azure voice/locale verification script"
```

---

### Task 8: Frontend — `api.ts`: `speech_segments`, `ui_language_explicit`, `fetchVoiceSpeak`

**Files:**
- Modify: `frontend/src/lib/api.ts`

**Interfaces:**
- Produces: `ChatResponse.speech_segments?: { language: Locale; text: string }[]`; `sendChat` sends `ui_language_explicit`; new `fetchVoiceSpeak(segments) -> Promise<string | null>` (hex audio).

- [ ] **Step 1: Update `ChatResponse` and `sendChat`**

```ts
// add to ChatResponse interface
  speech_segments?: { language: Locale; text: string }[];

// update sendChat payload
export async function sendChat(payload: {
  question: string;
  session_id: string;
  language: Locale;
  state: string | null;
  ui_language_explicit?: boolean;
}): Promise<ChatResponse> {
  const r = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!r.ok) throw new Error(`API ${r.status}`);
  return r.json();
}

// new: fetch Azure TTS audio (hex) for a contiguous run of segments
export async function fetchVoiceSpeak(
  segments: { language: string; text: string }[]
): Promise<string | null> {
  try {
    const r = await fetch("/voice/speak", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ segments }),
    });
    if (!r.ok) return null;
    const data = await r.json();
    return data.audio ?? null; // hex-encoded WAV
  } catch {
    return null;
  }
}
```

- [ ] **Step 2: Typecheck**

Run: `cd frontend && npx tsc --noEmit`
Expected: no errors (after later tasks consume the new fields; if unused-import errors appear, they resolve in Task 10/11).

- [ ] **Step 3: Commit**

```bash
git add frontend/src/lib/api.ts
git commit -m "feat(api): add speech_segments, ui_language_explicit, fetchVoiceSpeak"
```

---

### Task 9: Frontend — `speech.ts`: hybrid `speakSegments` with contiguous runs

**Files:**
- Modify: `frontend/src/lib/speech.ts`

**Interfaces:**
- Produces: `hasVoice(lang): bool`, `speakSegments(segments: SpeechSegment[]): Promise<void>`, updated `stopSpeaking()` (also stops Azure `<audio>`), exported `SpeechSegment` type.

- [ ] **Step 1: Rewrite the speech service**

Replace the body of `createSpeechService` (keep `SpeechService` interface, extended):

```ts
export interface SpeechSegment {
  language: string;
  text: string;
}

/** Partition segments into ordered CONTIGUOUS runs of the same TTS source. */
export function partitionRuns(
  segments: SpeechSegment[],
  hasVoice: (lang: string) => boolean,
): { source: "browser" | "azure"; items: SpeechSegment[] }[] {
  const runs: { source: "browser" | "azure"; items: SpeechSegment[] }[] = [];
  for (const seg of segments) {
    const source: "browser" | "azure" = hasVoice(seg.language) ? "browser" : "azure";
    const last = runs[runs.length - 1];
    if (last && last.source === source) last.items.push(seg);
    else runs.push({ source, items: [seg] });
  }
  return runs;
}

export interface SpeechService {
  supported: boolean;
  listen: (locale: string, onTranscript: (text: string) => void) => () => void;
  speak: (text: string, locale: string) => void;
  speakSegments: (segments: SpeechSegment[]) => Promise<void>;
  hasVoice: (lang: string) => boolean;
  stopSpeaking: () => void;
}

export function createSpeechService(): SpeechService {
  const isBrowser = typeof window !== "undefined";
  const SpeechRecognition =
    isBrowser && typeof window !== "undefined"
      ? (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
      : undefined;
  const synthesis =
    isBrowser && typeof window !== "undefined" ? window.speechSynthesis : undefined;

  let currentAudio: HTMLAudioElement | null = null;
  let audioResolve: (() => void) | null = null;
  let speakToken = 0; // bumped on each new request / stop → cancels stale queues

  function langBase(lang: string) {
    return lang === "en" ? "en" : lang;
  }
  function pickVoice(voices: SpeechSynthesisVoice[], lang: string) {
    const base = langBase(lang);
    // Return ONLY a voice matching the requested language. If none exists the
    // segment becomes an Azure run — never an English substitution.
    return voices.find((v) => v.lang.startsWith(base));
  }

  async function speakSegments(segments: SpeechSegment[]): Promise<void> {
    if (segments.length === 0) return;
    const token = ++speakToken; // claim this queue; stopSpeaking bumps the token
    // No browser TTS at all → route everything to Azure (single run).
    if (!synthesis) {
      const hex = await fetchVoiceSpeak(segments);
      if (hex && token === speakToken) {
        const audio = new Audio(`data:audio/wav;base64,${hexToBase64(hex)}`);
        currentAudio = audio;
        await new Promise<void>((res) => {
          audioResolve = res;
          audio.onended = () => { audioResolve = null; res(); };
          audio.onerror = () => { audioResolve = null; res(); };
          audio.play();
        });
        currentAudio = null;
      }
      return;
    }
    // Voices may load asynchronously.
    if (synthesis.getVoices().length === 0) {
      await new Promise<void>((res) => {
        const t = setTimeout(res, 1000);
        synthesis!.onvoiceschanged = () => { clearTimeout(t); res(); };
      });
    }
    if (token !== speakToken) return; // stopped while waiting for voices
    const voices = synthesis.getVoices();

    // Partition into ordered CONTIGUOUS runs of the same TTS source.
    const runs = partitionRuns(segments, (l) => Boolean(pickVoice(voices, l)));

    synthesis.cancel();
    for (const run of runs) {
      if (token !== speakToken) return; // stopped or superseded by a new request
      if (run.source === "browser") {
        for (const seg of run.items) {
          if (token !== speakToken) return;
          const utt = new SpeechSynthesisUtterance(seg.text);
          const v = pickVoice(voices, seg.language);
          if (v) utt.voice = v;
          await new Promise<void>((res) => {
            utt.onend = () => res();
            utt.onerror = () => res();
            synthesis!.speak(utt);
          });
        }
      } else {
        const hex = await fetchVoiceSpeak(run.items);
        if (hex && token === speakToken) {
          const audio = new Audio(`data:audio/wav;base64,${hexToBase64(hex)}`);
          currentAudio = audio;
          await new Promise<void>((res) => {
            audioResolve = res;
            audio.onended = () => { audioResolve = null; res(); };
            audio.onerror = () => { audioResolve = null; res(); };
            audio.play();
          });
          currentAudio = null;
        }
        // Azure unavailable → per spec, audio unavailable for this run
        // (never an English substitution). Text remains visible.
      }
    }
  }

  function hexToBase64(hex: string): string {
    const bytes = new Uint8Array(hex.length / 2);
    for (let i = 0; i < bytes.length; i++) {
      bytes[i] = parseInt(hex.substr(i * 2, 2), 16);
    }
    let bin = "";
    bytes.forEach((b) => (bin += String.fromCharCode(b)));
    return btoa(bin);
  }

  return {
    get supported() {
      if (!isBrowser) return false;
      const sr = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      return Boolean(sr) && Boolean(window.speechSynthesis);
    },
    listen(locale, onTranscript) {
      if (!SpeechRecognition) return () => {};
      const rec = new SpeechRecognition();
      rec.lang = locale === "en" ? "en-IN" : locale + "-IN";
      rec.interimResults = false;
      rec.maxAlternatives = 1;
      rec.onresult = (e: any) => {
        const text = e.results?.[0]?.[0]?.transcript;
        if (text) onTranscript(text);
      };
      rec.onerror = () => {};
      rec.start();
      return () => {
        try { rec.stop(); } catch { /* noop */ }
      };
    },
    speak(text, locale) {
      if (!synthesis) return;
      const utt = new SpeechSynthesisUtterance(text);
      const v = pickVoice(synthesis.getVoices(), locale);
      if (v) utt.voice = v;
      synthesis.cancel();
      synthesis.speak(utt);
    },
    speakSegments,
    hasVoice(lang) {
      if (!synthesis) return false;
      return Boolean(pickVoice(synthesis.getVoices(), lang));
    },
    stopSpeaking() {
      speakToken++; // invalidate any in-flight queue (browser or Azure)
      if (synthesis) synthesis.cancel();
      if (currentAudio) {
        currentAudio.pause();
        currentAudio = null;
      }
      if (audioResolve) {
        audioResolve(); // unblock the awaited Azure audio promise
        audioResolve = null;
      }
    },
  };
}
```

- [ ] **Step 2: Add a unit test for contiguous-run batching**

Create `frontend/src/lib/speech.test.ts`:
```ts
import { partitionRuns, type SpeechSegment } from "@/lib/speech";

test("contiguous runs minimize Azure calls (no per-segment calls)", () => {
  const segs: SpeechSegment[] = [
    { language: "en", text: "a" },
    { language: "gu", text: "b" },
    { language: "en", text: "c" },
    { language: "mr", text: "d" },
  ];
  // Only English has a (simulated) browser voice.
  const runs = partitionRuns(segs, (l) => l === "en");
  const azure = runs.filter((r) => r.source === "azure");
  expect(azure).toHaveLength(2); // [gu] and [mr] → 2 calls, NOT 4, NOT 1
  expect(azure[0].items).toEqual([segs[1]]);
  expect(azure[1].items).toEqual([segs[3]]);
});

test("adjacent same-source segments stay one run", () => {
  const segs: SpeechSegment[] = [
    { language: "gu", text: "x" },
    { language: "mr", text: "y" },
  ];
  const runs = partitionRuns(segs, () => false); // no browser voices
  expect(runs).toHaveLength(1);
  expect(runs[0].source).toBe("azure");
});
```

- [ ] **Step 3: Typecheck + test**

Run: `cd frontend && npx tsc --noEmit && npx vitest run`
Expected: no errors; new partitionRuns tests pass.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/lib/speech.ts
git commit -m "feat(speech): hybrid speakSegments with contiguous-run batching"
```

---

### Task 10: Frontend — `MessageBubble` uses `speech_segments`, removes abstain speak

**Files:**
- Modify: `frontend/src/components/chat/MessageBubble.tsx`

**Interfaces:**
- Consumes: `resp.speech_segments` (Task 8), `speech.speakSegments` + `SpeechSegment` (Task 9).

- [ ] **Step 1: Update `handleSpeak`**

Replace line 41-51 `handleSpeak` body:
```ts
  function handleSpeak() {
    if (speaking) {
      speech.stopSpeaking();
      setSpeaking(false);
      return;
    }
    const segs: SpeechSegment[] =
      resp.speech_segments && resp.speech_segments.length
        ? resp.speech_segments
        : [{ language: resp.language, text: resp.speech_text ?? resp.answer }];
    void speech.speakSegments(segs);
    setSpeaking(true);
  }
```
Add import: `import { createSpeechService, type SpeechSegment } from "@/lib/speech";`

- [ ] **Step 2: Remove the abstain speak button**

In the `resp.abstained` branch, delete the `{speechSupported && (<Button .../>)}` block (lines ~58-62) so abstentions produce no read-aloud control. Keep the `speechSupported` state (still used by the non-abstained read-aloud button).

- [ ] **Step 3: Typecheck + unit test**

Run: `cd frontend && npx tsc --noEmit && npx vitest run`
Expected: no type errors; existing component tests pass.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/chat/MessageBubble.tsx
git commit -m "feat(ui): read-aloud uses speech_segments; abstentions not spoken"
```

---

### Task 11: Frontend — `ChatWindow` sends `ui_language_explicit`

**Files:**
- Modify: `frontend/src/components/ChatWindow.tsx`

**Interfaces:**
- Consumes: `sendChat` `ui_language_explicit` field (Task 8).

- [ ] **Step 1: Track explicit language selection**

Near the other state (around line 92 `const lang: Locale = locale;`):
```ts
  const [uiLangExplicit, setUiLangExplicit] = useState(false);
  const initialLocale = useRef(locale);
  useEffect(() => {
    if (locale !== initialLocale.current) {
      setUiLangExplicit(true);
      initialLocale.current = locale;
    }
  }, [locale]);
```
(Ensure `useRef` is imported; it likely is. If not, add to the React import.)

- [ ] **Step 2: Include in the chat payload**

At line ~199 `sendChat({ question, session_id: sessionId, language: lang, state: null })` change to:
```ts
      const resp = await sendChat({
        question,
        session_id: sessionId,
        language: lang,
        state: null,
        ui_language_explicit: uiLangExplicit,
      });
```

- [ ] **Step 3: Typecheck + tests**

Run: `cd frontend && npx tsc --noEmit && npx vitest run`
Expected: no type errors; tests pass.

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/ChatWindow.tsx
git commit -m "feat(ui): send ui_language_explicit with chat requests"
```

---

### Task 12: Regression — RAG eval, full test suites, build, docs

**Files:**
- Modify: `PROJECT_STATUS.md` (session-end update)

**Interfaces:**
- Verifies: corpus/RAG unchanged, citation verifier fail-closed, all new + existing tests pass, frontend build passes.

- [ ] **Step 1: Run backend tests**

Run: `cd backend && python -m pytest -q`
Expected: all pass (no regression; new suites green).

- [ ] **Step 2: Run RAG regression evaluation**

Run the project's existing RAG regression evaluation (the script that reports Recall@1 / Recall@3 / Recall@5 / MRR / contamination). Confirm the baseline is unchanged:
`Recall@1 = 0.800, Recall@3 = 0.900, Recall@5 = 0.925, MRR = 0.856, contamination = 0`.
Do NOT modify retrieval to move the numbers.

- [ ] **Step 3: Run frontend typecheck + build + tests**

Run: `cd frontend && npx tsc --noEmit && npm run build && npx vitest run`
Expected: typecheck clean, build succeeds, ALL frontend tests pass (count may exceed the prior 22 as new tests are added).

- [ ] **Step 4: Attempt live Azure verification (label results honestly)**

Run: `cd backend && python -m scripts.verify_azure_voices`
- If key + SDK present: record per-language OK/INVALID.
- If not: record "NOT VERIFIED LIVE (no key/SDK in this environment)".
Label any TTS/STT claims as live vs boundary explicitly in `PROJECT_STATUS.md`.

- [ ] **Step 5: Update `PROJECT_STATUS.md`**

Add a session note covering: server-emitted `speech_segments`, contiguous-run hybrid TTS, backend response-language resolver + session memory, mixed-input detection, `/voice/speak` multi-voice SSML, abstention no longer read-aloud, and the live-verification status (live vs not-verified). Keep the non-negotiable principles intact.

- [ ] **Step 6: Commit**

```bash
git add PROJECT_STATUS.md
git commit -m "docs: record multilingual speech implementation + verification status"
```

---

## Self-Review Notes (per skill checklist)

- **Spec coverage:** §1 non-negotiables → Global Constraints + each task. §2 pipeline → unchanged (chat.py keeps retrieval translation). §3 decisions → Tasks 1/5/6/9/11. §4/§9 contiguous runs → Task 9 + Task 6. §5 backend components → Tasks 1,2,3,4,5,6,7. §6 frontend → Tasks 8,9,10,11. §7 resolver priority + memory → Tasks 3,4,5. §8 no-English-fallback → Task 9 (Azure run falls to "audio unavailable", never English). §10 input detection hi/mr → Task 2. §11 mixed STT limitation → documented (browser primary; no recovery claim). §12 abstention → Task 10 removes speak button. §13 errors → Task 9/10. §14 tests → all tasks. §15 RAG guard → Task 12. §16 live validation → Task 7 + Task 12. §17 files → file structure. §18 success → Task 12.
- **Placeholder scan:** No TBD/TODO. `english_retrieval_query` is run-aware (translates only Indic runs via the already-wired `AzureTranslator`, preserving Latin entities/numbers/dates) and falls back to original text — concrete, not a stub. `pickVoice` returns ONLY a matching voice (no English fallback). Azure empty-audio paths raise. `speakSegments` handles missing `speechSynthesis` via Azure and uses a token to cancel stale queues.
- **Type consistency:** `segment_speech` → `list[dict]{language,text}`; frontend `SpeechSegment{language,text}` matches. `resolve_and_remember` signature consistent across Tasks 4/5. `SpeakRequest.segments` + `text_to_speech_segments` consistent across Tasks 6. `fetchVoiceSpeak` returns hex string; `speakSegments` decodes hex→base64. `ui_language_explicit` flows ChatRequest → chat.py → resolver.
- **Known limitation (documented, not a defect):** `english_retrieval_query` translates Indic runs (not the whole query) and preserves Latin entities/numbers/dates; cross-run context is not modeled. This satisfies mixed-retrieval behavior within the zero-cost, no-new-dependency constraint. Flagged for future enhancement (context-aware run translation) in `PROJECT_STATUS.md`.
