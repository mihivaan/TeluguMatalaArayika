-- ============================================================================
-- File           : schema.sql
-- Version        : 0.2.0
-- Reference Point: RP-006 (Schema v2)
-- ============================================================================

PRAGMA foreign_keys = ON;

-- ============================================================================
-- TABLE: entries
-- ============================================================================

CREATE TABLE entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    headword TEXT NOT NULL,

    lemma TEXT NOT NULL,

    homograph_index INTEGER NOT NULL
        DEFAULT 0
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

    is_deleted INTEGER NOT NULL 
        DEFAULT 0 CHECK (is_deleted IN (0, 1)),

    created_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    UNIQUE (lemma, homograph_index)
);

-- ============================================================================
-- TABLE: meanings
-- ============================================================================

CREATE TABLE meanings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    entry_id INTEGER NOT NULL,

    meaning_order INTEGER NOT NULL
        DEFAULT 1
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
-- TABLE: claims
-- ============================================================================

CREATE TABLE claims (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    entry_id INTEGER NOT NULL,

    meaning_id INTEGER,

    claim_text TEXT NOT NULL,

    confidence REAL
        DEFAULT 1.0
        CHECK (confidence >= 0.0 AND confidence <= 1.0),

    evidence_completeness REAL
        DEFAULT 0.0
        CHECK (
            evidence_completeness >= 0.0
            AND evidence_completeness <= 1.0
        ),

    rationale TEXT,

    status TEXT NOT NULL
        DEFAULT 'Draft'
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
-- TABLE: research_questions
-- ============================================================================

CREATE TABLE research_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    entry_id INTEGER NOT NULL,

    parent_question_id INTEGER,

    question_text TEXT NOT NULL,

    status TEXT NOT NULL
        DEFAULT 'Open'
        CHECK (
            status IN (
                'Open',
                'In Progress',
                'Partially Resolved',
                'Fully Resolved',
                'Superseded',
                'Abandoned',
                'Unresolved'
            )
        ),

    resolution_summary TEXT,

    created_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (entry_id)
        REFERENCES entries(id)
        ON DELETE CASCADE,

    FOREIGN KEY (parent_question_id)
        REFERENCES research_questions(id)
        ON DELETE SET NULL
);

-- ============================================================================
-- TABLE: question_relationships
-- ============================================================================

CREATE TABLE question_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_question_id INTEGER NOT NULL,
    to_question_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL
        CHECK (relationship_type IN ('linked_to', 'derived_from', 'merged_with', 'depends_on')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_question_id) REFERENCES research_questions(id) ON DELETE CASCADE,
    FOREIGN KEY (to_question_id) REFERENCES research_questions(id) ON DELETE CASCADE,
    CHECK (from_question_id <> to_question_id)
);

-- ============================================================================
-- TABLE: research_notes
-- ============================================================================

CREATE TABLE research_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    entry_id INTEGER NOT NULL,

    note_text TEXT NOT NULL,

    created_at DATETIME NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (entry_id)
        REFERENCES entries(id)
        ON DELETE CASCADE
);

-- ============================================================================
-- TABLE: sources
-- ============================================================================

CREATE TABLE sources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    author TEXT,
    publication_year INTEGER,
    source_type TEXT,
    description TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- TABLE: citations
-- ============================================================================

CREATE TABLE citations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    page TEXT,
    column_ref TEXT,
    line_ref TEXT,
    paragraph_ref TEXT,
    citation_text TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE
);

-- ============================================================================
-- TABLE: evidence
-- ============================================================================

CREATE TABLE evidence (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    claim_id INTEGER NOT NULL,
    citation_id INTEGER NOT NULL,
    evidence_type TEXT NOT NULL DEFAULT 'Unknown'
        CHECK (evidence_type IN ('Dictionary', 'Literature', 'Fieldwork', 'Inscription', 'Oral History', 'Comparative', 'Unknown')),
    evidence_role TEXT NOT NULL DEFAULT 'Supports'
        CHECK (evidence_role IN ('Supports', 'Contradicts', 'Background')),
    evidence_text TEXT NOT NULL,
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (claim_id) REFERENCES claims(id) ON DELETE CASCADE,
    FOREIGN KEY (citation_id) REFERENCES citations(id) ON DELETE CASCADE
);

