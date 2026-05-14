"""
Face Detection using RetinaFace

CONCEPT: Face detection finds faces in an image and returns:
- Bounding box coordinates (x1, y1, x2, y2)
- Facial landmarks (eyes, nose, mouth corners)
- Confidence score

RetinaFace is one of the most accurate face detectors available.
"""

from insightface.app import FaceAnalysis
import cv2
import numpy as np
from typing import List, Dict, Any


class FaceDetector:
    """Face detector using RetinaFace from InsightFace"""
    
    def __init__(self, det_size: tuple = (640, 640)):
        """
        Initialize RetinaFace detector
        
        Args:
            det_size: Detection size (width, height). Larger = more accurate but slower
        """
        print("🔄 Loading RetinaFace model...")
        self.app = FaceAnalysis(providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0, det_size=det_size)
        print("✅ RetinaFace model loaded successfully!")
        
    def detect(self, image: np.ndarray, conf_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Detect faces in image
        
        Args:
            image: numpy array in BGR format (from cv2.imread or cv2.VideoCapture)
            conf_threshold: Minimum confidence threshold for detections
            
        Returns:
            List of detected faces, each containing:
            - bbox: [x1, y1, x2, y2] bounding box coordinates
            - landmarks: 5 facial keypoints (eyes, nose, mouth corners)
            - confidence: detection confidence score
        """
        # Detect faces
        faces = self.app.get(image)
        
        # Filter by confidence and format results
        results = []
        for face in faces:
            if face.det_score >= conf_threshold:
                results.append({
                    'bbox': face.bbox.astype(int),  # [x1, y1, x2, y2]
                    'landmarks': face.kps.astype(int),  # 5 points: [[x,y], ...]
                    'confidence': float(face.det_score)
                })
        
        return results
    
    def draw_detections(self, image: np.ndarray, detections: List[Dict[str, Any]], 
                       color: tuple = (0, 255, 0), thickness: int = 2) -> np.ndarray:
        """
        Draw bounding boxes and landmarks on image for visualization
        
        Args:
            image: Input image
            detections: List of detections from detect()
            color: BGR color tuple for drawing
            thickness: Line thickness
            
        Returns:
            Image with drawn detections
        """
        img_copy = image.copy()
        
        for det in detections:
            bbox = det['bbox']
            conf = det['confidence']
            landmarks = det['landmarks']
            
            # Draw bounding box
            cv2.rectangle(img_copy, 
                         (bbox[0], bbox[1]), 
                         (bbox[2], bbox[3]), 
                         color, thickness)
            
            # Draw confidence score
            cv2.putText(img_copy, f"{conf:.2f}", 
                       (bbox[0], bbox[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)
            
            # Draw facial landmarks
            for point in landmarks:
                cv2.circle(img_copy, tuple(point), 2, (0, 0, 255), -1)
        
        return img_copy
    
    def crop_face(self, image: np.ndarray, bbox: np.ndarray, 
                  margin: float = 0.2) -> np.ndarray:
        """
        Crop face region from image with margin
        
        Args:
            image: Input image
            bbox: Bounding box [x1, y1, x2, y2]
            margin: Margin to add around face (0.2 = 20%)
            
        Returns:
            Cropped face image
        """
        h, w = image.shape[:2]
        x1, y1, x2, y2 = bbox
        
        # Calculate margin
        face_w = x2 - x1
        face_h = y2 - y1
        margin_w = int(face_w * margin)
        margin_h = int(face_h * margin)
        
        # Add margin and clip to image bounds
        x1 = max(0, x1 - margin_w)
        y1 = max(0, y1 - margin_h)
        x2 = min(w, x2 + margin_w)
        y2 = min(h, y2 + margin_h)
        
        return image[y1:y2, x1:x2]
