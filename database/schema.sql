-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Grant privileges to user
GRANT ALL PRIVILEGES ON DATABASE attendance_db TO attendance;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    employee_id VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Face embeddings table
CREATE TABLE IF NOT EXISTS face_embeddings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    embedding VECTOR(512) NOT NULL,
    quality_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vector index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_face_embeddings_vector 
ON face_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Attendance logs table
CREATE TABLE IF NOT EXISTS attendance_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence FLOAT NOT NULL,
    camera_id INTEGER DEFAULT 0
);

-- Index for fast queries
CREATE INDEX IF NOT EXISTS idx_attendance_user_date 
ON attendance_logs(user_id, DATE(timestamp));

CREATE INDEX IF NOT EXISTS idx_attendance_timestamp 
ON attendance_logs(timestamp DESC);
