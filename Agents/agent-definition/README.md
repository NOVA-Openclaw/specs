# Agent Definition

## Abstract

An **Agent Definition** is a platform-agnostic, JSON-based data object from which
any agent harness can configure a functional subagent. It separates WHO an
agent is (identity), WHAT it knows and how it works (bootstrap context), WHICH
models it prefers, and WHICH skills, tools, permissions, and I/O contract it
declares, into one portable document that no single harness owns.

Skills (how to do something) and tools (how to use a tool) already have
discoverable, installable, by-reference formats. Whole agent configurations do
not: exporting an agent from one harness and reconstituting an equivalent
agent in a different harness has, until now, been a manual, lossy, ad hoc
process. This specification fills that gap.

An Agent Definition does not run an agent by itself. It is consumed by a
**harness** (Claude Code, a Hermes profile, an OpenClaw-compatible gateway, or
any other agent runtime), which reads the definition and configures an
in-process or spawned agent to match it as closely as the harness is able.

## Status

This document is a **draft**. Spec version: `0.1.0` ([Semantic
Versioning 2.0.0](https://semver.org/)). It is a work in progress and subject
to breaking changes before a `1.0.0` release. See
[Versioning](#versioning) for how spec and definition versions relate, and the
repository's [issue tracker](https://github.com/NOVA-Openclaw/specs/issues)
for open design discussion.

**Feedback.** Questions, ideas, and "I tried it" reports are welcome in
[Discussions](https://github.com/NOVA-Openclaw/specs/discussions); concrete
problems or proposals belong in
[Issues](https://github.com/NOVA-Openclaw/specs/issues). See the
repository's [CONTRIBUTING](https://github.com/NOVA-Openclaw/specs/blob/main/CONTRIBUTING.md)
guide for how to propose a change. If you've built a harness or tool that
reads or writes an Agent Definition, please file an
[implementation report](https://github.com/NOVA-Openclaw/specs/issues/new?template=implementation-report.yml)
so it can be listed below.

**Implementations.**

- OpenClaw: in progress ([NOVA-Openclaw/nova-openclaw#233](https://github.com/NOVA-Openclaw/nova-openclaw/issues/233))

## Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in
[BCP 14](https://www.rfc-editor.org/info/bcp14)
[[RFC2119](https://www.rfc-editor.org/rfc/rfc2119)]
[[RFC8174](https://www.rfc-editor.org/rfc/rfc8174)] when, and only when, they
appear in all capitals, as shown here.

This specification uses [JSON Schema](https://json-schema.org/), draft
2020-12, as its normative schema language. Where this document's prose and
the schema in `schema/agent-definition.schema.json` disagree, the schema is
authoritative for structural validity; this document is authoritative for
semantics and processing rules.

## Terminology

**Agent definition.** A JSON document conforming to this specification: a
portable description of an agent, independent of any runtime.

**Harness.** The software that reads an agent definition and configures a
running agent from it: an IDE agent runtime, a chat-platform gateway, an
orchestration framework, or any other consumer of this format.

**Instantiate.** The act of a harness turning an agent definition into a
running (or runnable) agent, applying its own defaults, substitutions, and
enforcement where the definition under-specifies or cannot be fully
satisfied.

**Host identity.** An identity that the harness itself supplies,
independently of any agent definition it instantiates (for example, a
harness's default persona for agents that do not carry one). See
[Identity composition](#identity-composition).

**Role.** A human-readable description of what an agent does (for example,
"Research" or "Quality Assurance"), as distinct from a persona or a proper
name.

**Reference.** A pointer to a skill, tool, or MCP server that exists and is
maintained outside the agent definition itself: a registry identifier, a URL,
or both, optionally pinned to a version and checked against an integrity
hash. An agent definition never embeds the referenced skill, tool, or MCP
server's own content.

## Document Structure

An agent definition is a single JSON object. [`spec_version`](#spec_version)
is always REQUIRED. Beyond that, nearly every top-level field is OPTIONAL: a
definition may be identity and bootstrap text with no tools; a minimal
bootstrap with only tool and skill references and no identity; or any other
combination, subject to two inclusive validity rules:

1. **At least one of `metadata.name` or `metadata.role` MUST be present.**
   Both MAY be present (for example, name `"Scout"`, role `"Research"`).
   This is an inclusive *either-or-both* rule, not an exclusive
   *either-or-neither* rule: in JSON Schema terms it is an `anyOf` of two
   `required` clauses, **not** a `oneOf`. A definition carrying both a name
   and a role is valid; a schema that uses `oneOf` here would wrongly reject
   it (see [`examples/valid/named-agent-with-identity.agent.json`](examples/valid/named-agent-with-identity.agent.json),
   which exists specifically to catch that mistake).
2. **At least one substantive field MUST be present**: `bootstrap`,
   `identity`, `skills`, `tools`, or `model`. A document with only
   `spec_version` and a name or role is not an agent definition; it has
   nothing for a harness to act on. This is also an inclusive `anyOf`: any
   number of these fields MAY be present together.

Once an OPTIONAL top-level block is present, its own core sub-fields become
REQUIRED. For example: a `model` list entry MUST carry both `provider` and
`model`; a `skills` or `tools` entry MUST carry a locator (`id` and/or
`url`); an `identity` block MUST carry `persona`. This conditional
requirement is distinct from, and layered on top of, the two validity rules
above, and is encoded directly in the nested schemas under `$defs` in
`schema/agent-definition.schema.json`.

Top-level fields:

| Field | Type | Requirement |
|---|---|---|
| [`spec_version`](#spec_version) | string (SemVer) | REQUIRED |
| [`metadata`](#metadata) | object | REQUIRED if name or role is supplied (see above) |
| [`model`](#model) | array | OPTIONAL |
| [`bootstrap`](#bootstrap) | string | OPTIONAL |
| [`identity`](#identity) | object | OPTIONAL |
| [`skills`](#skills) | array | OPTIONAL |
| [`tools`](#tools) | array | OPTIONAL |
| [`permissions`](#permissions) | object | OPTIONAL |
| [`contract`](#contract) | object | OPTIONAL |
| [`integrity`](#integrity) | object | OPTIONAL |
| [`limits`](#limits) | object | OPTIONAL |
| [`environment`](#environment) | array | OPTIONAL |
| [`initial_prompt`](#initial_prompt) | string | OPTIONAL |
| [`execution`](#execution) | object | OPTIONAL |
| [`schedules`](#schedules) | array | OPTIONAL |
| [`delegation`](#delegation) | object | OPTIONAL |
| [`extensions`](#extensions) | object | OPTIONAL, free-form (see [Extensibility](#extensibility)) |

## Example (informative)

The canonical examples are the `.agent.json` files under
[`examples/`](examples/); this section shows one in full as a
verbatim excerpt for readability. If this excerpt and the file on disk
ever disagree, the file is authoritative.

Excerpt of [`examples/valid/role-only-focus-agent.agent.json`](examples/valid/role-only-focus-agent.agent.json),
a minimal role-only, identity-less definition:

```json
{
  "spec_version": "0.1.0",
  "metadata": {
    "role": "Research"
  },
  "bootstrap": "You are a research-focus agent within a larger agent swarm. Your job is to find, verify, and summarize information relevant to the task you are given. Cite sources. When a claim cannot be verified from at least one primary source, label it as unverified rather than presenting it as fact. Keep summaries under 500 words unless the requester asks for more detail."
}
```

See [`examples/valid/`](examples/valid/) and
[`examples/invalid/`](examples/invalid/) for the full set, including a
definition with both `name` and `role`, a tools/skills-only definition, a
definition carrying `extensions`, and a full example combining model
preferences, tool references (including an MCP server), permissions, an I/O
contract, and an integrity hash.

## Field Definitions

### `spec_version`

Type: string, SemVer 2.0.0. **REQUIRED.**

The version of this specification that the document conforms to (e.g.
`"0.1.0"`). A harness or validator MUST reject a document that lacks
`spec_version`: without it, there is no way to know which revision of this
spec's rules to apply. See [Versioning](#versioning).

### `metadata`

Type: object. REQUIRED once the document carries a `name` or `role` (which,
per [Document Structure](#document-structure), is effectively always, since
every valid definition needs at least one of the two).

| Sub-field | Type | Requirement | Semantics |
|---|---|---|---|
| `name` | string | at least one of `name`/`role` REQUIRED | The agent's display/invocation name (e.g. `"Scout"`). |
| `role` | string | at least one of `name`/`role` REQUIRED | What the agent does, human-readable (e.g. `"Research"`, `"Quality Assurance"`). |
| `id` | string | OPTIONAL | An opaque, globally-unique identifier for this *document* (reverse-DNS string, UUID, etc.). Distinct from identity: this identifies the definition, not a persona. |
| `version` | string (SemVer) | OPTIONAL | The version of this particular agent definition. Independent of `spec_version`; see [Versioning](#versioning). |
| `description` | string | OPTIONAL | Free-text description for humans browsing a registry or catalog. |
| `authors` | array<string> | OPTIONAL | Author name(s) and/or contact(s). |
| `license` | string | OPTIONAL | An [SPDX](https://spdx.org/licenses/) license identifier for this document. |
| `homepage` | string (URI) | OPTIONAL | A homepage or source URL for this agent definition. |
| `tags` | array<string> | OPTIONAL | Free-form classification tags. |

**`name` vs. `role`.** `name` is *who the agent is called*; `role` is *what
it does*. A role-based, identity-less "focus" agent typically carries only
`role`. A named, persona-bearing agent typically carries `name`, and MAY
also carry `role` for classification. If `identity` is present,
`metadata.name` SHOULD be present: a persona without a name is unusual,
though not forbidden. When `name` is absent, a harness MUST derive a
fallback invocation/log handle from `role` (for example, `role: "Research"`
yields handle `focus-research`) and MUST report what handle it derived; see
[Identity composition](#identity-composition).

### `model`

Type: array of objects, 1 or more entries. OPTIONAL.

An ordered list of model preferences, most preferred first. Each entry:

| Sub-field | Type | Requirement | Semantics |
|---|---|---|---|
| `provider` | string | REQUIRED | An identifier for the model's provider (e.g. `"anthropic"`, `"openai"`, `"google"`). Not a closed enum: new providers require no spec change. |
| `model` | string | REQUIRED | The provider's own model identifier string (e.g. `"claude-sonnet-4-5"`, `"gpt-5"`). |
| `label` | string | OPTIONAL | A human-readable label for this entry (e.g. `"primary"`, `"fallback"`). |
| `settings` | object | OPTIONAL | Provider- and model-specific parameters, see below. |
| `notes` | string | OPTIONAL | Free-text notes about this preference (why it is listed, when to prefer it, etc.). |

**Reasoning and thinking settings are model-specific, with no global
vocabulary.** Providers name and scope "how hard to think" differently:
Anthropic's extended thinking takes a `thinking` object with `type` and a
`budget_tokens` integer; OpenAI's reasoning models take a `reasoning_effort`
string (`"low"` / `"medium"` / `"high"`, model-dependent); Google's Gemini
takes a `thinkingConfig` object with a `thinkingBudget` integer. This
specification does **not** define a universal reasoning/effort enum. A model
entry's `settings` object carries that provider's own parameter names and
values, verbatim, scoped to that one entry. A harness MUST pass `settings`
through to the named provider/model unmodified, or, if it cannot, MUST ignore
settings it does not understand rather than failing instantiation because of
them (unknown `settings` keys are not a validity failure; see
[Extensibility](#extensibility) for the general principle).

**Selection and substitution.** See [Model selection and substitution
reporting](#model-selection-and-substitution-reporting) under Processing
rules.

### `bootstrap`

Type: string. OPTIONAL.

A single text blob of bootstrap context for the agent: role description,
domain knowledge, procedures, rules, anything the agent needs to know to do
its job. This specification defines **no internal structure** for this text.
It may contain the exporting system's own organizational remnants (headers,
bullet lists, section breaks); a harness MUST treat the entire string as
opaque, and MUST NOT attempt to parse or extract structure from it beyond
what is needed to insert it verbatim into the agent's context.

`bootstrap` is WHAT the agent knows and how it works. It is distinct from
[`identity`](#identity), which is WHO the agent is; see [Identity
composition](#identity-composition) for how the two combine.

Because `bootstrap` is natural-language text that will be placed in an
agent's context, it is untrusted input with respect to prompt injection; see
[Security Considerations](#security-considerations).

### `identity`

Type: object. OPTIONAL.

| Sub-field | Type | Requirement | Semantics |
|---|---|---|---|
| `persona` | string | REQUIRED (once `identity` is present) | The core identity text: who the agent is, in the agent's own voice or a description of it. |
| `pronouns` | string | OPTIONAL | The agent's declared pronouns. |
| `voice` | string | OPTIONAL | Free-text description of tone, register, and speaking style. |
| `values` | array<string> | OPTIONAL | A list of short value/principle statements the agent holds. |

`identity` is WHO the agent is: name, persona, voice, values, pronouns. It is
a field separate from `bootstrap`, and the two MUST NOT be merged by an
exporter, because a harness that supplies its own identity (a **host
identity**) needs to be able to use, replace, or ignore the definition's
identity independently of its bootstrap content. That separation is
impossible if identity text has been folded into the bootstrap blob. See
[Identity composition](#identity-composition).

### `skills`

Type: array of objects, 1 or more entries. OPTIONAL.

References to published, maintained skills the agent may use. A skill is
**never embedded**: a definition references a skill by registry identifier
and/or URL, never inlines its content. Each entry:

| Sub-field | Type | Requirement | Semantics |
|---|---|---|---|
| `id` | string | at least one of `id`/`url` REQUIRED | A registry identifier for the skill. |
| `url` | string (URI) | at least one of `id`/`url` REQUIRED | A URL locating the skill (manifest or package). |
| `version` | string | OPTIONAL | An exact version to resolve. |
| `version_range` | string | OPTIONAL | A version range/constraint (e.g. `"^1.2.0"`, `"~3.1"`), in whatever range syntax the registry uses. |
| `integrity` | object | OPTIONAL | A content hash for the referenced skill; see [`integrity`](#integrity) shape. |
| `name` | string | OPTIONAL | A human-readable label for this reference. |

A skill reference with neither `id` nor `url` is invalid: see
[`examples/invalid/skill-missing-locator.agent.json`](examples/invalid/skill-missing-locator.agent.json).

A skill reference's `url` MAY point at a `SKILL.md` file inside an
[Agent Plugins](https://agent-plugins.org/) package (for example,
`.../skills/<name>/SKILL.md` within a published plugin); see [Relationship
to Agent Plugins](#relationship-to-agent-plugins-informative).

### `tools`

Type: array of objects, 1 or more entries. OPTIONAL.

References to published, maintained tools — including MCP servers — the
agent may use. Like skills, tools are **never embedded**: reference only.
Each entry uses the same locator shape as a skill reference (`id` and/or
`url`, optional `version`/`version_range`/`integrity`), plus:

| Sub-field | Type | Requirement | Semantics |
|---|---|---|---|
| `required` | boolean | REQUIRED | Whether the agent needs this tool to function. |
| `kind` | string enum (`"tool"`, `"mcp_server"`) | OPTIONAL | `"mcp_server"` marks that the locator points at an MCP server (by registry id or connection URL) rather than one tool. Defaults to `"tool"` when absent. |
| `name` | string | OPTIONAL | A human-readable label for this reference. |

**Required vs. optional tools.** `required: true` means the agent's
documented behavior depends on this tool. If a harness **cannot satisfy** a
`required: true` tool reference — the registry id does not resolve, the
version range is unsatisfiable, the integrity hash does not match, or the
harness has no mechanism to connect an MCP server at all — the harness **MUST
refuse to instantiate** the agent rather than run it in a silently degraded
state. `required: false` tools MAY be dropped, with the harness proceeding
and reporting the omission; see [Tool and skill resolution and
refusal](#tool-and-skill-resolution-and-refusal).

**MCP servers as tool references.** An MCP server is referenced the same way
as any other tool, with `kind: "mcp_server"`. Its `id` or `url` identifies
the server (for example, an entry in a published MCP server registry, or a
direct connection endpoint); this specification does not define MCP
transport-level details (stdio/SSE/HTTP, launch arguments), which remain the
Model Context Protocol's own concern and the harness's own responsibility to
resolve from the reference.

A `kind: "mcp_server"` tool reference's `url` MAY point at an
[Agent Plugins](https://agent-plugins.org/) package's `mcp.json`, which can
declare more than one server under its `mcpServers` map. When it does, this
reference's `name` field MAY be used to select one entry from that map —
the same `name` field this spec otherwise uses only as a human-readable
label gets a second, specific use here. See [Relationship to Agent
Plugins](#relationship-to-agent-plugins-informative).

A tool reference with neither `id` nor `url`, or missing `required`, is
invalid.

### `permissions`

Type: object, at least one property. OPTIONAL.

Declared operating limits for the agent.

| Sub-field | Type | Requirement | Semantics |
|---|---|---|---|
| `filesystem` | object (`read`, `write`: array<string>) | OPTIONAL | Declared filesystem scopes, as path globs. |
| `network` | object (`enabled`: boolean, `allowed_hosts`: array<string>) | OPTIONAL | Declared network access. |
| `side_effects` | array<string> | OPTIONAL | Declared side-effect classes the agent may perform (e.g. `"sends_notifications"`, `"spends_funds"`). Free-form strings; no global enum is defined. |

At least one of the above MUST be present once `permissions` is included; an
empty `permissions` object declares nothing and is invalid. See [Permission
enforcement and reporting](#permission-enforcement-and-reporting).

### `contract`

Type: object, at least one of `input`/`output`. OPTIONAL.

| Sub-field | Type | Requirement | Semantics |
|---|---|---|---|
| `input` | object (JSON Schema) | at least one of `input`/`output` REQUIRED | A JSON Schema describing the agent's expected input. |
| `output` | object (JSON Schema) | at least one of `input`/`output` REQUIRED | A JSON Schema describing the agent's produced output. |

An I/O contract lets a harness validate what it sends to, and receives from,
the agent. Both `input` and `output` MAY be present; at least one MUST be,
once `contract` is included.

### `integrity`

Type: object. OPTIONAL.

| Sub-field | Type | Requirement | Semantics |
|---|---|---|---|
| `algorithm` | string | REQUIRED | The hash algorithm used (e.g. `"sha256"`, `"sha512"`). |
| `value` | string | REQUIRED | The hash digest, hex- or base64-encoded. |
| `canonicalization` | string, const `"JCS"` | OPTIONAL | The canonicalization scheme the hash was computed over. This spec defines [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) (JCS) as that scheme; see [Integrity](#integrity-1) under Processing rules. |

This top-level `integrity` block covers the agent definition document
itself. Skill and tool references carry their own, separate `integrity`
sub-fields covering the referenced artifact.

### `limits`

Type: object, at least one property. OPTIONAL.

| Sub-field | Type | Requirement | Semantics |
|---|---|---|---|
| `max_turns` | integer, >= 1 | at least one of `max_turns`/`timeout_seconds` REQUIRED | The maximum number of conversational turns the agent may take before the harness stops it. |
| `timeout_seconds` | integer, >= 1 | at least one of `max_turns`/`timeout_seconds` REQUIRED | The maximum wall-clock time, in seconds, the agent may run before the harness stops it. |

A harness that cannot honor a declared limit MUST report that it could not;
see [Limits, execution, and schedule reporting](#limits-execution-and-schedule-reporting).

### `environment`

Type: array of objects, 1 or more entries. OPTIONAL.

A list of environment variables the agent needs the harness to resolve (for
example, API keys or endpoint URLs the agent's tools depend on). Each entry:

| Sub-field | Type | Requirement | Semantics |
|---|---|---|---|
| `name` | string | REQUIRED | The environment variable's name. |
| `description` | string | OPTIONAL | A human-readable description of what this variable is for. |
| `required` | boolean | OPTIONAL, defaults to `true` | Whether the harness MUST be able to resolve this variable for the agent to be instantiated. |
| `secret` | boolean | OPTIONAL, defaults to `false` | Whether this variable's value should be treated as a secret (e.g. masked in logs). |

**An `environment` entry declares a variable's NAME and requirements only.
It MUST NOT carry the variable's actual value** — the normative schema
structurally forbids a `value` property on an environment entry. A
definition is a portable description of an agent, not a credential bundle;
resolving named variables to actual values is the harness's job, from
whatever secret store or environment it has available. See [Environment
resolution](#environment-resolution).

### `initial_prompt`

Type: string. OPTIONAL.

A single text blob auto-submitted to the agent as its first user turn, as
distinct from `bootstrap`, which configures the agent but is not itself a
turn in the conversation. `bootstrap` stays a single, structureless blob
regardless of whether `initial_prompt` is present.

Because `initial_prompt` is natural-language text submitted into the
agent's conversation, it is untrusted input with respect to prompt
injection, exactly like `bootstrap` and `identity`; see [Security
Considerations](#security-considerations).

### `execution`

Type: object, at least one property. OPTIONAL.

| Sub-field | Type | Requirement | Semantics |
|---|---|---|---|
| `background` | boolean | at least one of `background`/`isolation` REQUIRED | Whether the agent is intended to run as a background task rather than an interactive, foreground session. |
| `isolation` | string | at least one of `background`/`isolation` REQUIRED | The isolation level the agent expects to run under. Recommended values: `"none"`, `"process"`, `"container"`, `"vm"`. |

`isolation` is an **open vocabulary, not a closed enum**: this specification
recommends the four values above for cross-harness consistency, but a
harness MAY encounter a value it does not recognize (a harness-specific
isolation mechanism, for example) and MUST report it rather than rejecting
the definition because of it. See [Limits, execution, and schedule
reporting](#limits-execution-and-schedule-reporting).

### `schedules`

Type: array of objects, 1 or more entries. OPTIONAL.

A list of recurring schedules on which the agent should run a prompt
autonomously, with no human initiating each run. Each entry:

| Sub-field | Type | Requirement | Semantics |
|---|---|---|---|
| `id` | string | REQUIRED | A stable identifier for this schedule entry, unique within the definition. |
| `cron` | string | REQUIRED | A cron expression describing when this schedule fires. |
| `prompt` | string | REQUIRED | The prompt to submit to the agent when this schedule fires. |
| `enabled` | boolean | OPTIONAL | Whether this schedule is enabled. |
| `timezone` | string | OPTIONAL | The IANA time zone name the cron expression is evaluated in (e.g. `"UTC"`, `"America/New_York"`). |

Because a schedule causes the agent to run autonomously and repeatedly, a
harness SHOULD require explicit operator approval before enabling a
schedule imported from a definition, rather than honoring `enabled: true`
unconditionally; see [Security Considerations](#security-considerations).

### `delegation`

Type: object, at least one property. OPTIONAL.

| Sub-field | Type | Requirement | Semantics |
|---|---|---|---|
| `when_to_use` | string | at least one of `when_to_use`/`may_delegate_to` REQUIRED | Guidance for an orchestrator deciding whether to delegate to this agent. Distinct from `metadata.description`, which is a general description rather than delegation-routing guidance. |
| `may_delegate_to` | array\<string\> | at least one of `when_to_use`/`may_delegate_to` REQUIRED | Names or roles of agents this agent may itself delegate to. |

### `extensions`

Type: object. OPTIONAL. MAY appear at the top level, and MAY also appear
inside `metadata`, `identity`, each `model` list entry, each `skills` or
`tools` entry, `permissions`, and `contract`.

A free-form object for vendor- or implementation-specific data that this
specification does not define and does not need to be updated to
accommodate. See [Extensibility](#extensibility) for the full rules.

## Processing Rules for Harnesses

### Validation

A conforming harness or validator MUST validate an agent definition against
the normative schema (`schema/agent-definition.schema.json`) before
instantiating it. A document that fails schema validation — missing
`spec_version`, missing both `metadata.name` and `metadata.role`, missing
every substantive field, or an incomplete nested block — MUST NOT be
instantiated.

### Model selection and substitution reporting

Given a `model` list, a harness MUST attempt entries in the order given and
instantiate the agent against the **first entry it can fully satisfy**
(provider reachable, model id resolvable, `settings` applicable or at least
not fatal). If the harness supports the named provider and model exactly, it
MUST use that model and those settings. If it does not — the exact model id
is unavailable, but an equivalent or successor model is — the harness MAY
substitute its nearest equivalent, but **MUST report the substitution**
(which entry was requested, which model was actually used, and why) to
whatever surface it uses for instantiation diagnostics. If **no** entry in
the list can be satisfied at all, the harness MUST refuse to instantiate the
agent, or instantiate it with a harness-default model while clearly reporting
that none of the declared preferences were honored; a harness's conformance
notes (see [Conformance](#conformance)) MUST state which behavior it
implements.

### Tool and skill resolution and refusal

For each `tools` entry, the harness MUST attempt to resolve the locator
(`id` and/or `url`) to a usable tool or MCP server connection, honoring
`version`/`version_range` and verifying `integrity` when present. If
resolution succeeds, the tool becomes available to the agent. If resolution
fails:

- `required: true` — the harness **MUST refuse to instantiate** the agent.
  It MUST NOT run the agent without the tool and MUST NOT silently treat the
  tool as absent.
- `required: false` — the harness MAY instantiate the agent without the
  tool, but MUST report the omission (which reference, why it could not be
  resolved) wherever it reports instantiation diagnostics.

`skills` entries are resolved the same way (locator, version, integrity),
but this specification does not mandate refusal on failed skill resolution;
a harness SHOULD report an unresolved skill reference and MAY proceed
without it, since a missing skill degrades capability rather than making the
agent's documented behavior impossible to satisfy the way a missing required
tool does.

### Identity composition

When both `identity` and `bootstrap` are present, a harness MUST compose
them identity-first: present `identity` content to the agent before
`bootstrap` content. This ordering is fixed by this specification because it
mirrors how most harnesses structure a system prompt (who you are, then what
you know).

A harness that has its own host identity (an identity it supplies
independently of any agent definition — see [Terminology](#terminology))
MUST follow a **declared identity policy** when a definition also carries an
`identity` block. This specification defines three policy values a harness
MAY declare for itself, matching the "uses, replaces, or ignores" language
in this spec's originating design discussion:

- `use` — the harness uses the definition's `identity`: it is composed
  identity-first as described above, and the harness's own host identity is
  not applied for this instantiation.
- `replace` — the harness's own host identity replaces the definition's
  `identity`: the host identity is presented instead, and the definition's
  `identity` content is not presented to the agent at all.
- `ignore` — the harness ignores the definition's `identity` and does
  **not** substitute its own host identity in its place either: the agent is
  instantiated from `bootstrap` (and any other non-identity fields) alone,
  with no identity content from either source.

A harness MUST declare which policy it implements (in its own documentation
or conformance notes) and **MUST report, per instantiation, which of the
declared behaviors it actually applied** when a definition's `identity` was
present and the harness has a host identity of its own. This specification
does not mandate any one policy; it mandates that one is declared and its
application is reported.

When `metadata.name` is absent, the harness MUST derive a fallback handle
from `metadata.role` (e.g. `role: "Research"` to `focus-research`, exact
derivation scheme left to the harness) and MUST report the derived handle
wherever it reports instantiation diagnostics.

### Limits, execution, and schedule reporting

A harness that cannot honor a declared `limits` value (`max_turns`,
`timeout_seconds`), a declared `execution.isolation` level, a declared
`execution.background` request, or a declared `schedules` entry MUST
report that it could not, wherever it reports instantiation diagnostics.
This mirrors [Permission enforcement and reporting](#permission-enforcement-and-reporting):
enforce what the runtime is capable of, and be honest about what it is not.
This specification does not require a harness to be capable of running
agents in the background, under a given isolation level, or on a schedule
at all; it requires that gap to be visible rather than silent.

### Environment resolution

For each `environment` entry, the harness MUST attempt to resolve the named
variable from whatever environment or secret store it has available. If
resolution fails:

- `required` absent or `true` (the default) — the harness **MUST refuse to
  instantiate** the agent, the same refusal this specification requires for
  an unsatisfiable `required: true` tool reference (see [Tool and skill
  resolution and refusal](#tool-and-skill-resolution-and-refusal)).
- `required: false` — the harness MAY instantiate the agent without the
  variable resolved, but MUST report the omission.

Separately, and regardless of resolution outcome: a harness MUST NOT accept,
and a definition MUST NOT carry, an actual value for an `environment` entry
(enforced structurally in the normative schema). An agent definition
declares what it needs; it is never the place actual secrets or
configuration values live.

### Permission enforcement and reporting

A harness MUST enforce every declared `permissions` constraint that its
runtime is capable of enforcing (for example, restricting filesystem access
to declared paths, or network access to declared hosts, when the harness's
sandboxing supports it). For any declared constraint the harness **cannot**
enforce in its runtime environment, the harness MUST NOT silently ignore it:
it MUST report, at instantiation time, which declared permissions it could
not enforce. This specification does not require a harness to be capable of
enforcing every permission shape; it requires honesty about which ones it
is not enforcing.

## Extensibility

This specification provides exactly **one** spec-defined extension point: an
optional `extensions` object.

`extensions` MAY appear at the top level of a definition, and the same,
independent `extensions` object MAY also appear inside `metadata`,
`identity`, each `model` list entry, each `skills` or `tools` entry,
`permissions`, and `contract` — so vendor- or implementation-specific data
sits next to the block it extends, rather than only at the document root.
Each `extensions` object is free-form: its value MAY be any JSON.

**Namespacing.** Keys within an `extensions` object SHOULD be namespaced to
avoid collisions between unrelated vendors or tools — for example a
reverse-DNS string or a short vendor prefix, such as
`"org.example.harness": { ... }`. This specification does not enforce a
namespace syntax; it is a SHOULD, not a MUST, matching the convention used by
[MCP's `_meta`](https://modelcontextprotocol.io/specification/2026-07-28/basic)
(see Prior art below) rather than Kubernetes' stricter `prefix/name` syntax.

**Harness rules.** A conforming harness:

- **MUST NOT refuse to instantiate** a definition because of unrecognized
  `extensions` content.
- **MAY drop** any `extensions` namespace it does not understand when
  importing a definition. It is not required to retain data it cannot
  interpret.
- **SHOULD preserve** a namespace it understands when it re-exports or
  transforms a definition. Preserving a namespace it does **not** understand
  on re-export is **OPTIONAL** (MAY) — a harness is free to drop unknown
  extension data rather than carry it through unexamined, but losing data it
  does understand without a reason defeats the point of declaring it.
- **MUST NOT** let `extensions` override the meaning of any spec-defined
  field. `extensions` is additive, side-channel data; it is never an
  alternate way to satisfy a spec-defined field's requirements.

**Unknown top-level fields outside `extensions`.** This specification may
define new, additional top-level or nested fields in future minor versions
(see [Versioning](#versioning)). A harness built against an older minor
version MUST continue to ignore fields it does not recognize rather than
fail validation, which is why `additionalProperties` is not set to `false`
anywhere in the normative schema. However, this tolerance exists for
**forward compatibility with later versions of this spec**, not as a general
invitation to invent fields: producers conforming to this version of the
spec MUST NOT invent new top-level or nested fields of their own and SHOULD
place vendor- or implementation-specific data in `extensions` instead, where
a harness's conformance obligations (never refuse to instantiate because of
them, and preserve a namespace it understands when re-exporting) are
explicit and spec-guaranteed.

**Prior art.** The single spec-defined, namespaced-key extension object
follows the shape of (each verified against its source before citing here):

- **[Model Context Protocol `_meta`](https://modelcontextprotocol.io/specification/2026-07-28/basic)**
  — an object of string keys to arbitrary JSON values carried on requests,
  results, and notifications, with reverse-DNS-style namespaced key prefixes
  and reserved prefixes for the protocol itself. This specification's
  `extensions` is closest in spirit to `_meta`: one object, namespaced keys,
  freeform values.
- **[Kubernetes `metadata.annotations`](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/)**
  — an unstructured key/value map attached to an object for tools and
  libraries to read and write, explicitly not used for identification or
  selection (that is what labels are for). Kubernetes annotation values are
  strings; this specification's `extensions` values MAY be any JSON, closer
  to `_meta` than to annotations in that respect.
- **[CloudEvents extension context attributes](https://github.com/cloudevents/spec/blob/main/cloudevents/extensions/README.md)**
  — additional named attributes alongside CloudEvents' core context
  attributes, with no meaning defined by the core spec; this specification's
  rule that harnesses MUST ignore namespaces they do not understand mirrors
  CloudEvents' treatment of extension attributes as optional, independently
  defined metadata.
- **[Agent Plugins `extensions`](https://agent-plugins.org/schemas/1.0.0/)**
  — a packaging spec for skills and MCP servers (see [Relationship to Agent
  Plugins](#relationship-to-agent-plugins-informative)) whose own
  `plugin.json` manifest carries an `extensions` property following the
  same reverse-domain namespacing convention this specification recommends.
  Cited here as prior art for the convention, not as a dependency of this
  specification.

See [`examples/valid/with-extensions.agent.json`](examples/valid/with-extensions.agent.json)
for a definition carrying `extensions` at the top level and inside a
`tools` entry.

## Versioning

**Of the specification.** This specification follows
[SemVer 2.0.0](https://semver.org/). `spec_version` in a document names the
spec version that document was authored against. A MAJOR version increment
MAY make breaking changes to required fields or validity rules. A MINOR
version increment MUST only add optional fields or relax constraints; a
document valid under spec version `X.Y.0` remains valid under `X.(Y+1).0`.
A PATCH version increment MUST only clarify wording or fix errors in the
prose or schema with no effect on which documents validate.

**Of a definition.** `metadata.version`, when present, is the version of
that particular agent definition document — independent of, and unrelated
to, `spec_version`. An agent definition author SHOULD follow SemVer for
`metadata.version` and bump it whenever the definition's `bootstrap`,
`identity`, `model`, `skills`, `tools`, `permissions`, or `contract`
content changes in a way that could change the agent's behavior.

## Integrity

An agent definition's top-level `integrity` block (and each skill/tool
reference's own `integrity` sub-field) names a hash `algorithm` and a
`value`. This specification defines the canonicalization scheme for
computing that hash over the document itself as
[**RFC 8785, the JSON Canonicalization Scheme (JCS)**](https://www.rfc-editor.org/rfc/rfc8785):
to compute or verify an `integrity.value` for an agent definition, serialize
the JSON document (excluding the `integrity` block being computed, to avoid
self-reference) per RFC 8785 and hash the resulting canonical byte sequence
with the named `algorithm`. Using JCS, rather than an implementation's
default JSON serializer, ensures two different tools produce the same hash
for the same logical document regardless of key order or whitespace.

A harness or validator that checks `integrity` MUST perform this same
canonicalize-then-hash procedure before comparing against `value`, and MUST
treat a mismatch as an integrity failure (not a warning) when the reference
being checked is marked `required: true`.

## Media Type and File Extension

This specification proposes the media type `application/agent-definition+json`
and the file extension `.agent.json` for documents conforming to it.

**These are provisional and are NOT registered with IANA.** Implementations
MAY use them informally (for content negotiation, file associations, editor
tooling) but MUST NOT rely on IANA recognizing them until and unless a formal
registration is filed and accepted. Until then, a plain `application/json`
media type and a `.json` extension remain valid and interoperable choices for
transmitting or storing an agent definition.

## Security Considerations

**Bootstrap text is untrusted, by design.** `bootstrap` (and `identity.persona`
and related free-text identity fields) are natural-language content placed
directly into an agent's context. Any natural-language content placed into a
model's context is a vector for prompt injection, whether the text originates
from the definition's original author, from a compromised or malicious
registry/URL the definition was fetched from, or from tampering in transit.
This specification does **not** attempt to sanitize or neutralize this risk
within the format itself — it is structurally impossible to fully "sanitize"
natural language a model will read — and instead requires implementers to
treat this risk as inherent: a harness SHOULD apply the same scrutiny to a
fetched agent definition's text fields that it would to any other untrusted
input reaching a model's context, and MUST NOT grant an agent definition's
own bootstrap or identity text the ability to expand that agent's own
declared `permissions` or `tools`.

**Reference pinning and integrity.** Because `skills` and `tools` are
resolved by reference at instantiation time, the resolved content can change
between the time a definition is authored and the time it is instantiated —
including to a malicious version, if the registry or URL is compromised.
Authors SHOULD pin an exact `version` and supply `integrity` for any
reference where supply-chain tampering is a concern, particularly for
`required: true` tools. A harness SHOULD verify `integrity` when present and
MUST refuse a `required: true` reference that fails integrity verification.

**Permission escalation.** `permissions` are declarations, not a sandbox by
themselves; see [Permission enforcement and reporting](#permission-enforcement-and-reporting).
A harness that cannot enforce a declared constraint and does not report that
gap creates a false sense of containment. Implementers MUST treat
unenforceable-and-unreported permission gaps as a security defect in their
harness, not an acceptable shortcut.

**Initial prompt is untrusted, by design.** `initial_prompt`, like
`bootstrap` and `identity`, is natural-language content submitted into the
agent's conversation, and carries the same prompt-injection risk described
above for `bootstrap`. A harness SHOULD apply the same scrutiny to
`initial_prompt` that it applies to `bootstrap`.

**Schedules run prompts autonomously.** A `schedules` entry causes the
harness to submit `prompt` to the agent repeatedly, on a cron schedule,
with no human initiating any individual run. This is a materially larger
blast radius than a single interactive session: a malicious or compromised
`schedules` entry runs unattended, indefinitely, until disabled. A harness
**SHOULD require explicit operator approval before enabling a schedule
imported from a definition** — `enabled: true` in an imported definition is
a request, not an instruction the harness is obligated to honor
automatically.

**Identity spoofing.** Because `identity` is free text, a definition can
claim any name, persona, or voice, including one that impersonates a
specific person, organization, or another known agent. This specification
does not define an authentication mechanism for identity claims. Harnesses
and registries that distribute agent definitions SHOULD apply their own
provenance and authenticity controls (e.g. signed commits, registry-level
verified-author badges) independently of this format; `metadata.authors` and
`integrity` support but do not by themselves guarantee provenance.

## Conformance

**A conforming agent definition** is a JSON document that validates against
`schema/agent-definition.schema.json` under JSON Schema draft 2020-12
semantics: it carries `spec_version`; at least one of `metadata.name` or
`metadata.role`; at least one of `bootstrap`, `identity`, `skills`,
`tools`, or `model`; and, for every optional block it includes, that
block's own core sub-fields.

**A conforming harness**:

1. MUST validate a definition against the normative schema before
   instantiating it, and MUST NOT instantiate a definition that fails
   validation (see [Validation](#validation)).
2. MUST implement [model selection and substitution
   reporting](#model-selection-and-substitution-reporting) as specified.
3. MUST implement [tool resolution and refusal](#tool-and-skill-resolution-and-refusal)
   as specified, in particular refusing to instantiate when a
   `required: true` tool reference cannot be satisfied.
4. MUST implement [identity composition](#identity-composition) as
   specified, including declaring and reporting its identity policy.
5. MUST enforce every declared permission it is capable of enforcing and
   MUST report every declared permission it is not (see [Permission
   enforcement and reporting](#permission-enforcement-and-reporting)).
6. MUST ignore unrecognized fields rather than rejecting a definition
   because of them (see [Extensibility](#extensibility)).
7. SHOULD document, in its own conformance notes, which of this
   specification's MAY-level choices it makes (e.g. its identity policy
   value, its behavior when no `model` entry can be satisfied).

A harness MAY support only a subset of optional blocks (for example, a
harness with no permission-sandboxing capability at all), provided it
reports that gap per point 5 above rather than silently ignoring it.

## Appendix A: Mapping to/from Claude Code Subagent Frontmatter (informative)

Claude Code subagents are Markdown files with YAML frontmatter under
`.claude/agents/` (project/user/managed scopes) or shipped by a plugin; the
frontmatter configures the subagent, and the Markdown body becomes its system
prompt. Source, verified by direct fetch on 2026-10-17 and re-verified
2026-10-18: <https://code.claude.com/docs/en/sub-agents>.

Verified frontmatter fields (per that page): `name`, `description`,
`tools`, `disallowedTools`, `model`, `permissionMode`, `mcpServers`,
`hooks`, `maxTurns`, `autoCompactWindow`, `skills`, `initialPrompt`,
`memory`, `effort`, `background`, `omitClaudeMd`, `isolation`, `color`,
`experimental`. Only `name` and `description` are required; a file missing
either is skipped rather than erroring.

**VERIFIED: unrecognized-field handling.** The documentation states, quoted
verbatim: "Multi-word field names use camelCase, such as `maxTurns` and
`disallowedTools`, and must match the table exactly: **Claude Code ignores
a field it doesn't recognize without reporting an error.**" It further
states: "To find a misspelled field in a subagent that loaded, run
`claude --debug` in your shell and search the debug log at
`~/.claude/debug/<session-id>.txt` for `does not recognize or apply`. The
debug log names up to five top-level fields in the subagent's file that
Claude Code doesn't recognize, with the likely intended name when a
supported field is close. **Requires Claude Code v2.1.296 or later.**" This
confirms, for Claude Code specifically, the same "ignore unknown fields,
don't reject" posture this spec requires of every conforming harness (see
[Extensibility](#extensibility)) — with the caveat that below v2.1.296,
Claude Code ignores the field silently with no debug-log trace at all.

| Agent Definition | Claude Code frontmatter | Notes |
|---|---|---|
| `metadata.name` | `name` | Both are the invocation/display name. |
| `metadata.description` and/or `delegation.when_to_use` | `description` | Claude Code's `description` drives automatic delegation (Claude decides when to invoke the subagent from this text), which is what this spec's `delegation.when_to_use` is for; it is also the human-readable description, which is what `metadata.description` is for. Claude Code conflates the two into one field. Exporting *to* Claude Code, this spec's `delegation.when_to_use` is the better source if both are present, since that is the field Claude Code's own routing behavior most resembles. **Lossy on export to Claude Code** if a definition has neither — Claude Code requires `description`. |
| `bootstrap` | Markdown body (system prompt) | Direct mapping: the body *is* the bootstrap text, with no internal structure imposed, matching this spec's "opaque blob" rule. |
| `initial_prompt` | `initialPrompt` | Direct mapping: both are auto-submitted as the first user turn when the agent runs as the main session agent, and both are distinct from the system-prompt-equivalent field (`bootstrap`/Markdown body). |
| `identity` | *(no dedicated field)* | Claude Code has no separate identity/persona field; a Claude Code subagent's "who it is" lives in the same Markdown body as everything else. Exporting *to* Claude Code: an identity block, if present, SHOULD be composed into the body ahead of the bootstrap content per [Identity composition](#identity-composition), since Claude Code offers nowhere else to put it. Importing *from* Claude Code: there is no identity to extract; the whole body becomes `bootstrap` with no `identity` block. |
| `model` (first entry) | `model` | Claude Code's `model` accepts a family alias (`sonnet`/`opus`/`haiku`), a full model ID, or `inherit`. This spec's ordered list has no equivalent of `inherit` (inherit the host's own model choice); exporting an `inherit`-configured subagent has no faithful representation and SHOULD be dropped or flagged rather than guessed. |
| `model[].settings` | `effort` | Claude Code's `effort` (a reasoning-effort-like dial) belongs in the relevant model entry's `settings` object on export, the same place this spec puts any other provider- or model-specific reasoning parameter (see [`model`](#model)), rather than in `extensions`. |
| `limits.max_turns` | `maxTurns` | Direct mapping: both cap the number of turns the agent may take. |
| `execution.background` | `background` | Direct mapping. |
| `execution.isolation` | `isolation` | Partial mapping. Claude Code's documented value is `worktree` (a git-worktree-based isolation mechanism), which is not one of this spec's recommended `execution.isolation` vocabulary (`none`/`process`/`container`/`vm`) and has no cross-harness equivalent. Exporting *to* this spec, carry the Claude-Code-specific mechanism as `extensions["com.anthropic.claude-code"].isolation = "worktree"` rather than overloading `execution.isolation` with a value no other harness can act on; a generic `execution.isolation` value MAY still be set alongside it (e.g. `"process"`) as a best-effort cross-harness hint. || `tools` (by reference) | `tools` (allowlist) | **Not a direct mapping.** Claude Code's `tools` names *built-in or MCP tool identifiers already available to the session*; it is a filter, not a by-reference installable tool list. This spec's `tools` are externally published, versioned, integrity-checkable references. Converting in either direction requires a resolution step this spec does not define: from Claude Code, each allowed tool name would need an external registry entry to become a reference; from this spec, each tool reference would need to resolve to a Claude Code tool name before it can appear in `tools`. || `tools[].kind: "mcp_server"` | `mcpServers` | Claude Code's `mcpServers` can reference an already-configured server by name or supply an inline connection config; this spec's MCP tool references always use a locator (`id`/`url`), never an inline config, so an inline `mcpServers` entry has no direct equivalent without first publishing it somewhere resolvable. |
| `permissions` | *(no direct equivalent)* | Claude Code's `permissionMode` (see below) selects an approval-flow *mode*, not filesystem/network/side-effect scopes; it goes to `extensions`, not `permissions`. |
| `contract` | *(no equivalent)* | Claude Code has no declared I/O JSON Schema contract for a subagent. |
| `integrity` | *(no equivalent)* | Not applicable; Claude Code subagent files are local, version-controlled Markdown, not fetched-by-reference artifacts. |
| *(no equivalent)* | `skills` (preload list) | Claude Code's `skills` frontmatter field *preloads* named skill content into context at startup; this is closer to inlining than to this spec's by-reference `skills`, and has no faithful round-trip without resolving each preloaded skill name to a published, referenceable skill. |
| **extensions only** (`extensions["com.anthropic.claude-code"]`) | `disallowedTools`, `permissionMode`, `hooks`, `memory`, `color`, `autoCompactWindow`, `omitClaudeMd`, cache TTL (`experimental.cacheTtl`) | Harness-specific runtime controls with no corresponding concept in this spec: hooks execute commands with a harness-specific event model; `disallowedTools` is a harness-specific tool-name denylist (this spec's `permissions` covers refusal at the capability level, not by tool name); memory scope semantics diverge across harnesses; the rest (`permissionMode`, `color`, `autoCompactWindow`, `omitClaudeMd`, cache TTL) are Claude-Code-specific UI/runtime tuning. An exporter carries these inside `extensions` rather than inventing new top-level fields. |

## Appendix B: Mapping to/from Hermes Agent Profile Distributions (informative)

A Hermes profile distribution is a git repository that packages a complete
Hermes agent for sharing and installation (`hermes profile install
<repo>`). Source, verified by direct fetch on 2026-10-17:
<https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions>.
**Re-verified 2026-10-18 against the hermes-agent source at commit
`0ab43d4f67e41be75f4f6c0fa14a86dbcfd3e5b3`**, specifically
`hermes_cli/profile_distribution.py`, which this draft fetched directly and
confirms: the manifest filename is `distribution.yaml`
(`MANIFEST_FILENAME = "distribution.yaml"`), and the default
distribution-owned paths are `SOUL.md`, `config.yaml`, `mcp.json`,
`skills`, and `cron` (`DEFAULT_DIST_OWNED`), confirming the repository
layout below at the source-code level, not just from documentation prose.
The specific field names inside `config.yaml` and `mcp.json` below were
verified as part of this spec's own gap-analysis (NOVA-Openclaw/specs#1)
rather than independently re-derived from source in this draft; see
`cli-config.yaml.example` in the same repository for the CLI's own
(distinct, global) configuration format.

Verified repository layout and manifest fields: `distribution.yaml`
(manifest: `name` required; also `version`, `description`,
`hermes_requires`, `author`, `license`, `env_requires` — each with
`name`, `description`, `required`, `default` —, and
`distribution_owned`), `SOUL.md` (identity/system-prompt text, no required
internal schema, strongly recommended but not strictly required),
`config.yaml` (`model.default`, `model.provider`, `agent.max_turns`,
`agent.reasoning_effort`, `mcp_servers`), `mcp.json` (a `$schema`
pointing at the [agent-plugins.org](https://agent-plugins.org) MCP schema,
plus `mcpServers`), `skills/` (bundled skill directories), and
`cron/jobs.json` (scheduled jobs; distribution content). Versioning is via
git tags/branches/commit SHAs, not a manifest version-range field.

| Agent Definition | Hermes distribution | Notes |
|---|---|---|
| `metadata.name` | `distribution.yaml: name` | Direct mapping; both are the agent/distribution's canonical name. |
| `metadata.version` | `distribution.yaml: version` | Direct mapping, though Hermes additionally expects a matching git tag (`vX.Y.Z`) for that version to be meaningfully installable/updatable — a concept this spec does not require. |
| `metadata.description` | `distribution.yaml: description` | Direct mapping. |
| `metadata.authors` | `distribution.yaml: author` | Hermes's field is singular (one author string); this spec's `authors` is a list. Exporting multiple authors to Hermes is lossy without a policy choice (e.g. join into one string). |
| `metadata.license` | `distribution.yaml: license` | Direct mapping. |
| `identity.persona` (+ `voice`, `values`, `pronouns`) | `SOUL.md` | Close conceptual mapping: Hermes explicitly separates `SOUL.md` (identity) from the rest of the distribution, the same identity/bootstrap separation this spec requires. `SOUL.md` has no internal schema (plain Markdown, scanned for prompt injection, used as-is), so `identity.persona` maps to `SOUL.md`'s content directly; this spec's additional structured sub-fields (`pronouns`, `voice`, `values`) have no dedicated Hermes equivalent and would need to be folded into `SOUL.md` prose on export. |
| `bootstrap` | *(no single dedicated file)* | Hermes has no exact equivalent of one opaque bootstrap blob; domain/procedural context in a Hermes distribution is typically split across `config.yaml` tool defaults, bundled `skills/`, and whatever the author put in `SOUL.md` beyond pure identity. Importing *from* Hermes, a faithful `bootstrap` would need to be assembled from these non-identity parts; exporting *to* Hermes, `bootstrap` content has no single canonical destination file and would most naturally become part of `SOUL.md` (after `identity.persona`) or a project-level instructions file, which is a lossy, harness-specific choice this spec does not prescribe. |
| `model` (first entry: `provider`, `model`) | `config.yaml: model.provider`, `model.default` | Direct mapping for a single preferred model. Hermes's `config.yaml` does not document an *ordered list* of fallback models the way this spec's `model` array does; only the first (most-preferred) entry has an obvious Hermes destination, and additional entries have no verified Hermes equivalent. |
| `model[].settings.reasoning_effort` | `config.yaml: agent.reasoning_effort` | Direct mapping: both are a reasoning-effort-style dial on the active model. |
| `limits.max_turns` | `config.yaml: agent.max_turns` | Direct mapping. |
| `schedules` | `cron/jobs.json` | Conceptual correspondence: both describe recurring, autonomously-triggered prompts. Hermes's per-job field names within `cron/jobs.json` were not independently re-verified at the source level for this draft; treat the `id`/`cron`/`prompt`/`enabled`/`timezone` shape as this spec's own design, not a confirmed field-for-field match. |
| `environment` | `distribution.yaml: env_requires` | Close structural mapping: Hermes's `env_requires` entries (`name`, `description`, `required`, `default`) line up with this spec's `environment` entries (`name`, `description`, `required`, `secret`) for three of four fields. **One-way mapping caveat:** Hermes's `env_requires[].default` MAY carry a literal default *value* for the variable; this spec's `environment` entries MUST NOT carry a value at all (see [`environment`](#environment)). Importing `env_requires` into this spec's `environment`, any `default` value MUST be dropped, not carried over, to stay conformant. |
| `skills` (by reference) | `skills/<name>/SKILL.md` | **Not a direct mapping.** Hermes bundles skill directories *inside* the distribution (shipped, versioned together with the agent via the same git repo/tags); this spec's `skills` are external references to independently published, independently versioned skills. Importing from Hermes would require publishing each bundled skill externally to get a referenceable `id`/`url`; exporting to Hermes would mean materializing each referenced skill's content into a `skills/` subdirectory, which is exactly the embedding this spec's `skills` are designed to avoid. |
| `tools` (`kind: "mcp_server"`) | `mcp.json: mcpServers` | Direct conceptual mapping: both describe MCP server connections for the agent. Hermes's `mcp.json` declares a `$schema` pointing at the [agent-plugins.org](https://agent-plugins.org) MCP schema — a vendor-neutral format Hermes defers to rather than defining its own, which this spec's `tools` locator shape is compatible with in spirit (reference by id/url, not inline embedding) without being schema-identical to it. **Resolved:** Agent Plugins and this spec are complementary, not competing — see [Relationship to Agent Plugins](#relationship-to-agent-plugins-informative). |
| `permissions` | *(no verified equivalent)* | Hermes's security/sandboxing model, if any, was outside what was verified for this appendix. |
| `contract` | *(no equivalent)* | Not found in the verified sources. |
| `integrity` | *(no equivalent as a manifest field)* | Hermes relies on git's own content-addressing (commits, tags) rather than a declared hash field; not a direct field-for-field mapping. |
| **extensions only** (`extensions["com.nousresearch.hermes"]`) | `hermes_requires`, `distribution_owned`, compression/display/terminal settings | `hermes_requires` is a minimum-Hermes-version constraint with no equivalent in a harness-agnostic spec; `distribution_owned` is Hermes's own update-merge mechanic (which of a distribution's files survive `hermes profile update` unmodified); compression/display/terminal settings are Hermes CLI UI/runtime tuning (see `cli-config.yaml.example`, a separate, global CLI config file, not the per-distribution `config.yaml` mapped above). |

## Relationship to Agent Plugins (informative)

[Agent Plugins](https://agent-plugins.org/) (spec `1.0.0`, schemas at
<https://agent-plugins.org/schemas/1.0.0/>) is a packaging and distribution
format for skills and MCP servers; Hermes implements it (see [Appendix
B](#appendix-b-mapping-tofrom-hermes-agent-profile-distributions-informative)).
Agent Plugins `1.0.0`'s `plugin.json` manifest
(schema: <https://agent-plugins.org/schemas/1.0.0/plugin.schema.json>)
defines only these properties: `$schema`, `name`, `version`,
`description`, `author`, `homepage`, `repository`, `license`, `keywords`,
and `extensions`. There is no `model`, `prompt`, or `permissions` field —
Agent Plugins defines no agent. A package instead bundles the things an
agent might *use*: skills (`skills/<name>/SKILL.md`) and MCP servers
(`mcp.json`).

**This makes Agent Plugins and this specification complementary layers, not
competing ones.** Agent Plugins packages and distributes components; an
Agent Definition declares an agent — which model(s) it prefers, what it
knows (`bootstrap`/`identity`/`initial_prompt`), and what it is and isn't
allowed to do (`permissions`, `limits`, `environment`). An agent
definition's `skills` and `tools` references are exactly where the two
specs meet: see the reference-form notes under [`skills`](#skills) and
[`tools`](#tools) above, and
[`examples/valid/agent-plugins-refs.agent.json`](examples/valid/agent-plugins-refs.agent.json)
for a definition that references a skill and an MCP server by pointing into
a published Agent Plugins package.

**Packaging note.** An Agent Plugins package MAY ship an Agent Definition
file alongside its skills and MCP servers — for example, `<name>.agent.json`
at the package root — so that a single published bundle supplies the agent
itself plus the skills and MCP servers it depends on. This specification
does not define a new extension namespace for this: it is a plain
packaging and file-naming convention between two already-composable
formats, not a schema feature either spec needs to encode.

Both specs also converge on the same extensibility convention: Agent
Plugins' own `plugin.json` carries an `extensions` property following the
same reverse-domain namespacing this specification recommends for its own
`extensions` object (see [Extensibility](#extensibility)).

## References

- [RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels](https://www.rfc-editor.org/rfc/rfc2119)
- [RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words](https://www.rfc-editor.org/rfc/rfc8174)
- [RFC 8785 — JSON Canonicalization Scheme (JCS)](https://www.rfc-editor.org/rfc/rfc8785)
- [JSON Schema, draft 2020-12](https://json-schema.org/draft/2020-12/release-notes)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [CloudEvents Specification](https://github.com/cloudevents/spec) (house style precedent for this document's structure)
- [Model Context Protocol — Base Protocol (`_meta`)](https://modelcontextprotocol.io/specification/2026-07-28/basic)
- [Kubernetes — Annotations](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/)
- [CloudEvents — Extension Context Attributes](https://github.com/cloudevents/spec/blob/main/cloudevents/extensions/README.md)
- [Claude Code — Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Hermes Agent — Profile Distributions: Share a Whole Agent](https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions)
- [Agent Plugins](https://agent-plugins.org/) (schemas at <https://agent-plugins.org/schemas/1.0.0/>) — packaging/distribution spec for skills and MCP servers; see [Relationship to Agent Plugins](#relationship-to-agent-plugins-informative)
