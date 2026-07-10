from pathlib import Path

from scripts.validate_community import validate_community_files


ROOT = Path(__file__).resolve().parents[1]
FILES = ("SECURITY.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SUPPORT.md")


def seed(root: Path) -> None:
    for name in FILES:
        (root / name).write_text("safe baseline", encoding="utf-8")


def test_committed_files_are_valid() -> None:
    assert validate_community_files(ROOT) == []


def test_security_requires_private_reporting(tmp_path: Path) -> None:
    seed(tmp_path)
    (tmp_path / "SECURITY.md").write_text("Open a public issue", encoding="utf-8")
    assert "security policy must require private reporting" in validate_community_files(tmp_path)


def test_public_email_is_rejected(tmp_path: Path) -> None:
    seed(tmp_path)
    (tmp_path / "SUPPORT.md").write_text("contact person@example.com", encoding="utf-8")
    assert "unverified public email" in validate_community_files(tmp_path)


def test_sdk_specific_defaults_are_rejected(tmp_path: Path) -> None:
    seed(tmp_path)
    (tmp_path / "CONTRIBUTING.md").write_text(
        "no Python-side prompt construction", encoding="utf-8"
    )
    assert "SDK-specific organization default" in validate_community_files(tmp_path)
