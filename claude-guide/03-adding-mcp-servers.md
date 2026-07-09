# Adding an MCP Server in Claude Code

*A reference guide for connecting Claude Code to external tools and data sources
through the Model Context Protocol.*

---

## 1. Purpose of This Document

This document explains what the Model Context Protocol (MCP) is, why connecting an MCP
server to Claude Code is useful, and how to add, authenticate, list, inspect, and remove
MCP servers, at both an individual and a team level.

---

## 2. What Is MCP and Why Add a Server

The Model Context Protocol (MCP) is an open standard for AI-tool integrations. It lets
Claude Code connect to external tools and data sources — issue trackers, databases,
monitoring dashboards, design tools, communication platforms, and internal systems —
beyond what is available out of the box.

The practical benefit is direct action instead of manual copy-paste: rather than
pulling data out of another system and pasting it into chat, Claude can query and act on
that system directly. Representative examples:

- "Add the feature described in JIRA issue ENG-4521 and open a pull request on GitHub."
- "Check Sentry and our analytics tool to see how the new feature is being used."
- "Find the emails of ten random users from our PostgreSQL database."
- "Update the email template to match the latest Figma design."

The signal that a new MCP server is worth adding is the same signal that motivates most
integrations: repeatedly copying information from one tool into a Claude Code
conversation by hand.

---

## 3. How MCP Servers Are Added

MCP servers are configured with the `claude mcp` family of CLI subcommands, run from a
terminal (not inside a Claude Code session).

### 3.1 Adding a local (stdio) server

A stdio server runs as a subprocess on your own machine.

```bash
claude mcp add <server-name> -- <command> <arg1> <arg2>...
```

Example — a browser automation server:

```bash
claude mcp add playwright -- npx -y @playwright/mcp@latest
```

Additional arguments are passed straight through after the command:

```bash
claude mcp add playwright -- npx -y @playwright/mcp@latest --browser firefox
```

### 3.2 Adding an HTTP server

An HTTP server connects to a hosted service over a URL rather than running locally.

```bash
claude mcp add --transport http <server-name> <url>
```

Example — a documentation server with no authentication:

```bash
claude mcp add --transport http claude-code-docs https://code.claude.com/docs/mcp
```

With a bearer token for authentication:

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer <TOKEN>"
```

With custom headers or environment variables:

```bash
claude mcp add --transport http my-server https://api.example.com/mcp \
  --header "X-Team: platform" \
  --env API_KEY=secret --env REGION=us-west
```

### 3.3 Adding a server from a JSON snippet

```bash
claude mcp add-json <server-name> '<json-config>'
```

Example — an HTTP server:

```bash
claude mcp add-json weather-api '{"type":"http","url":"https://api.weather.com/mcp","headers":{"Authorization":"Bearer token"}}'
```

Example — a stdio server:

```bash
claude mcp add-json local-weather '{"type":"stdio","command":"/path/to/weather-cli","args":["--api-key","abc123"],"env":{"CACHE_DIR":"/tmp"}}'
```

### 3.4 Importing from Claude Desktop

On macOS and WSL, servers already configured in the Claude Desktop app can be imported
directly:

```bash
claude mcp add-from-claude-desktop
```

This copies the relevant entries from Claude Desktop's own configuration file into
Claude Code.

---

## 4. Choosing a Scope

Every `claude mcp add` command accepts a `-s` / `--scope` flag that determines who can
see the server and where its configuration is stored.

| Scope | Meaning | Storage location | Visible to |
|---|---|---|---|
| `local` (default) | Private to you, active only in the current project | `~/.claude.json`, under the project's entry | Only you, only this project |
| `user` | Private to you, active in every project you work in | `~/.claude.json`, under the top-level `mcpServers` key | Only you, all your projects |
| `project` | Shared with the whole team through version control | `.mcp.json` in the project root | Everyone who clones the repository |

Examples:

```bash
# Available in every project you personally work in
claude mcp add --scope user --transport http sentry https://mcp.sentry.dev/mcp