-- ============================================================================
-- TABLE: examples
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
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE SET NULL
);

-- ============================================================================
-- TABLE: relationships
-- ============================================================================

CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_entry_id INTEGER NOT NULL,
    to_entry_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL
        CHECK (relationship_type IN ('derived_from', 'compound_of', 'cognate_of', 'variant_of', 'dialect_variant', 'synonym_of', 'antonym_of', 'semantic_shift_from', 'influence_of', 'translation_of', 'reconstructed_from')),
    confidence REAL NOT NULL DEFAULT 1.0 CHECK (confidence >= 0.0 AND confidence <= 1.0),
    notes TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    FOREIGN KEY (to_entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    CHECK (from_entry_id <> to_entry_id)
);

-- ============================================================================
-- TABLE: audit_logs
-- ============================================================================

CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    change_summary TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES
-- ============================================================================

CREATE INDEX idx_entries_headword ON entries(headword);
CREATE INDEX idx_entries_lemma ON entries(lemma);
CREATE INDEX idx_entries_classification ON entries(classification);
CREATE INDEX idx_meanings_entry ON meanings(entry_id);
CREATE INDEX idx_meanings_order ON meanings(entry_id, meaning_order);
CREATE INDEX idx_claims_entry ON claims(entry_id);
CREATE INDEX idx_claims_meaning ON claims(meaning_id);
CREATE INDEX idx_claims_status ON claims(status);
CREATE INDEX idx_sources_name ON sources(name);
CREATE INDEX idx_sources_type ON sources(source_type);
CREATE INDEX idx_citations_source ON citations(source_id);
CREATE INDEX idx_citations_location ON citations(source_id, page, column_ref, line_ref, paragraph_ref);
CREATE INDEX idx_evidence_claim ON evidence(claim_id);
CREATE INDEX idx_evidence_citation ON evidence(citation_id);
CREATE INDEX idx_evidence_role ON evidence(evidence_role);
CREATE INDEX idx_examples_entry ON examples(entry_id);
CREATE INDEX idx_examples_source ON examples(source_id);
CREATE INDEX idx_relationships_from ON relationships(from_entry_id);
CREATE INDEX idx_relationships_to ON relationships(to_entry_id);
CREATE INDEX idx_relationships_type ON relationships(relationship_type);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);

CREATE INDEX idx_research_questions_entry ON research_questions(entry_id);
CREATE INDEX idx_research_questions_parent ON research_questions(parent_question_id);
CREATE INDEX idx_research_questions_status ON research_questions(status);
CREATE INDEX idx_research_notes_entry ON research_notes(entry_id);

CREATE INDEX idx_question_relationships_from ON question_relationships(from_question_id);
CREATE INDEX idx_question_relationships_to ON question_relationships(to_question_id);
CREATE INDEX idx_question_relationships_type ON question_relationships(relationship_type);

CREATE UNIQUE INDEX idx_relationships_unique
ON relationships (from_entry_id, to_entry_id, relationship_type);

CREATE UNIQUE INDEX idx_question_relationships_unique
ON question_relationships (from_question_id, to_question_id, relationship_type);

-- ============================================================================
-- UPDATE TRIGGERS
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

CREATE TRIGGER trg_research_questions_updated
AFTER UPDATE ON research_questions
FOR EACH ROW
WHEN OLD.updated_at = NEW.updated_at
BEGIN
    UPDATE research_questions
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;

CREATE TRIGGER trg_question_relationships_updated
AFTER UPDATE ON question_relationships
FOR EACH ROW
WHEN OLD.updated_at = NEW.updated_at
BEGIN
    UPDATE question_relationships
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.id;
END;