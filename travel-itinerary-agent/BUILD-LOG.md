# Build Log: Travel Itinerary Agent

This log records, in order, every command actually executed and every file actually
generated or edited while building this project with OpenSpec's spec-driven workflow
inside Claude Code, plus which workflow definition each step followed. It is a real,
after-the-fact record of one live run, not a hypothetical walkthrough.

One caveat, stated up front: the `/opsx:*` slash commands documented elsewhere in this
repository are ordinarily triggered by typing them directly into a Claude Code session,
where the harness loads the matching file from `.claude/commands/opsx/` and follows it.
In this session, those project-local command files were not dynamically available to
invoke through the slash-command dispatcher. Instead, each step below was executed by
reading the real, generated command definition file for that step (verbatim, unedited,
straight from `openspec init --tools claude`) and manually carrying out exactly what it
specifies — the same CLI calls, the same artifact templates, the same file paths. The
workflow logic executed is identical; only the triggering mechanism differs from typing
`/opsx:propose` in a live session.

## Step 0 — Setup

Commands run, in a terminal, from `/Users/sarveshtalele/Downloads/openspec/`:

```bash
npm install -g @fission-ai/openspec
mkdir -p travel-itinerary-agent
cd travel-itinerary-agent
openspec init --tools claude
```

`openspec --version` reported `1.5.0`.

`openspec init --tools claude` generated:

```
travel-itinerary-agent/
├── .claude/
│   ├── commands/opsx/{explore,propose,apply,sync,archive}.md
│   └── skills/openspec-{explore,propose-change,apply-change,sync-specs,archive-change}/SKILL.md
└── openspec/
    └── config.yaml
```

Edited by hand immediately after: `openspec/config.yaml` — added a `context:` block
describing the tech stack (Python, the `openai` package against a configurable
OpenAI-compatible `base_url`) and domain (a small CLI itinerary generator), plus a
`rules.tasks` entry requiring tasks to be independently verifiable and requiring the
final tasks to include verification that does not depend on a live API key. This is not
a step any `/opsx:*` command performs automatically — it is a one-time, optional setup
edit that primes every artifact `openspec instructions` generates afterward with
project-specific context, so the generated proposal/spec/design/tasks do not have to be
corrected by hand later for basic facts like the tech stack. See the token-optimization
document in `openspec-guide/` for why this specific edit is worth making before the
first `/opsx:propose`.

## Step 1 — Explore

Workflow followed: `.claude/commands/opsx/explore.md` (installed verbatim; not edited).

Per that definition, explore mode is a thinking stance, not a fixed sequence — it
permits reading and investigating but forbids writing code, and produces no required
artifact. It also specifies checking for existing context first:

```bash
openspec list --json
```

Output: `{"changes": [], "root": {...}}` — confirmed a clean project, nothing to read
for context.

