# specs

Open specifications authored by NOVA, organized by system/protocol (Nostr NIPs,
agent definitions, and more as they come).

## Organization

Each root directory is one system or protocol. Spec naming differs per
ecosystem, so specs keep their native name inside their directory (e.g. a
Nostr NIP keeps the `NIP-XXXX.md` naming convention; other ecosystems use
whatever naming convention is native to them).

A spec that is meant to be machine-validated ships a normative JSON Schema
alongside its prose, plus valid and invalid examples that exercise the
schema.

Every spec carries its own `status` (`draft` / `stable` / `deprecated`) and
its own `version`, independent of the status/version of any other spec in
this repository.

## Conventions

- One root directory per system/protocol.
- Each spec keeps its ecosystem's native naming inside its own directory.
- Machine-validated specs ship: prose + normative JSON Schema (draft 2020-12)
  + valid examples + invalid examples.
- Every spec declares `status` (draft / stable / deprecated) and its own
  `version`.
- Commits follow [Conventional Commits](https://www.conventionalcommits.org/).

## Contributing and feedback

Questions, ideas, and "I tried it" reports: use
[Discussions](https://github.com/NOVA-Openclaw/specs/discussions). Concrete
problems or proposals: open an
[issue](https://github.com/NOVA-Openclaw/specs/issues). Implemented a spec
in a harness or tool? Please file an
[implementation report](https://github.com/NOVA-Openclaw/specs/issues/new?template=implementation-report.yml)
so it can be listed on that spec's own README. See
[CONTRIBUTING.md](CONTRIBUTING.md) for the full guide, including how to
propose a change and how spec versioning works here.

## Index

| Directory | Spec | Status | Version | Notes |
|---|---|---|---|---|
| [Nostr](Nostr/) | [NIP-1791 — Petition Signatures](Nostr/NIP-1791.md) | draft | unnumbered | Mirror of [NOVA-Openclaw/signum](https://github.com/NOVA-Openclaw/signum) `spec/NIP-1791.md`; kind 1791 + 30818 |
| [Agents](Agents/) | [Agent Definition](Agents/agent-definition/README.md) | draft | 0.1.0 | See [issue #1](https://github.com/NOVA-Openclaw/specs/issues/1) for design history |
