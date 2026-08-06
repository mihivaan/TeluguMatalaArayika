from __future__ import annotations

import json
import sys
from collections import defaultdict
from dataclasses import fields, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from src.models import Claim, Entry, Evidence, Meaning, ResearchNote, ResearchQuestion
from src.queries import (
    get_claims_for_entry,
    get_evidence_for_claim,
    get_entry_by_id,
    get_meanings_for_entry,
    get_research_notes_for_entry,
    get_research_questions_for_entry,
)


def _format_datetime(value: datetime | str | None) -> str:
    """
    Safely format datetime objects or ISO timestamp strings.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    return str(value)


def _format_multiline_indented(text: str, indent: str) -> str:
    lines = text.splitlines() or [""]
    if not lines:
        return indent
    rendered = [lines[0]]
    rendered.extend(f"{indent}{line}" for line in lines[1:])
    return "\n".join(rendered)


def _stable_sort_key(item: Any) -> tuple[str, int]:
    created_at = getattr(item, "created_at", None)
    created_key = created_at.isoformat(sep=" ", timespec="seconds") if isinstance(created_at, datetime) else ""
    item_id = getattr(item, "id", 0) or 0
    return (created_key, int(item_id))


def _model_to_serializable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat(sep=" ", timespec="seconds")
    if is_dataclass(value):
        return {field.name: _model_to_serializable(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, dict):
        return {str(key): _model_to_serializable(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_model_to_serializable(item) for item in value]
    if isinstance(value, tuple):
        return [_model_to_serializable(item) for item in value]
    return value


def _question_tree(
    questions: list[ResearchQuestion],
) -> list[dict[str, Any]]:
    children: dict[int | None, list[ResearchQuestion]] = defaultdict(list)
    for question in questions:
        children[question.parent_question_id].append(question)

    for bucket in children.values():
        bucket.sort(key=_stable_sort_key)

    def build(parent_id: int | None) -> list[dict[str, Any]]:
        nodes: list[dict[str, Any]] = []
        for question in children.get(parent_id, []):
            node = {
                "id": question.id,
                "entry_id": question.entry_id,
                "parent_question_id": question.parent_question_id,
                "question_text": question.question_text,
                "status": question.status,
                "resolution_summary": question.resolution_summary,
                "created_at": _format_datetime(question.created_at),
                "updated_at": _format_datetime(question.updated_at),
                "children": build(question.id),
            }
            nodes.append(node)
        return nodes

    return build(None)


def _entry_header(entry: Entry) -> list[str]:
    header = f"# {entry.headword} (Lemma: {entry.lemma}, Homograph: {entry.homograph_index})"
    metadata = [
        "> **Metadata**",
        f"> Entry ID: {entry.id if entry.id is not None else ''}",
        f"> Provenance: {entry.provenance}",
        f"> Classification: {entry.classification}",
    ]
    if entry.created_at is not None:
        metadata.append(f"> Created at: {_format_datetime(entry.created_at)}")
    if entry.updated_at is not None:
        metadata.append(f"> Updated at: {_format_datetime(entry.updated_at)}")
    return [header, "", *metadata, ""]


def _get_entry_or_raise(entry_id: int) -> Entry:
    entry = get_entry_by_id(entry_id)
    if entry is None:
        raise ValueError(f"Entry ID {entry_id} not found.")
    return entry


def export_entry_to_markdown(
    entry_id: int,
    include_meanings: bool = True,
    include_claims: bool = True,
    include_evidence: bool = True,
    include_questions: bool = True,
    include_notes: bool = True,
) -> str:
    """
    Export a single entry and selected child records as Markdown.
    """
    entry = _get_entry_or_raise(entry_id)

    lines: list[str] = []
    lines.extend(_entry_header(entry))

    if include_meanings:
        meanings = sorted(get_meanings_for_entry(entry_id), key=lambda m: (m.meaning_order, _stable_sort_key(m)))
        if meanings:
            lines.append("## Meanings")
            for meaning in meanings:
                lines.append(f"{meaning.meaning_order}. {meaning.meaning}")
                if meaning.notes:
                    lines.append(f"   - Notes: {meaning.notes}")
            lines.append("")

    if include_claims:
        claims = sorted(get_claims_for_entry(entry_id), key=_stable_sort_key)
        if claims:
            lines.append("## Claims & Evidence")
            for claim in claims:
                confidence = f"{claim.confidence:.2f}"
                lines.append(f"- [{claim.status}] (Confidence: {confidence}) {claim.claim_text}")
                if claim.rationale:
                    lines.append(f"  - Rationale: {_format_multiline_indented(claim.rationale, '    ')}")

                if include_evidence:
                    evidence_list = sorted(get_evidence_for_claim(claim.id or 0), key=_stable_sort_key)
                    for evidence in evidence_list:
                        lines.append(f"  └─ [{evidence.evidence_role}] {evidence.evidence_text}")
                        if evidence.notes:
                            lines.append(f"     - Notes: {_format_multiline_indented(evidence.notes, '       ')}")
                lines.append("")
            if lines and lines[-1] != "":
                lines.append("")

    if include_questions:
        questions = get_research_questions_for_entry(entry_id)
        if questions:
            lines.append("## Research Questions")

            children: dict[int | None, list[ResearchQuestion]] = defaultdict(list)
            for question in questions:
                children[question.parent_question_id].append(question)
            for bucket in children.values():
                bucket.sort(key=_stable_sort_key)

            def render_questions(parent_id: int | None, depth: int = 0) -> None:
                for question in children.get(parent_id, []):
                    indent = "  " * depth
                    lines.append(f"{indent}- [{question.status}] {question.question_text}")
                    if question.resolution_summary:
                        lines.append(f"{indent}  - Resolution: {_format_multiline_indented(question.resolution_summary, indent + '    ')}")
                    render_questions(question.id, depth + 1)

            render_questions(None)
            lines.append("")

    if include_notes:
        notes = sorted(get_research_notes_for_entry(entry_id), key=_stable_sort_key)
        if notes:
            lines.append("## Research Journal")
            for note in notes:
                timestamp = _format_datetime(note.created_at) if note.created_at is not None else ""
                lines.append(f"- [{timestamp}]")
                lines.append(_format_multiline_indented(note.note_text, "  "))
                lines.append("")

    while lines and lines[-1] == "":
        lines.pop()

    return "\n".join(lines) + "\n"


def export_entry_to_json(
    entry_id: int,
    include_meanings: bool = True,
    include_claims: bool = True,
    include_evidence: bool = True,
    include_questions: bool = True,
    include_notes: bool = True,
) -> str:
    """
    Export a single entry and selected child records as structured JSON.
    """
    entry = _get_entry_or_raise(entry_id)

    payload: dict[str, Any] = {
        "entry": _model_to_serializable(entry),
    }

    if include_meanings:
        meanings = sorted(get_meanings_for_entry(entry_id), key=lambda m: (m.meaning_order, _stable_sort_key(m)))
        payload["meanings"] = _model_to_serializable(meanings)

    if include_claims:
        claims = sorted(get_claims_for_entry(entry_id), key=_stable_sort_key)
        claims_payload: list[dict[str, Any]] = []
        for claim in claims:
            claim_dict = _model_to_serializable(claim)
            if include_evidence:
                evidence_list = sorted(get_evidence_for_claim(claim.id or 0), key=_stable_sort_key)
                claim_dict["evidence"] = _model_to_serializable(evidence_list)
            claims_payload.append(claim_dict)
        payload["claims"] = claims_payload

    if include_questions:
        questions = get_research_questions_for_entry(entry_id)
        payload["research_questions"] = _question_tree(questions)

    if include_notes:
        notes = sorted(get_research_notes_for_entry(entry_id), key=_stable_sort_key)
        payload["research_notes"] = _model_to_serializable(notes)

    return json.dumps(payload, indent=2, ensure_ascii=False)


def export_entry_to_file(
    entry_id: int,
    output_path: str,
    format_type: str = "markdown",
    **filter_flags: Any,
) -> Path:
    """
    Export an entry to a file in Markdown or JSON format.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fmt = format_type.strip().lower()
    if fmt in {"markdown", "md"}:
        content = export_entry_to_markdown(entry_id, **filter_flags)
    elif fmt == "json":
        content = export_entry_to_json(entry_id, **filter_flags)
    else:
        raise ValueError("format_type must be either 'markdown' or 'json'.")

    path.write_text(content, encoding="utf-8")
    return path


def main() -> int:
    markdown = export_entry_to_markdown(1)
    print(markdown, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())