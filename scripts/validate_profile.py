from __future__ import annotations

import re
import sys
from pathlib import Path


LANES = (
    "Organization Control Plane",
    "Visual Systems",
    "Writing Systems",
    "Agent Infrastructure",
    "Research and Evaluation",
    "Integrations, Internal, and Archive",
)
ALLOWED_URLS = {
    "https://github.com/vulca-org",
    "https://github.com/vulca-org/vulca-visual-control-sdk",
    "https://github.com/vulca-org/vulca-plugin",
    "https://github.com/vulca-org/comfyui-vulca",
}
FORBIDDEN_MARKERS = (
    "Agent-native discipline checked",
    "Python-side prompt construction",
    "Unknown node 'whitespace_analyze'",
    "CONTRIBUTING.md#anti-patterns--what-will-not-be-merged",
)
URL_PATTERN = re.compile(r"https://github\.com/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)?")


def validate_profile(text: str) -> list[str]:
    errors: list[str] = []
    if not text.startswith("# Vulca Systems\n"):
        errors.append("profile must start with the Vulca Systems heading")
    for lane in LANES:
        if lane not in text:
            errors.append(f"missing lane: {lane}")
    for url in URL_PATTERN.findall(text):
        if url.rstrip("/") not in ALLOWED_URLS:
            errors.append("unapproved public link")
    if any(marker in text for marker in FORBIDDEN_MARKERS):
        errors.append("SDK-specific policy marker")
    return sorted(set(errors))


def main() -> int:
    errors = validate_profile(Path("profile/README.md").read_text(encoding="utf-8"))
    if errors:
        for error in errors:
            print(f"profile validation error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
