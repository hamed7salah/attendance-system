# Database Schema & API Design

## 🗄️ DATABASE SCHEMA

### **Design Principles**
- Normalized structure (3NF)
- UUID primary keys (distributed-friendly)
- Timestamps for audit trail
- Soft deletes where appropriate
- Indexes for performance
- Foreign key constraints for integrity

---

## 📊 ENTITY RELATIONSHIP DIAGRAM

```
┌─────────────────┐         ┌──────────────────┐
│     users       │         │    cameras       │
├─────────────────┤         ├──────────────────┤
│ id (PK)         │         │ id (PK)          │
│ email           │         │ name             │
│ full_name       │         │ location         │
│ employee_id     │         │ rtsp_url         │
│ department      │         │ is_active        │
│ role            │         │ created_at       │
│ is_active       │         └──────────────────┘
│ created_at      │                │
│ updated_at      │                │
└─────────────────┘                │
        │                          │
        │ 1                        │
        │                          │
        │ N                        │ N
        ▼                          ▼
┌─────────────────────────────────────────┐
│         attendance_logs                 │
├─────────────────────────────────────────┤
│ id (PK)                                 │
│ user_id (FK → users.id)                │
│ camera_id (FK → cameras.id)            │
│ timestamp                               │
│ confidence                              │
│ image_path (optional)                   │
│ status (present/absent/late)            │
│ created_at                              │
└─────────────────────────────────────────┘
        │
        │ 1
        │
        │ N
        ▼
┌─────────────────────────────────────────┐
│         face_embeddings                 │
├─────────────────────────────────────────┤
│ id (PK)                                 │
│ user_id (FK → users.id)                │
│ embedding (VECTOR(512))                 │
│ quality_score                           │
│ image_path                              │
│ is_primary                              │
│ created_at                              │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         unknown_faces                   │
├─────────────────────────────────────────┤
│ id (PK)                                 │
│ camera_id (FK → cameras.id)            │
│ timestamp                               │
│ embedding (VECTOR(512))                 │
│ image_path                              │
│ reviewed                                │
│ created_at                              │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│         system_config                   │
├─────────────────────────────────────────┤
│ id (PK)                                 │
│ key                                     │
│ value (JSONB)                           │
│ description                             │
│ updated_at                              │
└─────────────────────────────────────────┘
```

---

## 📋 TABLE DEFINITIONS

### **1. users**
Stores user/employee information.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    employee_id VARCHAR(50) UNIQUE,
    department VARCHAR(100),
    role VARCHAR(50) DEFAULT 'employee',
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_employee_id ON users(employee_id);
CREATE INDEX idx_users_is_active ON users(is_active);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

**Fields Explanation:**
- `id`: UUID primary key
- `email`: Unique email for login/notifications
- `employee_id`: Company employee ID (optional)
- `department`: For analytics/reporting
- `role`: 'admin', 'employee', 'security' (for future RBAC)
- `is_active`: Soft delete flag

---

### **2. face_embeddings**
Stores face embeddings for recognition. Multiple embeddings per user for robustness.

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE face_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    embedding VECTOR(512) NOT NULL,
    quality_score FLOAT,
    image_path VARCHAR(500),
    is_primary BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_face_embeddings_user_id ON face_embeddings(user_id);
CREATE INDEX idx_face_embeddings_is_primary ON face_embeddings(is_primary);

-- Vector similarity index (IVFFlat for speed)
CREATE INDEX idx_face_embeddings_vector 
ON face_embeddings 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Alternative: HNSW index (better accuracy, slower build)
-- CREATE INDEX idx_face_embeddings_vector_hnsw 
-- ON face_embeddings 
-- USING hnsw (embedding vector_cosine_ops);
```

**Fields Explanation:**
- `embedding`: 512-dimensional vector from ArcFace
- `quality_score`: Face quality metric (blur, lighting, angle)
- `is_primary`: Main embedding for this user
- `image_path`: Reference to stored face image

**Vector Search Query:**
```sql
-- Find most similar face
SELECT 
    fe.user_id,
    u.full_name,
    1 - (fe.embedding <=> $1::vector) AS similarity
