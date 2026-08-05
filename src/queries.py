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
from src.models import (
    Entry,
    Meaning,
    Claim,
    ResearchQuestion,
    QuestionRelationship,
    ResearchNote,
)
from src.validation import (
    validate_provenance,
    validate_classification,
    validate_claim_status,
    validate_research_question_status,
    validate_question_relationship_type,
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
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def row_to_research_question(row: sqlite3.Row) -> ResearchQuestion:
    """Convert a SQLite row into a ResearchQuestion dataclass."""

    return ResearchQuestion(
        id=row["id"],
        entry_id=row["entry_id"],
        parent_question_id=row["parent_question_id"],
        question_text=row["question_text"],
        status=row["status"],
        resolution_summary=row["resolution_summary"],
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
                classification
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                entry.headword,
                entry.lemma,
                entry.homograph_index,
                entry.provenance,
                entry.classification,
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


def get_claims_for_entry(
    entry_id: int,
    status: Optional[str] = None,
) -> list[Claim]:
    """
    Retrieve claims associated with an entry, optionally filtering by status.
    """
    if status is not None:
        validate_claim_status(status)
        sql = "SELECT * FROM claims WHERE entry_id = ? AND status = ? ORDER BY id"
        params = (entry_id, status)
    else:
        sql = "SELECT * FROM claims WHERE entry_id = ? ORDER BY id"
        params = (entry_id,)

    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall()

    return [row_to_claim(row) for row in rows]

# ==========================================================
# Meaning Operations
# ==========================================================

def create_meaning(meaning: Meaning) -> int:
    """
    Insert a new Meaning into the database.

    Returns
    -------
    int
        Newly generated meaning ID.
    """

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO meanings (
                entry_id,
                meaning_order,
                meaning,
                notes
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                meaning.entry_id,
                meaning.meaning_order,
                meaning.meaning,
                meaning.notes,
            ),
        )

        return cursor.lastrowid


def get_meanings_for_entry(entry_id: int) -> list[Meaning]:
    """
    Retrieve all meanings belonging to an entry.

    Results are ordered by their dictionary meaning order.
    """

    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT *
            FROM meanings
            WHERE entry_id = ?
            ORDER BY meaning_order
            """,
            (entry_id,),
        )

        rows = cursor.fetchall()

    return [row_to_meaning(row) for row in rows]


# ==========================================================
# List All Entries Operation (For GUI / Data Grids)
# ==========================================================

def get_all_entries() -> list[Entry]:
    """
    Retrieve all entries in the database ordered alphabetically
    by lemma and homograph index.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT *
            FROM entries
            ORDER BY lemma, homograph_index
            """
        )
        rows = cursor.fetchall()

    return [row_to_entry(row) for row in rows]


# ==========================================================
# Entry Update / Delete Operations
# ==========================================================

def update_entry(entry: Entry) -> bool:
    """
    Update an existing Entry.

    Returns
    -------
    bool
        True if a row was updated.
    """

    if entry.id is None:
        raise ValueError("Entry ID is required for update.")

    validate_provenance(entry.provenance)
    validate_classification(entry.classification)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE entries
            SET
                headword = ?,
                lemma = ?,
                homograph_index = ?,
                provenance = ?,
                classification = ?
            WHERE id = ?
            """,
            (
                entry.headword,
                entry.lemma,
                entry.homograph_index,
                entry.provenance,
                entry.classification,
                entry.id,
            ),
        )

        return cursor.rowcount > 0



def delete_entry(entry_id: int) -> bool:
    """
    Delete an Entry. Child records are removed automatically via CASCADE.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """
            DELETE FROM entries
            WHERE id = ?
            """,
            (entry_id,),
        )

        return cursor.rowcount > 0


# ==========================================================
# Meaning Update / Delete Operations
# ==========================================================

def update_meaning(meaning: Meaning) -> bool:
    """
    Update an existing Meaning.
    """
    if meaning.id is None:
        raise ValueError("Meaning ID is required for update.")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE meanings
            SET
                meaning_order = ?,
                meaning = ?,
                notes = ?
            WHERE id = ?
            """,
            (
                meaning.meaning_order,
                meaning.meaning,
                meaning.notes,
                meaning.id,
            ),
        )

        return cursor.rowcount > 0


def delete_meaning(meaning_id: int) -> bool:
    """
    Delete a Meaning.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """
            DELETE FROM meanings
            WHERE id = ?
            """,
            (meaning_id,),
        )

        return cursor.rowcount > 0


# ==========================================================
# Claim Update / Delete Operations
# ==========================================================

def update_claim(claim: Claim) -> bool:
    """
    Update an existing Claim.
    """
    if claim.id is None:
        raise ValueError("Claim ID is required for update.")

    validate_claim_status(claim.status)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE claims
            SET
                claim_text = ?,
                confidence = ?,
                evidence_completeness = ?,
                rationale = ?,
                status = ?
            WHERE id = ?
            """,
            (
                claim.claim_text,
                claim.confidence,
                claim.evidence_completeness,
                claim.rationale,
                claim.status,
                claim.id,
            ),
        )

        return cursor.rowcount > 0


