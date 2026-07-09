# Travel Itinerary Agent — Build Log

This document shows you exactly how this project was built with OpenSpec's
spec-driven workflow in Claude Code: which slash command you run at each step, what it
generates, and what you have to review or edit yourself. OpenSpec's own CLI
(`openspec status`, `openspec instructions`, `openspec archive`, and so on) runs
internally behind each slash command — you never type it directly, so it isn't shown
here. Every artifact referenced below still exists in this repository at the path
given.

## 1. Workflow Overview

| Step | You Run | Generates | How the Code Gets Created |
|---|---|---|---|
| Setup (once) | `openspec init --tools claude` | `.claude/commands/opsx/*.md`, `.claude/skills/openspec-*/SKILL.md`, `openspec/config.yaml` | — |
| Explore | `/opsx:explore` | Nothing on disk — a conversation only | — |
| Propose | `/opsx:propose` | `proposal.md`, `design.md`, `specs/<capability>/spec.md`, `tasks.md` | Not yet — these are planning artifacts |
| Apply | `/opsx:apply` | Source code and tests for every task in `tasks.md`; checkboxes flipped to `[x]` | Each task maps to one file or test module; see Section 4 |
| Archive | `/opsx:archive` | `openspec/specs/<capability>/spec.md` (merged, durable); change moved to `openspec/changes/archive/` | — |

This project went through this loop twice: once to build the tool, once to fix a bug a
live test uncovered (Section 7).

## 2. One-Time Setup

You run `openspec init --tools claude` once, before any `/opsx:*` command exists. It
installs the five slash-command definitions, the matching Skills, and
`openspec/config.yaml`.

**Edit before your first `/opsx:propose`**: `openspec/config.yaml`'s `context` and
`rules` blocks. Every artifact every `/opsx:*` command generates includes this block
automatically, so writing it once means you never retype the tech stack or domain.

```yaml
context: |
  Tech stack: Python 3.11+, stdlib argparse, the `openai` package against a
  configurable base_url so any OpenAI-compatible provider works, not just OpenAI.
  Domain: a small CLI travel itinerary generator — destination, trip length, and
  preferences in; a structured day-by-day itinerary out.
  No database, no web server, no auth. The API key is never hardcoded.

rules:
  tasks:
    - Break tasks into small, independently verifiable steps
    - The final tasks must include verification steps that do not require a live API key
```

## 3. `/opsx:explore` and `/opsx:propose`

`/opsx:explore` produces no file. Its output is the decisions you carry into
`/opsx:propose`:

- Scope: destination, trip length, and preferences (pace, interests, budget) in; a
  day-by-day itinerary out. No booking, no maps, no live availability.
- "OpenAI-compatible" means both the API key and the base URL must be configurable at
  runtime — hardcoding either narrows it to "OpenAI only."
- No API key exists yet, so the model call has to be isolated behind one function, so
  everything else can be verified without it.
- Ask the model for structured JSON, not prose, so the response can be validated.

`/opsx:propose` turns those decisions into four files, in dependency order:

| File | What It Contains for This Project |
|---|---|
| `proposal.md` | One new capability, `travel-itinerary`. Why: manual trip research is tedious for a simple case. |
| `design.md` | The core decision: isolate the model call in `generate_itinerary(...)`. Read/base-URL/model all come from separate environment variables, never hardcoded. |
| `specs/travel-itinerary/spec.md` | 4 requirements, each with 2–3 scenarios: CLI arguments, environment-variable configuration, structured generation, terminal rendering. |
| `tasks.md` | 7 task groups, 17 checkboxes, ending in a "verify without a live API key" group. |

**You review/edit**:
- `proposal.md` — the **Capabilities** section. A wrong capability name here means the
  wrong spec file gets created.
- `specs/.../spec.md` — every scenario header needs exactly four `#` characters
  (`#### Scenario:`). Three fails silently.
- `tasks.md` — keep each checkbox on one line. A wrapped line still works, but only its
  first line shows in the live progress view.
- Run the spec validation check right after this step, before `/opsx:apply` — it's
  local and free, and it catches the four-hashtag mistake before it costs you a wasted
  apply cycle.

## 4. `/opsx:apply`

This is the only step that writes your project's actual code. `tasks.md` is the only
file inside `openspec/` it touches — each finished task's `- [ ]` becomes `- [x]`.

