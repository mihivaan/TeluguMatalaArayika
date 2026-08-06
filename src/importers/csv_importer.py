# src/importers/csv_importer.py
from __future__ import annotations

import csv
import sys
from pathlib import Path
from typing import Any

from src.models import Entry, Meaning
from src.queries import create_entry, create_meaning, find_entries_by_lemma
from src.validation import validate_classification, validate_provenance


REQUIRED_HEADERS = {"headword", "lemma"}
OPTIONAL_HEADERS = {"homograph_index", "provenance", "classification", "meaning"}


def _clean_cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _parse_homograph_index(raw_value: str) -> int | None:
    text = raw_value.strip()
    if not text:
        return 0
    try:
        return int(text)
    except ValueError:
        return None


def _entry_exists(lemma: str, homograph_index: int) -> bool:
    existing_entries = find_entries_by_lemma(lemma)
    for entry in existing_entries:
        if entry.lemma.strip() == lemma and int(entry.homograph_index) == homograph_index:
            return True
    return False


def import_entries_from_csv(csv_path: str) -> tuple[int, int]:
    """
    Import entries from a CSV file.

    Returns:
        tuple[int, int]: (inserted_count, skipped_count)
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    inserted_count = 0
    skipped_count = 0

    with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError("CSV file does not contain a header row.")

        headers = {name.strip() for name in reader.fieldnames if name is not None}
        missing_headers = REQUIRED_HEADERS - headers
        if missing_headers:
            missing_list = ", ".join(sorted(missing_headers))
            raise ValueError(f"CSV is missing required header(s): {missing_list}")

        for row_number, row in enumerate(reader, start=2):
            cleaned = {key.strip(): _clean_cell(value) for key, value in row.items() if key is not None}

            headword = cleaned.get("headword", "")
            lemma = cleaned.get("lemma", "")
            raw_homograph_index = cleaned.get("homograph_index", "")
            raw_provenance = cleaned.get("provenance", "Attested")
            raw_classification = cleaned.get("classification", "Inherited Dravidian")
            meaning_text = cleaned.get("meaning", "")

            if not headword or not lemma:
                skipped_count += 1
                continue

            homograph_index = _parse_homograph_index(raw_homograph_index)
            if homograph_index is None:
                skipped_count += 1
                continue

            try:
                provenance = validate_provenance(raw_provenance or "Attested")
                classification = validate_classification(raw_classification or "Inherited Dravidian")
            except ValueError:
                skipped_count += 1
                continue

            lemma = lemma.strip()
            headword = headword.strip()
            meaning_text = meaning_text.strip()

            if _entry_exists(lemma, homograph_index):
                skipped_count += 1
                continue

            entry = Entry(
                headword=headword,
                lemma=lemma,
                homograph_index=homograph_index,
                provenance=provenance,
                classification=classification,
            )
            entry_id = create_entry(entry)

            if meaning_text:
                meaning = Meaning(
                    entry_id=entry_id,
                    meaning_order=1,
                    meaning=meaning_text,
                )
                create_meaning(meaning)

            inserted_count += 1

    return inserted_count, skipped_count


def main() -> int:
    sample_path = Path("sample_import.csv")

    sample_rows = [
        {
            "headword": "తెలుగు",
            "lemma": "తెలుగు",
            "homograph_index": "0",
            "provenance": "Attested",
            "classification": "Inherited Dravidian",
            "meaning": "The Telugu language.",
        },
        {
            "headword": "గాడిద",
            "lemma": "గాడిద",
            "homograph_index": "0",
            "provenance": "Attested",
            "classification": "Inherited Dravidian",
            "meaning": "Donkey; ass.",
        },
        {
            "headword": "సరుదు",
            "lemma": "సరుదు",
            "homograph_index": "1",
            "provenance": "Attested",
            "classification": "Inherited Dravidian",
            "meaning": "A sample lexical item for importer testing.",
        },
    ]

    try:
        with sample_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "headword",
                    "lemma",
                    "homograph_index",
                    "provenance",
                    "classification",
                    "meaning",
                ],
            )
            writer.writeheader()
            writer.writerows(sample_rows)

        inserted_count, skipped_count = import_entries_from_csv(str(sample_path))
        print(f"Inserted: {inserted_count}")
        print(f"Skipped: {skipped_count}")
        return 0
    finally:
        try:
            sample_path.unlink(missing_ok=True)
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())