def delete_claim(claim_id: int) -> bool:
    """
    Delete a Claim.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """
            DELETE FROM claims
            WHERE id = ?
            """,
            (claim_id,),
        )

        return cursor.rowcount > 0


# ==========================================================
# Research Question Operations
# ==========================================================

def create_research_question(rq: ResearchQuestion) -> int:
    """
    Insert a new ResearchQuestion into the database.

    Returns
    -------
    int
        Newly generated research question ID.
    """

    validate_research_question_status(rq.status)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO research_questions (
                entry_id,
                parent_question_id,
                question_text,
                status,
                resolution_summary
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                rq.entry_id,
                rq.parent_question_id,
                rq.question_text,
                rq.status,
                rq.resolution_summary,
            ),
        )

        return cursor.lastrowid


def get_research_questions_for_entry(entry_id: int) -> list[ResearchQuestion]:
    """
    Retrieve all research questions for an entry, ordered by ID.
    """

    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT *
            FROM research_questions
            WHERE entry_id = ?
            ORDER BY id
            """,
            (entry_id,),
        )

        rows = cursor.fetchall()

    return [row_to_research_question(row) for row in rows]


def update_research_question(rq: ResearchQuestion) -> bool:
    """
    Update an existing research question.

    Returns
    -------
    bool
        True if a row was updated.
    """

    if rq.id is None:
        raise ValueError("Research question ID is required for update.")

    validate_research_question_status(rq.status)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE research_questions
            SET
                entry_id = ?,
                parent_question_id = ?,
                question_text = ?,
                status = ?,
                resolution_summary = ?
            WHERE id = ?
            """,
            (
                rq.entry_id,
                rq.parent_question_id,
                rq.question_text,
                rq.status,
                rq.resolution_summary,
                rq.id,
            ),
        )

        return cursor.rowcount > 0


def update_research_question_status(
    question_id: int,
    status: str,
    resolution_summary: str | None = None,
) -> bool:
    """
    Update only the status and resolution summary of a research question.

    Returns
    -------
    bool
        True if a row was updated.
    """

    validate_research_question_status(status)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE research_questions
            SET
                status = ?,
                resolution_summary = ?
            WHERE id = ?
            """,
            (
                status,
                resolution_summary,
                question_id,
            ),
        )

        return cursor.rowcount > 0


def delete_research_question(question_id: int) -> bool:
    """
    Delete a research question.

    Returns
    -------
    bool
        True if a row was deleted.
    """

    with get_connection() as conn:
        cursor = conn.execute(
            """
            DELETE FROM research_questions
            WHERE id = ?
            """,
            (question_id,),
        )

        return cursor.rowcount > 0


# ==========================================================
# Question Relationship Operations
# ==========================================================

def row_to_question_relationship(row: sqlite3.Row) -> QuestionRelationship:
    """Convert a SQLite row into a QuestionRelationship dataclass."""
    return QuestionRelationship(
        id=row["id"],
        from_question_id=row["from_question_id"],
        to_question_id=row["to_question_id"],
        relationship_type=row["relationship_type"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def link_research_questions(rel: QuestionRelationship) -> int:
    """
    Link two research questions together in the research graph.

    Returns
    -------
    int
        Newly generated question relationship ID.
    """
    validate_question_relationship_type(rel.relationship_type)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO question_relationships (
                from_question_id,
                to_question_id,
                relationship_type
            )
            VALUES (?, ?, ?)
            """,
            (
                rel.from_question_id,
                rel.to_question_id,
                rel.relationship_type,
            ),
        )

        return cursor.lastrowid


def get_question_relationships(question_id: int) -> list[QuestionRelationship]:
    """
    Retrieve all relationship edges connected to or from a research question.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT *
            FROM question_relationships
            WHERE from_question_id = ? OR to_question_id = ?
            ORDER BY id
            """,
            (question_id, question_id),
        )

        rows = cursor.fetchall()

    return [row_to_question_relationship(row) for row in rows]


def update_question_relationship(rel: QuestionRelationship) -> bool:
    """
    Update an existing question relationship.

    Returns
    -------
    bool
        True if a row was updated.
    """
    if rel.id is None:
        raise ValueError("Question relationship ID is required for update.")

    validate_question_relationship_type(rel.relationship_type)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            UPDATE question_relationships
            SET
                from_question_id = ?,
                to_question_id = ?,
                relationship_type = ?
            WHERE id = ?
            """,
            (
                rel.from_question_id,
                rel.to_question_id,
                rel.relationship_type,
                rel.id,
            ),
        )

        return cursor.rowcount > 0


def unlink_research_questions(relationship_id: int) -> bool:
    """
    Remove a link between two research questions.

    Returns
    -------
    bool
        True if a row was deleted.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """
            DELETE FROM question_relationships
            WHERE id = ?
            """,
            (relationship_id,),
        )

        return cursor.rowcount > 0


# ==========================================================
# Research Note Operations (Append-Only Journal)
# ==========================================================

def row_to_research_note(row: sqlite3.Row) -> ResearchNote:
    """Convert a SQLite row into a ResearchNote dataclass."""
    return ResearchNote(
        id=row["id"],
        entry_id=row["entry_id"],
        note_text=row["note_text"],
        created_at=row["created_at"],
    )


def add_research_note(note: ResearchNote) -> int:
    """
    Add a timestamped research progress note to an entry.

    Returns
    -------
    int
        Newly generated research note ID.
    """
    if not note.note_text.strip():
        raise ValueError("Note text cannot be empty.")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO research_notes (
                entry_id,
                note_text
            )
            VALUES (?, ?)
            """,
            (
                note.entry_id,
                note.note_text,
            ),
        )

        return cursor.lastrowid


def get_research_notes_for_entry(entry_id: int) -> list[ResearchNote]:
    """
    Retrieve all research notes for an entry, ordered by creation time.
    """
    with get_connection() as conn:
        cursor = conn.execute(
            """
            SELECT *
            FROM research_notes
            WHERE entry_id = ?
            ORDER BY created_at ASC
            """,
            (entry_id,),
        )

        rows = cursor.fetchall()

    return [row_to_research_note(row) for row in rows]