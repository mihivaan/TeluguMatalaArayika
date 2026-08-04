"""
తెలుగు మాటల అరయిక (TLRE)

Domain Models

Version: 0.1.0
Reference Point: RP-006

Plain Python dataclasses representing the core linguistic
entities used throughout the application.

These classes intentionally contain no database logic.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# ==========================================================
# Entry
# ==========================================================

@dataclass(slots=True)
class Entry:
    id: Optional[int] = None

    headword: str = ""
    lemma: str = ""
    homograph_index: int = 0

    provenance: str = "Unknown"
    classification: str = "Unknown"

    research_question: Optional[str] = None
    notes: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ==========================================================
# Meaning
# ==========================================================

@dataclass(slots=True)
class Meaning:
    id: Optional[int] = None

    entry_id: int = 0

    meaning_order: int = 1
    meaning: str = ""

    notes: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ==========================================================
# Claim
# ==========================================================

@dataclass(slots=True)
class Claim:
    id: Optional[int] = None

    entry_id: int = 0
    meaning_id: Optional[int] = None

    claim_text: str = ""

    confidence: float = 1.0
    evidence_completeness: float = 0.0

    rationale: Optional[str] = None

    status: str = "Draft"

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ==========================================================
# Source
# ==========================================================

@dataclass(slots=True)
class Source:
    id: Optional[int] = None

    name: str = ""

    author: Optional[str] = None
    publication_year: Optional[int] = None

    source_type: Optional[str] = None
    description: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ==========================================================
# Citation
# ==========================================================

@dataclass(slots=True)
class Citation:
    id: Optional[int] = None

    source_id: int = 0

    page: Optional[str] = None
    column_ref: Optional[str] = None
    line_ref: Optional[str] = None
    paragraph_ref: Optional[str] = None

    citation_text: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ==========================================================
# Evidence
# ==========================================================

@dataclass(slots=True)
class Evidence:
    id: Optional[int] = None

    claim_id: int = 0
    citation_id: int = 0

    evidence_type: str = "Unknown"
    evidence_role: str = "Supports"

    evidence_text: str = ""

    notes: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ==========================================================
# Example
# ==========================================================

@dataclass(slots=True)
class Example:
    id: Optional[int] = None

    entry_id: int = 0
    source_id: Optional[int] = None

    example_text: str = ""

    translation: Optional[str] = None
    context: Optional[str] = None
    dialect: Optional[str] = None

    notes: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ==========================================================
# Relationship
# ==========================================================

@dataclass(slots=True)
class Relationship:
    id: Optional[int] = None

    from_entry_id: int = 0
    to_entry_id: int = 0

    relationship_type: str = ""

    confidence: float = 1.0

    notes: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ==========================================================
# Audit Log
# ==========================================================

@dataclass(slots=True)
class AuditLog:
    id: Optional[int] = None

    entity_type: str = ""
    entity_id: int = 0

    change_summary: str = ""

    created_at: Optional[datetime] = None