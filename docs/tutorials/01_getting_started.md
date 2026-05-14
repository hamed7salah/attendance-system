# Tutorial: Getting Started with Face Recognition Attendance

## Prerequisites

- Python 3.10+
- Docker (recommended) or PostgreSQL 12+
- A webcam or face images for testing
- Basic command line knowledge

## Step 1: Setup

### Option A: Using Docker (Recommended)

```bash
# Clone or navigate to project
cd attendance-system

# Start all services
docker-compose up

# Services running:
# - PostgreSQL on port 5432
# - Streamlit app on http://localhost:8501
```

### Option B: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL (if not running)
docker-compose up -d postgres

# Wait for database to be ready
# Then run Streamlit
streamlit run app.py
```

## Step 2: Access the Application

Open your browser to http://localhost:8501

You should see the Face Recognition Attendance System interface.

## Step 3: Enroll Your First User

1. Go to **"👤 Enroll User"** page
2. Fill in user information:
   - **Full Name**: Your name
   - **Email**: Your email (optional)
   - **Employee ID**: Your ID (optional)
3. **Upload a clear face photo**:
   - Good: Frontal face, well-lit, clear
   - Bad: Extreme angles, shadows, blurry
4. Click **"✅ Enroll User"**
5. System will:
   - Detect your face
   - Generate embedding
   - Store in database
   - Show success message

## Step 4: Learn Concepts

### Understand Face Embeddings

Go to **"📖 Learn Concepts"** and select **"What are Face Embeddings?"**

Here you can:
- Upload your face image
- See the embedding generated
- Visualize all 512 dimensions
- Understand how they're used

### Understand pgvector

Select **"What is pgvector?"** to learn:
- How vector databases work
- Why we need them for face recognition
- Performance characteristics
- Database optimization

## Step 5: Test Live Recognition

1. Go to **"🎥 Live Recognition"** page
2. Check settings:
   - **Camera ID**: 0 (for default webcam)
   - **Show FPS**: Enable to see performance
   - **Show Landmarks**: Enable to see facial points
3. Click **"🎥 Start Camera"**
4. Face your webcam
5. System will:
   - Detect your face in real-time
   - Generate embedding
   - Search database
   - Show match result (green box = recognized, red = unknown)
   - Log attendance automatically (once per day)

## Step 6: View Attendance Records

1. Go to **"📊 View Attendance"**
2. Select date range
3. View:
   - Total logs
   - Unique users
   - Average confidence
   - Detailed attendance records
4. **Download CSV** for external analysis

## Step 7: Manage Users

Go to **"👥 Manage Users"** to:
- See all enrolled users
- View embedding counts
- Plan for future operations

## Running Jupyter Notebooks

### Notebook 1: Face Embeddings Explained

```bash
cd notebooks
jupyter notebook 01_embeddings_explained.ipynb
```

Learn:
- What embeddings are
- How ArcFace generates them
- How to visualize them
- Similarity matching

### Notebook 2: pgvector Tutorial

```bash
jupyter notebook 02_pgvector_tutorial.ipynb
```

Learn:
- Vector database concepts
- pgvector SQL operations
- Performance characteristics
- Scaling considerations

## Common Workflows

### Scenario 1: Daily Attendance

**Goal**: Take daily attendance for office

```
1. Enroll all employees (👤 Enroll User)
   - Collect one clear photo per person
   - Store in database

2. Daily morning:
   - Employees pass by camera (🎥 Live Recognition)
   - System automatically logs attendance
   - No manual action needed!

3. End of day:
   - Download attendance report (📊 View Attendance)
   - Export to CSV
   - Submit to HR
```

### Scenario 2: Multi-Person Group

**Goal**: Recognize multiple people in a group photo

```
1. Enroll all people (👤 Enroll User)

2. Take group photo

3. Run in notebook:
   ```python
   import cv2
   from cv_pipeline import FaceDetector, FaceRecognizer
   from database import Database
   
   image = cv2.imread('group_photo.jpg')
   detector = FaceDetector()
   recognizer = FaceRecognizer()
   db = Database(os.getenv('DATABASE_URL'))
   
   detections = detector.detect(image)
   for det in detections:
       embedding = recognizer.get_embedding_from_detection(image, det['bbox'])
       match = db.find_matching_user(embedding, threshold=0.55)
       if match:
           print(f"Found: {match['name']}")
   ```
