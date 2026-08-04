"""
తెలుగు మాటల అరయిక (TLRE)

Database Bootstrap

Version: 0.1.0
Reference Point: RP-005.1

Initializes the SQLite database using schema.sql.
"""

from pathlib import Path
import sqlite3
import sys


def get_project_root() -> Path:
    """
    Returns the root directory of the TLRE project.

    Since this file lives inside src/,
    its parent directory is the project root.
    """
    return Path(__file__).resolve().parent.parent


def initialize_database() -> None:
    """
    Creates (or updates) the SQLite database
    using the schema.sql script.
    """

    project_root = get_project_root()

    schema_path = project_root / "schema.sql"

    data_directory = project_root / "data"

    database_path = data_directory / "tlre.db"

    data_directory.mkdir(exist_ok=True)

    if not schema_path.exists():
        print(f"ERROR: schema.sql not found:\n{schema_path}")
        sys.exit(1)

    print("========================================")
    print("TLRE Database Initialization")
    print("========================================")
    print(f"Project : {project_root}")
    print(f"Schema  : {schema_path}")
    print(f"Database: {database_path}")
    print()

    try:

        with sqlite3.connect(database_path) as connection:

            connection.execute("PRAGMA foreign_keys = ON;")

            with schema_path.open(
                mode="r",
                encoding="utf-8"
            ) as schema_file:

                schema_sql = schema_file.read()

            connection.executescript(schema_sql)

        print("Database initialized successfully.")
        print(f"SQLite database created at:\n{database_path}")

    except sqlite3.Error as error:

        print("SQLite Error")
        print(error)
        sys.exit(1)

    except OSError as error:

        print("File Error")
        print(error)
        sys.exit(1)


def main() -> None:
    initialize_database()


if __name__ == "__main__":
    main()