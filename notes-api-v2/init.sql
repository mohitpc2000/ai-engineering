CREATE EXTENSION IF NOT EXISTS VECTOR;
CREATE TABLE IF NOT EXISTS notes(
    id TEXT PRIMARY KEY,
    text TEXT,
    tag TEXT DEFAULT 'general',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    embedding VECTOR(768)
);
CREATE INDEX IF NOT EXISTS notes_embedding_idx
    ON notes USING ivfflat (embedding vector_cosine_ops) WITH (lists=100);
    