# Shared with the team via .mcp.json, committed to the repository
claude mcp add --scope project --transport http github https://api.githubcopilot.com/mcp/
```

On Windows, `~/.claude.json` resolves to `%USERPROFILE%\.claude.json`. If the
`CLAUDE_CONFIG_DIR` environment variable is set, Claude Code reads `.claude.json` from
inside that directory instead.

---

## 5. Managing Configured Servers

| Command | Purpose |
|---|---|
| `claude mcp list` | Lists every configured server and its current connection status. |
| `claude mcp get <server-name>` | Shows the full configuration and, if disconnected, the error detail for a specific server. |
| `claude mcp remove <server-name>` | Removes a server. |
| `claude mcp remove <server-name> --scope <scope>` | Removes a server from a specific scope, when the same name exists in more than one. |

Status indicators shown by `claude mcp list`:

| Indicator | Meaning |
|---|---|
| Connected | Ready to use. |
| Connected, tools fetch failed | Connected, but the tool list could not be retrieved — run `claude mcp get <name>` for detail. |
| Needs authentication | Reachable, but requires a browser sign-in or a token before use. |
| Failed to connect | The server did not respond. |
| Connection error | The connection attempt raised an error. |
| Pending approval | A project-scoped server is awaiting your one-time approval. |

---

## 6. Checking MCP Status Inside a Session

Inside a running `claude` session, the `/mcp` slash command opens an interactive panel
that:

- Lists every connected server and its status.
- Lets you select a server to inspect its available tools and resources.
- Prompts an `Authenticate` action for servers awaiting OAuth sign-in.
- Offers a way to reconnect a failed server.

From a plain terminal, without starting a session, the equivalent view is:

```bash
claude mcp list
```

To run the OAuth flow for a server without opening a full session:

```bash
claude mcp login <server-name>
```

Add `--no-browser` in headless or SSH environments — Claude Code prints the
authorization URL instead of opening a browser; paste the resulting redirect URL back at
the prompt. To clear stored credentials for a server:

```bash
claude mcp logout <server-name>
```

---

## 7. Authenticating Remote Servers

Two authentication patterns are supported for HTTP servers:

**OAuth (interactive sign-in)** — typical for services such as Sentry, Linear, or
Notion:

1. Add the server: `claude mcp add --transport http sentry https://mcp.sentry.dev/mcp`
2. Run `/mcp` inside a session, select the server, and choose `Authenticate`.
3. A browser window opens to the service's own sign-in page; approve the connection.
4. The server's status changes from `Needs authentication` to `Connected`.

By default, Claude Code selects a random available local port for the OAuth callback.
If the server's OAuth application has a fixed, pre-registered redirect URI, pin the
callback port explicitly:

```bash
claude mcp login sentry --callback-port 8080
```

**Static token (non-interactive)** — typical for services such as GitHub:

```bash
claude mcp add --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer <TOKEN>"
```

---

## 8. Environment Variable Expansion in `.mcp.json`

`.mcp.json` supports environment variable substitution, which keeps secrets and
per-developer values out of the committed configuration file itself.

| Syntax | Behavior |
|---|---|
| `${VAR}` | Expands to the value of environment variable `VAR`. |
| `${VAR:-default}` | Expands to `VAR` if it is set, otherwise falls back to `default`. |

Expansion applies to the `command`, `args`, `env`, `url`, and `headers` fields. If a
referenced variable has no value and no default, Claude Code fails to parse the
configuration.

```json
{
  "mcpServers": {
    "api-server": {
      "type": "http",
      "url": "${API_BASE_URL:-https://api.example.com}/mcp",
      "headers": {
        "Authorization": "Bearer ${API_KEY}"
      }
    }
  }
}
```

---

## 9. Practical Example: Adding the GitHub MCP Server End to End

**Step 1 — Generate a GitHub personal access token.** In GitHub, go to Settings →
Developer settings → Personal access tokens, generate a fine-grained token scoped to the
repositories Claude should access, and grant it the permissions required (for example,
`Contents: Read & Write` and `Issues: Read & Write`).

**Step 2 — Add the server:**

```bash
claude mcp add --scope project --transport http github https://api.githubcopilot.com/mcp/ \
  --header "Authorization: Bearer ghp_YOUR_TOKEN_HERE"
```

