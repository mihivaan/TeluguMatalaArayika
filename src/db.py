"""
తెలుగు మాటల అరయిక (TLRE)

Database Bootstrap & Infrastructure

Version: 0.2.1
Reference Point: RP-005.1

Initializes and manages SQLite database connections, Write-Ahead Logging (WAL),
and automated rolling backups.
"""

from __future__ import annotations

import datetime
from pathlib import Path
import shutil
import sqlite3
import sys

# ==========================================================
# Project Paths (Single Source of Truth)
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = PROJECT_ROOT / "schema.sql"
DATA_DIRECTORY = PROJECT_ROOT / "data"
DATABASE_PATH = DATA_DIRECTORY / "tlre.db"
BACKUP_DIRECTORY = DATA_DIRECTORY / "backups"


def get_project_root() -> Path:
    """
    Return the root directory of the TLRE project.
    """
    return PROJECT_ROOT


def backup_database(max_backups: int = 10) -> Path | None:
    """
    Create a timestamped backup of tlre.db inside data/backups/
    and retain the most recent 'max_backups' files.
    """
    if not DATABASE_PATH.exists():
        return None

    BACKUP_DIRECTORY.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"tlre_backup_{timestamp}.db"
    backup_path = BACKUP_DIRECTORY / backup_filename

    try:
        shutil.copy2(DATABASE_PATH, backup_path)

        # Maintain rolling limit of max_backups
        backups = sorted(BACKUP_DIRECTORY.glob("tlre_backup_*.db"))
        if len(backups) > max_backups:
            for old_backup in backups[:-max_backups]:
                old_backup.unlink(missing_ok=True)

        return backup_path
    except OSError as error:
        print(f"Backup warning: Could not create backup copy: {error}")
        return None


def restore_latest_backup() -> bool:
    """
    Restore tlre.db from the most recent backup in data/backups/.
    """
    if not BACKUP_DIRECTORY.exists():
        return False

    backups = sorted(BACKUP_DIRECTORY.glob("tlre_backup_*.db"))
    if not backups:
        return False

    latest_backup = backups[-1]
    try:
        shutil.copy2(latest_backup, DATABASE_PATH)
        print(f"Database successfully restored from: {latest_backup.name}")
        return True
    except OSError as error:
        print(f"Restore error: {error}")
        return False


def get_connection() -> sqlite3.Connection:
    """
    Create and return a configured SQLite connection.

    Configuration:
    - Foreign keys enabled (PRAGMA foreign_keys = ON;).
    - Write-Ahead Logging enabled (PRAGMA journal_mode = WAL;).
    - sqlite3.Row row factory enabled (dictionary-style column access).
    """
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.execute("PRAGMA journal_mode = WAL;")
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database() -> None:
    """
    Create (or re-initialize) the SQLite database using schema.sql.
    Automatically creates a safety backup if an existing database is found.
    """
    DATA_DIRECTORY.mkdir(exist_ok=True)

    # Take safety backup before initializing
    if DATABASE_PATH.exists():
        backup_database()

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
        print(f"SQLite database ready at:\n{DATABASE_PATH}")

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