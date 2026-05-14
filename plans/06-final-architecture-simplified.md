# Final Architecture Decisions - Updated

## ✅ CONFIRMED TECHNOLOGY STACK

### **Core Stack**
- **Architecture:** Modular Monolith
- **Backend:** FastAPI
- **Database:** PostgreSQL with pgvector extension (Docker)
- **Frontend:** Streamlit

### **Computer Vision Stack**
- **Detection:** RetinaFace (best accuracy + landmarks)
- **Tracking:** ByteTrack (fast, robust)
- **Recognition:** ArcFace via InsightFace (SOTA accuracy)

### **Data & Processing**
- **Vector Storage:** PostgreSQL pgvector (single database)
- **Async Processing:** Threading with Thread Pool (simple, sufficient)
- **GPU Strategy:** CPU-first, GPU-optional

---

## 🏗️ SIMPLIFIED ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Stack                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         FastAPI Backend (Port 8000)                │    │
│  │                                                     │    │
│  │  Main Thread:                                      │    │
│  │  ├─ API Routes (/api/v1/...)                      │    │
│  │  ├─ WebSocket Server (/ws/...)                    │    │
│  │  └─ Request Handling                              │    │
│  │                                                     │    │
│  │  Thread Pool (4 workers):                         │    │
│  │  ├─ Capture Thread 1 (Camera 1)                   │    │
│  │  ├─ Capture Thread 2 (Camera 2)                   │    │
│  │  ├─ Processing Thread 1 (CV Pipeline)             │    │
│  │  └─ Processing Thread 2 (CV Pipeline)             │    │
│  │                                                     │    │
│  │  CV Pipeline:                                      │    │
│  │  └─ RetinaFace → ByteTrack → ArcFace             │    │
│  └────────────────────────────────────────────────────┘    │
│                         │                                   │
│                         ├─────────────────┐                │
│                         │                 │                │
│  ┌──────────────────────▼──┐   ┌─────────▼─────────┐      │
│  │  PostgreSQL + pgvector  │   │  Streamlit UI     │      │
│  │  (Port 5432)            │   │  (Port 8501)      │      │
│  │                         │   │                   │      │
│  │  Tables:                │   │  Pages:           │      │
│  │  ├─ users               │   │  ├─ Live Feed    │      │
│  │  ├─ attendance_logs     │   │  ├─ Analytics    │      │
│  │  ├─ cameras             │   │  ├─ User Mgmt    │      │
│  │  └─ system_config       │   │  └─ Reports      │      │
│  │                         │   │                   │      │
│  │  pgvector:              │   │  Real-time via:   │      │
│  │  └─ face_embeddings     │   │  └─ WebSocket    │      │
│  │     (512-dim vectors)   │   │     or polling    │      │
│  └─────────────────────────┘   └───────────────────┘      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 DATA FLOW

```
Video Stream (Camera)
    │
    ▼
[Capture Thread] ──► Frame Queue (thread-safe)
                          │
                          ▼
                  [Processing Thread]
                          │
                          ├─► RetinaFace Detection
                          │   (find faces + landmarks)
                          │
                          ├─► ByteTrack Tracking
                          │   (maintain face IDs)
                          │
                          ├─► Face Alignment
                          │   (using landmarks)
                          │
                          ├─► ArcFace Recognition
                          │   (512-dim embedding)
                          │
                          ├─► PostgreSQL pgvector Search
                          │   (cosine similarity)
                          │
                          └─► Attendance Logic
                                  │
                                  ├─► Check duplicate (same day)
                                  │
                                  ├─► Log to PostgreSQL
                                  │
                                  └─► Emit WebSocket event
                                          │
                                          ▼
                                  [Streamlit Dashboard]
                                  (real-time update)
```

---

## ⚡ THREADING ARCHITECTURE

### **Thread Pool Design**

```python
from concurrent.futures import ThreadPoolExecutor
import queue
import threading

# Thread-safe queues
frame_queue = queue.Queue(maxsize=30)
result_queue = queue.Queue(maxsize=100)

# Thread pool for CV processing
cv_executor = ThreadPoolExecutor(max_workers=4)

# Capture threads (one per camera)
def capture_thread(camera_id):
    cap = cv2.VideoCapture(camera_id)
    while running:
        ret, frame = cap.read()
        if ret:
            frame_queue.put((camera_id, frame))

# Processing threads (from thread pool)
def process_frame(camera_id, frame):
    # CV pipeline (runs in thread pool)
    detections = retinaface.detect(frame)
    tracks = bytetrack.update(detections)
    
    for track in tracks:
        face = align_face(frame, track.bbox, track.landmarks)
        embedding = arcface.get_embedding(face)
        
        # Search in PostgreSQL pgvector
        user = db.search_similar_face(embedding, threshold=0.55)
        
        if user:
            # Log attendance
            attendance = db.log_attendance(user.id, camera_id)
            result_queue.put(attendance)

# Result handler thread
def result_handler():
    while running:
        result = result_queue.get()
        # Emit WebSocket event
        websocket_manager.broadcast(result)
```

### **Why Threading is Sufficient**

1. **I/O Operations Release GIL:**
   - Video capture: I/O-bound
   - Database queries: I/O-bound
   - WebSocket: I/O-bound

2. **CV Processing:**
   - RetinaFace/ArcFace use ONNX Runtime
   - ONNX Runtime releases GIL during inference
   - Effective parallelism even with threading

3. **Simplicity:**
   - Shared memory (no serialization)
   - Easy debugging
   - Lower memory usage
   - Sufficient for 2-5 cameras

4. **Performance:**
   - 5-10 FPS per camera (CPU)
   - 30+ FPS per camera (GPU)
   - Acceptable for attendance system

---

## 📊 PERFORMANCE EXPECTATIONS

### **CPU-Only (Intel i5/i7)**
- **Single Camera:** 8-10 FPS
- **2 Cameras:** 5-7 FPS each
- **3 Cameras:** 3-5 FPS each
- **Memory:** ~2 GB RAM

### **With GPU (NVIDIA GTX 1660+)**
- **Single Camera:** 30-40 FPS
- **3 Cameras:** 25-30 FPS each
- **5 Cameras:** 15-20 FPS each
- **Memory:** ~3 GB RAM + 2 GB VRAM

### **Optimizations for CPU**
1. Frame skipping (process every 2nd-3rd frame)
2. Detection throttling (detect every N frames, track between)
3. ROI processing (crop to face regions)
4. ONNX Runtime optimizations

---

## 🗄️ POSTGRESQL + PGVECTOR

### **Why This Choice:**
- Single database for all data
- No data synchronization issues
- ACID transactions
- SQL for analytics
- Free hosting available
- Simple deployment

### **Vector Search Performance:**
- **1K users:** <1ms
- **10K users:** 1-5ms
- **50K users:** 5-15ms
- **100K users:** 10-30ms (with index)

### **Storage:**
- Each embedding: 512 floats × 4 bytes = 2 KB
- 1K users: ~2 MB
- 10K users: ~20 MB
- 100K users: ~200 MB

---

## 📝 NEXT STEPS

Now we'll design:
1. **Database Schema** (tables, relationships, indexes)
2. **API Structure** (endpoints, WebSocket, authentication)
3. **Project Structure** (directory layout, modules)
4. **Implementation Phases** (step-by-step roadmap)

Ready to proceed with database schema design?
