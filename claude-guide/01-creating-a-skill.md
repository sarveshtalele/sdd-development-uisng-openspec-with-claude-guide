# Creating a SKILL.md File in Claude Code

*A reference guide for building, structuring, and maintaining Skills in Claude Code.*

## 1. Purpose of This Document

This document explains what a Skill is, why the feature exists, how Claude Code
discovers and uses Skills at runtime, and how to author a `SKILL.md` file correctly. It
is intended as a self-contained reference for engineers, technical writers, and team
leads who want to package repeatable instructions, procedures, or expertise into Claude
Code.

## 2. What Is a Skill

A Skill is a self-contained, filesystem-based capability that extends what Claude can
do. At minimum, a Skill is a directory containing one required file, `SKILL.md`, which
combines YAML frontmatter (metadata) with markdown instructions. A Skill directory may
also bundle supporting files — reference documents, templates, or executable scripts —
that Claude reads or runs only when the Skill is actually in use.

Claude Code Skills follow the **Agent Skills architecture**: a filesystem-based model
built around progressive disclosure, with a set of Claude Code–specific frontmatter
extensions layered on top (Section 7). See [Agent Skills](02-creating-agent-skills.md)
for how that underlying architecture works and why it is designed the way it is.

Once a Skill directory exists in the right location, Claude adds it to its toolkit
automatically — there is no separate install or registration step.

## 3. Why Skills Exist

Skills solve a specific problem: instructions that are used repeatedly, but not on
every single turn of every conversation, are expensive to keep permanently loaded and
tedious to paste in by hand each time.

The official rationale, in summary:

- **Context efficiency.** Unlike the contents of a `CLAUDE.md` file, which are loaded
  into every conversation, a Skill's full instructions load only when the Skill is
  actually triggered. Long reference material costs almost nothing until it is needed.
- **Progressive disclosure.** Skill content loads in stages — lightweight metadata at
  session startup, full instructions only when triggered, and any bundled resource
  files only when explicitly referenced. This keeps the working context window small
  by default.
- **Reusable expertise.** A Skill is written once and is then available in every
  relevant conversation, rather than being re-explained from scratch each time.
- **A natural home for procedures.** When a section of `CLAUDE.md` grows from a short
  fact into a multi-step procedure or checklist, that is the signal to move it into a
  Skill instead.

In short: create a Skill whenever the same instructions, checklist, or multi-step
procedure keeps being pasted into chat by hand.

## 4. How Skills Work in Claude Code

### 4.1 Progressive disclosure

Skill content is loaded in three levels, each more expensive than the last:

| Level | Content | When it loads | Approximate cost |
|---|---|---|---|
| 1. Metadata | The `name` and `description` fields from frontmatter | Always, at session startup | Lightweight — roughly 100 tokens per Skill |
| 2. Instructions | The markdown body of `SKILL.md` | Only when the Skill is triggered | Loaded on demand |
| 3. Resources | Bundled files (reference docs, templates, scripts) | Only when explicitly read or executed | No cost unless actually used |

### 4.2 Discovery and triggering

Every Skill's `name` and `description` are included in the system prompt at the start
of a session, so Claude is always aware a Skill exists and roughly what it is for.
When a user's request matches what a Skill's `description` says it does, Claude loads
that Skill's full instructions into context and follows them. The `description` field
is therefore the single most important part of a Skill — it is what drives automatic
triggering (see Section 8).

A Skill can also be invoked directly and explicitly by the user, without relying on
automatic matching, by typing `/skill-name` in the Claude Code prompt.

### 4.3 Live discovery, no restart required

Adding, editing, or removing a Skill takes effect within the current session — Claude
Code does not need to be restarted for a Skill change to be picked up.

## 5. Where Skills Live

Skill directories are discovered from several locations, and higher-precedence
locations take priority when names collide.

| Level | Location | Scope | Shared with team |
|---|---|---|---|
| Personal | `~/.claude/skills/<skill-name>/SKILL.md` | All of your own projects | No — local to your machine |
| Project | `.claude/skills/<skill-name>/SKILL.md` | The current project only | Yes — commit to version control |
| Plugin | `<plugin>/skills/<skill-name>/SKILL.md` | Wherever the plugin is enabled | Yes — distributed with the plugin |

Additional notes on discovery:

- Project Skills are loaded from `.claude/skills/` in the current working directory and
  in every parent directory up to the repository root.
- Nested `.claude/skills/` directories inside subdirectories (for example,
  `packages/frontend/.claude/skills/`) are discovered on demand as Claude works in that
  part of the repository.
- Skills from directories added with `--add-dir` are also discovered from `.claude/skills/`
  inside those additional directories.
- If a nested Skill shares a name with another Skill already in scope, both remain
  available; the nested one is given a directory-qualified name, for example
  `/apps/web:deploy`.

