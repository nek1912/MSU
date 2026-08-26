# Sources, Tools, APIs, and Open-Source Code

Everything here was checked against a live source as of 2026-08-26. Free-tier
terms change — re-verify quotas on Day 1 against the actual account you sign up
with, not against this document alone.

## Hosted APIs (cloud, free tier)

| Purpose | Service | Where | Caveat |
|---|---|---|---|
| Hindi STT/TTS/translation | Bhashini (ULCA) | https://bhashini.gitbook.io/bhashini-apis | Free, government-run, self-serve registration at bhashini.gov.in. Suitable for PoC/hackathon; production/commercial use may need separate arrangement. Register on Day 1 — approval lead time is unverified. |
| Embeddings | Gemini API, `gemini-embedding-2` @ 768 dims | https://ai.google.dev/gemini-api/docs/embeddings | Stable GA (2026-04), per-string embeddings with auto-renormalized reduced dims, official replacement for `gemini-embedding-001` (shutdown 2028-05-14). Phase 0 guard: smoke-test N inputs → N distinct vectors before ingesting. Re-verify free-tier quotas on account creation. |
| LLM (fast, primary) | Groq | https://console.groq.com/docs/rate-limits | No credit card. Confirmed free-tier ballpark: ~30 RPM, several thousand TPM, ~1,000-14,400 RPD depending on model — check console.groq.com for the current per-model numbers, they vary by model. |
| LLM (fallback) | Gemini 2.5 Flash | https://ai.google.dev/gemini-api/docs/pricing | Free tier confirmed generous (~1,500 RPD, 1M TPM as of mid-2026) but Google's own docs warn free-tier inputs/outputs may be used to improve their models — don't send real grievance PII through this path. |
| STT fallback | Groq-hosted Whisper v3 Turbo | https://console.groq.com/docs | Hosted, no GPU required on your side. |

## Infrastructure (free tier)

| Purpose | Service | Where | Caveat |
|---|---|---|---|
| Frontend hosting | Vercel Hobby | https://vercel.com/docs/plans/hobby | Personal/non-commercial eligibility terms — read them, a hackathon submission is normally fine but check. |
| Frontend alternative | Render Static Site | https://render.com/docs/free | Free static hosting, no card. |
| Backend hosting | Render Free | https://render.com/docs/free | Sleeps after inactivity, cold starts on wake, ephemeral filesystem — don't store anything on local disk you need to persist. |
| Database + vectors | Supabase Free + pgvector | https://supabase.com/docs/guides/database/extensions/pgvector | ~500MB DB on free tier, HNSW indexing supported. Free projects may pause after a period of inactivity — reactivate before demos and rehearsals. |

## Open-source code (reference or dependency, with license)

| Repository | Use | License | URL |
|---|---|---|---|
| OpenNyAI Jugalbandi Manager | Reference reading for multilingual conversation, retriever, and grievance-flow patterns. Real repo, Apache-2.0, but thin documentation (an "installation instructions missing" issue sat open for over a year) — treat as design reference, not a cloned dependency. | Apache-2.0 | https://github.com/OpenNyAI/Jugalbandi-Manager |
| Docling | PDF/DOCX → structured Markdown/JSON for ingestion | MIT | https://github.com/docling-project/docling |
| FAISS | Local retrieval testing before/alongside pgvector | MIT | https://github.com/facebookresearch/faiss |
| Bhashini ULCA | Language-layer reference / SDK patterns | MIT | https://github.com/bhashini-dibd/ulca |
| Bhashini Lekhaanuvaad | Indic document-translation reference | MIT | https://github.com/bhashini-dibd/lekhaanuvaad |
| AI4Bharat IndicTrans2 | Translation reference only — do not self-host for this project, use Bhashini's hosted API instead | MIT | https://github.com/AI4Bharat/IndicTrans2 |
| IndicLID | Indian-language identification | MIT | https://github.com/AI4Bharat/IndicLID |
| Ragas | RAG evaluation (eval-time only, not a runtime dependency) | Apache-2.0 | https://github.com/vibrantlabsai/ragas (formerly explodinggradients/ragas — same project, org renamed) |
| DeepEval | Alternative LLM/RAG eval harness | Verify current license before depending on it | https://github.com/confident-ai/deepeval |

### Explicitly not used — and why

| Repository | Why it's out |
|---|---|
| NyayaSetu-Offline-Multilingual-AI (ShAuRyA-Noodle) | Could not be independently verified in search — no stars, forks, or discussion anywhere. Don't build the grievance module around an unverified repo. If someone on the team has personally opened it and confirmed its state, that's a decision to log in DECISIONS.md, not to assume. |
| COSS-India VoicEra / voicera_mono_repository | Real, and actually mirrored under the official `bhashini-dibd` GitHub org — so it's more credible than it first appeared. Still not adopted directly: it's a fuller telephony/voice stack than this MVP needs. Worth skimming for the voice-server pattern if Bhashini's direct API proves awkward to integrate. |

## Official content sources (curated manifest, not a generic scraper)

- Ministry of Cooperation — schemes, Model PACS Byelaws, PACS information
- PMFBY official portal — operational guidelines, FAQ, scheme documentation
- Selected state cooperative department — cooperative act, rules, state-specific
  notifications (pick the state on Day 1, see PROJECT_STATUS.md)
- RBI — financial-literacy material
- PMJDY — financial-literacy material
- Relevant government grievance documentation — categories, workflow, escalation
  information (for classification examples only, not for a claimed integration)

Curate roughly 8-15 high-value scheme/service documents plus the domain-specific
legal, agriculture, financial-literacy, and grievance documents. Don't try to be
exhaustive — useful user journeys beat document count.

Each entry in `sources.yaml` should contain: `id, url, organization, domain,
jurisdiction, state, document_type, effective_date, verified_date`.
