from __future__ import annotations

import re
import sys
from pathlib import Path


FILES = ("SECURITY.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md", "SUPPORT.md")
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
SDK_MARKERS = ("Python-side prompt construction", "whitespace_analyze", "layer_generate")


def validate_community_files(root: Path) -> list[str]:
    errors: list[str] = []
    texts: dict[str, str] = {}
    for name in FILES:
        path = root / name
        if not path.is_file():
            errors.append(f"missing community file: {name}")
            continue
        texts[name] = path.read_text(encoding="utf-8")
    combined = "\n".join(texts.values())
    if EMAIL.search(combined):
        errors.append("unverified public email")
    if any(marker in combined for marker in SDK_MARKERS):
        errors.append("SDK-specific organization default")
    security = texts.get("SECURITY.md", "").casefold()
    if "private vulnerability reporting" not in security:
        errors.append("security policy must require private reporting")
    if "do not open a public issue" not in security:
        errors.append("security policy must prohibit public issue reporting")
    return sorted(set(errors))


def main() -> int:
    errors = validate_community_files(Path.cwd())
    for error in errors:
        print(f"community validation error: {error}", file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
