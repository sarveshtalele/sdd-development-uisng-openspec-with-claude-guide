## Context

`generate_itinerary` in `itinerary/generator.py` calls `client.chat.completions.create`
directly. The `openai` Python SDK raises `openai.APIError` (and subclasses like
`AuthenticationError`, `RateLimitError`, `APIConnectionError`, `APIStatusError`) when
that call fails. Nothing in this codebase catches that exception family today, so it
propagates unchanged out of `generate_itinerary`, out of `cli.main`, and prints as a raw
Python traceback — the only failure mode in this tool that does not already exit cleanly
through the existing `ConfigError` / `ItineraryValidationError` pattern.

This was discovered by live-testing the CLI against a real OpenAI-compatible proxy with
a deliberately invalid API key.

## Goals / Non-Goals

**Goals:**
- Any failure raised by the `openai` client during the network call surfaces as a single
  clean error line on stderr and a non-zero exit code, matching the existing error
  convention in `cli.main`.
- No behavior change for the success path or for the existing malformed-response path.

**Non-Goals:**
- Retrying failed requests. A CLI tool that fails once and exits is acceptable; adding
  retry/backoff logic is out of scope for this fix.
- Distinguishing between different `openai.APIError` subclasses in the user-facing
  message. One generic "request failed" message covering the whole family is sufficient
  for a small CLI tool with no monitoring or alerting to differentiate for.

## Decisions

- **Catch `openai.APIError` (the SDK's common base class) in `generate_itinerary`,
  re-raised as `ItineraryValidationError`.** Alternative considered: catch it in
  `cli.main` instead, as its own `except` clause. Rejected because
  `ItineraryValidationError` already is the "something about getting a valid itinerary
  failed" error type `cli.main` knows how to handle, and reusing it avoids adding a
  second error type and a second `except` clause to `main` for what is, from the CLI's
  perspective, the same category of failure: the tool could not produce an itinerary.
- **Do not inspect or branch on the specific `APIError` subclass.** Alternative
  considered: give `AuthenticationError` a distinct message ("check your API key") from
  `RateLimitError` ("try again later"). Rejected for this change's scope — worth doing
  later if this tool grows real users, not justified for the current size.

## Risks / Trade-offs

- [Risk] Folding API errors into `ItineraryValidationError` slightly blurs that
  exception's original meaning ("the model's response was malformed") with a new one
  ("the request never got a response at all"). → Mitigation: the error message text
  itself states which case occurred, so the distinction is preserved for the user even
  though the exception type is shared.