There is no separate "install" command for a standalone Skill — placing a correctly
structured directory in one of the locations above is sufficient for Claude Code to
discover it.

## 6. Creating a SKILL.md File — Step by Step

1. **Choose the scope.** Decide whether the Skill is personal (`~/.claude/skills/`) or
   belongs to a specific project and should be committed to version control
   (`.claude/skills/`).
2. **Create the directory.** Use a short, descriptive, kebab-case name for the Skill
   directory — this becomes the Skill's `/name` when invoked directly.

   ```bash
   mkdir -p .claude/skills/commit-message
   ```

3. **Write `SKILL.md`.** Create the file inside that directory with YAML frontmatter at
   the top, followed by markdown instructions in the body.
4. **Write the `description` field carefully.** This is what Claude compares against a
   user's request to decide whether to trigger the Skill (see Section 8).
5. **Add supporting files if needed.** Reference documents, templates, and scripts can
   live alongside `SKILL.md` in the same directory or in subdirectories (see Section 9).
6. **Test it.** Start a Claude Code session in the project (or restart if testing a
   personal Skill for the first time) and either describe a task that should trigger the
   Skill automatically, or invoke it directly with `/skill-name`.
7. **Iterate on the description.** If the Skill does not trigger when expected, or
   triggers when it should not, refine the `description` field first — it is the most
   common source of triggering problems.

## 7. Frontmatter Reference

The YAML frontmatter block sits between two `---` lines at the top of `SKILL.md`. Only
`name` and `description` are commonly required in practice; the rest are optional
Claude Code extensions that control behavior when the Skill is active.

| Field | Type | Purpose |
|---|---|---|
| `name` | string | Display name and invocation name. Maximum 64 characters; lowercase letters, numbers, and hyphens only; reserved words such as `anthropic` and `claude` are not permitted. |
| `description` | string | What the Skill does and when to use it. Maximum 1,024 characters. This is the field that drives automatic triggering. |
| `when_to_use` | string | Additional triggering context, appended to `description` in the Skill listing. Combined length of `description` and `when_to_use` is capped at 1,536 characters. |
| `disable-model-invocation` | boolean | If `true`, only the user can invoke the Skill (via `/skill-name`); Claude cannot trigger it automatically. Useful for workflows with side effects. Default: `false`. |
| `user-invocable` | boolean | If `false`, the Skill is hidden from the `/` command menu and can only be triggered by Claude automatically. Default: `true`. |
| `allowed-tools` | string or list | Tools Claude may use without an additional permission prompt while this Skill is active. Does not restrict tool use — only pre-approves it. |
| `disallowed-tools` | string or list | Tools removed from Claude's available tool set while this Skill is active. |
| `argument-hint` | string | Hint text shown during autocomplete for the arguments a Skill expects, for example `[issue-number]`. |
| `arguments` | string or list | Named positional arguments, made available for substitution as `$name` in the Skill body. |
| `paths` | string or list of glob patterns | Restricts automatic activation to sessions working with files matching these patterns, for example `src/**,*.test.ts`. |
| `shell` | string | Shell used to evaluate inline commands in the Skill body. `bash` (default) or `powershell`. |
| `model` | string | Overrides the active model while the Skill runs, for example `claude-opus`, `claude-sonnet`, or `inherit`. |
| `effort` | string | Overrides the effort level while the Skill runs: `low`, `medium`, `high`, `xhigh`, or `max`. |
| `context` | string | Set to `fork` to run the Skill in an isolated subagent context rather than inline in the current conversation. |
| `agent` | string | Which subagent type to use when `context: fork` is set, for example a built-in type (`Explore`, `Plan`, `general-purpose`) or a custom subagent defined under `.claude/agents/`. |
| `hooks` | object | Hooks scoped to this Skill's own lifecycle, for example `pre-invoke` and `post-invoke`. |

## 8. Writing an Effective Description

Because the `description` field drives automatic triggering, it should state both what
the Skill does and when it should be used, written in the third person.

**Do:**

```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

```yaml
description: Generate descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages or reviewing staged changes.
```

**Avoid:**

```yaml
description: Helps with documents
description: Processes data
description: I can help you with PDFs
```

The vague examples above give Claude no concrete signal about when the Skill applies,
and the first-person phrasing does not match the standard's conventions. A good
description names concrete triggers — file types, task verbs, or phrases a user is
likely to say — rather than describing the Skill only in the abstract.

## 9. Bundling Supporting Files

A Skill is not limited to a single file. `SKILL.md` is the entry point; additional
markdown references, templates, and executable scripts can live alongside it and are
only loaded into context when actually needed, preserving the progressive-disclosure
benefit described in Section 4.1.

Example directory structure:

```
pdf-processing/
├── SKILL.md          # Main instructions — references the files below
├── FORMS.md           # Form-filling guide
├── REFERENCE.md        # Detailed API reference
├── examples.md          # Usage examples
└── scripts/
    ├── analyze_form.py    # Executed via bash; only its output enters context
    ├── fill_form.py
    └── validate.py
