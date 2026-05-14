# Face Recognition Attendance System - Docker Setup Guide

## 🚀 Quick Start with Docker

This guide will help you run the attendance system using Docker without installing anything on your local machine.

### Prerequisites

- Docker Desktop installed and running
- At least 4GB of free RAM
- Internet connection (for downloading Docker images)

### Step 1: Start the Application

Open a terminal in the project directory and run:

```bash
docker-compose up -d
```

This command will:
- Download the PostgreSQL image with pgvector extension
- Build the attendance system Docker image
- Start both containers (database and application)

### Step 2: Check Status

Wait for the containers to start (about 1-2 minutes), then check their status:

```bash
docker-compose ps
```

You should see both containers running:
- `attendance-postgres` - PostgreSQL database
- `attendance-app` - Streamlit application

### Step 3: Access the Application

Open your web browser and navigate to:

```
http://localhost:8501
```

You should see the Face Recognition Attendance System interface!

### Step 4: View Logs (Optional)

To see what's happening inside the containers:

```bash
# View app logs
docker-compose logs -f app

# View database logs
docker-compose logs -f postgres
```

Press `Ctrl+C` to stop viewing logs.

## 🛠️ Common Commands

### Stop the Application

```bash
docker-compose down
```

### Stop and Remove All Data (including database)

```bash
docker-compose down -v
```

⚠️ **Warning**: This will delete all enrolled users and attendance records!

### Restart the Application

```bash
docker-compose restart
```

### Rebuild After Code Changes

```bash
docker-compose up -d --build
```

### View Container Status

```bash
docker-compose ps
```

### Access Database Directly

```bash
docker exec -it attendance-postgres psql -U attendance -d attendance_db
```

Useful SQL commands:
```sql
-- List all tables
\dt

-- View enrolled users
SELECT * FROM users;

-- View attendance logs
SELECT * FROM attendance_logs;

-- Exit
\q
```

## 📊 System Architecture

```
┌─────────────────────────────────────────┐
│  Your Computer (Host)                   │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  Docker Network                   │ │
│  │                                   │ │
│  │  ┌─────────────────────────────┐ │ │
│  │  │  attendance-app             │ │ │
│  │  │  - Streamlit UI             │ │ │
│  │  │  - Face Detection/Recognition│ │ │
│  │  │  - Port: 8501               │ │ │
│  │  └──────────┬──────────────────┘ │ │
│  │             │                     │ │
│  │             ▼                     │ │
│  │  ┌─────────────────────────────┐ │ │
│  │  │  attendance-postgres        │ │ │
│  │  │  - PostgreSQL + pgvector    │ │ │
│  │  │  - Port: 5432               │ │ │
│  │  │  - Stores face embeddings   │ │ │
│  │  └─────────────────────────────┘ │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 🔧 Troubleshooting

### Problem: Port 8501 already in use

**Solution**: Stop any other Streamlit applications or change the port in [`docker-compose.yml`](docker-compose.yml:28):

```yaml
ports:
  - "8502:8501"  # Change 8501 to 8502
```

### Problem: Port 5432 already in use

**Solution**: You have PostgreSQL running locally. Either stop it or change the port in [`docker-compose.yml`](docker-compose.yml:11):

```yaml
ports:
  - "5433:5432"  # Change 5432 to 5433
```

### Problem: Container keeps restarting

**Solution**: Check the logs to see what's wrong:

```bash
docker-compose logs app
```

Common issues:
- Database not ready: Wait a bit longer (30-60 seconds)
- Out of memory: Close other applications or increase Docker memory limit
- Missing dependencies: Rebuild the image with `docker-compose up -d --build`

### Problem: Can't access the application

**Solution**: 
1. Check if containers are running: `docker-compose ps`
2. Check if port 8501 is accessible: `curl http://localhost:8501`
3. Check firewall settings
4. Try accessing from `http://127.0.0.1:8501` instead

### Problem: Database connection failed

**Solution**:
1. Ensure PostgreSQL container is healthy: `docker-compose ps`
2. Check database logs: `docker-compose logs postgres`
3. Restart containers: `docker-compose restart`

### Problem: Face detection/recognition not working

**Solution**:
1. Ensure you have a working webcam
2. Grant browser permission to access camera
3. Try uploading an image instead of using live camera
4. Check that the image has a clear, front-facing face

## 📁 Data Persistence

### Database Data

Database data is stored in a Docker volume named `postgres_data`. This means:
- ✅ Data persists when you stop/restart containers
- ✅ Data survives container recreation
- ❌ Data is deleted when you run `docker-compose down -v`

### Face Images

Face images are stored in the `./storage` directory on your host machine:
- `./storage/faces/` - Enrolled face images
- `./storage/models/` - Downloaded AI models

These directories are mounted as volumes, so data persists even if containers are deleted.

## 🔐 Security Notes

**For Learning Purposes Only**

This is a learning project with default credentials:
- Database User: `attendance`
- Database Password: `attendance123`

**Do NOT use in production without:**
1. Changing default passwords
2. Adding authentication to the web interface
3. Using HTTPS/SSL
4. Implementing proper access controls
5. Adding data encryption

## 🎓 Learning Resources

### Understanding Docker Components

1. **[`Dockerfile`](Dockerfile:1)** - Defines how to build the application image
2. **[`docker-compose.yml`](docker-compose.yml:1)** - Orchestrates multiple containers
3. **[`entrypoint.sh`](entrypoint.sh:1)** - Startup script that waits for database
4. **[`.dockerignore`](.dockerignore:1)** - Files to exclude from Docker build

### Key Technologies

- **Streamlit**: Web interface framework
- **InsightFace**: Face detection and recognition models
- **PostgreSQL**: Relational database
- **pgvector**: Vector similarity search extension
- **Docker**: Containerization platform

## 📚 Next Steps

1. **Enroll Users**: Go to "👤 Enroll User" and add some faces
2. **Test Recognition**: Use "🎥 Live Recognition" to test the system
3. **View Logs**: Check "📊 View Attendance" to see attendance records
4. **Learn Concepts**: Explore "📖 Learn Concepts" to understand how it works
5. **Experiment**: Try the Jupyter notebooks in the `notebooks/` directory

## 🆘 Getting Help

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify containers are running: `docker-compose ps`
3. Restart everything: `docker-compose restart`
4. Rebuild from scratch:
   ```bash
   docker-compose down -v
   docker-compose up -d --build
   ```

## 🎯 System Requirements

**Minimum:**
- 4GB RAM
- 2 CPU cores
- 5GB free disk space
- Docker Desktop

**Recommended:**
- 8GB RAM
- 4 CPU cores
- 10GB free disk space
- Webcam for live recognition

## 📝 Environment Variables

The system uses these environment variables (defined in [`.env`](.env:1)):

- `DATABASE_URL`: PostgreSQL connection string
- `RECOGNITION_THRESHOLD`: Face matching threshold (0.0-1.0)

You can modify these in the `.env` file or in [`docker-compose.yml`](docker-compose.yml:29).

---

**Happy Learning! 🎓**

For more information, check the documentation in the `docs/` directory.
