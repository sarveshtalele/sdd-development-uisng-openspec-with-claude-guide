## Context

Greenfield, single-file-scale CLI tool. No existing codebase constraints. The one real
constraint on this design is practical rather than architectural: the OpenAI-compatible
API key will not be available until later, so the design has to make everything except
the live network call independently verifiable today.

## Goals / Non-Goals

**Goals:**
- Isolate the model call behind one function so the rest of the tool is testable
  without a live API key.
- Support any OpenAI-compatible endpoint, not only OpenAI itself.
- Fail with a clear, specific error message when required configuration is missing,
  rather than a raw stack trace.
- Validate the model's output shape before rendering it, so a malformed response is
  caught explicitly rather than silently mis-rendered.

**Non-Goals:**
- No persistence — nothing is written to disk unless the user redirects output.
- No verification that suggested activities are real, open, or currently bookable.
- No support for multiple concurrent requests, streaming output, or a web/API server —
  this is a single-shot CLI invocation.

## Decisions

- **Isolate the model call in one function, `generate_itinerary(...)`, that takes
  already-validated inputs and returns a parsed, already-shape-checked Python object.**
  Alternative considered: inline the API call in `main()`. Rejected because it would
  make everything downstream of the call untestable without a live key — isolating it
  is what makes the rest of the tool verifiable today.

- **Request structured JSON from the model (an explicit day/activity schema) rather than
  free-form prose, and validate that shape before rendering.** Alternative considered:
  ask for plain text and render it directly. Rejected because free text gives no
  concrete, checkable definition of "the response is well-formed" — a JSON schema does.

- **Read both the API key and the base URL from environment variables
  (`OPENAI_API_KEY` and `OPENAI_BASE_URL`, with the latter optional and defaulting to
  OpenAI's own endpoint), and the model name from a third, `ITINERARY_MODEL`.**
  Alternative considered: hardcode the endpoint and only accept a key. Rejected because
  it would silently narrow "OpenAI-compatible" to "OpenAI only," contradicting the
  proposal.

- **Fail fast with a specific message if `OPENAI_API_KEY` is unset, before attempting
  any network call.** Alternative considered: let the underlying HTTP client's error
  surface naturally. Rejected because that error is generic and unhelpful; a targeted
  check produces a message that names the exact missing variable.

- **Use Python's standard library `argparse` for the CLI, with no additional CLI
  framework dependency.** Alternative considered: a third-party CLI library. Rejected
  as unnecessary for three arguments and a couple of optional flags.

## Risks / Trade-offs

- [Risk] The model may suggest venues or activities that don't exist or aren't
  currently open. → Mitigation: none implemented — this is a stated, accepted
  limitation of a small demo tool, not something this design attempts to solve.
- [Risk] Without a live API key during this build, the `generate_itinerary` function's
  actual network behavior cannot be verified end-to-end right now. → Mitigation: the
  function is isolated and unit-testable up to the network boundary; the boundary
  itself is exercised with a stand-in response so the parsing and validation logic is
  verified even though the live call is not. This gap is called out explicitly in
  `tasks.md` and in this project's `BUILD-LOG.md` rather than glossed over.
- [Risk] A malformed or unexpected JSON response from the model could crash the tool. →
  Mitigation: explicit shape validation between the model call and rendering, with a
  clear error message on validation failure instead of an unhandled exception.
