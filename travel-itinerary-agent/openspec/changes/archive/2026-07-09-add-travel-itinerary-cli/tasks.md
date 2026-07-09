## 1. Project scaffold

- [x] 1.1 Create the package layout (`itinerary/` package plus `pyproject.toml` or a
      `requirements.txt`, whichever is simpler for a single-package CLI tool)
- [x] 1.2 Add the `openai` package as the one runtime dependency

## 2. CLI argument parsing

- [x] 2.1 Implement `argparse`-based parsing for destination (required), days
      (required, positive integer), and optional preferences (pace, interests, budget)
- [x] 2.2 Reject a missing destination or missing/invalid days with a clear usage error,
      before any other logic runs

## 3. Configuration handling

- [x] 3.1 Implement a config-loading function that reads `OPENAI_API_KEY` (required),
      `OPENAI_BASE_URL` (optional, defaults to the standard OpenAI endpoint), and
      `ITINERARY_MODEL` (optional, with a sensible default) from the environment
- [x] 3.2 Fail with a specific, named error if `OPENAI_API_KEY` is unset, before any
      network call is attempted

## 4. Itinerary generation

- [x] 4.1 Implement `generate_itinerary(...)`, isolated from argument parsing and
      rendering, that builds the prompt, calls the model, and returns the raw response
- [x] 4.2 Define the expected itinerary JSON shape (one entry per day, each with an
      ordered list of activities)
- [x] 4.3 Implement validation of the model's response against that shape, raising a
      descriptive error on mismatch instead of allowing a malformed result through

## 5. Rendering

- [x] 5.1 Implement a renderer that takes a validated itinerary object and prints it as
      day-ordered plain text

## 6. Wiring and error handling

- [x] 6.1 Implement `main()` that wires argument parsing, configuration loading,
      generation, validation, and rendering together
- [x] 6.2 Ensure configuration and validation errors produce a clean, single-line error
      message and non-zero exit code, not a raw traceback

## 7. Verification without a live API key

- [x] 7.1 Verify argument parsing directly: valid inputs are accepted, missing or
      invalid inputs are rejected with the expected error
- [x] 7.2 Verify configuration loading directly: confirm the missing-`OPENAI_API_KEY`
      error fires correctly, and that `OPENAI_BASE_URL`/`ITINERARY_MODEL` defaults apply
      when unset
- [x] 7.3 Verify shape validation directly, against both a well-formed stand-in
      response and a deliberately malformed one, without calling the network
- [x] 7.4 Verify rendering directly, against a known-valid itinerary object
- [x] 7.5 Record explicitly, in this project's `BUILD-LOG.md`, that the live network
      call inside `generate_itinerary` remains unverified pending a real API key
