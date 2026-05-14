# Face Detection with RetinaFace

## Overview

Face detection is the first step in any face recognition system. It:
1. Locates faces in an image
2. Returns bounding box coordinates
3. Provides confidence scores
4. Extracts facial landmarks

## RetinaFace: State-of-the-Art Detector

**RetinaFace** is one of the most accurate face detectors available, especially for small, blurry, or partially occluded faces.

### Why RetinaFace?

| Feature | RetinaFace |
|---------|-----------|
| Accuracy | ⭐⭐⭐⭐⭐ Excellent on faces of all sizes |
| Speed | ⭐⭐⭐⭐ Real-time capable (30+ FPS) |
| Small faces | ⭐⭐⭐⭐⭐ Detects tiny faces |
| Occluded faces | ⭐⭐⭐⭐ Handles partial occlusions |
| Landmarks | ⭐⭐⭐⭐⭐ 5-point landmarks for alignment |

### Architecture

RetinaFace uses a multi-task learning approach:

```
Input Image
    ↓
[Backbone Network] (ResNet-based)
    ↓
├─ Face Detection Head → Bounding boxes
├─ Landmark Detection Head → 5 facial keypoints
└─ Mesh Detection Head → 468 face mesh points
    ↓
Output: Detections with confidence and landmarks
```

### Output Format

For each detected face:

```python
{
    'bbox': [x1, y1, x2, y2],          # Bounding box coordinates
    'landmarks': [[x,y], [x,y], ...],  # 5 facial keypoints (eyes, nose, mouth)
    'confidence': 0.95                  # Detection confidence 0-1
}
```

### Facial Landmarks

The 5 landmarks are:
1. **Left eye**
2. **Right eye**
3. **Nose tip**
4. **Left mouth corner**
5. **Right mouth corner**

These are useful for:
- Face alignment
- Face rotation detection
- Liveness detection
- Quality assessment

## Detection Parameters

### Detection Size

```python
detector = FaceDetector(det_size=(640, 640))
```

- Larger size → More accurate, slower
- Smaller size → Faster, less accurate
- Typical values: (320, 320), (640, 640), (1280, 1280)

### Confidence Threshold

```python
detections = detector.detect(image, conf_threshold=0.5)
```

- Lower threshold → More detections (may include false positives)
- Higher threshold → Fewer detections (only high-confidence ones)
- Default: 0.5 (good balance)

## Practical Usage

### Single Image Detection

```python
import cv2
from cv_pipeline import FaceDetector

detector = FaceDetector()

# Load image
image = cv2.imread('photo.jpg')

# Detect faces
detections = detector.detect(image)

# Visualize
image_with_boxes = detector.draw_detections(image, detections)
cv2.imshow('Detections', image_with_boxes)
cv2.waitKey(0)
```

### Video Processing

```python
cap = cv2.VideoCapture(0)  # Webcam

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    detections = detector.detect(frame)
    
    for det in detections:
        x1, y1, x2, y2 = det['bbox']
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
```

## Common Issues and Solutions

### ❌ Missing Small Faces

**Problem**: Small faces in the image aren't detected

**Solutions**:
1. Lower `conf_threshold` to catch more detections
2. Increase `det_size` for higher resolution
3. Crop regions and detect separately
4. Use image upscaling

### ❌ Too Many False Positives

**Problem**: Objects are detected as faces (books, faces on posters, etc.)

**Solutions**:
1. Increase `conf_threshold` to be more strict
2. Verify with additional checks (face alignment, landmark quality)
3. Use face verification after detection

### ❌ Detection is Slow

**Problem**: Face detection is taking too long

**Solutions**:
1. Reduce `det_size` for faster inference
2. Downscale input image
3. Use GPU acceleration
4. Batch process multiple images

## Performance Benchmarks

On a CPU (Intel i7):
- Single face: ~50-100ms
- Multiple faces: ~100-200ms
- Video (640x480): ~30-50ms per frame

On GPU (RTX 3080):
- Single face: ~2-5ms
- Multiple faces: ~5-10ms
- Video: ~2-5ms per frame (30+ FPS)

## Next Steps

1. ➡️ Extract detected faces with `detector.crop_face()`
2. ➡️ Pass cropped faces to **FaceRecognizer** for embeddings
3. ➡️ Store embeddings in database for matching
