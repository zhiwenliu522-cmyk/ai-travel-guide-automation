#!/usr/bin/env python3
"""Audit whether a guide reused same-city text as well as source images."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from zipfile import BadZipFile, ZipFile
from xml.etree import ElementTree as ET


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": WORD_NS}
ALLOWED_CHANGES = {
    "date",
    "time",
    "hotel",
    "transport",
    "weather",
    "reservation",
    "business_status",
    "user_requirement",
}
REUSE_VALUES = {"verbatim", "adapted", "new"}


def normalize(text: str) -> str:
    return re.sub(r"\s+", "", text).strip()


def extract_docx(path: Path, min_sentence_chars: int) -> tuple[set[str], set[str], set[str]]:
    try:
        with ZipFile(path) as archive:
            root = ET.fromstring(archive.read("word/document.xml"))
            paragraphs: set[str] = set()
            sentences: set[str] = set()
            for paragraph in root.findall(".//w:body/w:p", NS):
                text = "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))
                normalized = normalize(text)
                if not normalized:
                    continue
                paragraphs.add(normalized)
                for sentence in re.split(r"(?<=[。！？；!?;])", text):
                    item = normalize(sentence)
                    if len(item) >= min_sentence_chars:
                        sentences.add(item)

            media_hashes = {
                hashlib.sha256(archive.read(name)).hexdigest()
                for name in archive.namelist()
                if name.startswith("word/media/") and not name.endswith("/")
            }
            return paragraphs, sentences, media_hashes
    except (FileNotFoundError, BadZipFile, KeyError, ET.ParseError) as exc:
        raise ValueError(f"无法读取 DOCX {path}: {exc}") from exc


def resolve_contract_path(value: str | None, contract_dir: Path) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    return path if path.is_absolute() else (contract_dir / path).resolve()


def validate_contract(path: Path) -> tuple[list[str], int]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"无法读取复用合同 {path}: {exc}"], 0

    if data.get("mode") != "full_new_guide":
        errors.append("合同 mode 必须是 full_new_guide")

    primary = resolve_contract_path(data.get("primary_reference"), path.parent)
    if primary is None or not primary.is_file():
        errors.append("合同 primary_reference 必须指向存在的 DOCX")

    selection = data.get("selection")
    if not isinstance(selection, dict) or not selection.get("reason"):
        errors.append("合同 selection 必须记录主案例选择理由")

    outline = data.get("outline")
    blocks = data.get("blocks")
    if not isinstance(outline, list) or not outline or not all(isinstance(x, str) and x for x in outline):
        errors.append("合同 outline 必须是非空字符串列表")
        outline = []
    if not isinstance(blocks, list) or not blocks:
        errors.append("合同 blocks 必须是非空列表")
        blocks = []

    slots: list[str] = []
    reused_blocks = 0
    for index, block in enumerate(blocks):
        prefix = f"blocks[{index}]"
        if not isinstance(block, dict):
            errors.append(f"{prefix} 必须是对象")
            continue
        slot = block.get("slot")
        if not isinstance(slot, str) or not slot:
            errors.append(f"{prefix}.slot 不能为空")
        else:
            slots.append(slot)

        reuse = block.get("reuse")
        if reuse not in REUSE_VALUES:
            errors.append(f"{prefix}.reuse 必须是 verbatim、adapted 或 new")
            continue

        changes = block.get("allowed_changes")
        if not isinstance(changes, list) or any(change not in ALLOWED_CHANGES for change in changes):
            errors.append(f"{prefix}.allowed_changes 含合同白名单外字段")
            changes = []

        if reuse == "verbatim":
            reused_blocks += 1
            if changes:
                errors.append(f"{prefix} 为 verbatim 时不得声明修改字段")
        elif reuse == "adapted":
            reused_blocks += 1
            if not changes:
                errors.append(f"{prefix} 为 adapted 时必须声明修改字段")
            if not block.get("reason"):
                errors.append(f"{prefix} 为 adapted 时必须写明原因")
        else:
            if block.get("source_doc") is not None or block.get("source_locator") is not None:
                errors.append(f"{prefix} 为 new 时来源字段必须为 null")
            if not block.get("reason"):
                errors.append(f"{prefix} 为 new 时必须写明原创原因")

        if reuse != "new":
            source = resolve_contract_path(block.get("source_doc"), path.parent)
            if source is None or not source.is_file():
                errors.append(f"{prefix}.source_doc 必须指向存在的 DOCX")
            if not block.get("source_locator"):
                errors.append(f"{prefix}.source_locator 不能为空")
            if not isinstance(block.get("source_images", []), list):
                errors.append(f"{prefix}.source_images 必须是列表")

    if len(slots) != len(set(slots)):
        errors.append("合同 blocks 中的 slot 不得重复")
    if set(outline) != set(slots):
        missing = sorted(set(outline) - set(slots))
        extra = sorted(set(slots) - set(outline))
        if missing:
            errors.append(f"合同缺少槽位: {missing}")
        if extra:
            errors.append(f"合同存在大纲外槽位: {extra}")

    return errors, reused_blocks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--contract", type=Path)
    parser.add_argument("--min-sentence-chars", type=int, default=12)
    args = parser.parse_args()

    errors: list[str] = []
    reused_blocks = 0
    if args.contract:
        contract_errors, reused_blocks = validate_contract(args.contract)
        errors.extend(contract_errors)

    try:
        output_paragraphs, output_sentences, output_media = extract_docx(
            args.output, args.min_sentence_chars
        )
        reference_paragraphs: set[str] = set()
        reference_sentences: set[str] = set()
        reference_media: set[str] = set()
        for reference in args.reference:
            paragraphs, sentences, media = extract_docx(reference, args.min_sentence_chars)
            reference_paragraphs.update(paragraphs)
            reference_sentences.update(sentences)
            reference_media.update(media)
    except ValueError as exc:
        errors.append(str(exc))
        output_paragraphs = output_sentences = output_media = set()
        reference_paragraphs = reference_sentences = reference_media = set()

    shared_paragraphs = output_paragraphs & reference_paragraphs
    shared_sentences = output_sentences & reference_sentences
    shared_media = output_media & reference_media

    if shared_media and not shared_paragraphs:
        errors.append("复用了同城图片，但没有任何完整同城段落保持不变；疑似只借用了样式外壳")
    recognizable_matches = len(shared_paragraphs) + len(shared_sentences)
    if reused_blocks and recognizable_matches < reused_blocks:
        errors.append(
            "复用合同包含 "
            f"{reused_blocks} 个 verbatim/adapted 槽位，但只找到 "
            f"{recognizable_matches} 个完整段落或原句命中"
        )

    result = {
        "status": "fail" if errors else "pass",
        "references": [str(path) for path in args.reference],
        "output": str(args.output),
        "shared_exact_paragraphs": len(shared_paragraphs),
        "shared_exact_sentences": len(shared_sentences),
        "shared_media": len(shared_media),
        "contract_reused_blocks": reused_blocks,
        "sample_shared_paragraphs": sorted(shared_paragraphs, key=len, reverse=True)[:5],
        "sample_shared_sentences": sorted(shared_sentences, key=len, reverse=True)[:5],
        "errors": errors,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
