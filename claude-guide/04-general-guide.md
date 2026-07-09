# General Guide: Skills, Subagents, Hooks, and Plugins in Claude Code

*An orientation guide to Claude Code's four extensibility mechanisms, how they relate to
one another, and how to choose between them.*

## 1. Purpose of This Document

Claude Code can be extended in four distinct ways: Skills, Subagents, Hooks, and
Plugins. Each solves a different problem, and they are frequently combined rather than
used in isolation. This document gives a working overview of all four, with enough
detail to get started, and points to the two dedicated documents in this folder for a
full treatment of Skills specifically.

## 2. Overview

| Mechanism | What it is | Who or what invokes it | Typical use |
|---|---|---|---|
| Skill | Reusable instructions Claude loads on demand | Claude automatically, or the user via `/skill-name` | Reference material, checklists, repeatable procedures |
| Subagent | An isolated AI assistant with its own context window, tools, and prompt | Claude automatically, or the user via `@agent-name` | Self-contained work whose output does not need to stay in the main conversation |
| Hook | A shell command, HTTP call, or MCP tool that fires automatically at a defined lifecycle event | The system, automatically, at the matching event | Deterministic enforcement — formatting, validation, blocking a dangerous action |
| Plugin | A distributable package bundling any combination of Skills, Subagents, Hooks, MCP servers, and commands | Installed once via `/plugin install`, then behaves as if its contents were configured locally | Sharing a complete toolset with a team or the wider community |

Skills are covered in full detail in [Creating a SKILL.md File in Claude
Code](01-creating-a-skill.md) and [Agent Skills](02-creating-agent-skills.md).
This document summarizes Skills briefly and covers Subagents, Hooks, and Plugins in
full.

## 3. Skills — Summary

A Skill is a directory containing a `SKILL.md` file (YAML frontmatter plus markdown
instructions), optionally bundled with reference files or scripts, stored under
`.claude/skills/` (project) or `~/.claude/skills/` (personal). Claude loads a Skill's
full instructions only when its `description` matches the current task, keeping the
default context window small. See the two dedicated Skill documents in this folder for
the complete frontmatter reference, authoring guidance, and examples.

## 4. Subagents

### 4.1 What a subagent is

A subagent is a specialized assistant that runs in its own, isolated context window,
with its own system prompt, its own tool permissions, and independent context from the
main conversation. Delegating a task to a subagent keeps large or noisy intermediate
output — search results, exploratory reading, long tool output — out of the main
conversation, since only the subagent's final response returns to it.

### 4.2 Where subagents are defined

| Level | Location | Scope |
|---|---|---|
| Project | `.claude/agents/<name>.md` | This project, shared via version control |
| Personal | `~/.claude/agents/<name>.md` | All of your projects |
| Session (CLI) | Passed as JSON via the `--agents` flag | Current session only |
| Plugin | `<plugin>/agents/<name>.md` | Wherever the plugin is enabled, namespaced as `plugin-name:agent-name` |

### 4.3 Frontmatter reference

| Field | Type | Purpose |
|---|---|---|
| `name` | string | Unique identifier; becomes the agent's invocation name. |
| `description` | string | What the subagent is for — drives automatic delegation, the same way a Skill's `description` drives triggering. |
| `tools` | string or list | Tools the subagent is allowed to use. If omitted, it inherits the full tool set available to the main session. |
| `disallowedTools` | string or list | Tools explicitly removed from an otherwise inherited set. |
| `model` | string | `sonnet`, `opus`, `haiku`, `fable`, a full model identifier, or `inherit` to match the main session's model. |
| `permissionMode` | string | Controls how the subagent handles permission prompts: `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`, or `manual`. |
| `maxTurns` | number | Maximum number of agentic turns before the subagent is stopped. |
| `skills` | list | Skills to preload into the subagent's context at startup. |
| `mcpServers` | list | MCP servers available to the subagent. |
| `hooks` | object | Hooks scoped to the subagent's own lifecycle. |
| `color` | string | Display color in the UI, for example `blue` or `purple`. |

### 4.4 A realistic example

```yaml
---
name: db-safety-checker
description: Execute read-only database queries safely. Validates every query before execution. Use when you need to run database queries.
tools: Bash
model: haiku
permissionMode: default
---

You are a database safety specialist. You run read-only queries only.

Before running any SQL:
1. Parse the command to confirm it is SELECT-only.
2. Refuse any INSERT, UPDATE, DELETE, DROP, CREATE, ALTER, or TRUNCATE statement.
3. Log every query executed, for audit purposes.

If the user requests a non-SELECT operation, explain why you cannot do it and suggest
how they can make the change themselves.
```

