# 🚀 QUICK START GUIDE

## For Windows Users (Company Laptop - No Installation Needed!)

### Step 1: Start the Application
```
Double-click: start.bat
```
**OR** open terminal and run:
```bash
docker-compose up -d
```

### Step 2: Wait
- First time: 5-10 minutes (downloads AI models)
- After that: 30-60 seconds

### Step 3: Open Browser
```
http://localhost:8501
```

### Step 4: Use the App!
1. Go to "👤 Enroll User" - Add people with their photos
2. Go to "🎥 Live Recognition" - Test face recognition
3. Go to "📊 View Attendance" - See attendance logs

### To Stop:
```
Double-click: stop.bat
```
**OR** run:
```bash
docker-compose down
```

---

## 📋 Common Commands

| Action | Command |
|--------|---------|
| **Start** | `docker-compose up -d` |
| **Stop** | `docker-compose down` |
| **View logs** | `docker-compose logs -f app` |
| **Check status** | `docker-compose ps` |
| **Restart** | `docker-compose restart` |
| **Rebuild** | `docker-compose up -d --build` |
| **Reset everything** | `docker-compose down -v` ⚠️ Deletes data! |

---

## 🆘 Troubleshooting

### Problem: "Port 8501 already in use"
**Fix:** Stop other Streamlit apps or change port in `docker-compose.yml`

### Problem: "Docker is not running"
**Fix:** Start Docker Desktop

### Problem: "Can't access http://localhost:8501"
**Fix:** 
1. Wait longer (first run takes time)
2. Check logs: `docker-compose logs app`
3. Check status: `docker-compose ps`

### Problem: "Database connection failed"
**Fix:** 
```bash
docker-compose restart
```

### Problem: "Everything is broken!"
**Fix:** Complete reset:
```bash
docker-compose down -v
docker-compose up -d --build
```

---

## 📚 Documentation

- **Detailed Docker Guide**: [`DOCKER_SETUP.md`](DOCKER_SETUP.md)
- **Completion Summary**: [`COMPLETION_SUMMARY.md`](COMPLETION_SUMMARY.md)
- **Main README**: [`README.md`](README.md)

---

## ✅ What You Get

- ✅ Face detection and recognition
- ✅ Real-time video processing
- ✅ Attendance logging
- ✅ PostgreSQL database with vector search
- ✅ Web interface (Streamlit)
- ✅ Learning resources and notebooks

---

## 🎯 Perfect for Company Laptops!

- ✅ No installation required (uses Docker)
- ✅ Isolated environment
- ✅ Easy to remove (just delete containers)
- ✅ Professional deployment method

---

**Need help?** Check [`DOCKER_SETUP.md`](DOCKER_SETUP.md) for detailed instructions!
