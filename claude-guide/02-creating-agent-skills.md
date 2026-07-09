# Creating Agent Skills

*A reference guide for the Agent Skills standard, and for building custom Skills that
run through the Claude Developer Platform (API) in addition to Claude Code.*

---

## 1. Purpose of This Document

This document follows the same structure as [Creating a SKILL.md File in Claude
Code](01-creating-a-skill.md) but addresses a broader question: what "Agent Skills" means
as an official, portable standard, how it is used outside of Claude Code — specifically
through the Claude API — and how to author and deploy a Skill for that context. Read this
document alongside the Claude Code–specific guide rather than in place of it; the two
are complementary.

---

## 2. What Are Agent Skills

**Agent Skills** is Anthropic's official umbrella term for the portable `SKILL.md`
format itself — an open standard, published at `agentskills.io`, describing how to
package instructions, metadata, and optional resources into a modular capability that
an AI agent can load on demand.

The same `SKILL.md` format is used, with product-specific extensions, across:

- **Claude Code** — filesystem-based Skills, covered in
  [Creating a SKILL.md File in Claude Code](01-creating-a-skill.md).
- **The Claude Developer Platform (API)** — Skills uploaded via a dedicated `/v1/skills`
  endpoint and attached to a request through the `container` parameter.
- **Claude.ai** — Skills uploaded as a ZIP archive through account settings, used
  automatically in the background during conversations.
- **AWS Claude Platform and Microsoft Foundry** — Skills managed through those
  platforms' own upload mechanisms, using the same underlying format.

Anthropic's documentation consistently uses "Agent Skills" for the general, cross-product
concept and standard, and "Skills in Claude Code" or "Skills with the Claude API" when
referring to a specific product's implementation of it.

---

## 3. Why Agent Skills Exist

The motivation is the same as for Skills in Claude Code (see Section 3 of the companion
document): avoid permanently loading long instructions into every request, and make
expertise reusable rather than something that has to be re-explained from scratch. The
Agent Skills standard exists specifically to make that reusability **portable** — a
Skill authored once, following the standard format, is not locked to a single product.

A secondary motivation specific to the API is enabling teams to build custom agents
(through the Claude Agent SDK or direct API integration) that draw on the same modular
capabilities — including Anthropic's own pre-built Skills for common document formats —
without re-implementing that logic themselves.

---

## 4. How Agent Skills Work Across Products

The core mechanism — a `SKILL.md` file with YAML frontmatter plus a markdown body,
optionally bundled with supporting files, loaded via progressive disclosure — is
identical everywhere. What differs is how a Skill is registered, shared, and invoked in
each product:

| Aspect | Claude Code | Claude API | Claude.ai |
|---|---|---|---|
| Skill types available | Custom only | Anthropic pre-built (4 skills) plus custom | Anthropic pre-built (4 skills) plus custom |
| How a Skill is added | Placed in a filesystem location (Section 5 of the companion doc) | Uploaded via the `/v1/skills` API endpoint | Uploaded as a ZIP through account settings |
| Sharing scope | Personal (`~/.claude/`) or project (`.claude/`, via version control) | Workspace-wide — available to all members of the API workspace | Individual user only |
| How a Skill is invoked | Automatic match against `description`, or `/skill-name` | Attached explicitly per request via the `container.skills` parameter | Automatic, in the background |
| Execution environment | The local machine — full bash and network access | Claude's managed code execution container — no network access, only pre-installed packages | Claude's managed execution environment — network access varies by administrator settings |
| Versioning | None — filesystem-based, always reflects the current file contents | Explicit versions, identified by an epoch timestamp or the literal string `latest` | None — a single uploaded version |
| Cross-product sync | Not synced with the API or Claude.ai | Not synced with Claude Code or Claude.ai | Not synced with Claude Code or the API |

A Skill must be uploaded or placed separately in each product where it is meant to be
used — there is no automatic synchronization between Claude Code, the API, and Claude.ai.