### 4.5 Invoking a subagent

- **Automatic delegation** — Claude compares the task at hand against each available
  subagent's `description` and decides on its own whether to delegate, the same
  mechanism used for Skill triggering.
- **Explicit mention** — typing `@` shows a picker of available subagents; typing
  `@agent-name` (or `@plugin-name:agent-name` for a plugin-provided one) delegates
  directly.
- **Session-wide** — `claude --agent code-reviewer` runs an entire session as that
  subagent, rather than delegating a single task to it.

## 5. Hooks

### 5.1 What a hook is

A hook is a shell command, HTTP call, LLM prompt, or MCP tool invocation that Claude
Code runs automatically at a specific point in its lifecycle. Hooks exist for
deterministic enforcement — actions that must always happen, or must always be blocked,
regardless of Claude's own judgment in the moment.

### 5.2 Hook events

| Category | Events |
|---|---|
| Session | `SessionStart`, `SessionEnd` |
| Turn | `UserPromptSubmit`, `Stop`, `PreCompact` |
| Tool | `PreToolUse`, `PostToolUse` |
| Subagent | `SubagentStart`, `SubagentStop` |
| Other | `Notification`, `PermissionRequest` |

`PreToolUse` and `PostToolUse` are the two most commonly used events: the former can
block a tool call before it runs, and the latter can react after a tool call has
already succeeded — for example, running a formatter after every file edit.

### 5.3 Configuration schema

Hooks are configured under a `hooks` key inside a settings file.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-dangerous.sh"
          }
        ]
      }
    ]
  }
}
```

| Field | Purpose |
|---|---|
| Top-level key (for example `PreToolUse`) | The event this entry attaches to. |
| `matcher` | Which tool name(s) this entry applies to. Supports exact names (`Bash`), alternation (`Edit\|Write`), regex (`^Bash.*`), or `*` for all tools. |
| `hooks` | An array of one or more actions to run when the event and matcher both match. |
| `hooks[].type` | `command` (a shell command), `http` (a webhook call), or `mcp_tool` (an MCP tool invocation). |
| `hooks[].command` | The shell command to run, for `type: command`. |

Hook settings can live in `~/.claude/settings.json` (personal, all projects),
`.claude/settings.json` (project, committed to version control), or
`.claude/settings.local.json` (project, not committed) — the same three-tier structure
used for other Claude Code configuration.

### 5.4 Exit code and output conventions

A hook script communicates its result back to Claude Code through its exit code and,
optionally, JSON written to stdout:

| Exit code | Meaning |
|---|---|
| `0` | Success. If JSON is present on stdout, Claude Code parses it for additional instructions (for example, to deny a tool call). |
| `2` | Blocking error. The action is blocked, and stderr is shown to the user. |
| Any other value | Non-blocking error. Stderr is shown to the user, but execution continues. |

### 5.5 A realistic example — blocking a dangerous command

`.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PROJECT_DIR}/.claude/hooks/block-dangerous.sh"
          }
        ]
      }
    ]
  }
}
```

`.claude/hooks/block-dangerous.sh`:

```bash
#!/bin/bash
set -e

INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

if echo "$COMMAND" | grep -iE 'rm -rf' > /dev/null; then
  echo "Blocked: rm -rf is not allowed by project policy" >&2
  jq -n '{
    "hookSpecificOutput": {
      "hookEventName": "PreToolUse",
      "permissionDecision": "deny",
      "permissionDecisionReason": "Destructive command blocked by project policy"
    }
  }'
  exit 0
fi

exit 0
```

The `/hooks` slash command, run inside a session, lists and lets you test currently
configured hooks.

## 6. Plugins

### 6.1 What a plugin is

A plugin is a self-contained, distributable directory that bundles any combination of
Skills, Subagents, Hooks, and MCP server configuration into a single installable unit.
Plugins are the distribution mechanism for sharing an entire toolset — not just one
component — with a team or the broader community.

### 6.2 Plugin structure

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json          # Manifest, required for marketplace distribution
├── skills/
│   └── skill-one/
│       └── SKILL.md
├── agents/
│   └── code-reviewer.md
├── hooks/
│   └── hooks.json
├── .mcp.json                 # MCP server configuration bundled with the plugin
├── README.md
└── LICENSE
```

### 6.3 The plugin manifest

`.claude-plugin/plugin.json`:

