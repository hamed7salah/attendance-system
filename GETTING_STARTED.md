# Getting Started Guide

## 🚀 Quick Start

Follow these steps to get the attendance system running on your machine.

### Prerequisites

1. **Docker Desktop** (for PostgreSQL)
   - Download: https://www.docker.com/products/docker-desktop
   - Install and start Docker Desktop

2. **Python 3.10+**
   - Download: https://www.python.org/downloads/
   - Verify: `python --version`

3. **Git** (optional, for cloning)
   - Download: https://git-scm.com/downloads

### Step 1: Set Up the Project

```bash
# Navigate to project directory
cd attendance-system

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start PostgreSQL Database

```bash
# Start PostgreSQL with pgvector using Docker Compose
docker-compose up -d postgres

# Verify it's running
docker ps

# You should see: attendance-postgres container running
```

### Step 3: Run the Application

```bash
# Run Streamlit app
streamlit run app.py

# The app will open in your browser at http://localhost:8501
```

## 🎓 First Time Usage

### 1. Enroll Your First User

1. Go to **"👤 Enroll User"** page
2. Enter user information (name, email, employee ID)
3. Upload a clear face photo
4. Click **"✅ Enroll User"**

### 2. Test Recognition

1. Go to **"🎥 Live Recognition"** page
2. Click **"🎥 Start Camera"**
3. Show your face to the camera
4. System will recognize you and log attendance

### 3. View Attendance

1. Go to **"📊 View Attendance"** page
2. Select date range
3. View attendance logs

## 🐳 Using Docker (Full Stack)

To run everything in Docker:

```bash
# Build and start all services
docker-compose up --build

# Access app at http://localhost:8501
```

## 📚 Learning Path

### Week 1: Understand Concepts

1. Read **"📖 Learn Concepts"** in the app
2. Run the Jupyter notebooks in `notebooks/` folder:
   ```bash
   jupyter notebook
   ```
3. Experiment with face embeddings

### Week 2: Build and Test

1. Enroll multiple users
2. Test recognition accuracy
3. Experiment with different threshold values
4. Try different lighting conditions

### Week 3: Explore Code

1. Read through `cv_pipeline/` modules
2. Understand database operations in `database/operations.py`
3. Modify and experiment with the code

## 🔧 Troubleshooting

### Camera Not Working

**Problem**: Camera doesn't open or shows black screen

**Solutions**:
- Check camera permissions in your OS
- Try different camera ID (0, 1, 2) in settings
- Close other apps using the camera
- Restart the application

### Database Connection Error

**Problem**: "Could not connect to database"

**Solutions**:
```bash
# Check if PostgreSQL is running
docker ps

# If not running, start it
docker-compose up -d postgres

# Check logs
docker logs attendance-postgres

# Verify connection string in .env file
DATABASE_URL=postgresql://attendance:attendance123@localhost:5432/attendance_db
```

### Model Download Issues

**Problem**: Models not downloading or slow download

**Solutions**:
- Ensure stable internet connection
- Models are downloaded automatically on first run
- They're cached in `~/.insightface/` directory
- Total size: ~100-200 MB

### Import Errors

**Problem**: "ModuleNotFoundError: No module named 'X'"

**Solutions**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific package
pip install streamlit opencv-python insightface
```

### Face Not Detected

**Problem**: "No face detected in image"

**Solutions**:
- Ensure good lighting
- Face should be clearly visible
- Try different angle
- Image should contain only one face for enrollment
- Face should be at least 100x100 pixels

## 🎯 Next Steps

After getting the system running:

1. **Experiment**: Try enrolling multiple people
2. **Learn**: Read the concept explanations in the app
3. **Customize**: Modify threshold, add features
4. **Deploy**: Try deploying to cloud (see deployment guide)

## 📖 Additional Resources

- **InsightFace Documentation**: https://github.com/deepinsight/insightface
- **pgvector Documentation**: https://github.com/pgvector/pgvector
- **Streamlit Documentation**: https://docs.streamlit.io

## 💡 Tips

1. **Good Lighting**: Face recognition works best with good, even lighting
2. **Clear Photos**: Use high-quality images for enrollment
3. **Multiple Angles**: Enroll multiple photos of same person for better accuracy
4. **Threshold Tuning**: Adjust recognition threshold based on your needs
   - Higher (0.6-0.7): More strict, fewer false positives
   - Lower (0.4-0.5): More lenient, may have false positives

## 🆘 Getting Help

If you encounter issues:

1. Check this troubleshooting guide
2. Review error messages carefully
3. Check Docker logs: `docker logs attendance-postgres`
4. Check application logs in terminal
5. Open an issue on GitHub (if applicable)

---

**Happy Learning! 🚀**