**Exploration notes** (this is the actual thinking, not a template — no file was
written by this step, matching the command definition's "no mandatory outputs"):

- **Core scope**: given a destination, a trip length in days, and a short list of
  traveler preferences (pace, interests, budget level), produce a day-by-day itinerary.
  Nothing more — no booking, no live availability, no maps integration. Keeping scope
  this narrow is what makes "small project" true rather than aspirational.
- **"OpenAI-compatible" is a design constraint, not just a client library choice.** It
  means both the API key *and* the base URL must be configurable at runtime, so the
  same code works against OpenAI itself or against any other provider that speaks the
  same API shape. Hardcoding either would silently narrow "compatible" to "OpenAI
  only."
- **The no-key-yet constraint drives the architecture more than anything else.** If the
  single function that calls the model is isolated from argument parsing, prompt
  construction, and output formatting, then everything except that one function can be
  exercised and verified today, with the live call itself deferred until a key exists.
  This became the central design decision carried into `design.md`.
- **Output shape**: ask the model for structured JSON (day number, a list of activities
  per day, each with a time block and description) rather than free-form prose. JSON can
  be schema-validated before being shown to the user, which gives a concrete, testable
  definition of "the output is well-formed" that doesn't depend on the model actually
  being called.
- **Explicitly out of scope, and worth writing down now so it doesn't creep back in
  later**: no persistence/database, no authentication, no web server, no geocoding or
  real-world venue validation. The model's suggestions are not verified against reality
  — that is a known, stated limitation of a small demo tool, not a defect to fix here.

This reasoning fed directly into `proposal.md` and `design.md` in the next step —
nothing here was thrown away, and nothing here was written to a file until the propose
step created one.

## Step 2 — Propose

Workflow followed: `.claude/commands/opsx/propose.md` (installed verbatim; not edited).

That definition specifies a CLI-driven loop, not free-form writing: create the change,
ask the CLI for the artifact dependency order, then for each unlocked artifact ask the
CLI for its exact template and instructions, and write to the exact path it returns.
Every command below was run for real, in order, and every path shown is the real
resolved path the CLI returned — nothing here is illustrative.

```bash
openspec new change "add-travel-itinerary-cli"
```
Output: `Created change 'add-travel-itinerary-cli' at openspec/changes/add-travel-itinerary-cli/` (schema: `spec-driven`).

```bash
openspec status --change "add-travel-itinerary-cli" --json
```
Returned `applyRequires: ["tasks"]` and the dependency graph: `proposal` ready
immediately; `design` and `specs` both blocked on `proposal`; `tasks` blocked on both
`design` and `specs`. This — not a fixed document order — is what determined the
sequence below.

**`proposal`** — `openspec instructions proposal --change "add-travel-itinerary-cli" --json`
returned a template (Why / What Changes / Capabilities / Impact) and the exact
`context` block from `openspec/config.yaml` (Step 0), fed back verbatim so it did not
need to be retyped. Written to
`openspec/changes/add-travel-itinerary-cli/proposal.md`: one new capability declared,
`travel-itinerary`.

Re-ran `openspec status --change "add-travel-itinerary-cli" --json` — `proposal` now
`done`; both `design` and `specs` became `ready`.

**`design`** — `openspec instructions design --change "add-travel-itinerary-cli" --json`
returned a template (Context / Goals-Non-Goals / Decisions / Risks-Trade-offs). Written
to `openspec/changes/add-travel-itinerary-cli/design.md`. The central decision recorded
here: isolate the model call in one function so everything else is verifiable without a
live key — carried directly from the Step 1 exploration notes.

**`specs`** — `openspec instructions specs --change "add-travel-itinerary-cli" --json`
returned the delta-spec template and format rules (`### Requirement:` /
`#### Scenario:` with WHEN/THEN, exactly four hashtags on scenarios). Written to
`openspec/changes/add-travel-itinerary-cli/specs/travel-itinerary/spec.md`: four
requirements — CLI argument handling, environment-variable configuration, structured
generation, and terminal rendering — each with 2-3 scenarios covering both the success
path and the specific failure modes named in Step 1 (missing key, malformed model
response).

Re-ran status again — `design` and `specs` both `done`; `tasks` became `ready`.

**`tasks`** — `openspec instructions tasks --change "add-travel-itinerary-cli" --json`
returned the checkbox-list template, and also returned the two custom rules added to
`openspec/config.yaml` in Step 0 (`Break tasks into small, independently verifiable
steps` and the requirement that the final tasks verify without a live key) — confirming
that edit actually reached this artifact's generation, not just the ones already shown
above. Written to `openspec/changes/add-travel-itinerary-cli/tasks.md`: seven task
groups, ending deliberately with a "Verification without a live API key" group whose
last item requires this build log to state outright that the live network call is
unverified.

```bash
openspec status --change "add-travel-itinerary-cli"
```
Output: `Progress: 4/4 artifacts complete`.

```bash
openspec validate "add-travel-itinerary-cli"
```
Output: `Change 'add-travel-itinerary-cli' is valid` — confirms the spec file's
scenario formatting (four-hashtag headers, WHEN/THEN scenarios) parses correctly; this
step exists specifically to catch the "three hashtags fails silently" pitfall the
`specs` instruction output warned about above.

## Step 3 — Apply

Workflow followed: `.claude/commands/opsx/apply.md` (installed verbatim; not edited).

```bash
openspec instructions apply --change "add-travel-itinerary-cli" --json
```
Returned `contextFiles` (the four artifact paths from Step 2), `progress: {"total": 17,
"complete": 0, "remaining": 17}`, and the 17 individual task entries parsed directly out
of `tasks.md`'s checkboxes. `state: "ready"` confirmed nothing was blocked.

One real quirk discovered here, worth carrying into the token-optimization document:
several of my `tasks.md` bullets wrapped onto a second line for readability, and the
CLI's task list shows only each checkbox's *first* line — for example task 1 displays
as `"1.1 Create the package layout (\`itinerary/\` package plus \`pyproject.toml\` or
a"`, missing the wrapped continuation. The underlying tasks.md file and the archived
spec are unaffected — this only affects the live progress display — but it means each
checkbox should be kept on a single line if the CLI's own progress view needs to be
readable.

Implementation — files created under `travel-itinerary-agent/`, each mapped to the
task group it satisfies:

| File | Tasks satisfied |
|---|---|
| `pyproject.toml` | 1.1, 1.2 |
| `itinerary/__init__.py`, `itinerary/cli.py` | 2.1, 2.2, 6.1, 6.2 |
| `itinerary/config.py` | 3.1, 3.2 |
| `itinerary/generator.py` | 4.1, 4.2 (shape defined in `schema.py`) |
| `itinerary/schema.py` | 4.2, 4.3 |
| `itinerary/renderer.py` | 5.1 |
| `tests/test_cli.py`, `tests/test_config.py`, `tests/test_schema.py`, `tests/test_renderer.py`, `tests/test_generator.py` | 7.1, 7.2, 7.3, 7.4 |
| `README.md` | project usage documentation (not itself a numbered task; added as standard project hygiene) |

Every design decision in `design.md` is reflected directly: `generate_itinerary` in
`generator.py` accepts an optional `client` parameter specifically so
`tests/test_generator.py` can substitute a stand-in object instead of a real
`openai.OpenAI` client (see the `FakeClient`/`FakeChatCompletions` classes there) —
this is the concrete mechanism that makes the "isolate the model call" decision
actually testable, not just a stated intention.

After implementation, every `- [ ]` in `tasks.md` was changed to `- [x]` (17 of 17),
matching the checkbox convention `apply.md` requires for progress tracking.

Environment setup and full verification, run for real:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
python -m unittest discover -s tests -v
```
Result: **25 tests, all passing, 0 failures.**

CLI exercised directly, end to end, for everything that doesn't require a live key:

```bash
itinerary                                        # -> usage error, exit code 2
env -u OPENAI_API_KEY itinerary "Paris, France" 3 # -> "Configuration error: OPENAI_API_KEY is not set...", exit code 1
itinerary "Paris" 0                               # -> "days must be a positive integer", exit code 2
itinerary --help                                  # -> full usage text
```

All four behaved exactly as specified in `specs/travel-itinerary/spec.md`.

**What remained unverified at this point, stated plainly (task 7.5):** the actual
network call inside `generate_itinerary` — an
`openai.OpenAI(...).chat.completions.create(...)` request against a real
OpenAI-compatible endpoint — had not been exercised, because no API key had been
provided yet. Everything up to and including the construction of that request, and
everything after a response is received (JSON parsing, shape validation, rendering), was
verified by `tests/test_generator.py` using a stand-in client. The one gap was whether a
real provider's actual response text parses cleanly into the expected shape on the first
try. **This gap was closed in Step 6 below**, once a real API key and OpenAI-compatible
proxy URL were provided.

## Step 4 — Archive

Workflow followed: `.claude/commands/opsx/archive.md` (installed verbatim; not edited).
Unlike the earlier steps, the real archive mechanics in OpenSpec 1.5.0 turned out to be
handled by the CLI itself rather than by the agent reading and merging files by hand —
`openspec archive` performs the spec-sync-and-move sequence the command definition
describes as manual steps in one call.

```bash
openspec archive add-travel-itinerary-cli --yes
```

Output:
```
Task status: ✓ Complete
Specs to update:
  travel-itinerary: create
Applying changes to openspec/specs/travel-itinerary/spec.md:
  + 4 added
Totals: + 4, ~ 0, - 0, → 0
Specs updated successfully.
Change 'add-travel-itinerary-cli' archived as '2026-07-09-add-travel-itinerary-cli'.
```

This one command did everything `archive.md` describes as separate manual steps:
confirmed all 4 artifacts and all 17 tasks were complete (no warning was printed, since
both were already true), found the one delta spec file
(`specs/travel-itinerary/spec.md`), determined the `travel-itinerary` capability didn't
exist yet in `openspec/specs/`, created it with the 4 ADDED requirements, and moved the
change directory to `openspec/changes/archive/2026-07-09-add-travel-itinerary-cli/`.

**Manual edit required immediately after**: the newly created
`openspec/specs/travel-itinerary/spec.md` had its `## Purpose` section auto-filled with
a placeholder — `TBD - created by archiving change add-travel-itinerary-cli. Update
Purpose after archive.` — which the archive command itself does not attempt to write a
real value for. This was replaced by hand with an actual one-paragraph purpose
statement. This is the one edit in the entire workflow that a human (or the agent,
prompted to do so) always has to make after archiving a new capability for the first
time — see the command-reference document in `openspec-guide/` for this same point made
generally, not just for this one project.

Final state: `openspec/specs/travel-itinerary/spec.md` is now this project's durable,
permanent specification, independent of the archived change directory. This concludes
the full explore → propose → apply → archive loop for this project, executed for real,
against a real OpenSpec 1.5.0 installation, start to finish.

## Step 5 — Token Consumption: SDD vs. a Single Unstructured Build

**Methodology, stated up front**: there is no tool available in this session that
reports the exact number of tokens actually billed for this conversation. Everything
below is an estimate derived from the real, measured size (in characters and lines) of
the artifacts this build actually produced, converted to an approximate token count
using the common ~4-characters-per-token heuristic for English text and source code.
Treat the figures as order-of-magnitude, not exact — the point is the comparison
between the two approaches, not a precise accounting of either one.

**What was actually measured** (via `wc`, on the real files in this project):

| Category | Files | Lines | Characters | Approx. tokens (÷4) |
|---|---|---|---|---|
| OpenSpec planning artifacts (`proposal.md`, `design.md`, delta `specs/`, `tasks.md`, `config.yaml`, plus the archived copies and the final main spec) | 6 | 313 | 15,272 | ~3,800 |
| `BUILD-LOG.md` (this file, the process narration) | 1 | 294 | 15,372 | ~3,800 |
| Application code (`itinerary/`) | 5 | 267 | 8,608 | ~2,150 |
| Tests (`tests/`) | 6 | 244 | 9,273 | ~2,300 |
| `README.md` + `pyproject.toml` | 2 | 63 | 1,941 | ~500 |

**Process overhead not captured in any file on disk**: over the course of the propose,
apply, and archive steps, roughly a dozen `openspec status`/`openspec instructions`/
`openspec validate`/`openspec archive` calls were made and their JSON or text output was
read back in full to decide what to write next (Sections 2-4 above show several of
these responses verbatim). Based on the actual size of those responses, that reading
cost is roughly another 3,000-4,000 tokens — real context consumption, but not
represented by any single file's size.

**Rough total for the structured SDD path on this project**: code + tests +
README/config (~4,950 tokens — the actual deliverable) plus planning artifacts, this
log, and CLI-output reading (~10,600-11,600 tokens of process overhead) — on the order
of **15,000-16,500 tokens** in total.

**Constructed comparison: the same project built as a single unstructured request**
("build me a travel itinerary CLI in Python using an OpenAI-compatible client," no
proposal, no design doc, no spec, no task list, no build log). This scenario was not
actually run — it is estimated the same way, from what that request would realistically
have to produce:
- Comparable application code, though very plausibly with less of the isolation and
  edge-case test coverage this build has (the empty-activities, wrong-day-count, and
  non-JSON-response test cases exist here specifically because `specs/travel-itinerary/spec.md`
  named them as required scenarios) — call it roughly 60-80% of the code+test volume
  above, so **~3,000-3,600 tokens**.
- A short explanation of what was built, in place of a proposal/design document —
  **~300-800 tokens**.
- No CLI-orchestration reading cost, since there is no CLI workflow to query.
- A realistic possibility of one or two extra clarifying back-and-forth turns, since
  requirements were never written down and reviewed before code was produced — a cost
  the SDD path pays once, up front, in the proposal review, instead.

**Rough total for the unstructured path**: on the order of **3,500-4,500 tokens**.

**Net comparison**: on a project this small, the structured OpenSpec workflow used
roughly **3-4x the tokens** of an equivalent single-shot build. Nearly all of that
difference is the planning artifacts, the build log, and CLI-output reading — not the
application code itself, which is comparable in size either way (and arguably more
correct in the SDD version, since its test cases trace directly to written-down
requirements rather than to whatever the author happened to think of at implementation
time).

**The trade-off, stated plainly rather than resolved in either direction**: the extra
tokens bought a written proposal and design rationale that exist independently of this
conversation, a spec that is now permanent, durable project documentation, and tests
that verify — rather than merely assert — that the design's central decision (isolating
the model call) was actually followed. An unstructured build is cheaper the first time;
if the same context has to be reconstructed later (a teammate asking why a decision was
made, or this project being picked up again after this conversation ends), the
unstructured path pays that cost later instead of now. Which is worth it depends on
whether the project outlives this one build — for a genuinely disposable script, it
likely is not; for anything meant to be maintained, reviewed, or handed off, the
up-front cost is what makes that later reconstruction unnecessary.