```

### Scenario 3: Optimize Recognition Quality

**Goal**: Improve recognition accuracy

```
1. Collect multiple photos per person
   - Different angles
   - Different lighting
   - Different expressions

2. Enroll each photo separately
   - Each creates a separate embedding
   - Better coverage of variations

3. Test recognition
   - Run 🎥 Live Recognition
   - Adjust threshold if needed (sidebar)

4. If still poor:
   - Lower threshold
   - Collect better quality photos
   - Check image quality in app
```

## Troubleshooting

### ❌ "No face detected" error

**Problem**: System can't find face in uploaded image

**Solution**:
- Use clearer photo
- Ensure face is frontal (looking at camera)
- Improve lighting
- Ensure only one face in image

### ❌ Live recognition not working

**Problem**: Camera shows unknown/red box

**Solution**:
1. Ensure user is enrolled
2. Face the camera frontally
3. Adequate lighting (not backlit)
4. Try adjusting threshold slider (lower = more lenient)
5. Enroll with multiple photos from different angles

### ❌ "Camera not found" error

**Problem**: Can't access webcam

**Solution**:
- Check camera ID (try 0, 1, 2 in settings)
- Ensure other apps aren't using camera
- Restart browser and app
- Check camera permissions (Linux/Mac)

### ❌ System is slow

**Problem**: Detection/recognition takes long time

**Solution**:
- Close other applications
- Use GPU if available
- Lower image resolution
- Use CPU optimization: set threading pool size

## Performance Tips

### For CPU-only systems

```python
# Use smaller detection model
from cv_pipeline import FaceDetector
detector = FaceDetector(det_size=(320, 320))  # Smaller, faster
```

### For better accuracy

```python
# Use larger detection model
detector = FaceDetector(det_size=(1280, 1280))  # Larger, accurate
```

### For batch processing

```python
# Process multiple images efficiently
images = [img1, img2, img3]
for image in images:
    detections = detector.detect(image)  # Reuse detector
    # ... process
```

## Next Steps

1. **Explore the codebase**:
   - [cv_pipeline/detector.py](../../cv_pipeline/detector.py) - Face detection
   - [cv_pipeline/recognizer.py](../../cv_pipeline/recognizer.py) - Face recognition
   - [database/operations.py](../../database/operations.py) - Database operations

2. **Read the concepts**:
   - [01_face_detection.md](../concepts/01_face_detection.md)
   - [02_face_recognition.md](../concepts/02_face_recognition.md)
   - [03_vector_databases.md](../concepts/03_vector_databases.md)

3. **Try the notebooks**:
   - [01_embeddings_explained.ipynb](../../notebooks/01_embeddings_explained.ipynb)
   - [02_pgvector_tutorial.ipynb](../../notebooks/02_pgvector_tutorial.ipynb)

4. **Customize for your needs**:
   - Modify threshold in app
   - Add new features (email alerts, etc.)
   - Export data for analysis
   - Integrate with existing systems

## Advanced: API Integration

You can use the system as an API:

```python
from database import Database
from cv_pipeline import FaceRecognizer
import cv2

# Initialize
db = Database("postgresql://...")
recognizer = FaceRecognizer()

# Recognize someone
image = cv2.imread("photo.jpg")
embedding = recognizer.get_embedding(image)
match = db.find_matching_user(embedding, threshold=0.55)

if match:
    print(f"Recognized: {match['name']}")
    db.log_attendance(match['user_id'], match['confidence'])
```

## Getting Help

1. **Check logs**: Look for error messages in app
2. **Jupyter notebooks**: Run notebooks for understanding
3. **Concept docs**: Read [docs/concepts/](../concepts/) for detailed explanations
4. **Code comments**: Source code has detailed learning comments

## What You've Learned

✅ How face detection works (RetinaFace)
✅ How face recognition works (ArcFace)
✅ How vector databases work (pgvector)
✅ How to build end-to-end ML system
✅ Real-time processing techniques
✅ Database optimization

🎉 You're ready to build your own face recognition system!
