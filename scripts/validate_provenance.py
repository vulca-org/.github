from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from scripts.build_provenance import DESIGN_COMMIT, SOURCE_FILES, git_bytes


BLOCK = re.compile(r"```json\n(?P<payload>\{.*\})\n```", re.DOTALL)
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")


def parse_payload(text: str) -> dict[str, object]:
    match = BLOCK.search(text)
    if not match:
        raise ValueError("missing provenance JSON block")
    value = json.loads(match.group("payload"))
    if not isinstance(value, dict):
        raise ValueError("provenance payload must be an object")
    return value


def validate_payload(payload: dict[str, object]) -> None:
    required = {
        "schema_version",
        "source_commit",
        "wave0a_commit",
        "candidate_content_commit",
        "source_hashes",
        "excluded",
        "transformations",
    }
    if set(payload) != required or payload["schema_version"] != 1:
        raise ValueError("invalid provenance schema")
    for field in ("source_commit", "wave0a_commit", "candidate_content_commit"):
        if not isinstance(payload[field], str) or not SHA40.fullmatch(payload[field]):
            raise ValueError(f"invalid commit field: {field}")
    hashes = payload["source_hashes"]
    if not isinstance(hashes, dict) or not hashes:
        raise ValueError("source_hashes must be non-empty")
    for path, digest in hashes.items():
        if not isinstance(path, str) or Path(path).is_absolute():
            raise ValueError("source hashes require relative paths")
        if not isinstance(digest, str) or not SHA64.fullmatch(digest):
            raise ValueError("invalid source hash")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path)
    args = parser.parse_args()
    try:
        payload = parse_payload(Path("PROVENANCE.md").read_text(encoding="utf-8"))
        validate_payload(payload)
        if args.source_root is not None:
            expected = payload["source_hashes"]
            assert isinstance(expected, dict)
            for path in SOURCE_FILES:
                actual = hashlib.sha256(git_bytes(args.source_root, DESIGN_COMMIT, path)).hexdigest()
                if expected.get(path) != actual:
                    raise ValueError("source hash mismatch")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"provenance validation error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