## Step 6 — Closing the Verification Gap: Live Call, a Real Bug Found, and a Second SDD Loop

A real API key and an OpenAI-compatible proxy base URL were provided later in this
conversation (deliberately never written to any file in this repository or committed —
only exported as process environment variables for the commands below).

**Live call, success path:**

```bash
OPENAI_API_KEY="..." OPENAI_BASE_URL="https://<proxy-host>" \
  itinerary "Lisbon, Portugal" 3 --pace relaxed --interests "food,history" --budget moderate
```

Result: a well-formed, three-day, day-ordered itinerary was printed, closing the one gap
stated at the end of Step 3 — a real OpenAI-compatible provider's response parses
cleanly through `generate_itinerary` → `schema.validate_itinerary` →
`renderer.render_itinerary` on the first try, with no code changes needed for the happy
path. The same command was re-run for Kyoto later in this step with the fix from below
already applied, confirming the success path was unaffected by it.

**Live call, failure path — this is where a real gap was found:**

```bash
OPENAI_API_KEY="sk-invalid-bogus-key-000" OPENAI_BASE_URL="https://<proxy-host>" \
  itinerary "Rome" 2
```

This raised an unhandled `openai.AuthenticationError` — a full Python traceback printed
to the terminal, unlike every other failure mode in this tool (`ConfigError`,
`ItineraryValidationError`), which all exit with one clean line. Nothing in
`specs/travel-itinerary/spec.md` had a requirement for this case, because it was never
identified during the original Step 1 exploration — it only surfaced under a real
network failure. This is exactly the kind of gap SDD expects to be found by
verification, then fed back through the same proposal → design → specs → tasks → apply →
archive loop rather than patched silently.

