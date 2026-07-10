from pathlib import Path


def test_setup_python_cache_uses_the_committed_dependency_file() -> None:
    workflow = Path(".github/workflows/validate.yml").read_text(encoding="utf-8")
    assert "cache-dependency-path: requirements-dev.txt" in workflow