```json
{
  "name": "my-plugin",
  "description": "Brief description shown in the marketplace listing",
  "version": "1.0.0",
  "author": {
    "name": "Your Name",
    "email": "you@example.com"
  },
  "homepage": "https://github.com/username/my-plugin",
  "repository": {
    "type": "git",
    "url": "https://github.com/username/my-plugin.git"
  },
  "license": "MIT"
}
```

### 6.4 Installing and managing plugins

```bash
# Install from a marketplace
/plugin install my-plugin@claude-plugins-official

# List configured marketplaces
/plugin marketplace list

# Add a marketplace
/plugin marketplace add anthropics/claude-plugins-official
/plugin marketplace add https://github.com/org/plugins.git

# Install, list, enable, or disable plugins
/plugin install my-plugin@myorg/internal-plugins
/plugin list
/plugin enable my-plugin
/plugin disable my-plugin
```

For local development, a plugin directory can be loaded directly without a marketplace:

```bash
claude --plugin-dir ./my-plugin
```

## 7. Custom Slash Commands

Custom slash commands are markdown files that create a `/command-name` shortcut,
located at `.claude/commands/<name>.md` (project) or `~/.claude/commands/<name>.md`
(personal). They use the same frontmatter conventions as Skills (Section 7 of [Creating
a SKILL.md File in Claude Code](01-creating-a-skill.md)):

```yaml
---
name: deploy-staging
description: Deploy the current branch to staging
disable-model-invocation: true
---

Deploy the current branch to staging:

1. Run the test suite.
2. Build the application.
3. Trigger the staging deployment pipeline.
```

Skills under `.claude/skills/` are the more capable, currently preferred way to define
an invocable command, since they additionally support bundled supporting files, dynamic
context injection, and forked subagent execution. Simple, single-file commands under
`.claude/commands/` remain fully supported.

## 8. How the Four Mechanisms Relate

| Question | Answer |
|---|---|
| I keep re-explaining the same procedure or checklist. | Use a **Skill**. |
| A task produces a lot of intermediate output I don't need to keep in the main conversation, or should run with restricted tools or a cheaper model. | Use a **Subagent**. |
| Something must always happen (or always be blocked) at a specific point, regardless of Claude's judgment in the moment. | Use a **Hook**. |
| I want to share several of the above as one package with my team or the community. | Use a **Plugin**. |

A single, realistic workflow often combines all four: a **Skill** holds the team's code
review checklist; a **Subagent** runs that checklist with read-only tools and a cheaper
model so the detailed findings don't clutter the main conversation; a **Hook** runs a
linter automatically after every file edit, independent of whether a review was
requested; and a **Plugin** bundles the Skill, the Subagent, and the Hook together so
every engineer on the team gets the same setup with a single `/plugin install`.

## 9. Best Practices

- Start with a Skill for anything that is primarily instructional; reach for a
  Subagent only once there is a real need for isolated context, restricted tools, or a
  different model.
- Keep hook scripts small, fast, and side-effect-focused — they run automatically and
  should not depend on Claude's judgment to decide whether to act.
- Commit project-scoped Skills, Subagents, and Hooks (`.claude/skills/`,
  `.claude/agents/`, `.claude/settings.json`) to version control so the whole team
  benefits from them, rather than keeping them personal.
- Package related Skills, Subagents, and Hooks into a single Plugin once there is more
  than one component to distribute — it is easier for a team to adopt one
  `/plugin install` than to replicate several files by hand.

## 10. Common Pitfalls

| Symptom | Likely cause | Fix |
|---|---|---|
| A hook doesn't fire | `matcher` does not match the tool name being used, or the hook is defined under the wrong event | Confirm the exact tool name and event; use `/hooks` to inspect configured hooks |
| A subagent is never delegated to automatically | `description` is too vague to trigger automatic delegation | Rewrite `description` with concrete trigger language, the same principle used for Skills |
| A hook blocks an action unexpectedly | Script exits with code `2` (or emits a `deny` decision) in a case broader than intended | Narrow the script's matching logic and test it directly before relying on it |
| A plugin's Skills or Subagents don't appear after installation | Plugin was not enabled, or the marketplace was not added first | Confirm with `/plugin list`, and check `/plugin marketplace list` for the source |

## 11. Related Documentation

See [Creating a SKILL.md File in Claude Code](01-creating-a-skill.md) and [Agent
Skills](02-creating-agent-skills.md) for the full Skill reference, [Creating a CLAUDE.md
File](05-creating-claude-md.md) for the companion project-memory mechanism, and the
[official documentation links table](../README.md#official-documentation-links) in this
repository's root README for the authoritative Anthropic sources this document was built
from.