| File | Task Group | Purpose |
|---|---|---|
| `pyproject.toml` | 1. Scaffold | Package metadata, one dependency: `openai` |
| `itinerary/cli.py`, `itinerary/__init__.py` | 2, 6 | Argument parsing, wiring, error handling |
| `itinerary/config.py` | 3 | Reads `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `ITINERARY_MODEL` |
| `itinerary/generator.py` | 4 | The isolated model call — `generate_itinerary(...)` |
| `itinerary/schema.py` | 4 | The itinerary JSON shape and its validation |
| `itinerary/renderer.py` | 5 | Plain-text, day-ordered output |
| `tests/*.py` | 7 | One test file per module above |

`generate_itinerary` accepts an optional `client` parameter, defaulting to a real
`openai.OpenAI` client. This is what makes the design's central decision testable:
`tests/test_generator.py` passes in a stand-in client (`FakeClient`) instead of a real
one, so every line up to the network call is verified without an API key.

**You review/edit**:
- Read the diff — a task marked `[x]` means the agent believes it's done, not that it's
  verified.
- Run the real test suite yourself: `python -m unittest discover -s tests -v`.
- If `/opsx:apply` reports a blocked artifact, go back to `/opsx:propose` — don't force
  it forward.

## 5. `/opsx:archive`

Merges the delta spec into `openspec/specs/<capability>/spec.md` and moves the change
directory to `openspec/changes/archive/YYYY-MM-DD-<name>/`.

**You review/edit — this one is a real, observed quirk, not hypothetical**: the first
time `/opsx:archive` creates a brand-new capability's spec file, its `## Purpose`
section is left as a placeholder — `TBD - created by archiving change <name>. Update
Purpose after archive.` Nothing fills this in automatically. It has to be replaced by
hand, once, the first time a capability is created. It does not recur on later archives
against the same capability (see Section 7).

This closes the first loop: `/opsx:explore` → `/opsx:propose` → `/opsx:apply` →
`/opsx:archive`, run for real against OpenSpec 1.5.0.

## 6. Using the Finished Tool

Setup:

```
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Usage:

```
itinerary "Lisbon, Portugal" 3 --pace relaxed --interests "food,history" --budget moderate
```

**Verified live**, against a real OpenAI-compatible proxy:

- Default model (`gpt-4o-mini`): well-formed 3-day itinerary, parsed and rendered
  correctly on the first try.
- A different model (`kimi-k2.6`), set only via `ITINERARY_MODEL`: equally well-formed
  output, with zero code changes — proof the "OpenAI-compatible" design decision holds.

## 7. A Bug Found by Live Testing, and a Second Loop to Fix It

Testing the failure path (a deliberately invalid API key) surfaced a real gap: the tool
crashed with a raw Python traceback (`openai.AuthenticationError`) instead of the clean
one-line error every other failure mode already produced. `specs/travel-itinerary/spec.md`
never accounted for this, because it only surfaces under a real network failure — no
stand-in test client can produce it on its own.

This went through the same loop again, as a second change:

| Step | What Happened |
|---|---|
| `/opsx:propose` | New requirement added: API failures exit cleanly instead of crashing. `design.md` decided to catch `openai.APIError` and re-raise as the existing `ItineraryValidationError`, reusing the handler `cli.py` already has. |
| `/opsx:apply` | `generator.py`: wrapped the model call in `try`/`except APIError`. `test_generator.py`: added a test using a real `openai.APIError` instance. Full suite: 26/26 passing (25 + 1 new). |
| `/opsx:archive` | New requirement merged into the existing spec. No `Purpose` placeholder this time — the capability already existed. |

Re-running the live failure-path test after the fix: the traceback was gone, replaced
by a clean `Itinerary validation error: Itinerary request failed: ...`, exit code 1.

**One nuance worth knowing**: `design.md`'s own guidance says to skip it for small,
low-risk changes — but `tasks.md` depends on `design.md` regardless of size in this
schema, so a short one was still required. Size alone doesn't excuse an artifact from
the dependency graph.

## 8. Token Consumption: SDD vs. a Single Unstructured Request

No tool in this session reports exact billed tokens. The figures below are estimated
from real, measured file sizes (`wc`), using the standard ~4-characters-per-token
heuristic — treat them as order-of-magnitude, not exact.

| Category | Approx. Tokens |
|---|---|
| Planning artifacts (both loops: proposals, designs, specs, tasks, config) | ~5,350 |
| This build log | ~5,400 |
| Application code | ~2,150 |
| Tests | ~2,550 |
| README + pyproject.toml | ~500 |
| Injected per-command context not stored in any file | ~3,500–4,500 |
| **Total, structured SDD, both loops** | **~19,500–20,500** |
| Constructed estimate: same project, single unstructured request | **~3,700–4,800** |

The SDD path used roughly **4–5x** the tokens. Almost all of the difference is planning
artifacts and process documentation, not the code itself, which is comparable in size
either way — and arguably more correct here, since its test cases trace to written-down
requirements rather than to whatever the author happened to think of at the time.

**The trade-off**: the extra tokens bought a spec that's now permanent documentation,
tests that verify design decisions instead of assuming them, and a repeatable mechanism
for turning a bug found by live testing into a documented fix instead of a silent
patch. An unstructured build is cheaper the first time; if the same context needs
reconstructing later — a teammate asking why, or a bug needing to be traced back to
what was actually specified — the unstructured path pays that cost later instead of
now.

## 9. Related Documentation

See `openspec-guide/Openspec-Documenetation.md` for the full `/opsx` command reference,
and `openspec-guide/02-command-outputs-and-token-optimization.md` for the
project-independent version of the per-command reference this document applies to one
real project.
