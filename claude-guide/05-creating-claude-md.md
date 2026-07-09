# Creating a CLAUDE.md File

*A reference guide for CLAUDE.md, Claude Code's persistent project-memory file: what it
is, why it exists, how it loads, and how to write one.*

## 1. Purpose of This Document

This document explains what a `CLAUDE.md` file is, why it exists alongside Skills
rather than replacing them, how Claude Code loads it, and how to create and maintain
one. It follows the same structure as the other documents in this folder and should be
read as the companion piece to [Creating a SKILL.md File in Claude Code](01-creating-a-skill.md):
the two mechanisms solve different problems and are meant to be used together.

## 2. What Is CLAUDE.md

`CLAUDE.md` is a markdown file, placed in a project's root directory, that Claude Code
reads at the start of every session. It holds the persistent instructions you would
otherwise have to retype into chat every time: build and test commands, coding
conventions, architecture notes, and anything else Claude should already know before
you ask it to do anything.

## 3. Why CLAUDE.md Exists

`CLAUDE.md` exists so that context does not have to be re-established by hand at the
start of every conversation. The official guidance for when to add something to it is
concrete and worth repeating directly: add an entry when Claude makes the same mistake
a second time, when a code review catches something Claude should already have known
about the codebase, when you find yourself typing the same correction into chat that
you typed last session, or when a new teammate would need the same context to be
productive.

Placed at the project root and committed to version control, it also gives an entire
team the same baseline instructions, rather than each person's own conversational
history being the only place that context lives.

## 4. How CLAUDE.md Loads — and How That Differs From a Skill

This is the single most important distinction to understand between `CLAUDE.md` and a
Skill (Section 4 of [Agent Skills](02-creating-agent-skills.md)):

| | `CLAUDE.md` | Skill |
|---|---|---|
| When it loads | In full, automatically, at the start of every session | Only when a matching request triggers it |
| Token cost | Paid on every session, whether or not it turns out to be relevant | Paid only when actually used |
| Claude's treatment of it | Context — informative, not enforced | Also context, loaded conditionally |
| Best suited to | Short, standing facts and conventions that apply broadly | Multi-step procedures relevant to specific tasks |

Because `CLAUDE.md` is loaded unconditionally, it is the wrong place for a long,
multi-step procedure that only matters for one part of a codebase — that content should
move into a Skill instead, exactly as noted in Section 3 of the Skill authoring guide.
`CLAUDE.md` is also context that Claude reasons over, not configuration that is
mechanically enforced — if an instruction must always be followed regardless of
Claude's own judgment in the moment, that is a job for a hook (Section 5 of the
[general guide](04-general-guide.md)), not for `CLAUDE.md`.

## 5. Where CLAUDE.md Files Live

| Location | Scope | Shared with team | Loaded |
|---|---|---|---|
| `CLAUDE.md` (project root) | This project | Yes — commit to version control | In full, at session start |
| `.claude/CLAUDE.md` | This project (alternative location) | Yes — commit to version control | In full, at session start |
| `CLAUDE.local.md` (project root) | This project, personal to you | No — add to `.gitignore` | In full, at session start |
| `~/.claude/CLAUDE.md` | Every project you work in | No — personal to you | In full, at session start |
| `<subdirectory>/CLAUDE.md` | That part of the repository (monorepo pattern) | Yes, if committed | On demand, when Claude reads files in that subdirectory |

Files that apply to the current session — the ones at the working directory and in the
directories above it — are loaded in full when the session starts. A subdirectory's own
`CLAUDE.md` is different: it is only loaded once Claude is actually working with files
in that subdirectory, which keeps a large monorepo's combined instructions from all
loading at once.

## 6. Creating a CLAUDE.md — Step by Step

1. **Let Claude generate a starting point.** Run `/init` inside a session. Claude
   analyzes the codebase and writes a starter `CLAUDE.md` covering the build and test
   commands, stack, and conventions it can detect. If a `CLAUDE.md` already exists,
   `/init` proposes improvements to it rather than overwriting it.
2. **Review and edit the generated file** — treat it as a first draft, not a finished
   document. Correct anything inaccurate and add anything Claude could not have
   inferred from the code alone.
3. **Commit it to the project root** so the whole team starts from the same baseline.
4. **Add to it over time**, using the trigger conditions in Section 3, rather than
   trying to write an exhaustive file up front.
5. **Use `/memory`** at any point to browse and edit every `CLAUDE.md`,
   `CLAUDE.local.md`, and rules file currently loaded into the session.

## 7. Importing Other Files

A `CLAUDE.md` file can pull in the contents of other files using `@path/to/file`
syntax, rather than duplicating their content inline.

