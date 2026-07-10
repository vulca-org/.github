from pathlib import Path

import pytest

from scripts.build_provenance import provenance_payload, render_provenance
from scripts.validate_provenance import parse_payload, validate_payload


def test_provenance_round_trip() -> None:
    payload = provenance_payload(
        source_commit="a" * 40,
        wave0a_commit="b" * 40,
        candidate_content_commit="c" * 40,
        source_hashes={"LICENSE": "d" * 64},
    )
    assert parse_payload(render_provenance(payload)) == payload


def test_provenance_rejects_absolute_paths() -> None:
    payload = provenance_payload(
        source_commit="a" * 40,
        wave0a_commit="b" * 40,
        candidate_content_commit="c" * 40,
        source_hashes={"/private/source": "d" * 64},
    )
    with pytest.raises(ValueError, match="relative paths"):
        validate_payload(payload)


def test_committed_provenance_is_valid() -> None:
    validate_payload(parse_payload(Path("PROVENANCE.md").read_text(encoding="utf-8")))
