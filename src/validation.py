"""
తెలుగు మాటల అరయిక (TLRE)

Application Validation

Version: 0.1.0
Reference Point: RP-006

Centralized validation functions for application-level
input checking.

These functions validate values before they reach the
database layer.
"""

from src.constants import (
    PROVENANCE,
    CLASSIFICATION,
    RELATIONSHIP_TYPES,
    EVIDENCE_TYPES,
    EVIDENCE_ROLES,
    CLAIM_STATUSES,
    RESEARCH_QUESTION_STATUSES,
    QUESTION_RELATIONSHIP_TYPES,
)


def _validate_choice(value: str, allowed: tuple[str, ...], field_name: str) -> str:
    """
    Validate that a value belongs to an allowed vocabulary.

    Parameters
    ----------
    value:
        The value to validate.

    allowed:
        The tuple containing the allowed values.

    field_name:
        Human-readable field name used in error messages.

    Returns
    -------
    str
        The validated value.

    Raises
    ------
    ValueError
        If the value is not permitted.
    """

    if value not in allowed:
        allowed_values = ", ".join(allowed)

        raise ValueError(
            f"Invalid {field_name!r}: {value!r}\n"
            f"Allowed values: {allowed_values}"
        )

    return value


def validate_provenance(value: str) -> str:
    """Validate entry provenance."""
    return _validate_choice(value, PROVENANCE, "provenance")


def validate_classification(value: str) -> str:
    """Validate entry classification."""
    return _validate_choice(value, CLASSIFICATION, "classification")


def validate_relationship_type(value: str) -> str:
    """Validate relationship type."""
    return _validate_choice(value, RELATIONSHIP_TYPES, "relationship type")


def validate_evidence_type(value: str) -> str:
    """Validate evidence type."""
    return _validate_choice(value, EVIDENCE_TYPES, "evidence type")


def validate_evidence_role(value: str) -> str:
    """Validate evidence role."""
    return _validate_choice(value, EVIDENCE_ROLES, "evidence role")


def validate_claim_status(value: str) -> str:
    """Validate claim status."""
    return _validate_choice(value, CLAIM_STATUSES, "claim status")


def validate_research_question_status(value: str) -> str:
    """Validate research question status."""
    return _validate_choice(value, RESEARCH_QUESTION_STATUSES, "research question status")


def validate_question_relationship_type(value: str) -> str:
    """Validate question relationship type."""
    return _validate_choice(value, QUESTION_RELATIONSHIP_TYPES, "question relationship type")