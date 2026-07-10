from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path


DESIGN_COMMIT = "bc30259f3dd97ed7aedbc0858e7ce6b14500a22a"
WAVE0A_COMMIT = "d61139ef1d088e68d0fa23798f37ca04c00399bf"
SOURCE_FILES = (
    "LICENSE",
    "docs/superpowers/specs/2026-07-10-vulca-systems-wave0b-local-control-plane-bootstrap-design.md",
)


def git_bytes(root: Path, commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(root), "show", f"{commit}:{path}"],
        check=True,
        capture_output=True,
    ).stdout


def provenance_payload(
    *,
    source_commit: str,
    wave0a_commit: str,
    candidate_content_commit: str,
    source_hashes: dict[str, str],
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "source_commit": source_commit,
        "wave0a_commit": wave0a_commit,
        "candidate_content_commit": candidate_content_commit,
        "source_hashes": dict(sorted(source_hashes.items())),
        "excluded": [
            ".github/CODEOWNERS",
            ".github/FUNDING.yml",
            ".github/ISSUE_TEMPLATE/",
            ".github/PULL_REQUEST_TEMPLATE.md",
            ".github/workflows/ci.yml",
        ],
        "transformations": [
            "derived a domain-neutral profile from the approved design",
            "created lightweight organization community-health documents",
            "excluded SDK-specific ownership, funding, templates, and workflows",
        ],
    }


def render_provenance(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, indent=2, sort_keys=True)
    return "# Provenance\n\nThis candidate uses a fresh Git history.\n\n" f"```json\n{encoded}\n```\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--candidate-content-commit", required=True)
    args = parser.parse_args()
    hashes = {
        path: hashlib.sha256(git_bytes(args.source_root, DESIGN_COMMIT, path)).hexdigest()
        for path in SOURCE_FILES
    }
    payload = provenance_payload(
        source_commit=DESIGN_COMMIT,
        wave0a_commit=WAVE0A_COMMIT,
        candidate_content_commit=args.candidate_content_commit,
        source_hashes=hashes,
    )
    Path("PROVENANCE.md").write_text(render_provenance(payload), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
