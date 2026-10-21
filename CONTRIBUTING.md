# Contributing

Thanks for reading these specs closely enough to want to improve them. This
document covers how to give feedback, how to propose a change, and how
spec versioning works in this repository.

## Giving feedback

- **Issues** are for concrete problems or proposals: a section is unclear
  or contradicts itself, a schema rejects a document it should accept (or
  accepts one it shouldn't), a field is missing, a real-world harness can't
  implement something as written. Open an issue.
- **[Discussions](../../discussions)** are for questions, ideas, and
  "I tried it" reports: you implemented part of a spec and want to share
  notes, you have a design idea that isn't a concrete proposal yet, or
  you're not sure if something is a bug in the spec or in your
  understanding of it. Open a discussion.

When in doubt, start a discussion. It's easy to turn a discussion into an
issue once a concrete problem or proposal emerges; it's harder to run a
design conversation inside an issue tracker.

## Proposing a change

1. **Open an issue first** for anything substantive -- a new field, a
   changed validity rule, a new section. This lets the design get
   discussed before anyone spends time writing a PR that might need to be
   reshaped or abandoned. Small, obviously-correct fixes (typos, broken
   links, clarifying wording with no behavioral change) can skip straight
   to a PR.
2. **Then open a PR** that references the issue. If the spec is
   machine-validated, your PR's examples MUST validate against the
   schema, and CI runs on every PR to check that.
3. A maintainer reviews, discussion continues on the PR as needed, and the
   PR is merged (normally squash-merged) once CI is green and the change
   is agreed.

## Spec versioning

Every spec in this repository carries its own `status` (`draft` / `stable`
/ `deprecated`) and its own SemVer `version`, independent of every other
spec here. See each spec's own README for its current status and version.

**While a spec is in `0.x`**, this repository treats the normal SemVer
pre-1.0 convention slightly more strictly: a breaking change bumps the
**minor** version (`0.1.0` -> `0.2.0`), not the patch version, and a
non-breaking addition (a new optional field, a relaxed constraint) also
bumps the minor version. Patch bumps are reserved for prose/schema
clarifications with no effect on which documents validate. Once a spec
reaches `1.0.0`, standard SemVer applies: breaking changes require a major
version bump.

## Implementers are especially welcome

If you've built something that reads or writes a document conforming to
one of these specs -- a harness, a converter, a validator, anything -- please
open an issue titled **"Implementation: <harness>"** (for example,
"Implementation: Claude Code"). That issue is how the relevant spec's
README comes to list your implementation. You don't need a polished
write-up; a link and a sentence or two about what you built is enough to
start. See each spec's own issue-template options for a structured
implementation-report format.

## Commit conventions

Commits in this repository follow
[Conventional Commits](https://www.conventionalcommits.org/).