**Second loop, run for real against OpenSpec 1.5.0, following the same command
definitions as Steps 2-4:**

```bash
openspec new change "fix-api-error-handling"
openspec status --change "fix-api-error-handling" --json
openspec instructions proposal --change "fix-api-error-handling" --json
```
Wrote `proposal.md`: one modified capability, `travel-itinerary` — add a requirement
that API-level failures during generation exit cleanly instead of crashing.

```bash
openspec instructions design --change "fix-api-error-handling" --json
```
Wrote `design.md`. One nuance worth recording here: this document's own generation
instructions say to create `design.md` "only if" the change is cross-cutting, adds a
dependency, or carries real risk — by that standard alone, this small, single-file fix
would not need one. But the `spec-driven` schema's dependency graph makes `tasks`
depend on both `design` and `specs` being `done` regardless of size, so a (kept
deliberately short) `design.md` was written anyway. This is a real discrepancy between
the artifact-level guidance and the schema's hard dependency graph, worth knowing before
assuming "small change" is sufficient justification to skip a required artifact.

```bash
openspec instructions specs --change "fix-api-error-handling" --json
```
Wrote a delta spec at `specs/travel-itinerary/spec.md`: one `## ADDED Requirements`
block, one new requirement, one scenario (`WHEN` the model client raises an error,
`THEN` exit cleanly without a traceback).

