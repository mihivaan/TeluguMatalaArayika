"""
తెలుగు మాటల అరయిక (TLRE)

Command-Line Interface

Version: 0.1.0
Reference Point: RP-006

Interactive terminal interface for the Telugu Linguistic
Research Environment.

This module provides a simple command-line interface while
keeping all database access inside src.queries.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path so 'src.' imports work when script is run directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models import Entry, Meaning, Claim
from src.constants import (
    PROVENANCE,
    CLASSIFICATION,
    CLAIM_STATUSES,
)
from src.queries import (
    find_entries_by_lemma,
    create_entry,
    create_meaning,
    add_claim,
    get_meanings_for_entry,
    get_claims_for_entry,
)


# ==========================================================
# Helper Functions
# ==========================================================

def prompt_choice(prompt_text: str, choices: tuple[str, ...]) -> str:
    """
    Display a numbered menu and return the selected value.
    """

    while True:
        print()
        print(prompt_text)

        for index, choice in enumerate(choices, start=1):
            print(f"  {index}. {choice}")

        selection = input("Enter choice number: ").strip()

        if not selection.isdigit():
            print("Please enter a valid number.")
            continue

        selection_number = int(selection)

        if 1 <= selection_number <= len(choices):
            return choices[selection_number - 1]

        print("Choice out of range. Please try again.")


def display_entry_details(entry: Entry) -> None:
    """
    Display an entry together with its meanings and
    active claims.
    """

    print("=" * 70)
    print(f"Entry ID           : {entry.id}")
    print(f"Headword           : {entry.headword}")
    print(f"Lemma              : {entry.lemma}")
    print(f"Homograph Index    : {entry.homograph_index}")
    print(f"Provenance         : {entry.provenance}")
    print(f"Classification     : {entry.classification}")

    if entry.research_question:
        print(f"Research Question  : {entry.research_question}")

    if entry.notes:
        print(f"Notes              : {entry.notes}")

    print()

    meanings = get_meanings_for_entry(entry.id)

    print("Meanings")
    print("--------")

    if meanings:
        for meaning in meanings:
            print(
                f"{meaning.meaning_order}. "
                f"{meaning.meaning}"
            )
    else:
        print("(No meanings recorded)")

    print()

    claims = get_claims_for_entry(
        entry.id,
        status="Active",
    )

    print("Active Claims")
    print("-------------")

    if claims:
        for claim in claims:
            print(f"- {claim.claim_text}")
            print(f"  Confidence : {claim.confidence:.2f}")

            if claim.rationale:
                print(f"  Rationale  : {claim.rationale}")

            print()
    else:
        print("(No active claims)")

    print("=" * 70)
    print()


# ==========================================================
# Search Workflow
# ==========================================================

def search_lemma_workflow() -> None:
    """
    Search for entries using a lemma.
    """

    try:
        print()
        lemma = input("Enter lemma: ").strip()

        if not lemma:
            print("Lemma cannot be empty.")
            return

        entries = find_entries_by_lemma(lemma)

        if not entries:
            print("No matching entries found.")
            return

        print()
        print(f"Found {len(entries)} matching entr{'y' if len(entries) == 1 else 'ies'}.\n")

        for entry in entries:
            display_entry_details(entry)

    except ValueError as exc:
        print(f"Validation error: {exc}")

    except (KeyboardInterrupt, EOFError):
        print("\nSearch cancelled.")


# ==========================================================
# Create Entry Workflow
# ==========================================================

def create_entry_workflow() -> None:
    """
    Interactively create a new dictionary entry.
    """

    try:
        print()
        print("Create New Entry")
        print("-" * 40)

        headword = input("Headword: ").strip()
        lemma = input("Lemma: ").strip()

        homograph_input = input(
            "Homograph Index [0]: "
        ).strip()

        homograph_index = (
            int(homograph_input)
            if homograph_input
            else 0
        )

        provenance = prompt_choice(
            "Select Provenance",
            PROVENANCE,
        )

        classification = prompt_choice(
            "Select Classification",
            CLASSIFICATION,
        )

        research_question = input(
            "Research Question (optional): "
        ).strip()

        notes = input(
            "Notes (optional): "
        ).strip()

        entry = Entry(
            headword=headword,
            lemma=lemma,
            homograph_index=homograph_index,
            provenance=provenance,
            classification=classification,
            research_question=research_question or None,
            notes=notes or None,
        )

        entry_id = create_entry(entry)

        print()
        print(f"Entry created successfully (ID: {entry_id}).")

    except ValueError as exc:
        print(f"Validation error: {exc}")

    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled.")


# ==========================================================
# Add Meaning Workflow
# ==========================================================

def add_meaning_workflow() -> None:
    """
    Interactively add a meaning to an existing entry.
    """

    try:
        print()
        print("Add Meaning")
        print("-" * 40)

        entry_id = int(
            input("Entry ID: ").strip()
        )

        order_input = input(
            "Meaning Order [1]: "
        ).strip()

        meaning_order = (
            int(order_input)
            if order_input
            else 1
        )

        meaning_text = input(
            "Meaning: "
        ).strip()

        notes = input(
            "Notes (optional): "
        ).strip()

        meaning = Meaning(
            entry_id=entry_id,
            meaning_order=meaning_order,
            meaning=meaning_text,
            notes=notes or None,
        )

        meaning_id = create_meaning(meaning)

        print()
        print(
            f"Meaning created successfully (ID: {meaning_id})."
        )

    except ValueError as exc:
        print(f"Validation error: {exc}")

    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled.")


# ==========================================================
# Add Claim Workflow
# ==========================================================

def add_claim_workflow() -> None:
    """
    Interactively add a claim to an entry.
    """

    try:
        print()
        print("Add Claim")
        print("-" * 40)

        entry_id = int(
            input("Entry ID: ").strip()
        )

        claim_text = input(
            "Claim Text: "
        ).strip()

        confidence_input = input(
            "Confidence [1.0]: "
        ).strip()

        confidence = (
            float(confidence_input)
            if confidence_input
            else 1.0
        )

        rationale = input(
            "Rationale (optional): "
        ).strip()

        status = prompt_choice(
            "Select Claim Status",
            CLAIM_STATUSES,
        )

        claim = Claim(
            entry_id=entry_id,
            claim_text=claim_text,
            confidence=confidence,
            rationale=rationale or None,
            status=status,
        )

        claim_id = add_claim(claim)

        print()
        print(
            f"Claim created successfully (ID: {claim_id})."
        )

    except ValueError as exc:
        print(f"Validation error: {exc}")

    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled.")


# ==========================================================
# Main Menu
# ==========================================================

def print_menu() -> None:
    """
    Display the main application menu.
    """

    print()
    print("=" * 70)
    print("తెలుగు మాటల అరయిక (TLRE)")
    print("=" * 70)
    print("1. Search Entry by Lemma")
    print("2. Create New Entry")
    print("3. Add Meaning to Entry")
    print("4. Add Claim to Entry")
    print("5. Exit")
    print()


# ==========================================================
# Main Application
# ==========================================================

def main() -> None:
    """
    Run the interactive command-line interface.
    """

    while True:
        print_menu()

        try:
            choice = input(
                "Select an option: "
            ).strip()

            if choice == "1":
                search_lemma_workflow()

            elif choice == "2":
                create_entry_workflow()

            elif choice == "3":
                add_meaning_workflow()

            elif choice == "4":
                add_claim_workflow()

            elif choice == "5":
                print("Goodbye.")
                break

            else:
                print("Invalid menu choice.")

        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye.")
            break


if __name__ == "__main__":
    main()