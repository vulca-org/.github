from pathlib import Path

from scripts.validate_profile import validate_profile


ROOT = Path(__file__).resolve().parents[1]


def test_committed_profile_is_valid() -> None:
    assert validate_profile((ROOT / "profile/README.md").read_text()) == []


def test_profile_requires_every_lane() -> None:
    errors = validate_profile("# Vulca Systems\n\nOrganization Control Plane\n")
    assert "missing lane: Visual Systems" in errors


def test_profile_accepts_renamed_sdk_repository_link() -> None:
    text = "# Vulca Systems\n" + "\n".join(
        [
            "Organization Control Plane",
            "Visual Systems",
            "Writing Systems",
            "Agent Infrastructure",
            "Research and Evaluation",
            "Integrations, Internal, and Archive",
            "https://github.com/vulca-org/vulca-visual-control-sdk",
        ]
    )
    assert "unapproved public link" not in validate_profile(text)


def test_profile_rejects_retired_sdk_repository_link() -> None:
    text = "# Vulca Systems\n" + "\n".join(
        [
            "Organization Control Plane",
            "Visual Systems",
            "Writing Systems",
            "Agent Infrastructure",
            "Research and Evaluation",
            "Integrations, Internal, and Archive",
            "https://github.com/vulca-org/vulca",
        ]
    )
    assert "unapproved public link" in validate_profile(text)


def test_profile_rejects_sdk_specific_policy() -> None:
    assert "SDK-specific policy marker" in validate_profile(
        "# Vulca Systems\nAgent-native discipline checked"
    )
