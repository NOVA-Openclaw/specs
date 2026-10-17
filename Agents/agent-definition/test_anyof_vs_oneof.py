#!/usr/bin/env python3
"""Regression guard: the metadata name/role validity rule MUST use anyOf,
not oneOf.

The Agent Definition spec requires an inclusive choice: at least one of
metadata.name or metadata.role, and BOTH MAY be present together. That is
an anyOf of two required clauses. A oneOf would wrongly reject a document
that legitimately carries both name and role. This script fails (non-zero
exit) if:

  - the real schema's name/role rule is not an anyOf (e.g. someone
    "simplified" it to oneOf), or
  - examples/valid/named-agent-with-identity.agent.json no longer carries
    both metadata.name and metadata.role, or
  - the real (anyOf) schema rejects that example, or
  - a oneOf-based variant of the SAME rule does NOT reject that example
    (which would mean this negative test no longer bites).

Run directly, or via the agent-definition-examples GitHub Actions workflow.
"""
import copy
import json
import os
import sys

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.stderr.write(
        "error: this script requires the 'jsonschema' package "
        "(pip install jsonschema)\n"
    )
    sys.exit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA_PATH = os.path.join(HERE, "schema", "agent-definition.schema.json")
BOTH_NAME_AND_ROLE_EXAMPLE = os.path.join(
    HERE, "examples", "valid", "named-agent-with-identity.agent.json"
)


def main():
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)

    rule = schema["allOf"][0]
    if "anyOf" not in rule:
        print(
            "FAIL: schema allOf[0] (the name/role rule) does not use 'anyOf'. "
            "The Agent Definition spec requires an inclusive anyOf here, not oneOf."
        )
        return 1
    if "oneOf" in rule:
        print("FAIL: schema allOf[0] unexpectedly also defines 'oneOf'.")
        return 1

    with open(BOTH_NAME_AND_ROLE_EXAMPLE) as f:
        doc = json.load(f)

    metadata = doc.get("metadata", {})
    if not (metadata.get("name") and metadata.get("role")):
        print(
            f"FAIL: {BOTH_NAME_AND_ROLE_EXAMPLE} no longer carries both "
            "metadata.name and metadata.role; the negative test needs an "
            "example that does."
        )
        return 1

    real_validator = Draft202012Validator(schema)
    real_errors = list(real_validator.iter_errors(doc))
    if real_errors:
        print(
            f"FAIL: the real anyOf schema rejects {BOTH_NAME_AND_ROLE_EXAMPLE}: "
            f"{[e.message for e in real_errors]}"
        )
        return 1

    # A oneOf variant of the SAME rule must reject this example, proving the
    # anyOf-vs-oneOf choice actually matters and this test would catch a
    # future regression.
    oneof_schema = copy.deepcopy(schema)
    oneof_schema["allOf"][0] = {"oneOf": rule["anyOf"]}
    oneof_validator = Draft202012Validator(oneof_schema)
    oneof_errors = list(oneof_validator.iter_errors(doc))
    if not oneof_errors:
        print(
            "FAIL: a oneOf variant of the name/role rule did NOT reject the "
            "name+role example. The negative test no longer bites."
        )
        return 1

    print(
        "PASS: name/role rule is anyOf in the real schema; a oneOf variant "
        "of the same rule correctly rejects the valid name+role example."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
