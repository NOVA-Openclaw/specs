#!/usr/bin/env python3
"""Reference validator for the Agent Definition specification.

Usage:
    python3 validate.py                      # validate every example under examples/
    python3 validate.py path/to/doc.json ...  # validate specific document(s)

Requires the `jsonschema` package (Draft 2020-12 support; jsonschema >= 4.18
recommended). Exit status is non-zero if any targeted document fails to
validate as expected (valid/ examples must pass, invalid/ examples must fail).
"""
import glob
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


def load_validator():
    with open(SCHEMA_PATH) as f:
        schema = json.load(f)
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def validate_file(validator, path):
    with open(path) as f:
        doc = json.load(f)
    return list(validator.iter_errors(doc))


def main(argv):
    validator = load_validator()
    exit_code = 0

    if argv:
        for path in argv:
            errors = validate_file(validator, path)
            if errors:
                exit_code = 1
                print(f"FAIL {path}")
                for e in errors:
                    print(f"  - {'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}")
            else:
                print(f"PASS {path}")
        return exit_code

    valid_dir = os.path.join(HERE, "examples", "valid")
    invalid_dir = os.path.join(HERE, "examples", "invalid")

    for path in sorted(glob.glob(os.path.join(valid_dir, "*.json"))):
        errors = validate_file(validator, path)
        ok = len(errors) == 0
        print(f"{'PASS' if ok else 'FAIL'} (expected valid)   {os.path.relpath(path, HERE)}")
        if not ok:
            exit_code = 1
            for e in errors:
                print(f"  - {'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}")

    for path in sorted(glob.glob(os.path.join(invalid_dir, "*.json"))):
        errors = validate_file(validator, path)
        ok = len(errors) > 0
        print(f"{'PASS' if ok else 'FAIL'} (expected invalid) {os.path.relpath(path, HERE)}")
        if not ok:
            exit_code = 1
            print("  - expected at least one validation error, got none")

    return exit_code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