**Step 3 — Verify the connection:**

```bash
claude mcp list
```

Expected output includes a line similar to:

```
github (http)   Connected
```

**Step 4 — Use it in a session:**

```
claude
```

```
Create a pull request for the feature described in the open GitHub issue.
```

**Step 5 — Resulting `.mcp.json`** (because `--scope project` was used):

```json
{
  "mcpServers": {
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ghp_YOUR_TOKEN_HERE"
      }
    }
  }
}
```

A secret committed in plain text like this is only appropriate for a personal-scope
file that is not checked in. For a team-shared `.mcp.json`, use environment variable
expansion instead — see Section 10.

---

## 10. Project-Level `.mcp.json` for Team Sharing

A `.mcp.json` file in the project root, committed to version control, lets an entire
team share the same MCP server configuration.

```json
{
  "mcpServers": {
    "claude-code-docs": {
      "type": "http",
      "url": "https://code.claude.com/docs/mcp"
    },
    "github": {
      "type": "http",
      "url": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer ${GITHUB_TOKEN}"
      }
    },
    "playwright": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest", "--browser", "chromium"],
      "env": {
        "HEADLESS": "true"
      }
    }
  }
}
```

Field reference:

| Field | Required | Applies to | Description |
|---|---|---|---|
| `type` | Yes | Both | `"http"` or `"stdio"`. |
| `url` | Yes | `http` | The server's HTTPS endpoint. Supports `${VAR}` expansion. |
| `command` | Yes | `stdio` | The executable name or path. Supports `${VAR}` expansion. |
| `args` | No | Both | Command-line arguments; each entry supports `${VAR}` expansion. |
| `env` | No | Both | Environment variables passed to the server process. Supports `${VAR:-default}`. |
| `headers` | No | `http` | HTTP headers, most commonly used for authentication. Supports `${VAR}` expansion. |
| `oauth` | No | `http` | Optional OAuth configuration: `clientId` and `callbackPort`. |

When a teammate clones the repository and starts Claude Code, they are prompted once to
approve each project-scoped server. After approval, `/mcp` shows the server as
`Connected`; for OAuth-based servers, each teammate still authenticates individually
with `claude mcp login <name>`. Secrets referenced with `${VAR}` (for example
`GITHUB_TOKEN`) must be set in each teammate's own environment — they are never stored
in the committed file itself.

---

## 11. Best Practices

- Default to `project` scope for anything the whole team should use, and reference
  secrets with `${VAR}` expansion rather than committing literal tokens.
- Use `local` (the default) scope for one-off, personal, or experimental server
  connections that should not affect teammates.
- Remove servers that are no longer in active use — each connected server's tool list
  occupies part of the context window even when idle.
- For servers that are slow to start (for example, an `npx` package being downloaded for
  the first time), raise the startup timeout with `MCP_TIMEOUT=60000 claude` rather than
  assuming the server is broken.
- Reset a project's stored server approvals with `claude mcp reset-project-choices` when
  the set of project-scoped servers in `.mcp.json` has changed significantly and needs
  re-review.

---

## 12. Common Pitfalls

| Symptom | Likely cause | Fix |
|---|---|---|
| Server shows `Needs authentication` indefinitely | OAuth flow was never completed | Run `/mcp` inside a session and choose `Authenticate`, or run `claude mcp login <name>` from a terminal |
| `.mcp.json` fails to parse | An `${VAR}` reference has no value and no default | Set the referenced environment variable, or add a `:-default` fallback |
| Server works locally but not for teammates | Server was added with the default `local` scope instead of `project` | Re-add with `--scope project`, or move the entry into `.mcp.json` directly |
| Stdio server times out on first run | Underlying command (for example `npx`) is downloading a package for the first time | Increase the timeout with `MCP_TIMEOUT=60000 claude` |
| Secret token visible in git history | Token was written directly into a committed `.mcp.json` instead of referenced via `${VAR}` | Rotate the token, then switch the configuration to environment variable expansion |

---

## 13. Related Documentation

See the [official documentation links table](../README.md#official-documentation-links)
in this repository's root README for the authoritative Anthropic sources this document
was built from.
