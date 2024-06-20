CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE embeddings (
    crop_id TEXT PRIMARY KEY,
    embedding_vector VECTOR(1024),
    class_name TEXT
);
