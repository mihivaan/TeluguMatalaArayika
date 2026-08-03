# తెలుగు మాటల అరయిక (TLRE)

# Software Requirements Specification

---

Version: 0.1.0

Status: Frozen (Phase 0)

Last Updated: 2026-08-03

---

# Introduction

తెలుగు మాటల అరయిక (TLRE) is an evidence-driven linguistic research environment designed to investigate Telugu vocabulary, historical development, etymology, lexical innovation, and comparative Dravidian linguistics.

The objective is not merely to store words, but to preserve the complete research process leading to linguistic conclusions.

---

# RP-001 — Research Methodology

TLRE follows an evidence-first methodology.

General workflow:

Concept

↓

Semantic analysis

↓

Historical investigation

↓

Evidence collection

↓

Comparative analysis

↓

Morphological analysis

↓

Semantic evaluation

↓

Proposal (if necessary)

↓

Validation

↓

Documentation

Research priorities:

- Evidence before preference.
- Transparent reasoning.
- Reproducibility.
- Revision when stronger evidence appears.

---

# RP-002 — Research Philosophy

TLRE recognises three complementary activities:

1. Investigation
2. Reconstruction
3. Disciplined lexical innovation

Innovation is considered a legitimate component of language development when:

- clearly documented,
- linguistically justified,
- morphologically sound,
- historically informed,
- transparently identified.

TLRE distinguishes:

- Facts
- Claims
- Evidence
- Hypotheses
- Proposals

No conclusion is permanent.

---

# RP-003 — Domain Model

Core entities:

- Entry
- Meaning
- Claim
- Source
- Citation
- Evidence
- Example
- Relationship
- Audit Log

Claims are the primary unit of reasoning.

Evidence always supports or contradicts Claims rather than Entries directly.

Multiple competing Claims may coexist.

---

## Claims-Based Evidence Structure

Entry

↓

Meaning (optional)

↓

Claim

↓

Evidence

↓

Citation

↓

Source

This model allows competing theories to exist without corrupting the underlying lexical record.

---

# RP-004 — Research Workflow

Stage 1

Question & Scope

- Define research objective.
- Define semantic scope.

Stage 2

Investigation & Evidence Collection

- Search existing Entries.
- Record Claims.
- Attach Evidence.
- Record Citations.

Stage 3

Decision & Provenance

Possible outcomes:

- Attested
- Revived
- Reconstructed
- Coined
- Experimental

Stage 4

Validation & Sentence Testing

- Usage examples
- Semantic collision testing
- Morphological validation
- Phonological validation
- Productivity analysis

Every investigation concludes with documented rationale.

---

# RP-005.1 — Physical Database Design

SQLite

Core tables:

- entries
- meanings
- claims
- sources
- citations
- evidence
- examples
- relationships
- audit_logs

Every table includes:

- created_at
- updated_at

Automatic update triggers maintain modification timestamps.

The schema enforces integrity through:

- Primary Keys
- Foreign Keys
- CHECK constraints
- Indexes
- Referential integrity

---

# RP-006 — Project Architecture

Repository

```text
TeluguMatalaArayika/

data/
docs/
src/
tests/

schema.sql
README.md
requirements.txt
```

Source Modules

db.py

Database initialization and management.

models.py

Python representations of domain entities.

queries.py

Database operations.

cli.py

Command-line interface for testing and early interaction.

The architecture separates:

Presentation

↓

Application Logic

↓

Database

↓

SQLite

Future graphical interfaces (PySide6) will reuse the same application logic.

---

# Project Principles

Evidence over preference.

Truth over ideology.

Reproducibility.

Historical traceability.

Long-term maintainability.

Incremental development.

No unnecessary dependencies.

Every significant decision should be reviewable.

---

# Current Status

Phase

Phase 1 — Implementation & Python Foundations

Reference Points

- RP-001
- RP-002
- RP-003
- RP-004
- RP-005.1
- RP-006

Status

Frozen

Implementation begins after this document.