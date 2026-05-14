# Face Recognition Attendance System

Learning-focused AI attendance system using Computer Vision.

## 🎯 Project Goals

- **Learn Computer Vision**: Face detection, tracking, recognition, and embeddings
- **Learn Vector Databases**: PostgreSQL with pgvector for similarity search
- **Build Production-Ready System**: Deployable with Docker
- **Portfolio Project**: Demonstrate AI/ML engineering skills

## 🏗️ Architecture

```
Streamlit App → CV Pipeline (RetinaFace + ByteTrack + ArcFace) → PostgreSQL + pgvector
```

## ✨ Features

- 👤 User enrollment with face images
- 🎥 Real-time face recognition
- 📊 Attendance logging and analytics
- 🔍 Vector similarity search for face matching
- 📚 Interactive learning notebooks
- 🐳 Docker deployment

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone repository
git clone <your-repo-url>
cd attendance-system

# Start services
docker-compose up

# Access app at http://localhost:8501
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL
docker-compose up -d postgres

# Run app
streamlit run app.py
```

## 📁 Project Structure

```
attendance-system/
├── app.py                  # Main Streamlit application
├── cv_pipeline/            # Computer vision modules
│   ├── detector.py         # Face detection (RetinaFace)
│   ├── tracker.py          # Face tracking (ByteTrack)
│   └── recognizer.py       # Face recognition (ArcFace)
├── database/               # Database operations
│   ├── schema.sql          # PostgreSQL schema
│   └── operations.py       # CRUD + vector search
├── notebooks/              # Learning notebooks
│   ├── 01_embeddings_explained.ipynb
│   └── 02_pgvector_tutorial.ipynb
├── storage/                # File storage
│   ├── faces/              # Enrolled face images
│   └── models/             # CV models
├── docker-compose.yml      # Docker setup
└── requirements.txt        # Python dependencies
```

## 📚 Learning Resources

### Notebooks
- `notebooks/01_embeddings_explained.ipynb` - Learn what face embeddings are
- `notebooks/02_pgvector_tutorial.ipynb` - Learn vector database operations

### Documentation
- `docs/concepts/` - Detailed explanations of CV concepts
- `docs/tutorials/` - Step-by-step tutorials

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **CV Models**: InsightFace (RetinaFace + ArcFace), ByteTrack
- **Database**: PostgreSQL with pgvector extension
- **Deployment**: Docker, Docker Compose
- **Language**: Python 3.10+

## 📖 Key Concepts

### Face Embeddings
Face embeddings are 512-dimensional vectors that represent a face numerically. Similar faces have similar embeddings, enabling face recognition through similarity search.

### Vector Database
pgvector extends PostgreSQL to store and search high-dimensional vectors efficiently using cosine similarity.

### Recognition Pipeline
1. **Detection**: Find faces in image (RetinaFace)
2. **Tracking**: Maintain face identity across frames (ByteTrack)
3. **Recognition**: Convert face to embedding and search database (ArcFace)

## 🎓 Learning Outcomes

After completing this project, you will understand:

- ✅ What face embeddings are and how they work
- ✅ How to use vector databases for similarity search
- ✅ Face detection, tracking, and recognition pipelines
- ✅ Real-time video processing
- ✅ Docker deployment
- ✅ Production-oriented code structure

## 📝 Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://attendance:attendance123@localhost:5432/attendance_db
```

## 🐛 Troubleshooting

### Camera not working
- Ensure camera permissions are granted
- Try different camera index (0, 1, 2)

### Database connection error
- Ensure PostgreSQL container is running: `docker-compose ps`
- Check connection string in `.env`

### Model download issues
- Models are downloaded automatically on first run
- Ensure stable internet connection

## 🤝 Contributing

This is a learning project. Feel free to:
- Add new features
- Improve documentation
- Create additional learning notebooks
- Optimize performance

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- InsightFace for face recognition models
- pgvector for PostgreSQL vector extension
- Streamlit for the amazing UI framework

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Happy Learning! 🚀**