```markdown
See @README.md for the project overview and @package.json for the available npm scripts.

## Additional instructions
- Git workflow: @docs/git-instructions.md
- Testing guidelines: @tests/README.md
```

Key behavior:

- Both relative and absolute paths are accepted; relative paths resolve relative to the
  file that contains the import, not the current working directory.
- An imported file can itself import further files, up to a maximum depth of four hops.
- Import parsing skips markdown code spans and fenced code blocks — to mention a path
  without triggering an import, wrap it in backticks, for example `` `@README.md` ``.
- The first time a session encounters an import, Claude Code shows an approval dialog
  listing the files that would be pulled in. Declining leaves imports disabled for that
  project without asking again.

Imports are useful for referencing a single source of truth — for example, pointing at
an existing `AGENTS.md` file used by other tools instead of maintaining a duplicate copy
of the same instructions inside `CLAUDE.md`.

## 8. What Belongs in CLAUDE.md

Suited to `CLAUDE.md`:

- Build, test, and lint commands
- Coding conventions — indentation, naming, export style
- Project architecture and directory layout
- Naming conventions and code style rules, written concretely — "use 2-space
  indentation" rather than "format code properly"
- Anything a new teammate would need to be told on their first day

Not suited to `CLAUDE.md`:

- A multi-step procedure relevant to only one part of the codebase — that belongs in a
  Skill (Section 8 of this document explains why).
- An instruction that must be mechanically guaranteed rather than followed at Claude's
  judgment — that belongs in a hook.

## 9. Size and Structure Guidance

Because the entire file is loaded on every single session regardless of relevance, size
directly costs context on every turn — and a long, dense file is also simply harder for
Claude to follow closely. Keep a project's `CLAUDE.md` under roughly 200 lines. If it
starts growing past that:

- Move anything that is really a multi-step procedure into a Skill instead (Section 4).
- Split unrelated topics into separate files and pull them in with `@path` imports
  (Section 7), rather than letting one file accumulate everything.
- Use markdown headers and bullet points to group related instructions — a well
  organized file is easier for Claude to follow than an equivalent wall of prose.

## 10. Managing CLAUDE.md During a Session

| Command | Purpose |
|---|---|
| `/init` | Generates a starter `CLAUDE.md` from the current codebase, or proposes improvements to an existing one. |
| `/memory` | Lists every `CLAUDE.md`, `CLAUDE.local.md`, and rules file currently loaded, and opens any of them for editing. |
| `/context` | Shows what is currently consuming the context window, including how much space `CLAUDE.md` itself occupies. |

## 11. Practical Example

A realistic, appropriately concise `CLAUDE.md` for a TypeScript and React project:

```markdown
# Project conventions

## Commands
- Build: `npm run build`
- Test: `npm test`
- Lint: `npm run lint`

## Stack
- TypeScript, strict mode enabled
- React, functional components only — no class components

## Rules
- Named exports only; never use default exports
- Tests live next to source: `foo.ts` -> `foo.test.ts`
- Every API route returns a `{ data, error }` shape
- Run `npm run lint` before considering a change complete
```

Each line is a concrete, checkable fact or rule — nothing here is a multi-step
procedure, which is what keeps it appropriate for a file that loads on every session.

## 12. Best Practices

- Write concrete, verifiable instructions rather than vague guidance — "use 2-space
  indentation," not "format code properly."
- Add to `CLAUDE.md` only when the trigger conditions in Section 3 actually occur;
  resist writing an exhaustive file speculatively before those moments happen.
- Commit the project-root file so the whole team benefits, and keep personal-only notes
  in `CLAUDE.local.md` instead.
- Revisit the file's size periodically, and move anything that has grown into a
  procedure out to a Skill.

## 13. Common Pitfalls

| Symptom | Likely cause | Fix |
|---|---|---|
| Claude ignores an instruction in `CLAUDE.md` | The file has grown too long, or the instruction is vague | Shorten the file and rewrite the instruction concretely (Section 9) |
| An instruction is followed inconsistently | The instruction needed to be mechanically enforced, not just stated as context | Move it to a hook instead (Section 4) |
| Teammates don't have the same context you do | Instructions were written into `CLAUDE.local.md` or typed into chat instead of the committed `CLAUDE.md` | Move shared context into the committed project-root file |
| `CLAUDE.md` keeps growing unmanageably | Multi-step procedures are being added directly instead of moved to Skills | Move procedural content into a Skill (Section 8), keep only standing facts here |

## 14. Related Documentation

See [Creating a SKILL.md File in Claude Code](01-creating-a-skill.md) and [Agent
Skills](02-creating-agent-skills.md) for the complementary, on-demand mechanism.
