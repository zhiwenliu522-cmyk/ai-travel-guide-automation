#!/usr/bin/env python3
"""Validate the publishable project without requiring third-party packages."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    ROOT / "README.md",
    ROOT / ".agents" / "travel-guide-planner.md",
    ROOT / "skills" / "customize-travel-guide" / "SKILL.md",
    ROOT / "skills" / "customize-travel-guide" / "agents" / "openai.yaml",
    ROOT / "skills" / "customize-travel-guide" / "references" / "guide-standards.md",
    ROOT / "skills" / "customize-travel-guide" / "references" / "restaurant-research.md",
    ROOT / "skills" / "customize-travel-guide" / "references" / "case-library.md",
    ROOT / "skills" / "customize-travel-guide" / "references" / "template-profile.md",
    ROOT / "skills" / "customize-travel-guide" / "references" / "block-reuse-contract.md",
    ROOT / "skills" / "customize-travel-guide" / "scripts" / "reference_fidelity_audit.py",
]


def main() -> int:
    errors: list[str] = []
    for path in REQUIRED:
        if not path.is_file():
            errors.append(f"缺少文件：{path.relative_to(ROOT)}")

    skill_path = ROOT / "skills" / "customize-travel-guide" / "SKILL.md"
    if skill_path.is_file():
        skill = skill_path.read_text(encoding="utf-8")
        if not skill.startswith("---\n"):
            errors.append("SKILL.md 缺少 YAML front matter")
        if "name: customize-travel-guide" not in skill:
            errors.append("SKILL.md 的 name 不正确")
        for reference in (
            "references/guide-standards.md",
            "references/restaurant-research.md",
            "references/case-library.md",
            "references/template-profile.md",
        ):
            if reference not in skill:
                errors.append(f"SKILL.md 未引用 {reference}")

    text_files = list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.yaml")) + list(ROOT.rglob("*.py"))
    local_path_pattern = re.compile(r"(?:[A-Za-z]:\\Users\\|[A-Za-z]:/Users/|Desktop[/\\])", re.I)
    for path in text_files:
        text = path.read_text(encoding="utf-8")
        if local_path_pattern.search(text):
            errors.append(f"包含本机绝对路径：{path.relative_to(ROOT)}")

    forbidden_binaries = [
        path for path in ROOT.rglob("*")
        if path.is_file() and path.suffix.lower() in {".doc", ".docx", ".pdf", ".png", ".jpg", ".jpeg", ".zip"}
    ]
    for path in forbidden_binaries:
        errors.append(f"发布包包含受限二进制文件：{path.relative_to(ROOT)}")

    if errors:
        print("项目校验失败")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"项目校验通过，共检查 {len(REQUIRED)} 个必需文件和 {len(text_files)} 个文本文件")
    return 0


if __name__ == "__main__":
    sys.exit(main())

