"""
Face Tracking using ByteTrack

CONCEPT: Face tracking maintains consistent IDs for faces across video frames.
This prevents duplicate recognition logs for the same person in consecutive frames.

ByteTrack is a state-of-the-art tracking algorithm that:
- Assigns unique IDs to detected faces
- Tracks faces as they move through frames
- Handles occlusions and re-entries
"""

import numpy as np
from typing import List, Dict, Any, Optional
from boxmot import YOLO_TRACKING


class FaceTracker:
    """Face tracker using ByteTrack algorithm"""
    
    def __init__(self, model: str = "yolov8n.pt", device: str = "cpu", 
                 tracker: str = "bytetrack", conf: float = 0.5):
        """
        Initialize ByteTrack face tracker
        
        Args:
            model: YOLOv8 model size (nano/small/medium/large)
            device: Device to run on ('cpu' or 'cuda')
            tracker: Tracking algorithm ('bytetrack', 'botsort', etc.)
            conf: Confidence threshold for detections
        """
        print("🔄 Loading ByteTrack tracker...")
        try:
            self.tracker = YOLO_TRACKING(model, device=device, tracker_type=tracker)
            self.conf = conf
            self.tracks: Dict[int, Dict[str, Any]] = {}  # Store active tracks
            print("✅ ByteTrack tracker loaded successfully!")
        except Exception as e:
            print(f"⚠️ Warning: Could not load ByteTrack: {e}")
            print("Falling back to simple distance-based tracking")
            self.tracker = None
    
    def update(self, image: np.ndarray, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Update tracker with new detections and assign track IDs
        
        Args:
            image: Current frame
            detections: List of detections from FaceDetector.detect()
                       Each detection should have 'bbox' and 'confidence'
        
        Returns:
            List of detections with added 'track_id' field
        """
        if not detections:
            return []
        
        if self.tracker:
            # Use ByteTrack for tracking
            return self._update_bytetrack(image, detections)
        else:
            # Fallback to simple centroid tracking
            return self._update_centroid_tracking(detections)
    
    def _update_bytetrack(self, image: np.ndarray, 
                         detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Update using ByteTrack
        
        LEARNING: ByteTrack is a state-of-the-art tracking algorithm that:
        - Handles low-confidence detections better than traditional trackers
        - Maintains tracks more robustly through occlusions
        - Uses ReID features for person re-identification
        """
        try:
            # Convert detections to format expected by tracker
            # Format: [[x1, y1, x2, y2, conf], ...]
            bboxes = []
            confidences = []
            
            for det in detections:
                bbox = det['bbox']
                conf = det['confidence']
                bboxes.append([bbox[0], bbox[1], bbox[2], bbox[3]])
                confidences.append(conf)
            
            if not bboxes:
                return []
            
            # Run tracker
            try:
                tracks = self.tracker.track(image, conf=self.conf, verbose=False)
                
                # Parse track results and add track IDs to detections
                tracked_detections = []
                for idx, det in enumerate(detections):
                    det_copy = det.copy()
                    
                    # Try to find matching track
                    if tracks is not None and len(tracks) > idx:
                        track = tracks[idx]
                        if len(track) >= 5:  # Has track ID
                            det_copy['track_id'] = int(track[4])
                        else:
                            det_copy['track_id'] = -1
                    else:
                        det_copy['track_id'] = -1
                    
                    tracked_detections.append(det_copy)
                
                return tracked_detections
            except:
                # If tracking fails, return detections with dummy track IDs
                for idx, det in enumerate(detections):
                    det['track_id'] = idx
                return detections
                
        except Exception as e:
            print(f"⚠️ ByteTrack error: {e}, falling back to centroid tracking")
            return self._update_centroid_tracking(detections)
    
    def _update_centroid_tracking(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Simple centroid-based tracking
        
        LEARNING: This is a basic tracking approach that:
        1. Calculates centroid of each detection
        2. Matches with previous frame centroids
        3. Assigns IDs based on proximity
        
        It's simpler but less robust than ByteTrack.
        """
        import cv2
        from scipy.spatial import distance
        
        # Calculate centroids for current detections
        current_centroids = []
        for det in detections:
            bbox = det['bbox']
            cx = (bbox[0] + bbox[2]) / 2
            cy = (bbox[1] + bbox[3]) / 2
            current_centroids.append((cx, cy))
        
        # Match with previous detections
        MAX_DISTANCE = 100  # Maximum distance to consider same track
        
        for det, centroid in zip(detections, current_centroids):
            # Find closest previous track
            best_track_id = None
            best_distance = MAX_DISTANCE
            
            for track_id, track_info in self.tracks.items():
                prev_centroid = track_info['centroid']
                dist = distance.euclidean(centroid, prev_centroid)
                
                if dist < best_distance:
                    best_distance = dist
                    best_track_id = track_id
            
            # Assign track ID
            if best_track_id is not None:
                det['track_id'] = best_track_id
                # Update track
                self.tracks[best_track_id] = {
                    'centroid': centroid,
                    'bbox': det['bbox'],
                    'frames_seen': self.tracks[best_track_id]['frames_seen'] + 1
                }
            else:
                # New track
                new_id = max(self.tracks.keys(), default=-1) + 1
                det['track_id'] = new_id
                self.tracks[new_id] = {
                    'centroid': centroid,
                    'bbox': det['bbox'],
                    'frames_seen': 1
                }
        
        # Clean up old tracks (not seen for 30 frames)
        self.tracks = {
            track_id: track_info 
            for track_id, track_info in self.tracks.items()
            if track_info['frames_seen'] > 30 or track_id in [d.get('track_id', -1) for d in detections]
        }
        
        return detections
    
    def reset(self):
        """Reset all tracks (call this between videos or sessions)"""
        self.tracks = {}
        print("🔄 Tracks reset")
    
    def get_track_info(self, track_id: int) -> Optional[Dict[str, Any]]:
        """Get information about a specific track"""
        return self.tracks.get(track_id)
    
    def get_active_tracks(self) -> Dict[int, Dict[str, Any]]:
        """Get all currently active tracks"""
        return self.tracks.copy()