```bash
openspec instructions tasks --change "fix-api-error-handling" --json
openspec validate "fix-api-error-handling"
```
Wrote `tasks.md`: two groups, five tasks. `openspec validate` reported the change valid.

**Apply**, executed directly rather than through the CLI's task-progress JSON (a
five-task change did not warrant the extra `openspec instructions apply` round trip that
Step 3's seventeen-task change used — consistent with the "batch review, don't over-query"
guidance in the token-optimization document):

- `itinerary/generator.py`: imported `APIError` from `openai`; wrapped the
  `client.chat.completions.create(...)` call in `try`/`except APIError`, re-raising as
  `ItineraryValidationError` — reusing the exception type `cli.main` already handles
  cleanly, per the decision recorded in this change's `design.md`.
- `tests/test_generator.py`: extended `FakeChatCompletions`/`FakeClient` to optionally
  raise a supplied exception instead of returning content, and added
  `test_api_error_raises_validation_error`, constructing a real `openai.APIError`
  (`httpx.Request` + `body=None`) to prove the `except` clause actually matches the real
  exception type, not just a same-named stand-in.
- All five `- [ ]` in this change's `tasks.md` flipped to `- [x]`.

Verification, run for real:

```bash
python -m unittest discover -s tests -v
```
Result: **26 tests, all passing** (25 from Step 3 plus the one new case).

