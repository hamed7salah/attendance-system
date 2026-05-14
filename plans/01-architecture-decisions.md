# Architecture Decisions Record (ADR)

## Project: AI-Powered Attendance System

**Date:** 2026-05-11  
**Status:** Planning Phase  
**Developer Level:** Intermediate Python/Web, New to CV/ML Deployment

---

## ✅ CONFIRMED TECHNOLOGY STACK

### **Architecture Pattern**
- **Choice:** Modular Monolith
- **Rationale:** 
  - Single developer project
  - Easier debugging and development
  - Lower deployment complexity
  - Suitable for 1-10 cameras
  - Can refactor to microservices later if needed
  - Focus on CV/ML learning, not distributed systems

### **Backend Framework**
- **Choice:** FastAPI
- **Rationale:**
  - Native async support (critical for CV processing)
  - Automatic API documentation (OpenAPI/Swagger)
  - Type hints and Pydantic validation
  - WebSocket support for real-time updates
  - Industry standard for ML/AI services
  - Modern and performant

### **Database**
- **Choice:** PostgreSQL with pgvector extension
- **Setup:** Docker container (matches production environment)
- **Rationale:**
  - Production-grade relational database
  - pgvector extension for face embedding storage
  - JSONB support for flexible metadata
  - Free hosting options (Render, Railway, Supabase)
  - Industry standard, great for portfolio
  - Docker setup ensures dev/prod parity

### **Frontend/Dashboard**
- **Choice:** Streamlit
- **Rationale:**
  - Python-only (no JavaScript context switching)
  - Rapid development for dashboards
  - Built-in components for data visualization
  - Easy real-time updates
  - Lower learning curve
  - Good for internal tools and MVPs
- **Trade-off Accepted:** Less "production-like" than React, but faster to build

### **Deployment Strategy**
- **Development:** Docker Compose (FastAPI + PostgreSQL + Streamlit)
- **Production:** Docker containers on free hosting (Render/Railway)
- **CI/CD:** GitHub Actions (to be added later)

---

## 🏗️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────┐
│                  Docker Compose Stack                    │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │         FastAPI Backend (Port 8000)            │    │
│  │                                                 │    │
│  │  ├─ API Routes (/api/v1/...)                  │    │
│  │  ├─ CV Pipeline (Detection→Tracking→Recog)    │    │
│  │  ├─ Attendance Service (Business Logic)       │    │
│  │  ├─ User Management                            │    │
│  │  └─ WebSocket (Real-time events)              │    │
│  └────────────────────────────────────────────────┘    │
│                         │                               │
│                         ├─────────────────┐            │
│                         │                 │            │
│  ┌──────────────────────▼──┐   ┌─────────▼─────────┐  │
│  │  PostgreSQL + pgvector  │   │  Streamlit UI     │  │
│  │  (Port 5432)            │   │  (Port 8501)      │  │
│  │                         │   │                   │  │
│  │  ├─ Users               │   │  ├─ Live Feed    │  │
│  │  ├─ Attendance Logs     │   │  ├─ Analytics    │  │
│  │  ├─ Face Embeddings     │   │  ├─ User Mgmt    │  │
│  │  └─ System Config       │   │  └─ Reports      │  │
│  └─────────────────────────┘   └───────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📊 DATA FLOW

```
Video Input → Face Detection → Face Tracking → Face Recognition
                                                      │
                                                      ▼
                                              Known User?
                                                 /        \
                                              Yes          No
                                               │            │
                                               ▼            ▼
                                        Check Duplicate   Log Unknown
                                               │            │
                                               ▼            │
                                        Already Logged?     │
                                          /        \        │
                                        Yes        No       │
                                         │          │       │
                                         ▼          ▼       ▼
                                       Skip    Log Attendance
                                                    │
                                                    ▼
                                            Update Dashboard
                                            Emit WebSocket Event
```

---

## 🎯 NEXT DECISIONS NEEDED

1. **Face Detection Model** (YOLOv8-face, RetinaFace, MTCNN, MediaPipe)
2. **Face Tracking Algorithm** (DeepSORT, ByteTrack, OC-SORT)
3. **Face Recognition Model** (FaceNet, ArcFace, InsightFace)
4. **Vector Storage Strategy** (PostgreSQL pgvector, FAISS, Qdrant, NumPy)
5. **Async Processing Approach** (Threading, Multiprocessing, AsyncIO, Celery)

---

## 📝 NOTES

- **Development Environment:** Windows 11, Docker Desktop required
- **Python Version:** 3.10+ (for modern type hints)
- **GPU Support:** Optional (will design for CPU-first, GPU-optional)
- **Hosting Budget:** Free tier (Render/Railway/Fly.io)
- **Learning Focus:** Computer Vision, ML deployment, production practices
- **Portfolio Goal:** Demonstrate end-to-end AI system engineering

---

## ⚠️ TRADE-OFFS ACCEPTED

1. **Streamlit vs React:** Chose speed of development over "production polish"
2. **Monolith vs Microservices:** Chose simplicity over maximum scalability
3. **Docker PostgreSQL:** Requires Docker Desktop (acceptable for dev/prod parity)

---

## 🔄 FUTURE REFACTORING PATHS

If the system needs to scale beyond initial design:

1. **Separate CV Service:** Move CV pipeline to dedicated service with Redis queue
2. **Migrate to React:** Replace Streamlit with React for better UX
3. **Add Caching Layer:** Redis for session management and rate limiting
4. **Horizontal Scaling:** Multiple FastAPI instances behind load balancer
5. **Edge Deployment:** Move inference to edge devices (Jetson Nano, Raspberry Pi)
