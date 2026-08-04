"""
తెలుగు మాటల అరయిక (TLRE)

Database Queries

Version: 0.1.0
Reference Point: RP-006

Database access functions for the core domain entities.

This module intentionally contains only persistence logic.
Business orchestration and audit logging belong to higher
application layers.
"""

from __future__ import annotations

import sqlite3
from typing import Optional

from src.db import get_connection
from src.models import Entry, Meaning, Claim
from src.validation import (
    validate_provenance,
    validate_classification,
    validate_claim_status,
)


# ==========================================================
# Row Mappers
# ==========================================================

def row_to_entry(row: sqlite3.Row) -> Entry:
    """Convert a SQLite row into an Entry dataclass."""

    return Entry(
        id=row["id"],
        headword=row["headword"],
        lemma=row["lemma"],
        homograph_index=row["homograph_index"],
        provenance=row["provenance"],
        classification=row["classification"],
        research_question=row["research_question"],
        notes=row["notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def row_to_meaning(row: sqlite3.Row) -> Meaning:
    """Convert a SQLite row into a Meaning dataclass."""

    return Meaning(
        id=row["id"],
        entry_id=row["entry_id"],
        meaning_order=row["meaning_order"],
        meaning=row["meaning"],
        notes=row["notes"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def row_to_claim(row: sqlite3.Row) -> Claim:
    """Convert a SQLite row into a Claim dataclass."""

    return Claim(
        id=row["id"],
        entry_id=row["entry_id"],
        meaning_id=row["meaning_id"],
        claim_text=row["claim_text"],
        confidence=row["confidence"],
        evidence_completeness=row["evidence_completeness"],
        rationale=row["rationale"],
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


# ==========================================================
# Entry Operations
# ==========================================================

def create_entry(entry: Entry) -> int:
    """
    Insert a new Entry into the database.

    Returns
    -------
    int
        Newly generated entry ID.
    """

    validate_provenance(entry.provenance)
    validate_classification(entry.classification)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO entries (
                headword,
                lemma,
                homograph_index,
                provenance,
                classification,
                research_question,
                notes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry.headword,
                entry.lemma,
                entry.homograph_index,
                entry.provenance,
                entry.classification,
                entry.research_question,
                entry.notes,
            ),
        )

        return cursor.lastrowid


def get_entry_by_id(entry_id: int) -> Optional[Entry]:
    """
    Retrieve an Entry by its primary key.
    """

    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT *
            FROM entries
            WHERE id = ?
            """,
            (entry_id,),
        )

        row = cursor.fetchone()

    if row is None:
        return None

    return row_to_entry(row)


def find_entries_by_lemma(lemma: str) -> list[Entry]:
    """
    Find every entry having the supplied lemma.

    Results are ordered by homograph index.
    """

    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT *
            FROM entries
            WHERE lemma = ?
            ORDER BY homograph_index
            """,
            (lemma,),
        )

        rows = cursor.fetchall()

    return [row_to_entry(row) for row in rows]


# ==========================================================
# Claim Operations
# ==========================================================

def add_claim(claim: Claim) -> int:
    """
    Insert a new claim.

    Returns
    -------
    int
        Newly generated claim ID.
    """

    validate_claim_status(claim.status)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO claims (
                entry_id,
                meaning_id,
                claim_text,
                confidence,
                evidence_completeness,
                rationale,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                claim.entry_id,
                claim.meaning_id,
                claim.claim_text,
                claim.confidence,
                claim.evidence_completeness,
                claim.rationale,
                claim.status,
            ),
        )

        return cursor.lastrowid


def get_claims_for_entry(entry_id: int) -> list[Claim]:
    """
    Retrieve every claim associated with an entry.
    """

    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT *
            FROM claims
            WHERE entry_id = ?
            ORDER BY id
            """,
            (entry_id,),
        )

        rows = cursor.fetchall()

    return [row_to_claim(row) for row in rows]