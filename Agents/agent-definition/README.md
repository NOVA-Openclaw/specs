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
   it (see [`examples/valid/named-agent-with-identity.json`](examples/valid/named-agent-with-identity.json),
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
| `x-*` | any | OPTIONAL, vendor extension (see [Extensibility](#extensibility)) |

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
[`examples/invalid/skill-missing-locator.json`](examples/invalid/skill-missing-locator.json).

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

### `x-*` (vendor extensions)

Any top-level or nested property name matching `^x-` is reserved for vendor
or implementation-specific extensions and is never defined by this
specification. See [Extensibility](#extensibility).

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
MAY declare for itself: `use_definition` (the definition's `identity`
replaces the host identity entirely), `use_host` (the host identity is kept
and the definition's `identity` is ignored), and `merge` (both are
presented, host identity first, harness-defined order otherwise). A harness
MUST declare which policy it implements (in its own documentation or
conformance notes) and **MUST report, per instantiation, which of the
declared behaviors it actually applied** when a definition's `identity` was
present and the harness has a host identity of its own. This specification
does not mandate any one policy; it mandates that one is declared and its
application is reported.

When `metadata.name` is absent, the harness MUST derive a fallback handle
from `metadata.role` (e.g. `role: "Research"` to `focus-research`, exact
derivation scheme left to the harness) and MUST report the derived handle
wherever it reports instantiation diagnostics.

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

Vendor- or implementation-specific fields SHOULD be prefixed with `x-` at
whatever level of the document they appear (top level or nested within a
block), following the precedent set by
[CloudEvents](https://github.com/cloudevents/spec) and similar specs. A
conforming harness or validator **MUST ignore unknown fields** — whether or
not they are `x-`-prefixed — rather than rejecting the document because of
them. This specification may define new, non-`x-` top-level or nested fields
in future minor versions; a harness built against an older minor version
MUST continue to ignore fields it does not recognize rather than fail
validation, which is why `additionalProperties` is not set to `false`
anywhere in the normative schema.

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
prompt. Source, verified by direct fetch on 2026-10-17:
<https://code.claude.com/docs/en/sub-agents>.

Verified frontmatter fields (per that page): `name`, `description`,
`tools`, `disallowedTools`, `model`, `permissionMode`, `mcpServers`,
`hooks`, `maxTurns`, `autoCompactWindow`, `skills`, `initialPrompt`,
`memory`, `effort`, `background`, `omitClaudeMd`, `isolation`, `color`,
`experimental`. Only `name` and `description` are required; a file missing
either is skipped rather than erroring.

| Agent Definition | Claude Code frontmatter | Notes |
|---|---|---|
| `metadata.name` | `name` | Both are the invocation/display name. |
| `metadata.description` | `description` | Claude Code's `description` additionally drives automatic delegation (Claude decides when to invoke the subagent from this text); this spec's `description` is purely descriptive. **Lossy on export to Claude Code** if a definition has no `description` — Claude Code requires one. |
| `bootstrap` | Markdown body (system prompt) | Direct mapping: the body *is* the bootstrap text, with no internal structure imposed, matching this spec's "opaque blob" rule. |
| `identity` | *(no dedicated field)* | Claude Code has no separate identity/persona field; a Claude Code subagent's "who it is" lives in the same Markdown body as everything else. Exporting *to* Claude Code: an identity block, if present, SHOULD be composed into the body ahead of the bootstrap content per [Identity composition](#identity-composition), since Claude Code offers nowhere else to put it. Importing *from* Claude Code: there is no identity to extract; the whole body becomes `bootstrap` with no `identity` block. |
| `model` (first entry) | `model` | Claude Code's `model` accepts a family alias (`sonnet`/`opus`/`haiku`), a full model ID, or `inherit`. This spec's ordered list has no equivalent of `inherit` (inherit the host's own model choice); exporting an `inherit`-configured subagent has no faithful representation and SHOULD be dropped or flagged rather than guessed. |
| `model[].settings` | *(no equivalent)* | Claude Code's frontmatter does not expose model-specific reasoning/thinking parameters at the subagent-definition level; `effort` (see below) is Claude Code's own, different mechanism. |
| `tools` (by reference) | `tools` (allowlist) | **Not a direct mapping.** Claude Code's `tools` names *built-in or MCP tool identifiers already available to the session*; it is a filter, not a by-reference installable tool list. This spec's `tools` are externally published, versioned, integrity-checkable references. Converting in either direction requires a resolution step this spec does not define: from Claude Code, each allowed tool name would need an external registry entry to become a reference; from this spec, each tool reference would need to resolve to a Claude Code tool name before it can appear in `tools`. |
| `tools[].kind: "mcp_server"` | `mcpServers` | Claude Code's `mcpServers` can reference an already-configured server by name or supply an inline connection config; this spec's MCP tool references always use a locator (`id`/`url`), never an inline config, so an inline `mcpServers` entry has no direct equivalent without first publishing it somewhere resolvable. |
| `permissions` | `permissionMode` | **Not a direct mapping.** `permissionMode` selects a *mode* (`default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan`) governing how Claude Code's own approval system behaves; it does not declare filesystem/network/side-effect scopes the way this spec's `permissions` does. The two are related but not interchangeable; a faithful export would need a policy decision about which `permissionMode` best approximates a given `permissions` declaration, which this spec does not prescribe. |
| `contract` | *(no equivalent)* | Claude Code has no declared I/O JSON Schema contract for a subagent. |
| `integrity` | *(no equivalent)* | Not applicable; Claude Code subagent files are local, version-controlled Markdown, not fetched-by-reference artifacts. |
| *(no equivalent)* | `skills` (preload list) | Claude Code's `skills` frontmatter field *preloads* named skill content into context at startup; this is closer to inlining than to this spec's by-reference `skills`, and has no faithful round-trip without resolving each preloaded skill name to a published, referenceable skill. |
| *(no equivalent)* | `maxTurns`, `autoCompactWindow`, `background`, `omitClaudeMd`, `isolation`, `color`, `initialPrompt`, `experimental.cacheTtl`, `effort`, `disallowedTools`, `hooks`, `memory` | Harness-specific runtime controls with no corresponding concept in this spec; these are expected to stay harness-local extensions (an exporter MAY carry them as `x-claude-code-*` fields) rather than becoming part of a platform-agnostic definition. |

**Could not verify:** whether Claude Code's frontmatter parser ignores
arbitrary unrecognized field names in general (as opposed to the two
specific named exceptions, `color` and `experimental`, which the fetched
page states are "ignored rather than rejected" in one particular context —
reuse as an agent-team teammate). This spec's own [extensibility
rule](#extensibility) — harnesses MUST ignore unknown fields — is this
spec's own requirement for conformance with this spec, independent of
what Claude Code's parser does with arbitrary unknown frontmatter keys in
general, which was not confirmed from the fetched page.

## Appendix B: Mapping to/from Hermes Agent Profile Distributions (informative)

A Hermes profile distribution is a git repository that packages a complete
Hermes agent for sharing and installation (`hermes profile install
<repo>`). Source, verified by direct fetch on 2026-10-17:
<https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions>.

Verified repository layout and manifest fields (per that page):
`distribution.yaml` (manifest: `name` required; also `version`,
`description`, `hermes_requires`, `author`, `license`, `env_requires`
— each with `name`, `description`, `required`, `default` —, and
`distribution_owned`), `SOUL.md` (identity/system-prompt text, no required
internal schema, strongly recommended but not strictly required), `config.yaml`
(model, provider, tool defaults), `mcp.json` (MCP server connections),
`skills/` (bundled skill directories), and `cron/jobs.json` (scheduled jobs;
distribution content). Versioning is via git tags/branches/commit SHAs, not
a manifest version-range field.

| Agent Definition | Hermes distribution | Notes |
|---|---|---|
| `metadata.name` | `distribution.yaml: name` | Direct mapping; both are the agent/distribution's canonical name. |
| `metadata.version` | `distribution.yaml: version` | Direct mapping, though Hermes additionally expects a matching git tag (`vX.Y.Z`) for that version to be meaningfully installable/updatable — a concept this spec does not require. |
| `metadata.description` | `distribution.yaml: description` | Direct mapping. |
| `metadata.authors` | `distribution.yaml: author` | Hermes's field is singular (one author string); this spec's `authors` is a list. Exporting multiple authors to Hermes is lossy without a policy choice (e.g. join into one string). |
| `metadata.license` | `distribution.yaml: license` | Direct mapping. |
| `identity.persona` (+ `voice`, `values`, `pronouns`) | `SOUL.md` | Close conceptual mapping: Hermes explicitly separates `SOUL.md` (identity) from the rest of the distribution, the same identity/bootstrap separation this spec requires. `SOUL.md` has no internal schema (plain Markdown, scanned for prompt injection, used as-is), so `identity.persona` maps to `SOUL.md`'s content directly; this spec's additional structured sub-fields (`pronouns`, `voice`, `values`) have no dedicated Hermes equivalent and would need to be folded into `SOUL.md` prose on export. |
| `bootstrap` | *(no single dedicated file)* | Hermes has no exact equivalent of one opaque bootstrap blob; domain/procedural context in a Hermes distribution is typically split across `config.yaml` tool defaults, bundled `skills/`, and whatever the author put in `SOUL.md` beyond pure identity. Importing *from* Hermes, a faithful `bootstrap` would need to be assembled from these non-identity parts; exporting *to* Hermes, `bootstrap` content has no single canonical destination file and would most naturally become part of `SOUL.md` (after `identity.persona`) or a project-level instructions file, which is a lossy, harness-specific choice this spec does not prescribe. |
| `model` (first entry) | `config.yaml` (model, provider, reasoning) | Conceptually corresponds (Hermes's `config.yaml` carries model/provider/reasoning defaults per the repo layout the docs describe) but the page fetched for this appendix did not show `config.yaml`'s internal field names, so the exact key-level mapping (e.g. whether it supports an *ordered list* of fallbacks the way this spec's `model` array does) **could not be verified** from the source fetched. |
| `skills` (by reference) | `skills/<name>/SKILL.md` | **Not a direct mapping.** Hermes bundles skill directories *inside* the distribution (shipped, versioned together with the agent via the same git repo/tags); this spec's `skills` are external references to independently published, independently versioned skills. Importing from Hermes would require publishing each bundled skill externally to get a referenceable `id`/`url`; exporting to Hermes would mean materializing each referenced skill's content into a `skills/` subdirectory, which is exactly the embedding this spec's `skills` are designed to avoid. |
| `tools` (`kind: "mcp_server"`) | `mcp.json` | Conceptual correspondence (both describe MCP server connections for the agent) but `mcp.json`'s internal schema was not shown on the fetched page and **could not be verified**. |
| `permissions` | *(no verified equivalent)* | Not confirmed from the fetched page; Hermes's security/sandboxing model, if any, was outside what was retrieved for this appendix. |
| `contract` | *(no equivalent)* | Not found in the fetched documentation. |
| `integrity` | *(no equivalent as a manifest field)* | Hermes relies on git's own content-addressing (commits, tags) rather than a declared hash field; not a direct field-for-field mapping. |
| *(no equivalent)* | `hermes_requires` | A minimum Hermes version constraint; no equivalent concept in this spec, which is explicitly harness-agnostic rather than versioned against one harness. |
| *(no equivalent)* | `env_requires` | Declares required/optional environment variables (e.g. API keys) an installer must supply; this spec's `tools`/`skills` references may implicitly require credentials to resolve, but this spec does not have a dedicated environment-variable-declaration field. |
| *(no equivalent)* | `distribution_owned`, `cron/jobs.json` | Hermes-specific update-merge and scheduling mechanics with no corresponding concept in this spec. |

**Could not verify:** the exact internal field names and schema of
`config.yaml` (model/provider/reasoning configuration) and `mcp.json` (MCP
server connection format) — the fetched documentation page described their
*purpose* and their place in the repository layout, but did not render their
field-level contents. A later revision of this appendix SHOULD fetch and
cite the relevant Hermes configuration-reference pages directly (candidates
seen in search results but not independently fetched/confirmed for this
draft: `https://hermes-agent.nousresearch.com/docs/user-guide/configuring-models`
and `https://hermes-agent.nousresearch.com/docs/user-guide/secrets/`) before
asserting a field-level mapping for those two files.

## References

- [RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels](https://www.rfc-editor.org/rfc/rfc2119)
- [RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words](https://www.rfc-editor.org/rfc/rfc8174)
- [RFC 8785 — JSON Canonicalization Scheme (JCS)](https://www.rfc-editor.org/rfc/rfc8785)
- [JSON Schema, draft 2020-12](https://json-schema.org/draft/2020-12/release-notes)
- [Semantic Versioning 2.0.0](https://semver.org/)
- [CloudEvents Specification](https://github.com/cloudevents/spec) (house style precedent for `x-` extension fields and this document's structure)
- [Claude Code — Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Hermes Agent — Profile Distributions: Share a Whole Agent](https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions)
