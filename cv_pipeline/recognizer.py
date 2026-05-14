"""
Face Recognition using ArcFace

CONCEPT: Face recognition converts a face image into a numerical representation
called an "embedding" - a 512-dimensional vector that captures the unique
characteristics of that face.

Similar faces produce similar embeddings, enabling face matching through
vector similarity comparison.
"""

from insightface.app import FaceAnalysis
import numpy as np
from typing import Optional
from sklearn.metrics.pairwise import cosine_similarity


class FaceRecognizer:
    """Face recognizer using ArcFace from InsightFace"""
    
    def __init__(self):
        """Initialize ArcFace recognizer"""
        print("🔄 Loading ArcFace model...")
        self.app = FaceAnalysis(providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=(640, 640))
        print("✅ ArcFace model loaded successfully!")
        
    def get_embedding(self, image: np.ndarray) -> np.ndarray:
        """
        Generate face embedding from image
        
        LEARNING: This is where the magic happens!
        The neural network processes the face image and outputs 512 numbers
        that represent the unique characteristics of this face.
        
        IMPORTANT: Image should contain exactly one face
        
        Args:
            image: numpy array in BGR format containing a face
            
        Returns:
            embedding: numpy array of shape (512,) - the face representation
            
        Raises:
            ValueError: If no face or multiple faces detected
        """
        # Detect and extract face
        faces = self.app.get(image)
        
        if len(faces) == 0:
            raise ValueError("No face detected in image. Please ensure image contains a clear face.")
        
        if len(faces) > 1:
            raise ValueError(f"Multiple faces detected ({len(faces)}). Please provide image with single face.")
        
        # Get embedding from the detected face
        embedding = faces[0].embedding
        
        # Normalize embedding (L2 normalization)
        # This ensures all embeddings have the same scale
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
    
    def compare_embeddings(self, embedding1: np.ndarray, 
                          embedding2: np.ndarray) -> float:
        """
        Compare two face embeddings using cosine similarity
        
        LEARNING: Cosine similarity measures how similar two vectors are.
        - 1.0 = identical (same person)
        - 0.6-0.8 = very similar (likely same person)
        - 0.4-0.6 = somewhat similar (maybe same person)
        - < 0.4 = different (different people)
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            
        Returns:
            similarity: float between 0 and 1
        """
        similarity = cosine_similarity([embedding1], [embedding2])[0][0]
        return float(similarity)
    
    def verify_face(self, embedding1: np.ndarray, embedding2: np.ndarray, 
                   threshold: float = 0.55) -> tuple[bool, float]:
        """
        Verify if two embeddings belong to the same person
        
        Args:
            embedding1: First face embedding
            embedding2: Second face embedding
            threshold: Similarity threshold for verification
            
        Returns:
            (is_same_person, similarity_score)
        """
        similarity = self.compare_embeddings(embedding1, embedding2)
        is_match = similarity >= threshold
        return is_match, similarity
    
    def get_embedding_from_detection(self, image: np.ndarray, 
                                    bbox: np.ndarray) -> np.ndarray:
        """
        Get embedding from a specific face region in image
        
        Useful when you already have detection results and want to
        get embeddings for specific faces.
        
        Args:
            image: Full image
            bbox: Bounding box [x1, y1, x2, y2] of the face
            
        Returns:
            embedding: 512-dimensional face embedding
        """
        # Crop face region
        x1, y1, x2, y2 = bbox.astype(int)
        face_img = image[y1:y2, x1:x2]
        
        # Get embedding
        return self.get_embedding(face_img)