```

Reference bundled markdown files from the body of `SKILL.md` using standard markdown
links:

```markdown
## Additional resources

**Form filling**: See [FORMS.md](FORMS.md) for the complete guide.
**API reference**: See [REFERENCE.md](REFERENCE.md) for all methods.
```

Reference bundled scripts using the `${CLAUDE_SKILL_DIR}` placeholder, which always
resolves to the Skill's own directory regardless of which scope it was installed at:

````markdown
Run the analysis:

```bash
python ${CLAUDE_SKILL_DIR}/scripts/analyze_form.py input.pdf
```
````

Files that are never referenced are never read into context — bundling large reference
material costs nothing unless Claude actually opens it.

## 10. Practical Example

The following is a complete, realistic `SKILL.md` file for a Skill that summarizes
uncommitted changes in a git repository:

```yaml
---
name: summarize-changes
description: Summarizes uncommitted changes and flags anything risky. Use when the user asks what changed, wants a commit message, or asks to review their diff.
---

## Current changes

!`git diff HEAD`

## Instructions

Summarize the changes above in two or three bullet points, then list any risks you
notice such as missing error handling, hardcoded values, or tests that need updating.
If the diff is empty, say there are no uncommitted changes.
```

The `` !`git diff HEAD` `` line is a dynamic context injection: Claude Code runs the
command and substitutes its output directly into the Skill content before Claude ever
sees it. This keeps the Skill self-contained — it always operates on the current state
of the repository rather than a snapshot written at authoring time.

A second example, for a Skill with bundled reference material:

````yaml
---
name: pdf-processing
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---

# PDF Processing

## Quick start

Extract text with pdfplumber:

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
    tables = pdf.pages[0].extract_tables()
```

## Form filling

See [FORMS.md](FORMS.md) for the complete form-filling guide.

## API reference

See [REFERENCE.md](REFERENCE.md) for complete API documentation.
````

## 11. Managing Skills

| Command | Purpose |
|---|---|
| `/skills` | Opens an interactive menu listing available Skills. Press `Space` to toggle a Skill's visibility state (on, name-only, user-invocable-only, or off), then `Enter` to save. |
| `/skill-name` | Invokes a specific Skill directly by name, for example `/pdf-processing`. |
| `/skill-name arg1 arg2` | Invokes a Skill and passes arguments to it. |
| `/plugin install <skill-plugin>@<marketplace>` | Installs a plugin that bundles one or more Skills. |

There is no dedicated `/skill create` command — Skills are discovered automatically
from the filesystem locations listed in Section 5, so creating one is simply a matter of
adding a correctly structured directory.

## 12. Best Practices

- Write the `description` field first, and revisit it whenever triggering behaves
  unexpectedly — it is the single highest-leverage part of a Skill.
- Keep the main body of `SKILL.md` focused on procedure; move long reference material
  into separate bundled files linked from the body.
- Use `disable-model-invocation: true` for Skills that perform side-effecting actions
  (deployments, destructive operations) so they only run when a user explicitly asks
  for them via `/skill-name`.
- Prefer project scope (`.claude/skills/`) and commit the directory to version control
  whenever a Skill is useful to the whole team, rather than keeping it personal.
- Scope automatic activation with the `paths` field when a Skill is only relevant to a
  specific part of a codebase, to avoid it being considered for unrelated work.

## 13. Common Pitfalls

| Symptom | Likely cause | Fix |
|---|---|---|
| Skill never triggers automatically | `description` is too vague or missing concrete trigger phrases | Rewrite `description` with specific file types, task verbs, or user phrasing (Section 8) |
| Skill triggers on unrelated requests | `description` is too broad | Narrow the wording, or add a `paths` restriction |
| Skill not found at all | Directory is in the wrong location, or `SKILL.md` is missing/misnamed | Confirm the path matches Section 5 exactly and the file is named `SKILL.md` |
| Bundled script not found at runtime | Hardcoded relative path instead of `${CLAUDE_SKILL_DIR}` | Use the `${CLAUDE_SKILL_DIR}` placeholder so the path resolves correctly at any install scope |
| Teammates cannot see a Skill | Skill was created under the personal (`~/.claude/skills/`) scope instead of project scope | Move the directory to `.claude/skills/` and commit it |

## 14. Related Documentation

See [Agent Skills](02-creating-agent-skills.md) for the architecture underneath this
file format — why it is designed the way it is, and how Claude decides what to load and
when.