FROM face_embeddings fe
JOIN users u ON fe.user_id = u.id
WHERE u.is_active = true
ORDER BY fe.embedding <=> $1::vector
LIMIT 1;
```

---

### **3. cameras**
Stores camera configuration.

```sql
CREATE TABLE cameras (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    rtsp_url VARCHAR(500),
    camera_type VARCHAR(50) DEFAULT 'webcam',
    is_active BOOLEAN DEFAULT true,
    config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_cameras_is_active ON cameras(is_active);

-- Trigger for updated_at
CREATE TRIGGER update_cameras_updated_at BEFORE UPDATE ON cameras
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

**Fields Explanation:**
- `rtsp_url`: For IP cameras (e.g., `rtsp://192.168.1.100:554/stream`)
- `camera_type`: 'webcam', 'rtsp', 'usb'
- `config`: JSONB for camera-specific settings (resolution, FPS, etc.)

**Example config:**
```json
{
  "resolution": [1920, 1080],
  "fps": 30,
  "detection_zone": [[0, 0], [1920, 1080]],
  "recognition_threshold": 0.55
}
```

---

### **4. attendance_logs**
Stores attendance records.

```sql
CREATE TABLE attendance_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    camera_id UUID NOT NULL REFERENCES cameras(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    confidence FLOAT NOT NULL,
    image_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'present',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_attendance_user_id ON attendance_logs(user_id);
CREATE INDEX idx_attendance_camera_id ON attendance_logs(camera_id);
CREATE INDEX idx_attendance_timestamp ON attendance_logs(timestamp);
CREATE INDEX idx_attendance_date ON attendance_logs(DATE(timestamp));

-- Composite index for duplicate detection
CREATE INDEX idx_attendance_user_date 
ON attendance_logs(user_id, DATE(timestamp));
```

**Fields Explanation:**
- `confidence`: Recognition confidence (0.0-1.0)
- `status`: 'present', 'late', 'early_departure'
- `metadata`: JSONB for additional info (temperature, mask detection, etc.)

**Duplicate Prevention Query:**
```sql
-- Check if user already logged today
SELECT EXISTS(
    SELECT 1 
    FROM attendance_logs 
    WHERE user_id = $1 
    AND DATE(timestamp) = CURRENT_DATE
) AS already_logged;
```

---

### **5. unknown_faces**
Stores unrecognized faces for review.

```sql
CREATE TABLE unknown_faces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    camera_id UUID NOT NULL REFERENCES cameras(id) ON DELETE CASCADE,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    embedding VECTOR(512) NOT NULL,
    image_path VARCHAR(500) NOT NULL,
    reviewed BOOLEAN DEFAULT false,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_unknown_faces_camera_id ON unknown_faces(camera_id);
CREATE INDEX idx_unknown_faces_timestamp ON unknown_faces(timestamp);
CREATE INDEX idx_unknown_faces_reviewed ON unknown_faces(reviewed);

-- Vector index for clustering similar unknown faces
CREATE INDEX idx_unknown_faces_vector 
ON unknown_faces 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 50);
```

**Use Cases:**
- Security review of unauthorized access attempts
- Identify frequent visitors for enrollment
- Cluster similar unknown faces

---

### **6. system_config**
Stores system-wide configuration.

```sql
CREATE TABLE system_config (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger for updated_at
CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_config
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

**Example Configurations:**
```sql
INSERT INTO system_config (key, value, description) VALUES
('recognition_threshold', '0.55', 'Minimum similarity for face match'),
('duplicate_window_hours', '24', 'Hours to prevent duplicate attendance'),
('max_embeddings_per_user', '5', 'Maximum face embeddings per user'),
('unknown_face_retention_days', '30', 'Days to keep unknown face records'),
('enable_liveness_detection', 'false', 'Enable anti-spoofing checks');
```

---

## 🔐 SECURITY & CONSTRAINTS

### **Row-Level Security (Optional for Multi-tenancy)**
```sql
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance_logs ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own attendance
CREATE POLICY user_attendance_policy ON attendance_logs
FOR SELECT
USING (user_id = current_setting('app.current_user_id')::uuid);

-- Policy: Admins can see all
CREATE POLICY admin_attendance_policy ON attendance_logs
FOR ALL
USING (
    EXISTS (
        SELECT 1 FROM users 
        WHERE id = current_setting('app.current_user_id')::uuid 
        AND role = 'admin'
    )
);
```

### **Data Retention Policies**
```sql
-- Delete old unknown faces (run daily)
DELETE FROM unknown_faces 
WHERE created_at < CURRENT_DATE - INTERVAL '30 days'
AND reviewed = false;

-- Archive old attendance logs (run monthly)
-- Move to separate archive table or export to S3
```

---

## 📊 USEFUL VIEWS

### **Daily Attendance Summary**
```sql
CREATE VIEW daily_attendance_summary AS
SELECT 
    DATE(timestamp) as date,
    COUNT(DISTINCT user_id) as unique_users,
    COUNT(*) as total_logs,
    AVG(confidence) as avg_confidence
FROM attendance_logs
GROUP BY DATE(timestamp)
ORDER BY date DESC;
```

### **User Attendance History**
```sql
CREATE VIEW user_attendance_history AS
SELECT 
    u.id as user_id,
    u.full_name,
    u.department,
    DATE(al.timestamp) as date,
    MIN(al.timestamp) as first_entry,
    MAX(al.timestamp) as last_exit,
    COUNT(*) as entry_count
FROM users u
LEFT JOIN attendance_logs al ON u.id = al.user_id
GROUP BY u.id, u.full_name, u.department, DATE(al.timestamp)
ORDER BY date DESC, u.full_name;
```

### **Camera Activity**
```sql
CREATE VIEW camera_activity AS
SELECT 
    c.id as camera_id,
    c.name as camera_name,
    c.location,
    COUNT(al.id) as total_logs,
    COUNT(DISTINCT al.user_id) as unique_users,
    MAX(al.timestamp) as last_activity
FROM cameras c
LEFT JOIN attendance_logs al ON c.id = al.camera_id
WHERE c.is_active = true
GROUP BY c.id, c.name, c.location;
```

---

## 🔍 PERFORMANCE OPTIMIZATION

### **Partitioning (For Large Datasets)**
```sql
-- Partition attendance_logs by month
CREATE TABLE attendance_logs_partitioned (
    LIKE attendance_logs INCLUDING ALL
) PARTITION BY RANGE (timestamp);

-- Create monthly partitions
CREATE TABLE attendance_logs_2026_05 
PARTITION OF attendance_logs_partitioned
FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');

-- Auto-create partitions with pg_partman extension
```

### **Materialized Views for Analytics**
```sql
CREATE MATERIALIZED VIEW monthly_attendance_stats AS
SELECT 
    DATE_TRUNC('month', timestamp) as month,
    u.department,
    COUNT(DISTINCT al.user_id) as unique_users,
    COUNT(*) as total_attendance,
    AVG(confidence) as avg_confidence
FROM attendance_logs al
JOIN users u ON al.user_id = u.id
GROUP BY DATE_TRUNC('month', timestamp), u.department;

-- Refresh daily
CREATE INDEX ON monthly_attendance_stats(month, department);
```

---

## 📝 MIGRATION STRATEGY

### **Initial Setup Script**
```sql
-- 001_initial_schema.sql
BEGIN;

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Create tables in order
-- (users, cameras, face_embeddings, attendance_logs, unknown_faces, system_config)

-- Create indexes
-- Create triggers
-- Create views

COMMIT;
```

### **Alembic Migrations (Python)**
```python
# migrations/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        # ... other columns
    )
    
    op.create_table(
        'face_embeddings',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.id')),
        sa.Column('embedding', Vector(512), nullable=False),
        # ... other columns
    )
```

---

## 🎯 NEXT: API STRUCTURE

Now that we have the database schema, let's design the REST API endpoints.

Ready to proceed with API design?
