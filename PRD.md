# Product Requirements Document

## Product

Multilingual, voice-capable, evidence-grounded citizen-assistance PWA for
cooperative governance, legal guidance, schemes, PMFBY, financial literacy, and
grievance redressal.

The system answers questions from official sources with citations, abstains when
evidence is insufficient, supports Hindi voice interaction, and supports a
prototype grievance workflow.

## Goals

1. Provide trustworthy, cited information about: cooperative law/by-laws, PACS,
   Ministry of Cooperation schemes, PMFBY, agriculture, financial literacy.
2. Support English text, Hindi text, and Hindi voice.
3. Provide grievance intake → follow-up → prototype reference → status lookup.
4. Deploy entirely in the cloud, no personal GPU, zero monetary cost for the
   hackathon demo.

## Non-goals (MVP)

Native Android, native iOS, WhatsApp integration, blockchain, custom model
training, self-hosted GPU inference, autonomous multi-agent systems, complex
authentication, analytics dashboard, real government grievance submission
(no public CPGRAMS API exists to integrate with), nationwide legal coverage.

## Target users

Cooperative members, farmers, and rural stakeholders seeking official guidance
in English or Hindi.

## Core requirements

1. English + Hindi text chat.
2. Central cooperative info + PACS info + ONE selected state's cooperative
   rules/by-laws. Mandatory metadata on every legal/cooperative answer:
   `jurisdiction, state, effective_date, verified_date`.
3. 8-15 curated official schemes/services (useful user journeys, not maximum
   document count).
4. PMFBY: FAQ, eligibility guidance, process guidance, grievance guidance.
5. 5-10 high-value agricultural workflows.
6. Curated RBI/PMJDY financial-literacy material.
7. Grievance: classify → extract entities → detect missing info → follow-up →
   create prototype reference → status lookup.
8. Voice: Hindi STT + TTS (Bhashini primary → Groq Whisper STT fallback →
   text-only fallback).
9. Domain routing + domain/jurisdiction-filtered RAG + grounded generation.
10. Citations, confidence, explicit abstention on every factual answer.
11. Responsive PWA (desktop + mobile browsers).
12. Demonstrably deployed in the cloud.

## API contracts (frozen Day 1)

```
POST /chat
POST /voice/transcribe
POST /voice/speak
POST /grievances
GET  /grievances/{reference}
GET  /sources/{id}
GET  /health
GET  /health/providers
```

**Chat response:** `answer, language, domain, confidence, citations[{title,page,url}],
abstained, follow_up_question`

**Grievance response:** `reference, status, missing_information[], is_official_submission`
(always `false`)

## Safety & trust requirements

1. Never fabricate facts, citations, or capabilities.
2. Every citation must map to a chunk retrieved in that request.
3. Low retrieval confidence forces abstention — not an LLM judgment call.
4. Never present national/model rules as universally applicable across states.
5. Grievances are prototypes, never official submissions.
6. Never expose provider API credentials.
7. Avoid sending real personal grievance data to free-tier LLM providers — use
   synthetic data for demo/testing.

## Success metrics (internal)

Groundedness, factual correctness, citation accuracy, latency, abstention
correctness, domain classification accuracy, jurisdiction accuracy, provider
fallback success. Demo reliability: three flagship stories run end-to-end
without failure (see PROJECT_STATUS.md for current status against these).

## Constraints

4 members, 10 days, zero budget, cloud-only, free tiers only, no personal GPU.
Free tiers have quotas, cold starts, and inactivity pauses — the architecture
must tolerate all three, not assume they won't happen.

## Risks

- "Completely free" holds for hackathon-scale demo traffic, not production —
  say this explicitly in the pitch, don't imply production-readiness.
- Free-tier limits: Bhashini is suitable for PoC/hackathon use (production/
  commercial use may need separate arrangements), Groq/Gemini have rate limits,
  Render sleeps on inactivity with cold starts, Supabase free projects may pause
  after inactivity, Vercel Hobby has personal/non-commercial eligibility terms.
- Legal coverage realism: central + one state only. Say this on screen in the demo.
- Scope creep: enforce the non-goals list. If someone proposes adding something
  from it before Tier 1 is stable, that's a decision for DECISIONS.md, not a
  silent addition.

## Definition of done (MVP / Tier 1)

Deployed PWA where a text question in English or Hindi flows through routing →
filtered RAG → grounded, cited answer, with correct abstention on unsupported
questions, and a grievance can be created and looked up. Voice is Tier 2.
