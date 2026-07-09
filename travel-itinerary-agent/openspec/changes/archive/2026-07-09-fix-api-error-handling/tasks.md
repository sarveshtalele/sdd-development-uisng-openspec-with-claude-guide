## 1. Implementation

- [x] 1.1 Catch `openai.APIError` in `generate_itinerary` and re-raise as `ItineraryValidationError` with a clear message
- [x] 1.2 Confirm `cli.main` already handles `ItineraryValidationError` cleanly (no change expected, verify only)

## 2. Testing

- [x] 2.1 Add a `test_generator.py` case with a fake client whose `create` raises `openai.APIError`, asserting it surfaces as `ItineraryValidationError`
- [x] 2.2 Run the full test suite and confirm all tests pass
- [x] 2.3 Re-run the CLI live against the real proxy with a deliberately invalid API key and confirm a clean one-line error instead of a traceback
