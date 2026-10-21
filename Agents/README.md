# Agents

This directory holds harness-agnostic agent specifications: data formats that
describe an agent (model preferences, bootstrap context, skills, tools,
permissions, etc.) in a way that is not tied to any specific agent harness or
runtime.

The first spec in progress here is the **Agent Definition** format, a
platform-agnostic JSON object from which any agent harness can configure a
functional subagent. See the tracking issue for design decisions, proposed
shape, and acceptance criteria.

See [`agent-definition/README.md`](agent-definition/README.md) for the current draft specification (spec version 0.1.0), its normative JSON Schema, and valid/invalid examples.
