# OpenSpec Documentation — Claude Code Integration

*A standalone reference for [OpenSpec](https://github.com/Fission-AI/OpenSpec) v1.5.0,
focused entirely on using it through Claude Code's `/opsx` slash commands. Applies to
any project — no dependency on any specific repository or prior setup.*

---

## 1. What Is OpenSpec

OpenSpec is a Spec-Driven Development (SDD) tool. Before Claude writes any code, work is
broken into reviewable artifacts:

| Artifact | Answers |
|---|---|
| `proposal.md` | Why does this change need to happen? What changes? What's out of scope? |
| `design.md` | What's the technical approach and key decisions? |
| `specs/<capability>/spec.md` | What is the exact required behavior, as testable scenarios? |
| `tasks.md` | What are the ordered, checkable implementation steps? |

Once every task is implemented and genuinely verified, the change is **archived** — its
specs become permanent, durable documentation under `openspec/specs/`.

---

## 2. Setup

Two one-time commands, run from your project root:

```bash
npm install -g @fission-ai/openspec
openspec init --tools claude
```

These two commands are the **only** ones you run in a terminal (`cmd.exe`, PowerShell,
or any shell) — one-time, to install OpenSpec and scaffold `openspec/` +
`.claude/skills/` + `.claude/commands/opsx/`. Restart your IDE afterward so the slash
commands register.

### Use claude for SDD Development

After initialisation for project directory use claude to start SDD development.

``` 
claude
```


---

## 3. `/opsx` Commands

### 3a. Installed by default (`core` profile — what `openspec init --tools claude` gives you)

| Command | Description | When to Use |
|---|---|---|
| `/opsx:explore <topic>` | Think through ideas, investigate problems, clarify requirements before committing to anything. Creates no files. | Before proposing anything — understanding existing/unfamiliar code, weighing approaches, tracing how something currently works. |
| `/opsx:propose <name-or-description>` | Creates a new change and generates proposal, design, specs, and tasks in one guided pass. | Once you know what to build and want a full plan before any code is written. |
| `/opsx:apply` | Implements the tasks in the active change's `tasks.md`, in order. | After proposal/design/specs/tasks are complete and reviewed, ready to write code. |
| `/opsx:sync` | Merges a change's delta specs into the main `openspec/specs/` tree without a full archive. | Mid-flight, when you want the durable spec tree updated before the change is fully done. |
| `/opsx:archive` | Archives a completed, verified change; folds its specs into `openspec/specs/` permanently. | Only once every task is genuinely verified working — the "done" checkpoint. |

### 3b. Available via the expanded/custom profile (per official OpenSpec docs — requires switching profile with `openspec config profile`, an interactive picker; not installed by `core`)

| Command | Description | When to Use |
|---|---|---|
| `/opsx:onboard` | Guided interactive tutorial — scans your codebase for one small, safe improvement and walks the full workflow on it with explanation. | First time using OpenSpec on an existing codebase and you want a hands-held example instead of picking your own first change. |
| `/opsx:update` | Revises a change's existing artifacts and keeps them coherent. | Requirements shifted after a proposal was already written. |
| `/opsx:verify` | Validates that the implementation matches the change's artifacts. | After `/opsx:apply`, before archiving, as an explicit correctness check. |
| `/opsx:new` | Starts a new change scaffold without generating artifacts yet. | You want to create the change shell first and fill in artifacts one at a time. |
| `/opsx:continue` | Creates the next artifact in dependency order. | Working through artifacts one at a time rather than all at once via `/opsx:propose`. |
| `/opsx:ff` | Fast-forward — creates all planning artifacts at once (same effect as `/opsx:propose` for an existing change). | Change scaffold already exists (via `/opsx:new`) and you want the rest generated immediately. |
| `/opsx:bulk-archive` | Archives multiple completed changes at once. | Cleaning up a backlog of several verified, unarchived changes together. |

Both tables reflect the same `openspec` package version (v1.5.0); only the profile you
pick determines which set is installed.

---

## 4. Typical Loop


- **/opsx:explore** - "How does the current styling system work"
- **/opsx:propose** - "Add dark mode support"
   ... review proposal.md / design.md / specs / tasks.md, edit if needed ...
- **/opsx:apply**
   ... implement runs, verify it actually works ...
- **/opsx:archive**


That's the entire day-to-day workflow. Everything — file creation, dependency ordering
between proposal/design/specs/tasks, validation — happens automatically inside Claude
Code when you run these commands; there is nothing else to invoke manually.

---

## 5. Using This for Reverse Engineering & Existing/Legacy Codebases

### 5a. `/opsx:explore` — understand before you touch anything

Works standalone in any project, including one you didn't write. No files are created,
so there's no risk in exploring freely:


- **/opsx:explore:** "map out how this codebase currently handles authentication"
- **/opsx:explore:** "trace how a request flows through the middleware before we add rate limiting"


Per OpenSpec's own guidance for existing codebases: *"You do not document your whole
codebase to start. You write specs only for what you're about to change."* — don't try
to reverse-engineer everything upfront. Explore only the area relevant to the next
change, propose that change, and let `openspec/specs/` accumulate coverage naturally as
you work through real changes over time.

### 5b. `/opsx:onboard` — guided first pass on an existing codebase

If this is your first time bringing OpenSpec into an existing/legacy project, `/opsx:onboard`
(expanded profile — see Section 3b) scans the codebase for one small, safe improvement and
walks through the entire propose → apply → archive loop on it, with explanation at each
step. Use it once, to see the workflow on your own code before doing it yourself on a
real feature.

### 5c. Pairing OpenSpec With a Custom Reverse-Engineering/Analyzer Skill

If you also have a custom Claude Code skill that automates deeper analysis of an existing
codebase (e.g. parsing a legacy app into a structured inventory of pages, components, and
business capabilities), it composes with OpenSpec through this folder convention, in any
project:

```
your-project/
├── .claude/
│   ├── skills/
│   │   ├── <your-analyzer-skill>/     Custom skill: analyzes the existing/legacy code
│   │   └── openspec-*/                Installed by `openspec init --tools claude`
│   └── commands/opsx/                 Installed by `openspec init --tools claude`
└── openspec/
    ├── config.yaml                    Put what the analyzer found here — tech stack,
    │                                   architecture, capability list, risk areas — so
    │                                   every /opsx:propose after this already has it.
    ├── changes/
    └── specs/
```

**Generic pipeline**, independent of which analyzer you use:

1. Run the analyzer skill — it should produce a structured inventory (capabilities,
   architecture facts, risk flags).
2. Put the relevant facts into `openspec/config.yaml`'s `context:` block once.
3. Pick the lowest-risk capability first (analyzer's own scoring, or judgment).
4. `/opsx:explore` that capability's legacy code, then `/opsx:propose` it — referencing
   the exact legacy pages/components it replaces.
5. `/opsx:apply`, verify genuinely, `/opsx:archive`.
6. Repeat per remaining capability. Done = `openspec/specs/` fully populated, not a
   percentage estimate.

Works the same with no custom analyzer at all — skip straight to `/opsx:explore` for
manual investigation. OpenSpec has no opinion on how you arrived at the context you put
in `config.yaml`.

---

## 6. Sample Project — Commands to Execute, Start to Finish (using expanded profile)

A real, complete run of the workflow, from an empty folder to an archived, durable spec.
Every command below was actually executed while writing this doc. Only the commands you
type are shown — Step 1 in a terminal, everything else in Claude Code chat.

**Goal**: a small CLI tool, `wordcount.py`, that counts words/lines/characters in a text
file and can report the N most frequent words.

### Step 1 — Setup (terminal: `cmd.exe`/PowerShell/bash)

```bash
>> mkdir word-counter-project && cd word-counter-project
>> openspec init --tools claude

>> claude
```

Default `core` profile gives you Steps 3, 4a, 5, 8, 9 below (`/opsx:explore`,
`/opsx:propose`, `/opsx:apply`, `/opsx:sync`, `/opsx:archive`). Steps 2, 4b, 6, 7, 10 need
the `custom`/expanded profile (Section 3b) — switch with `openspec config profile` first.

### Step 2 — Onboard (optional, first time only — Claude Code chat)

```
/opsx:onboard
```

Guided tutorial — scans the empty/new project and walks you through one small example
end to end. Skip if you already know the workflow; go straight to Step 3.

### Step 3 — Explore (optional — Claude Code chat)

```
/opsx:explore "what should a simple word-count CLI tool support"
```

### Step 4 — Create the change

Two ways — pick one:

**4a. All at once (Claude Code chat)**
```
/opsx:propose "Add a CLI tool that counts words, lines, and characters in a text file, with a --top N most-frequent-words option"
```
Creates `proposal.md`, `design.md`, `specs/word-counter/spec.md`, `tasks.md` in one pass.

**4b. Step by step (Claude Code chat)**
```
/opsx:new "Add a CLI tool that counts words, lines, and characters in a text file"
/opsx:continue
/opsx:continue
/opsx:continue
```
`new` scaffolds the change with no artifacts yet; each `continue` creates the next
artifact in dependency order (proposal, then design/specs, then tasks). Or skip the
repeated `continue` calls with:
```
/opsx:ff
```
which creates every remaining artifact in one shot, same end result as `/opsx:propose`.

Review the created artifacts; edit by hand if anything needs correcting.

### Step 5 — Apply (Claude Code chat)

```
/opsx:apply
```

Implements `wordcount.py` per the artifacts above. Verify it genuinely works before
moving on — run it yourself against a real file, a `--top N` case, and a missing file.

### Step 6 — Verify (optional — Claude Code chat)

```
/opsx:verify
```

Checks the implementation actually matches what the artifacts specified — an explicit
correctness gate before archiving, on top of your own manual testing in Step 5.

### Step 7 — Update (only if requirements changed — Claude Code chat)

```
/opsx:update
```

Only run this if something changed after the artifacts were already written (e.g. a new
requirement came up) — revises the existing artifacts and keeps them coherent, instead
of starting over.

### Step 8 — Sync (optional — Claude Code chat)

```
/opsx:sync
```

Only needed if you want the durable spec updated before the change is fully archived.

### Step 9 — Archive (Claude Code chat)

```
/opsx:archive
```

Only run this once every `tasks.md` item is genuinely verified working. Folds the
change's specs into `openspec/specs/word-counter/spec.md` permanently — the project's
living documentation from this point forward.

### Step 10 — Bulk-archive (only with multiple finished changes — Claude Code chat)

```
/opsx:bulk-archive
```

Not needed for this single-change example — included for completeness. Archives several
completed, verified changes in one pass instead of running `/opsx:archive` per change.

---

## 6b. Sample Project — Commands to Execute, Start to Finish (using core profile)

A second, complete run of the workflow — this time using only the `core` profile (Section
3a), which is what `openspec init --tools claude` installs by default. No profile switch,
and none of the expanded-only commands (`/opsx:onboard`, `/opsx:new`, `/opsx:continue`,
`/opsx:ff`, `/opsx:update`, `/opsx:verify`, `/opsx:bulk-archive`) are used anywhere below.
Every command below was actually executed while writing this doc, against OpenSpec
v1.5.0. Only the command you type in a terminal is shown in Step 1 — everything else runs
in Claude Code chat.

**Goal**: a small CLI tool, `todo.py`, that manages a to-do list stored in a local JSON
file, supporting `add`, `list`, `complete`, and `remove` commands.

### Step 1 — Setup (terminal: `cmd.exe`/PowerShell/bash)

```bash
>> mkdir todo-cli-project && cd todo-cli-project
>> openspec init --tools claude

>> claude
```

No `openspec config profile` switch is needed — `core` is the profile already installed.

### Step 2 — Explore (optional — Claude Code chat)

```
/opsx:explore "what should a minimal command-line to-do list tool support"
```

Creates no files. Useful here to settle on the JSON storage shape and command names
before committing to a proposal.

### Step 3 — Propose (Claude Code chat)

```
/opsx:propose "Add a CLI tool that manages a to-do list stored in a local JSON file, with add, list, complete, and remove commands"
```

Creates `proposal.md`, `design.md`, `specs/todo-cli/spec.md`, and `tasks.md` in one
guided pass. This is the only way to create a change under the core profile — the
step-by-step alternative (`/opsx:new` → `/opsx:continue` → `/opsx:continue` → `/opsx:ff`)
is expanded-profile only (Section 3b), not available here.

Review the created artifacts; edit by hand if anything needs correcting.

### Step 4 — Apply (Claude Code chat)

```
/opsx:apply
```

Implements `todo.py` per the artifacts above. Verify it genuinely works before moving
on — run `add`, `list`, `complete`, and `remove` yourself, plus an edge case such as
completing an item that doesn't exist.

### Step 5 — Sync (optional — Claude Code chat)

```
/opsx:sync
```

Only needed if you want the durable spec updated before the change is fully archived;
otherwise skip straight to Step 6.

### Step 6 — Archive (Claude Code chat)

```
/opsx:archive
```

Only run this once every `tasks.md` item is genuinely verified working. Folds the
change's specs into `openspec/specs/todo-cli/spec.md` permanently — the project's living
documentation from this point forward.

That is the complete loop: five commands (`/opsx:explore`, `/opsx:propose`,
`/opsx:apply`, `/opsx:sync`, `/opsx:archive`), matching Section 4's "Typical Loop" and
Section 3a's core command table exactly — no interactive profile picker, and nothing
beyond what `openspec init --tools claude` gives you out of the box.

---

## 7. Quick Reference

```
# Setup (once per project, terminal)
npm install -g @fission-ai/openspec

openspec init --tools claude

# core profile (default) — Claude Code chat only
/opsx:explore  "..."      # optional, before proposing

/opsx:propose  "..."      # create change + all artifacts in one pass

/opsx:apply                # implement tasks.md

/opsx:sync                  # optional, mid-flight — push delta specs early

/opsx:archive                # finalize once verified

# custom/expanded profile — needs `openspec config profile` (interactive) first

/opsx:onboard      # guided first pass on an existing/legacy codebase

/opsx:new  "..."   # scaffold a change with no artifacts yet

/opsx:continue      # create the next artifact in dependency order

/opsx:ff             # create all remaining artifacts at once (= /opsx:propose on an existing change)

/opsx:update         # revise artifacts after requirements changed

/opsx:verify          # confirm implementation matches the artifacts

/opsx:bulk-archive     # archive several finished changes at once
```