---

## 5. Where Agent Skills Live and Are Managed

- **Claude Code**: filesystem directories under `~/.claude/skills/` or
  `.claude/skills/`, exactly as described in Section 5 of the companion document.
- **Claude API**: Skills exist as server-side objects, each identified by a generated ID
  such as `skill_01AbCdEfGhIjKlMnOpQrStUv`, created and listed through the
  `client.beta.skills` interface of the Anthropic SDK.
- **Claude.ai**: Skills are uploaded and managed from the user's account settings; they
  are not visible to or usable from the API or Claude Code.

---

## 6. Creating an Agent Skill — Step by Step (Claude API)

1. **Author `SKILL.md` in a local directory.** Follow the same frontmatter and body
   conventions described in Section 7 of the companion document (`name`, `description`,
   and a markdown body); the Claude Code–only extensions listed there
   (`allowed-tools`, `paths`, `hooks`, and similar) are not used by the API and should be
   omitted for a Skill intended primarily for API use.
2. **Upload the Skill directory** using the Anthropic SDK's `files_from_dir` helper:

   ```python
   from anthropic.lib import files_from_dir
   import anthropic

   client = anthropic.Anthropic()

   skill = client.beta.skills.create(
       files=files_from_dir("my_custom_skill"),
   )

   print(f"Created skill: {skill.id}")
   print(f"Latest version: {skill.latest_version}")
   ```

3. **Enable the required beta features on the request.** Using a Skill requires the code
   execution tool and two beta headers.
4. **Attach the Skill to a request** through the `container.skills` parameter (Section 8).
5. **Iterate by creating a new version**, rather than overwriting the original, whenever
   the Skill's instructions change (Section 11).

---

## 7. Frontmatter Reference

The required frontmatter fields are identical to those used in Claude Code:

| Field | Type | Purpose |
|---|---|---|
| `name` | string | Skill identifier. Maximum 64 characters; lowercase letters, numbers, and hyphens only. |
| `description` | string | What the Skill does and when to use it. Maximum 1,024 characters; non-empty. Drives automatic use in Claude.ai and guides Claude's use of the Skill once attached in the API. |

Claude Code–specific extensions from Section 7 of the companion document —
`disable-model-invocation`, `allowed-tools`, `disallowed-tools`, `paths`,
`argument-hint`, `arguments`, `shell`, `hooks`, and the CLI-only string substitutions
such as `${CLAUDE_SESSION_ID}` — are not part of the portable API-facing standard. They
are recognized only when the same `SKILL.md` is used inside Claude Code. This
distinction exists because Claude Code runs locally with full filesystem and bash
access, while the API executes Skills inside a managed, sandboxed code execution
container without that context.

---

## 8. Attaching a Skill to an API Request

Skills are attached to a Claude API request using the `container` parameter, which
requires the code execution tool to be enabled and two beta headers.

```python
import anthropic

client = anthropic.Anthropic()

response = client.beta.messages.create(
    model="claude-opus-4-8",
    max_tokens=4096,
    betas=["code-execution-2025-08-25", "skills-2025-10-02"],
    container={
        "skills": [
            {"type": "anthropic", "skill_id": "pptx", "version": "latest"}
        ]
    },
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
    messages=[
        {"role": "user", "content": "Create a presentation about renewable energy"}
    ],
)
```

Key constraints:

- Up to **8 Skills** may be attached to a single request.
- `type` is either `"anthropic"` (a pre-built Skill) or `"custom"` (one you uploaded).
- `version` accepts a specific version identifier or the literal string `"latest"`.
- Both beta headers — `skills-2025-10-02` and a code execution beta such as
  `code-execution-2025-08-25` — must be present, and the `code_execution` tool must be
  included in `tools`.

---

## 9. Pre-built Agent Skills

Anthropic provides four pre-built Skills, available consistently across the API,
Claude.ai, and other managed platforms, identified by short skill IDs of type
`"anthropic"`:

| Skill ID | Purpose |
|---|---|
| `pptx` | Create and edit presentations, analyze slide content |
| `xlsx` | Create spreadsheets, analyze data, generate charts and reports |
| `docx` | Create and edit documents, format text |
| `pdf` | Generate formatted PDF documents and reports |

These require no upload step — reference the `skill_id` directly in `container.skills`
as shown in Section 8.

---

## 10. Practical Example: Custom Skill With Versioning

Uploading a new version of an existing custom Skill, then using that specific version
in a request:

```python
from anthropic.lib import files_from_dir

# Create a new version from an updated local directory
new_version = client.beta.skills.versions.create(
    skill_id="skill_01AbCdEfGhIjKlMnOpQrStUv",
    files=files_from_dir("/path/to/updated_skill"),
)

response = client.beta.messages.create(
    model="claude-opus-4-8",
    max_tokens=16000,
    betas=["skills-2025-10-02", "code-execution-2025-08-25"],
    container={
        "skills": [
            {
                "type": "custom",
                "skill_id": "skill_01AbCdEfGhIjKlMnOpQrStUv",
                "version": new_version.version,
            }
        ]
    },
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],
    messages=[{"role": "user", "content": "Run the analysis using the updated skill."}],
)
```

Pinning a specific `version` rather than `"latest"` is the recommended approach for
production workloads, so that an in-progress update to the Skill's instructions does not
change behavior mid-rollout.

---

## 11. Managing Agent Skills (API)

| Operation | Method |
|---|---|
| List all Skills (Anthropic and custom) | `client.beta.skills.list()` |
| List only custom Skills | `client.beta.skills.list(source="custom")` |
| Create a custom Skill | `client.beta.skills.create(files=files_from_dir(...))` |
| Create a new version of an existing Skill | `client.beta.skills.versions.create(skill_id=..., files=...)` |
| Use a specific version | Set `"version"` in `container.skills` to the version identifier returned above, instead of `"latest"` |

---

## 12. Best Practices

- Keep a Skill's `SKILL.md` free of Claude Code–only frontmatter fields if it needs to
  work identically across Claude Code and the API — author the portable subset (`name`,
  `description`, markdown body) and layer Claude Code extensions on separately if truly
  needed only there.
- Pin explicit versions in production API requests rather than relying on `"latest"`.
- Keep the number of Skills attached to a single request as small as the task actually
  requires; each attached Skill's metadata still occupies context.
- Treat Skill uploads to Claude.ai, the API, and Claude Code as three independent
  deployments of the same source directory — update all three deliberately rather than
  assuming a change in one propagates to the others.

---

## 13. Common Pitfalls

| Symptom | Likely cause | Fix |
|---|---|---|
| API request fails referencing a Skill | Missing one of the two required beta headers, or the `code_execution` tool is not included in `tools` | Confirm both `skills-2025-10-02` and a code execution beta are present, and `code_execution` is listed under `tools` |
| Skill behaves differently in Claude Code than through the API | The `SKILL.md` relies on Claude Code–only fields (`allowed-tools`, `paths`, shell substitutions) that the API does not interpret | Separate the portable instructions from the Claude Code–specific configuration |
| Updated Skill instructions have no effect on API responses | Request is still pinned to an older `version`, or `"latest"` was cached before the new version was created | Confirm the version identifier passed in `container.skills` matches the newly created version |
| Teammates cannot see a Skill uploaded to the API | Skills uploaded to Claude.ai are individual to the uploading user; only API-uploaded Skills are workspace-wide | Upload the Skill through the API rather than the Claude.ai UI if team-wide access is required |

---

## 14. Related Documentation

See [Creating a SKILL.md File in Claude Code](01-creating-a-skill.md) for the
Claude Code–specific mechanism, and the
[official documentation links table](../README.md#official-documentation-links) in this
repository's root README for the authoritative Anthropic sources this document was built
from.
