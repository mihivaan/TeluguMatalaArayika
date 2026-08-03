# తెలుగు మాటల అరయిక (TLRE)

**Telugu Linguistic Research Environment**

---

## Overview

తెలుగు మాటల అరయిక (TLRE) is an evidence-based linguistic research environment for the systematic investigation of Telugu words.

TLRE is **not merely a dictionary**.

It is designed to support:

- Historical lexical research
- Etymological investigation
- Claims-based evidence management
- Comparative Dravidian analysis
- Disciplined terminology innovation
- Transparent documentation of competing linguistic theories

Every conclusion remains traceable to its supporting evidence.

---

## Project Goals

The primary objectives of TLRE are:

- Investigate Telugu vocabulary objectively.
- Distinguish evidence from interpretation.
- Preserve competing linguistic hypotheses.
- Support reproducible research.
- Assist in disciplined lexical innovation where necessary.
- Build a long-term research environment rather than a static dictionary.

---

## Research Philosophy

TLRE follows several guiding principles:

- Evidence before opinion.
- Claims before conclusions.
- Every conclusion is revisable.
- Unknown is an acceptable result.
- Creativity must be disciplined.
- Historical research and lexical innovation complement one another.

---

## Technology Stack

Version 1.0 intentionally minimizes dependencies.

- Python (Standard Library)
- SQLite
- Git
- Ubuntu WSL
- VS Code

No third-party Python packages are required during the initial implementation.

---

## Local Development Environment

Operating System

Ubuntu running under Windows Subsystem for Linux (WSL)

Python

```
python
pip
```

Virtual Environment

```
source .venv/bin/activate
```

---

## Repository Layout

```text
TeluguMatalaArayika/

├── .venv/
├── data/
│   └── tlre.db
│
├── docs/
│   └── SRS.md
│
├── src/
│   ├── __init__.py
│   ├── db.py
│   ├── models.py
│   ├── queries.py
│   └── cli.py
│
├── tests/
│
├── schema.sql
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Initial Setup

Create and activate the virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Initialize Git.

```bash
git init
```

Generate the SQLite database.

```bash
python src/db.py
```

---

## Development Philosophy

TLRE is developed incrementally.

Every implementation step should correspond to an approved design decision documented in the Software Requirements Specification (SRS).

Major architectural changes should be discussed before implementation.

---

## License

To be determined.

---

## Status

Current Phase

Phase 1 — Implementation & Python Foundations

Current Architecture

RP-006 Approved

Current Database Design

RP-005.1 Approved