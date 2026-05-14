"""
Face Recognition Attendance System - Main Streamlit Application

This is a learning-focused attendance system that demonstrates:
- Face detection (RetinaFace)
- Face recognition (ArcFace)  
- Face embeddings and vector similarity search
- PostgreSQL with pgvector for vector database operations
"""

import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
from datetime import date, datetime, timedelta
from dotenv import load_dotenv
import pandas as pd

# Load environment variables
load_dotenv()

# Import our modules
from cv_pipeline import FaceDetector, FaceRecognizer, FaceTracker
from database import Database

# Page configuration
st.set_page_config(
    page_title="Face Recognition Attendance System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize components (cached for performance)
@st.cache_resource
def init_components():
    """Initialize CV pipeline and database connection"""
    try:
        detector = FaceDetector()
        recognizer = FaceRecognizer()
        db = Database(os.getenv('DATABASE_URL'))
        return detector, recognizer, db
    except Exception as e:
        st.error(f"❌ Error initializing components: {e}")
        st.info("💡 Make sure PostgreSQL is running: `docker-compose up -d postgres`")
        st.stop()

detector, recognizer, db = init_components()

# App header
st.markdown('<div class="main-header">🎓 Face Recognition Attendance System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Learning-focused AI attendance system with Computer Vision</div>', unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("📚 Navigation")
page = st.sidebar.radio("Go to", [
    "🏠 Home",
    "📖 Learn Concepts",
    "👤 Enroll User",
    "🎥 Live Recognition",
    "📊 View Attendance",
    "👥 Manage Users"
])

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚙️ Settings")
threshold = st.sidebar.slider("Recognition Threshold", 0.0, 1.0, 0.55, 0.05,
                              help="Higher = more strict matching")

# ============================================
# PAGE: Home
# ============================================

if page == "🏠 Home":
    st.header("Welcome to the Face Recognition Attendance System!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("### 👤 Users\n" + str(len(db.get_all_users())))
    
    with col2:
        today_logs = db.get_attendance_logs(date.today(), date.today())
        st.success("### ✅ Today's Attendance\n" + str(len(today_logs)))
    
    with col3:
        all_logs = db.get_attendance_logs()
        st.warning("### 📊 Total Logs\n" + str(len(all_logs)))
    
    st.markdown("---")
    
    st.markdown("""
    ## 🎯 What is this project?
    
    This is a **learning-focused** face recognition attendance system that demonstrates:
    
    - **Face Detection**: Finding faces in images using RetinaFace
    - **Face Recognition**: Identifying people using ArcFace embeddings
    - **Vector Databases**: Storing and searching face embeddings with PostgreSQL + pgvector
    - **Real-time Processing**: Live video processing and tracking
    
    ## 🚀 Quick Start
    
    1. **📖 Learn Concepts** - Understand how face embeddings work
    2. **👤 Enroll User** - Add users with their face images
    3. **🎥 Live Recognition** - Test real-time face recognition
    4. **📊 View Attendance** - See attendance logs and analytics
    
    ## 🎓 Key Learning Outcomes
    
    - ✅ Understand what face embeddings are (512-dimensional vectors)
    - ✅ Learn how vector similarity search works
    - ✅ Experience real-time computer vision
    - ✅ Work with production-grade CV models
    """)

# ============================================
# PAGE: Learn Concepts
# ============================================

elif page == "📖 Learn Concepts":
    st.header("Computer Vision Concepts")
    
    concept = st.selectbox("Choose a concept to learn", [
        "What are Face Embeddings?",
        "How does Face Detection work?",
        "How does Face Recognition work?",
        "What is pgvector?",
        "How does Similarity Search work?"
    ])
    
    if concept == "What are Face Embeddings?":
        st.markdown("""
        ## 🧠 Face Embeddings Explained
        
        ### What is an Embedding?
        An **embedding** is a way to represent a face as a list of numbers (a vector).
        
        - Instead of storing the entire image (millions of pixels)
        - We store just **512 numbers** that capture the essence of the face
        - These numbers are generated by a neural network (ArcFace)
        
        ### Why Embeddings?
        1. **Compact**: 512 numbers vs millions of pixels
        2. **Comparable**: Can measure similarity mathematically
        3. **Efficient**: Fast to search and compare
        
        ### Example:
        ```
        Person A (Photo 1): [0.23, -0.45, 0.67, ..., 0.12]  (512 numbers)
        Person A (Photo 2): [0.25, -0.43, 0.69, ..., 0.14]  (similar!)
        Person B:           [-0.89, 0.12, -0.34, ..., 0.56] (different!)
        ```
        
        ### How Similarity Works:
        - We use **cosine similarity** to compare embeddings
        - Result is a number between 0 and 1
        - > 0.6 = same person
        - < 0.4 = different person
        """)
        
        st.markdown("---")
        st.subheader("🧪 Try it yourself!")
        
        uploaded_file = st.file_uploader("Upload a face image", type=['jpg', 'png', 'jpeg'])
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            img_array = np.array(image)
            
            # Convert RGB to BGR for OpenCV
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            else:
                img_bgr = img_array
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.image(image, caption="Uploaded Image", use_column_width=True)
            
            with col2:
                try:
                    with st.spinner("Generating embedding..."):
                        embedding = recognizer.get_embedding(img_bgr)
                    
                    st.success("✅ Embedding generated!")
                    st.info(f"📊 Shape: {embedding.shape}")
                    st.info(f"📊 Type: {embedding.dtype}")
                    
                    with st.expander("View first 20 values"):
                        st.code(str(embedding[:20]))
                    
                    # Visualize
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(12, 3))
                    ax.bar(range(len(embedding)), embedding, width=1.0)
                    ax.set_title("Embedding Visualization (512 dimensions)")
                    ax.set_xlabel("Dimension")
                    ax.set_ylabel("Value")
                    ax.set_xlim(0, 512)
                    st.pyplot(fig)
                    
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif concept == "What is pgvector?":
        st.markdown("""
        ## 🗄️ pgvector: Vector Database Extension
        
        ### What is pgvector?
        **pgvector** is a PostgreSQL extension that adds support for vector similarity search.
        
        ### Why do we need it?
        - Traditional databases search by exact match: `name = "John"`
        - Vector databases search by similarity: `face ≈ stored_face`
        - Perfect for face recognition, recommendations, semantic search
        
        ### How it works:
        
        1. **Store vectors** in a special VECTOR column type:
        ```sql
        CREATE TABLE face_embeddings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER,
            embedding VECTOR(512)  -- 512-dimensional vector
        );
        ```
        
        2. **Search by similarity** using special operators:
        ```sql
        SELECT user_id, 
               1 - (embedding <=> query_vector) AS similarity
        FROM face_embeddings
        ORDER BY embedding <=> query_vector
        LIMIT 1;
        ```
        
        ### The `<=>` Operator:
        - Calculates **cosine distance** between vectors
        - Distance = 1 - similarity
        - Smaller distance = more similar
        
        ### Performance:
        - Without index: O(N) - checks every face
        - With IVFFlat index: O(log N) - much faster!
        - Can search millions of faces in milliseconds
        
        ### Real-world use:
        - **Face Recognition**: Find matching face (this project!)
        - **Recommendation Systems**: Find similar products
        - **Semantic Search**: Find similar documents
        - **Image Search**: Find similar images
        """)

# ============================================
# PAGE: Enroll User
# ============================================

elif page == "👤 Enroll User":
    st.header("Enroll New User")
    
    st.info("📝 Add a new user to the system by providing their information and a clear face photo.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("User Information")
        name = st.text_input("Full Name *", placeholder="John Doe")
        email = st.text_input("Email", placeholder="john.doe@example.com")
        employee_id = st.text_input("Employee ID", placeholder="EMP001")
    
    with col2:
        st.subheader("Face Image")
        uploaded_file = st.file_uploader("Upload face image *", type=['jpg', 'png', 'jpeg'],
                                        help="Upload a clear photo with one face")
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_column_width=True)
    
    st.markdown("---")
    
    if st.button("✅ Enroll User", type="primary", use_container_width=True):
        if not name or not uploaded_file:
            st.error("❌ Please provide name and image")
        else:
            try:
                with st.spinner("Processing..."):
                    # Convert image
                    img_array = np.array(image)
                    if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                    else:
                        img_bgr = img_array
                    
                    # Detect face
                    detections = detector.detect(img_bgr)
                    
                    if len(detections) == 0:
                        st.error("❌ No face detected. Please upload a clear face image.")
                    elif len(detections) > 1:
                        st.error(f"❌ Multiple faces detected ({len(detections)}). Please upload image with single face.")
                    else:
                        # Generate embedding
                        embedding = recognizer.get_embedding(img_bgr)
                        
                        # Add user to database
                        user_id = db.add_user(name, email, employee_id)
                        db.add_face_embedding(user_id, embedding)
                        
                        st.success(f"✅ {name} enrolled successfully!")
                        st.balloons()
                        
                        # Show details
                        st.info(f"👤 User ID: {user_id}")
                        st.info(f"📊 Embedding shape: {embedding.shape}")
                        
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ============================================
# PAGE: Live Recognition
# ============================================

elif page == "🎥 Live Recognition":
    st.header("Live Face Recognition")
    
    st.info("📸 This will use your webcam to recognize faces in real-time")
    
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.subheader("Settings")
        camera_id = st.number_input("Camera ID", 0, 10, 0)
        show_fps = st.checkbox("Show FPS", value=True)
        show_landmarks = st.checkbox("Show Landmarks", value=False)
    
    with col1:
        run = st.checkbox("🎥 Start Camera", value=False)
        frame_placeholder = st.empty()
    
    status_placeholder = st.empty()
    
    if run:
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            st.error(f"❌ Could not open camera {camera_id}")
            st.stop()
        
        # Track recognized faces to avoid duplicate logging
        recognized_today = set()
        
        frame_count = 0
        start_time = datetime.now()
        
        while run:
            ret, frame = cap.read()
            
            if not ret:
                st.error("❌ Failed to read from camera")
                break
            
            frame_count += 1
            
            # Detect faces
            detections = detector.detect(frame)
            
            # Process each detection
            for det in detections:
                bbox = det['bbox']
                
                try:
                    # Get embedding
                    embedding = recognizer.get_embedding(frame)
                    
                    # Search database
                    match = db.find_matching_user(embedding, threshold)
                    
                    if match:
                        # Recognized!
                        name = match['name']
                        conf = match['confidence']
                        user_id = match['user_id']
                        
                        # Draw green box
                        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
                        cv2.putText(frame, f"{name} ({conf:.2f})", 
                                   (bbox[0], bbox[1]-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        
                        # Log attendance (only once per day)
                        if user_id not in recognized_today:
                            log = db.log_attendance(user_id, conf)
                            if log:
                                status_placeholder.success(f"✅ Attendance logged for {name}")
                                recognized_today.add(user_id)
                    else:
                        # Unknown
                        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 2)
                        cv2.putText(frame, "Unknown", 
                                   (bbox[0], bbox[1]-10),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
                    # Draw landmarks if enabled
                    if show_landmarks and 'landmarks' in det:
                        for point in det['landmarks']:
                            cv2.circle(frame, tuple(point), 2, (255, 0, 0), -1)
                        
                except Exception as e:
                    # Draw red box for errors
                    cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 2)
            
            # Show FPS
            if show_fps:
                elapsed = (datetime.now() - start_time).total_seconds()
                fps = frame_count / elapsed if elapsed > 0 else 0
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display frame
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
        
        cap.release()

# ============================================
# PAGE: View Attendance
# ============================================

elif page == "📊 View Attendance":
    st.header("Attendance Logs")
    
    # Date filter
    col1, col2, col3 = st.columns(3)
    with col1:
        start_date = st.date_input("Start Date", date.today() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", date.today())
    with col3:
        st.write("")  # Spacing
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Get logs
    logs = db.get_attendance_logs(start_date, end_date)
    
    if logs:
        # Convert to DataFrame
        df = pd.DataFrame(logs)
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Logs", len(logs))
        with col2:
            unique_users = df['name'].nunique()
            st.metric("Unique Users", unique_users)
        with col3:
            avg_conf = df['confidence'].mean()
            st.metric("Avg Confidence", f"{avg_conf:.2f}")
        
        st.markdown("---")
        
        # Display table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"attendance_{start_date}_{end_date}.csv",
            mime="text/csv"
        )
    else:
        st.info("📭 No attendance records found for the selected date range")

# ============================================
# PAGE: Manage Users
# ============================================

elif page == "👥 Manage Users":
    st.header("Manage Users")
    
    users = db.get_all_users()
    
    if users:
        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Users", len(users))
        with col2:
            total_embeddings = sum(u['embedding_count'] for u in users)
            st.metric("Total Embeddings", total_embeddings)
        
        st.markdown("---")
        
        # Display users
        df = pd.DataFrame(users)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    else:
        st.info("👤 No users enrolled yet. Go to 'Enroll User' to add users.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🎓 Face Recognition Attendance System | Built with Streamlit, InsightFace, and PostgreSQL</p>
    <p>📚 Learning Project | Computer Vision & Vector Databases</p>
</div>
""", unsafe_allow_html=True)
