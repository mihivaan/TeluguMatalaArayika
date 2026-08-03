-- ============================================================================
-- తెలుగు మాటల అరయిక (TLRE)
-- Telugu Linguistic Research Environment
--
-- File           : schema.sql
-- Version        : 0.1.0
-- Reference Point: RP-005.1
-- Last Updated   : 2026-08-03
--
-- Description:
--     Physical SQLite database schema for TLRE.
--
-- Notes:
--     • SQLite 3.x
--     • Foreign key enforcement enabled.
--     • All timestamps stored as UTC using CURRENT_TIMESTAMP.
--     • Every table includes created_at and updated_at.
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ============================================================================
-- TABLE: entries
--
-- Represents a lexical item (word, compound, idiom, particle, etc.).
--
-- The combination (lemma, homograph_index) uniquely identifies an entry.
--
-- Example:
--
-- lemma = చాలు
--
-- homograph_index = 1
-- homograph_index = 2
--
-- This allows multiple homographs sharing the same canonical lemma.
-- ============================================================================

CREATE TABLE entries (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    headword TEXT NOT NULL,

    lemma TEXT NOT NULL,

    homograph_index INTEGER NOT NULL DEFAULT 0
        CHECK (homograph_index >= 0),

    provenance TEXT NOT NULL
        CHECK (
            provenance IN (
                'Attested',
                'Revived',
                'Reconstructed',
                'Coined',
                'Experimental',
                'Unknown'
            )
        ),

    classification TEXT NOT NULL
        CHECK (
            classification IN (
                'Inherited Dravidian',
                'Native Telugu Innovation',
                'Native Origin Uncertain',
                'Shared Dravidian',
                'Sanskrit Borrowing',
                'Prakrit Borrowing',
                'Pali Borrowing',
                'Tamil Borrowing',
                'Kannada Borrowing',
                'Malayalam Borrowing',
                'Gondi Borrowing',
                'Kui Borrowing',
                'Kuvi Borrowing',
                'Persian Borrowing',
                'Arabic Borrowing',
                'Hebrew Borrowing',
                'Aramaic Borrowing',
                'Portuguese Borrowing',
                'English Borrowing',
                'Hybrid Formation',
                'Unknown',
                'Disputed'
            )
        ),

    research_question TEXT,

    notes TEXT,

    created_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (lemma, homograph_index)
);

-- ============================================================================
-- TABLE: meanings
--
-- Stores individual semantic meanings (polysemy).
--
-- One Entry
--      ↓
-- Many Meanings
--
-- meaning_order preserves dictionary ordering.
-- ============================================================================

CREATE TABLE meanings (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    entry_id INTEGER NOT NULL,

    meaning_order INTEGER NOT NULL DEFAULT 1
        CHECK (meaning_order >= 1),

    meaning TEXT NOT NULL,

    notes TEXT,

    created_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (entry_id)
        REFERENCES entries(id)
        ON DELETE CASCADE
);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_entries_headword
ON entries(headword);

CREATE INDEX idx_entries_lemma
ON entries(lemma);

CREATE INDEX idx_entries_classification
ON entries(classification);

CREATE INDEX idx_meanings_entry
ON meanings(entry_id);

CREATE INDEX idx_meanings_order
ON meanings(entry_id, meaning_order);

-- ============================================================================
-- TABLE: claims
--
-- Represents an individual research assertion.
--
-- Claims are the fundamental unit of reasoning in TLRE.
--
-- A Claim always belongs to an Entry.
--
-- A Claim may optionally belong to a specific Meaning,
-- allowing semantic precision while still supporting
-- Entry-level claims (e.g., etymology).
-- ============================================================================

