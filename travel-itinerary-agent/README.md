# Travel Itinerary Agent

A small command-line tool that generates a day-by-day travel itinerary using an
OpenAI-compatible chat completion endpoint. Built with OpenSpec's spec-driven workflow
— see [BUILD-LOG.md](BUILD-LOG.md) for the full step-by-step record, and
`openspec/specs/travel-itinerary/spec.md` for the durable specification.

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuration

Set these environment variables before running:

| Variable | Required | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | Yes | Your OpenAI-compatible API key. |
| `OPENAI_BASE_URL` | No | Endpoint URL. Defaults to OpenAI's own API. Set this to point at any other OpenAI-compatible provider. |
| `ITINERARY_MODEL` | No | Model name to request. Defaults to `gpt-4o-mini`. |

## Usage

```bash
itinerary "Lisbon, Portugal" 3 --pace relaxed --interests "food,history" --budget moderate
```

`destination` and the number of `days` are required positional arguments; `--pace`,
`--interests`, and `--budget` are optional.

## Running the tests

```bash
python -m unittest discover -s tests -v
```

The test suite covers argument parsing, configuration loading, response-shape
validation, error handling, and rendering entirely without a live API key, using a
stand-in client in place of the network call (see `tests/test_generator.py`). A live
run against a real OpenAI-compatible endpoint has also been verified, including both
the success path and an API-level failure path — see `BUILD-LOG.md`, Sections 6-7.
