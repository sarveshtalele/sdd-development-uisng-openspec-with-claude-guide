## Why

Planning a multi-day trip by hand means manually researching activities for every day
of the trip. A small command-line tool that takes a destination, trip length, and a
short list of preferences, and returns a structured day-by-day itinerary, removes that
manual research step for a simple, personal-use case.

## What Changes

- Add a new CLI tool, `itinerary`, that accepts a destination, a number of days, and
  optional traveler preferences (pace, interests, budget level) as arguments.
- Add an itinerary-generation capability that calls an OpenAI-compatible chat completion
  endpoint, with the API key and base URL both read from environment variables, and
  requests a structured JSON itinerary from the model.
- Add validation of the model's JSON response against an expected shape (one entry per
  requested day, each with a time-ordered list of activities) before it is shown to the
  user.
- Add a plain-text rendering of the validated itinerary for terminal output.

## Capabilities

### New Capabilities
- `travel-itinerary`: accepts trip parameters, generates a structured day-by-day
  itinerary via an OpenAI-compatible model, validates its shape, and renders it as
  readable text in the terminal.

### Modified Capabilities
(none — this is a new project with no existing specs)

## Impact

- New Python package, no existing code affected (greenfield project).
- New runtime dependency: the `openai` Python package.
- New required environment variable for the API key, and an optional one for the base
  URL and model name, documented in the tool's own `--help` output and in `design.md`.
- No database, network service, or persistence layer introduced.
