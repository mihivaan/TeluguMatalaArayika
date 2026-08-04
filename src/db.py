"""
తెలుగు మాటల అరయిక (TLRE)

Database Bootstrap & Infrastructure

Version: 0.1.0
Reference Point: RP-005.1

Initializes and manages SQLite database connections.
"""

from pathlib import Path
import sqlite3
import sys

# ==========================================================
# Project Paths (Single Source of Truth)
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SCHEMA_PATH = PROJECT_ROOT / "schema.sql"

DATA_DIRECTORY = PROJECT_ROOT / "data"

DATABASE_PATH = DATA_DIRECTORY / "tlre.db"


def get_project_root() -> Path:
    """
    Return the root directory of the TLRE project.
    """
    return PROJECT_ROOT


def get_connection() -> sqlite3.Connection:
    """
    Create and return a configured SQLite connection.

    Configuration:
    - Foreign keys enabled (PRAGMA foreign_keys = ON;).
    - sqlite3.Row row factory enabled (dictionary-style column access).

    Returns
    -------
    sqlite3.Connection
    """
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """
    Create (or re-initialize) the SQLite database
    using the schema.sql script.
    """
    DATA_DIRECTORY.mkdir(exist_ok=True)

    if not SCHEMA_PATH.exists():
        print(f"ERROR: schema.sql not found:\n{SCHEMA_PATH}")
        sys.exit(1)

    print("========================================")
    print("TLRE Database Initialization")
    print("========================================")
    print(f"Project : {PROJECT_ROOT}")
    print(f"Schema  : {SCHEMA_PATH}")
    print(f"Database: {DATABASE_PATH}")
    print()

    try:
        with get_connection() as connection:
            with SCHEMA_PATH.open(mode="r", encoding="utf-8") as schema_file:
                schema_sql = schema_file.read()

            connection.executescript(schema_sql)

        print("Database initialized successfully.")
        print(f"SQLite database created at:\n{DATABASE_PATH}")

    except sqlite3.Error as error:
        print("SQLite Error:")
        print(error)
        sys.exit(1)

    except OSError as error:
        print("File Error:")
        print(error)
        sys.exit(1)


def main() -> None:
    initialize_database()


if __name__ == "__main__":
    main()