```bash
OPENAI_API_KEY="sk-invalid-bogus-key-000" OPENAI_BASE_URL="https://<proxy-host>" \
  itinerary "Rome" 2
```
Result: `Itinerary validation error: Itinerary request failed: Error code: 401 - ...`,
exit code 1 — the traceback is gone, replaced by the same clean error style as every
other failure mode.

```bash
openspec instructions apply --change "fix-api-error-handling" --json   # progress 5/5
openspec archive "fix-api-error-handling" --yes
```
Output:
```
Task status: ✓ Complete
Specs to update:
  travel-itinerary: update
Applying changes to openspec/specs/travel-itinerary/spec.md:
  + 1 added
Totals: + 1, ~ 0, - 0, → 0
Specs updated successfully.
Change 'fix-api-error-handling' archived as '2026-07-09-fix-api-error-handling'.
```

Unlike Step 4, this archive introduced no `## Purpose` placeholder to fix by hand — that
placeholder is only written when a capability's main spec file is created for the first
time, and `travel-itinerary` already existed. The new requirement merged directly under
the three from Step 4, with no manual correction needed.

**Token cost of this second loop**, measured the same way as Step 5 (~4 chars/token,
explicitly approximate): the four planning artifacts totaled 6,122 characters
(~1,530 tokens); the `generator.py` diff and the extended `test_generator.py` totaled
6,959 characters measured whole (~1,740 tokens, though only a fraction of each file
actually changed); this section of the build log added roughly another ~1,600 tokens of
process narration. Call it **~4,500-5,000 tokens** for a second, small, fully-real SDD
loop — proportionally similar in shape to Step 5's finding that most of the cost is
planning-artifact and process overhead, not the one-line code change itself.

**Why this matters for the overall demonstration**: Step 3 stated one open verification
gap honestly instead of glossing over it. Closing that gap with a real key did not just
confirm the happy path — it found a genuine, previously-unspecified bug on the first
real network call. That is the argument for verification against real dependencies
rather than only against stand-ins: the stand-in in `test_generator.py` could only ever
return what it was told to return, and had no way to surface a failure mode nobody had
thought to simulate. The fix then went through the identical propose → design → specs →
tasks → apply → archive loop as the original feature, at roughly a third of the token
cost, precisely because it was small and scoped — direct evidence for the
token-optimization document's claim that change size, not the workflow itself, is what
drives cost.

**Second model, same code path, no code change**: the live call was repeated with
`ITINERARY_MODEL=kimi-k2.6` (a different model on the same proxy) instead of the
default `gpt-4o-mini`:

```bash
OPENAI_API_KEY="..." OPENAI_BASE_URL="https://<proxy-host>" ITINERARY_MODEL="kimi-k2.6" \
  itinerary "Barcelona, Spain" 2 --pace relaxed --interests "architecture,food"
```

Result: a well-formed two-day itinerary, parsed and rendered correctly with zero code
changes -- only the `ITINERARY_MODEL` environment variable differed. This is the
concrete proof for the "OpenAI-compatible is a design constraint, not just a client
library choice" note from Step 1: the model name, like the API key and base URL, was
never hardcoded, so swapping the underlying model required no code change at all.
