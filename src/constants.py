"""
తెలుగు మాటల అరయిక (TLRE)

Application Constants

Version: 0.1.0
Reference Point: RP-005.1

Centralized application vocabulary.

These values mirror the SQLite CHECK constraints and
should be used throughout the application instead of
hard-coded string literals.
"""

# ==========================================================
# Entry Provenance
# ==========================================================

PROVENANCE = (
    "Attested",
    "Revived",
    "Reconstructed",
    "Coined",
    "Experimental",
    "Unknown",
)

# ==========================================================
# Entry Classification
# ==========================================================

CLASSIFICATION = (
    "Inherited Dravidian",
    "Native Telugu Innovation",
    "Native Origin Uncertain",
    "Shared Dravidian",
    "Sanskrit Borrowing",
    "Prakrit Borrowing",
    "Pali Borrowing",
    "Tamil Borrowing",
    "Kannada Borrowing",
    "Malayalam Borrowing",
    "Gondi Borrowing",
    "Kui Borrowing",
    "Kuvi Borrowing",
    "Persian Borrowing",
    "Arabic Borrowing",
    "Hebrew Borrowing",
    "Aramaic Borrowing",
    "Portuguese Borrowing",
    "English Borrowing",
    "Hybrid Formation",
    "Unknown",
    "Disputed",
)

# ==========================================================
# Relationship Types
# ==========================================================

RELATIONSHIP_TYPES = (
    "derived_from",
    "compound_of",
    "cognate_of",
    "variant_of",
    "dialect_variant",
    "synonym_of",
    "antonym_of",
    "semantic_shift_from",
    "influence_of",
    "translation_of",
    "reconstructed_from",
)

# ==========================================================
# Evidence Types
# ==========================================================

EVIDENCE_TYPES = (
    "Dictionary",
    "Literature",
    "Fieldwork",
    "Inscription",
    "Oral History",
    "Comparative",
    "Unknown",
)

# ==========================================================
# Evidence Roles
# ==========================================================

EVIDENCE_ROLES = (
    "Supports",
    "Contradicts",
    "Background",
)

# ==========================================================
# Claim Status
# ==========================================================

CLAIM_STATUSES = (
    "Active",
    "Rejected",
    "Superseded",
    "Draft",
)

# ==========================================================
# Research Question Statuses
# ==========================================================

RESEARCH_QUESTION_STATUSES = (
    "Open",
    "In Progress",
    "Partially Resolved",
    "Fully Resolved",
    "Superseded",
    "Abandoned",
    "Unresolved",
)

# ==========================================================
# Question Relationship Types
# ==========================================================

QUESTION_RELATIONSHIP_TYPES = (
    "linked_to",
    "derived_from",
    "merged_with",
    "depends_on",
)