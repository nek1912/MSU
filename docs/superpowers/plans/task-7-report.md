# Task 7: Add Gemini Retry/Backoff

## Status: DONE

**Commit:** `d72aa68` — `feat: add retry with exponential backoff for embedding provider`

## What was done

Added retry logic with exponential backoff to `GeminiEmbeddingProvider` in `backend/app/providers/embeddings.py`.

### Changes

- **`backend/app/providers/embeddings.py`** — Extracted per-text embedding into `_embed_single()` with a retry loop (max 3 attempts, 1s base delay, exponential backoff). Retries on 429, 5xx, timeouts, and connection errors. Non-retryable errors (400, 401, etc.) raise immediately.

- **`backend/tests/test_embedding_retry.py`** — 6 tests:
  - `test_retry_on_rate_limit` — 429 retried twice, succeeds on 3rd attempt
  - `test_retry_on_server_error` — 500 retried once, succeeds on 2nd attempt
  - `test_non_retryable_error_raises_immediately` — 400 raises without retry
  - `test_retry_exhausted_raises_last_error` — after 3 failures, last exception is raised
  - `test_retry_on_timeout` — timeout retried once, succeeds on 2nd attempt
  - `test_success_on_first_attempt` — no retries on success

## Test summary

86 passed, 2 failed (pre-existing schema smoke tests requiring live Supabase connection — unrelated to this task). All 6 new tests pass.

## Concerns

None. The implementation follows the plan exactly. The exponential backoff is simple `delay * 2^attempt` which is appropriate for the Gemini API's rate limiting behavior. No jitter is added, but that's acceptable for an MVP with low concurrency.
