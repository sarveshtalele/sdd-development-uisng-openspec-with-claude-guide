## Why

Live verification against a real OpenAI-compatible endpoint (a LiteLLM proxy) surfaced
a real gap: an API-level failure (invalid API key, rate limit, connection error) is not
caught anywhere in the call path. It propagates out of `generate_itinerary` as a raw
`openai.APIError` (or a subclass), and `cli.py` has no handler for it, so the tool exits
with a full Python traceback instead of the clean, single-line error message it produces
for every other failure mode (missing config, malformed model output, bad arguments).

## What Changes

- `generate_itinerary` (or `cli.main`) catches `openai.APIError` (the base class for all
  SDK-raised API failures, including `AuthenticationError`, `RateLimitError`, and
  `APIConnectionError`) and surfaces it as an `ItineraryValidationError`-style clean
  message, consistent with how a malformed model response is already handled.
- `cli.main` prints that message to stderr and exits with status 1, the same convention
  already used for `ConfigError` and `ItineraryValidationError`.
- No change to argument parsing, configuration loading, rendering, or the JSON response
  contract — this is scoped to the one call site that talks to the network.

## Capabilities

### New Capabilities
(none)

### Modified Capabilities
- `travel-itinerary`: add a requirement that the system SHALL handle an API-level
  request failure by printing a clear error and exiting without a stack trace, rather
  than leaving this case unspecified.

## Impact

- `itinerary/generator.py`: wrap the `client.chat.completions.create` call.
- `itinerary/cli.py`: catch and handle the new error type alongside the existing ones.
- `tests/test_generator.py`: add a case using a fake client that raises an API-style
  error, confirming it surfaces as a clean, catchable error rather than propagating raw.
- Discovered via a live call through a real OpenAI-compatible proxy using an invalid API
  key, which reproduced an unhandled `openai.AuthenticationError` with a full traceback.