CREATE TABLE claims (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    entry_id INTEGER NOT NULL,

    meaning_id INTEGER,

    claim_text TEXT NOT NULL,

    confidence REAL DEFAULT 1.0
        CHECK (
            confidence >= 0.0
            AND confidence <= 1.0
        ),

    evidence_completeness REAL DEFAULT 0.0
        CHECK (
            evidence_completeness >= 0.0
            AND evidence_completeness <= 1.0
        ),

    rationale TEXT,

    status TEXT NOT NULL DEFAULT 'Draft'
        CHECK (
            status IN (
                'Active',
                'Rejected',
                'Superseded',
                'Draft'
            )
        ),

    created_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (entry_id)
        REFERENCES entries(id)
        ON DELETE CASCADE,

    FOREIGN KEY (meaning_id)
        REFERENCES meanings(id)
        ON DELETE SET NULL
);

-- ============================================================================
-- TABLE: sources
--
-- Stores unique bibliographic sources,
-- field informants,
-- manuscripts,
-- inscriptions,
-- journals,
-- websites,
-- and other research sources.
--
-- Source metadata should never be duplicated.
-- ============================================================================

CREATE TABLE sources (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT NOT NULL UNIQUE,

    author TEXT,

    publication_year INTEGER,

    source_type TEXT,

    description TEXT,

    created_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: citations
--
-- Represents a precise location within a Source.
--
-- Examples:
--
-- page
-- column
-- paragraph
-- line
--
-- Multiple citations may belong to the same Source.
-- ============================================================================

CREATE TABLE citations (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    source_id INTEGER NOT NULL,

    page TEXT,

    column_ref TEXT,

    line_ref TEXT,

    paragraph_ref TEXT,

    citation_text TEXT,

    created_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (source_id)
        REFERENCES sources(id)
        ON DELETE CASCADE
);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_claims_entry
ON claims(entry_id);

CREATE INDEX idx_claims_meaning
ON claims(meaning_id);

CREATE INDEX idx_claims_status
ON claims(status);

CREATE INDEX idx_sources_name
ON sources(name);

CREATE INDEX idx_sources_type
ON sources(source_type);

CREATE INDEX idx_citations_source
ON citations(source_id);

CREATE INDEX idx_citations_location
ON citations(
    source_id,
    page,
    column_ref,
    line_ref,
    paragraph_ref
);


-- ============================================================================
-- TABLE: evidence
--
-- Links Claims to Citations.
--
-- Evidence is classified according to its role:
--
-- Supports
-- Contradicts
-- Background
--
-- This allows competing theories to coexist while maintaining
-- explicit reasoning.
-- ============================================================================

CREATE TABLE evidence (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    claim_id INTEGER NOT NULL,

    citation_id INTEGER NOT NULL,

    evidence_type TEXT NOT NULL DEFAULT 'Unknown'
        CHECK (
            evidence_type IN (
                'Dictionary',
                'Literature',
                'Fieldwork',
                'Inscription',
                'Oral History',
                'Comparative',
                'Unknown'
            )
        ),

    evidence_role TEXT NOT NULL DEFAULT 'Supports'
        CHECK (
            evidence_role IN (
                'Supports',
                'Contradicts',
                'Background'
            )
        ),

    evidence_text TEXT NOT NULL,

    notes TEXT,

    created_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (claim_id)
        REFERENCES claims(id)
        ON DELETE CASCADE,

    FOREIGN KEY (citation_id)
        REFERENCES citations(id)
        ON DELETE CASCADE
);

-- ============================================================================
-- TABLE: examples
--
-- Stores real-world usage examples.
--
-- Examples support:
--
-- • sentence testing
-- • dialect studies
-- • validation
-- • literary citations
-- ============================================================================

CREATE TABLE examples (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    entry_id INTEGER NOT NULL,

    source_id INTEGER,

    example_text TEXT NOT NULL,

    translation TEXT,

    context TEXT,

    dialect TEXT,

    notes TEXT,

    created_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (entry_id)
        REFERENCES entries(id)
        ON DELETE CASCADE,

    FOREIGN KEY (source_id)
        REFERENCES sources(id)
        ON DELETE SET NULL
);

-- ============================================================================
-- TABLE: relationships
--
-- Directed relationships between Entries.
--
-- This implements the lexical knowledge graph.
-- ============================================================================

CREATE TABLE relationships (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    from_entry_id INTEGER NOT NULL,

    to_entry_id INTEGER NOT NULL,

    relationship_type TEXT NOT NULL
        CHECK (
            relationship_type IN (
                'derived_from',
                'compound_of',
                'cognate_of',
                'variant_of',
                'dialect_variant',
                'synonym_of',
                'antonym_of',
                'semantic_shift_from',
                'influence_of',
                'translation_of',
                'reconstructed_from'
            )
        ),

    confidence REAL NOT NULL DEFAULT 1.0
        CHECK (
            confidence >= 0.0
            AND confidence <= 1.0
        ),

    notes TEXT,

    created_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (from_entry_id)
        REFERENCES entries(id)
        ON DELETE CASCADE,

    FOREIGN KEY (to_entry_id)
        REFERENCES entries(id)
        ON DELETE CASCADE,

    CHECK (from_entry_id <> to_entry_id)
);

-- ============================================================================
-- TABLE: audit_logs
--
-- Immutable record of significant changes.
--
-- This table intentionally does not include updated_at because
-- audit records should never be modified after creation.
-- New information should be recorded as a new audit entry.
-- ============================================================================

CREATE TABLE audit_logs (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    entity_type TEXT NOT NULL,

    entity_id INTEGER NOT NULL,

    change_summary TEXT NOT NULL,

    created_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_evidence_claim
ON evidence(claim_id);

CREATE INDEX idx_evidence_citation
ON evidence(citation_id);

CREATE INDEX idx_evidence_role
ON evidence(evidence_role);

CREATE INDEX idx_examples_entry
ON examples(entry_id);

CREATE INDEX idx_examples_source
ON examples(source_id);

CREATE INDEX idx_relationships_from
ON relationships(from_entry_id);

CREATE INDEX idx_relationships_to
ON relationships(to_entry_id);

CREATE INDEX idx_relationships_type
ON relationships(relationship_type);

CREATE INDEX idx_audit_entity
ON audit_logs(entity_type, entity_id);


-- ============================================================================
-- FINAL CONSTRAINTS
-- ============================================================================

-- Prevent duplicate graph edges.
CREATE UNIQUE INDEX idx_relationships_unique
ON relationships (
    from_entry_id,
    to_entry_id,
    relationship_type
);

-- ============================================================================
-- UPDATE TRIGGERS
--
-- Automatically refresh updated_at whenever a mutable row changes.
--
-- audit_logs intentionally has no UPDATE trigger because it is immutable.
-- ============================================================================

CREATE TRIGGER trg_entries_updated
AFTER UPDATE ON entries
FOR EACH ROW
WHEN OLD.updated_at = NEW.updated_at
BEGIN
    UPDATE entries
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

CREATE TRIGGER trg_meanings_updated
AFTER UPDATE ON meanings
FOR EACH ROW
WHEN OLD.updated_at = NEW.updated_at
BEGIN
    UPDATE meanings
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

CREATE TRIGGER trg_claims_updated
AFTER UPDATE ON claims
FOR EACH ROW
WHEN OLD.updated_at = NEW.updated_at
BEGIN
    UPDATE claims
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

CREATE TRIGGER trg_sources_updated
AFTER UPDATE ON sources
FOR EACH ROW
WHEN OLD.updated_at = NEW.updated_at
BEGIN
    UPDATE sources
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

CREATE TRIGGER trg_citations_updated
AFTER UPDATE ON citations
FOR EACH ROW
WHEN OLD.updated_at = NEW.updated_at
BEGIN
    UPDATE citations
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

CREATE TRIGGER trg_evidence_updated
AFTER UPDATE ON evidence
FOR EACH ROW
WHEN OLD.updated_at = NEW.updated_at
BEGIN
    UPDATE evidence
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

CREATE TRIGGER trg_examples_updated
AFTER UPDATE ON examples
FOR EACH ROW
WHEN OLD.updated_at = NEW.updated_at
BEGIN
    UPDATE examples
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

CREATE TRIGGER trg_relationships_updated
AFTER UPDATE ON relationships
FOR EACH ROW
WHEN OLD.updated_at = NEW.updated_at
BEGIN
    UPDATE relationships
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================