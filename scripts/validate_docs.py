#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MAX_AGENTS_WORDS = 400
REQUIRED_FILES = [
    "AGENTS.md",
    "ARCHITECTURE.md",
    "docs/PLANS.md",
    "docs/DESIGN.md",
    "docs/FRONTEND.md",
    "docs/PRODUCT_SENSE.md",
    "docs/QUALITY_SCORE.md",
    "docs/RELIABILITY.md",
    "docs/SECURITY.md",
    "docs/DOC_GARDENING.md",
    "docs/design-docs/index.md",
    "docs/design-docs/core-beliefs.md",
    "docs/design-docs/portfolio-control-plane-architecture.md",
    "docs/design-docs/template.md",
    "docs/product-specs/index.md",
    "docs/product-specs/portfolio-automarketing-control-plane.md",
    "docs/product-specs/template.md",
    "docs/exec-plans/active/README.md",
    "docs/exec-plans/completed/README.md",
    "docs/exec-plans/tech-debt-tracker.md",
    "docs/generated/db-schema.md",
    "docs/references/index.md",
    "docs/references/design-system-reference-llms.txt",
    "docs/references/mcp-application-contract.md",
    "docs/references/skills-and-automations.md",
    "docs/references/nixpacks-llms.txt",
    "docs/references/uv-llms.txt",
    "scripts/validate_docs.py",
    ".github/workflows/docs-validation.yml",
]
REQUIRED_DIRS = [
    "docs",
    "docs/design-docs",
    "docs/exec-plans",
    "docs/exec-plans/active",
    "docs/exec-plans/completed",
    "docs/generated",
    "docs/product-specs",
    "docs/references",
    "scripts",
    ".github/workflows",
]
GOVERNED_DOCS = [
    "AGENTS.md",
    "ARCHITECTURE.md",
    "docs/PLANS.md",
    "docs/DESIGN.md",
    "docs/FRONTEND.md",
    "docs/PRODUCT_SENSE.md",
    "docs/QUALITY_SCORE.md",
    "docs/RELIABILITY.md",
    "docs/SECURITY.md",
    "docs/DOC_GARDENING.md",
    "docs/design-docs/index.md",
    "docs/design-docs/core-beliefs.md",
    "docs/design-docs/portfolio-control-plane-architecture.md",
    "docs/design-docs/template.md",
    "docs/product-specs/index.md",
    "docs/product-specs/portfolio-automarketing-control-plane.md",
    "docs/product-specs/template.md",
    "docs/exec-plans/active/README.md",
    "docs/exec-plans/completed/README.md",
    "docs/exec-plans/tech-debt-tracker.md",
    "docs/references/index.md",
    "docs/references/design-system-reference-llms.txt",
    "docs/references/mcp-application-contract.md",
    "docs/references/skills-and-automations.md",
    "docs/references/nixpacks-llms.txt",
    "docs/references/uv-llms.txt",
]
INDEX_COVERAGE = {
    "docs/design-docs/index.md": [
        "docs/design-docs/core-beliefs.md",
        "docs/design-docs/portfolio-control-plane-architecture.md",
        "docs/design-docs/template.md",
    ],
    "docs/product-specs/index.md": [
        "docs/product-specs/portfolio-automarketing-control-plane.md",
        "docs/product-specs/template.md",
    ],
    "docs/references/index.md": [
        "docs/references/design-system-reference-llms.txt",
        "docs/references/mcp-application-contract.md",
        "docs/references/skills-and-automations.md",
        "docs/references/nixpacks-llms.txt",
        "docs/references/uv-llms.txt",
    ],
}
REQUIRED_METADATA_KEYS = {
    "Status",
    "Owner",
    "Last Reviewed",
    "Source of Truth For",
    "Related Docs",
}
LOCAL_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def parse_frontmatter(relative_path: str, errors: list[str]) -> dict[str, str]:
    text = read_text(relative_path)
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail(f"{relative_path}: missing leading frontmatter block", errors)
        return {}

    metadata: dict[str, str] = {}
    for raw_line in match.group(1).splitlines():
        if not raw_line.strip():
            continue
        if ":" not in raw_line:
            fail(f"{relative_path}: malformed metadata line `{raw_line}`", errors)
            continue
        key, value = raw_line.split(":", 1)
        metadata[key.strip()] = value.strip()

    missing = REQUIRED_METADATA_KEYS - set(metadata)
    if missing:
        fail(
            f"{relative_path}: missing metadata keys {', '.join(sorted(missing))}",
            errors,
        )
    return metadata


def strip_frontmatter(text: str) -> str:
    return re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)


def check_required_paths(errors: list[str]) -> None:
    for relative_path in REQUIRED_DIRS:
        if not (REPO_ROOT / relative_path).is_dir():
            fail(f"Missing required directory: {relative_path}", errors)

    for relative_path in REQUIRED_FILES:
        if not (REPO_ROOT / relative_path).is_file():
            fail(f"Missing required file: {relative_path}", errors)


def check_metadata(errors: list[str]) -> None:
    for relative_path in GOVERNED_DOCS:
        parse_frontmatter(relative_path, errors)


def check_generated_doc(errors: list[str]) -> None:
    relative_path = "docs/generated/db-schema.md"
    text = read_text(relative_path)
    if "Do not edit manually" not in text:
        fail(f"{relative_path}: missing manual edit warning", errors)
    if "Source command:" not in text:
        fail(f"{relative_path}: missing source command declaration", errors)
    if re.search(r"^(Status|Owner|Last Reviewed|Source of Truth For|Related Docs):", text, re.MULTILINE):
        fail(f"{relative_path}: generated docs must not define manual metadata fields", errors)


def check_index_coverage(errors: list[str]) -> None:
    for index_path, required_links in INDEX_COVERAGE.items():
        text = read_text(index_path)
        for linked_path in required_links:
            relative_link = Path(linked_path).name
            if relative_link not in text:
                fail(f"{index_path}: missing reference to {linked_path}", errors)


def check_local_links(errors: list[str]) -> None:
    doc_paths = GOVERNED_DOCS + ["docs/generated/db-schema.md"]
    for relative_path in doc_paths:
        source_path = REPO_ROOT / relative_path
        text = read_text(relative_path)
        for target in LOCAL_LINK_RE.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_path = target.split("#", 1)[0]
            if not target_path:
                continue
            resolved = (source_path.parent / target_path).resolve()
            try:
                resolved.relative_to(REPO_ROOT.resolve())
            except ValueError:
                fail(f"{relative_path}: link escapes repository root -> {target}", errors)
                continue
            if not resolved.exists():
                fail(f"{relative_path}: broken local link -> {target}", errors)


def check_agents_size(errors: list[str]) -> None:
    text = strip_frontmatter(read_text("AGENTS.md"))
    words = re.findall(r"\b[\w`.-]+\b", text)
    if len(words) > MAX_AGENTS_WORDS:
        fail(
            f"AGENTS.md: too long at {len(words)} words; keep at or below {MAX_AGENTS_WORDS}",
            errors,
        )


def main() -> int:
    errors: list[str] = []
    check_required_paths(errors)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    check_metadata(errors)
    check_generated_doc(errors)
    check_index_coverage(errors)
    check_local_links(errors)
    check_agents_size(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Documentation scaffold validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
