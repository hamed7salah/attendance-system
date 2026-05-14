# Face Recognition with ArcFace

## Overview

**Face Recognition** is the process of identifying or verifying who a person is based on their face.

Unlike face **detection** (finding faces), face **recognition** answers: *"Who is this person?"*

## Two Approaches

### 1. Face Verification (1:1 Matching)
- Question: "Is this person the same as my stored photo?"
- Output: Match / No match
- Use case: Unlock your phone with face ID

### 2. Face Identification (1:N Matching)
- Question: "Who is this person among all enrolled people?"
- Output: Person ID + confidence
- Use case: Our attendance system

## ArcFace: Face Recognition Model

**ArcFace** (Additive Angular Margin Loss) is a state-of-the-art face recognition model that generates face embeddings.

### How ArcFace Works

1. **Input**: Face image
2. **Processing**: Deep neural network extracts features
3. **Output**: 512-dimensional embedding vector

### Why 512 Dimensions?

```
Instead of storing: 224×224×3 = 150,528 pixels
We store:          512 numbers (embedding)

Compression: 300× smaller!
Speed: 600× faster to compare!
Meaning: Each number encodes important facial features
```

### ArcFace Training

ArcFace is trained using **angular margin loss**:

```
L = log(exp(s × cos(θ + m)) / (exp(s × cos(θ + m)) + Σexp(s × cos(θ_j))))
```

Where:
- θ = angle between embedding and class center
- m = angular margin (pushes different classes apart)
- s = scale factor

**Effect**: 
- Same person's faces cluster together
- Different people's faces spread apart
- Creates clear separation boundaries

## How to Use ArcFace

### Generating Embeddings

```python
from cv_pipeline import FaceRecognizer
import cv2

recognizer = FaceRecognizer()

# Load face image
image = cv2.imread('face.jpg')

# Generate embedding (512 numbers)
embedding = recognizer.get_embedding(image)

print(f"Embedding shape: {embedding.shape}")  # (512,)
print(f"Embedding values: {embedding[:10]}")  # First 10 values
```

### Comparing Two Faces

```python
# Get embeddings for two photos
emb1 = recognizer.get_embedding(cv2.imread('person_photo1.jpg'))
emb2 = recognizer.get_embedding(cv2.imread('person_photo2.jpg'))

# Compare similarity
similarity = recognizer.compare_embeddings(emb1, emb2)

print(f"Similarity: {similarity:.4f}")  # 0-1 score

if similarity > 0.55:
    print("✅ Same person!")
else:
    print("❌ Different people")
```

## Embedding Properties

### Normalization

ArcFace embeddings are L2-normalized:

```python
# Each embedding has length 1
norm = np.linalg.norm(embedding)
assert abs(norm - 1.0) < 0.001  # ≈ 1.0
```

This ensures:
- All embeddings are comparable
- Cosine similarity becomes simple dot product
- Consistent distance metrics

### Distribution

```python
embedding = recognizer.get_embedding(image)

# Typical statistics
print(f"Mean: {embedding.mean():.4f}")      # ≈ 0
print(f"Std:  {embedding.std():.4f}")       # ≈ 0.1
print(f"Min:  {embedding.min():.4f}")       # ≈ -0.3
print(f"Max:  {embedding.max():.4f}")       # ≈ +0.3
```

## Similarity Metrics

### Cosine Similarity

Best for normalized embeddings (what ArcFace produces):

$$\text{similarity} = \frac{\vec{v_1} \cdot \vec{v_2}}{|\vec{v_1}| |\vec{v_2}|} = \vec{v_1} \cdot \vec{v_2}$$

**Range**: -1 to 1 (typically 0.4 to 1.0 for same person)

### Euclidean Distance

Alternative (less common for face embeddings):

$$d = \sqrt{\sum_{i=1}^{512}(v_{1i} - v_{2i})^2}$$

**Range**: 0 to 2 for normalized vectors

### Why Cosine for Faces?

✅ More interpretable (0-1 is "how similar")  
✅ More robust to lighting changes  
✅ Better for high-dimensional data  
✅ Standard in face recognition  

## Threshold Selection

### Understanding Thresholds

```
Similarity Score: 0 ────────── 0.5 ─── 0.55 ──── 0.6 ────────── 1.0
Interpretation:   No match      Maybe        Match       Perfect match

Threshold = 0.55 means: if similarity ≥ 0.55, consider it a match
```

### Choosing Right Threshold

**Factors**:
- How confident do you need to be?
- Cost of false positives (wrong person admitted)
- Cost of false negatives (correct person rejected)

**Typical values**:
- **0.4**: Very permissive (catches most true matches, more false positives)
- **0.55**: Balanced (good default for attendance)
- **0.6**: Conservative (fewer false positives, fewer true matches)
- **0.7**: Very strict (only accepts very confident matches)

### Calibrating Threshold

```python
from sklearn.metrics import roc_curve, confusion_matrix
import numpy as np

# Collect same-person and different-person similarity scores
same_person_scores = [0.85, 0.82, 0.88, ...]  # Should be high
different_person_scores = [0.35, 0.42, 0.38, ...]  # Should be low

# Find optimal threshold using ROC curve
y_true = [1]*len(same_person_scores) + [0]*len(different_person_scores)
y_score = same_person_scores + different_person_scores

fpr, tpr, thresholds = roc_curve(y_true, y_score)

# Find threshold maximizing (TPR - FPR)
optimal_idx = np.argmax(tpr - fpr)
optimal_threshold = thresholds[optimal_idx]

print(f"Optimal threshold: {optimal_threshold:.4f}")
```

## Quality Factors

Good face recognition requires:

1. **Image Quality**
   - ✅ Clear, well-lit faces
   - ✅ Frontal or near-frontal pose
   - ✅ No extreme shadows
   - ✅ Eyes clearly visible

2. **Face Alignment**
   - Landmarks help align faces
   - Better alignment → better embeddings
   - ArcFace is somewhat rotation-robust

3. **Multiple Samples**
   - Store multiple embeddings per person
   - Average them for better matching
   - Reduces effect of lighting/angle variations

## Model Limitations

### Where ArcFace Works Well
- ✅ Clear frontal face photos
- ✅ Controlled lighting
- ✅ Good image quality
- ✅ Similar demographics to training data

### Where ArcFace Struggles
- ❌ Extreme pose changes (profile view)
- ❌ Heavy occlusions (mask covering face)
- ❌ Very poor image quality
- ❌ Extreme lighting (backlit)
- ❌ Heavy makeup or significant changes

## Performance Metrics

### Accuracy on LFW Dataset (Labeled Faces in the Wild)
- **ArcFace**: 99.83% accuracy
- Trained on millions of diverse faces
- Works well across ethnicities and ages

### Speed
- Single face embedding: 10-20ms (CPU)
- Single face embedding: 1-2ms (GPU)
- Fast enough for real-time applications

## Troubleshooting

### ❌ Poor Match Quality

**Problem**: System failing to recognize known people

**Solutions**:
1. Lower similarity threshold
2. Collect more enrollment photos (varied lighting/angles)
3. Check image quality (must be clear, frontally-facing)
4. Average multiple embeddings for each person

### ❌ False Positives

**Problem**: System matching unrelated people

**Solutions**:
1. Increase similarity threshold
2. Verify matches with additional checks
3. Collect enrollment samples from all users
4. Use face verification (check multiple angles)

### ❌ Slow Embedding Generation

**Problem**: Takes too long to generate embeddings

**Solutions**:
1. Use GPU acceleration
2. Batch process multiple faces
3. Cache embeddings (don't recompute)
4. Lower input image resolution

## Next Steps

1. ➡️ Store embeddings in **PostgreSQL + pgvector** database
2. ➡️ Use similarity search to find matching users
3. ➡️ Log attendance when matches are found
4. ➡️ Calibrate threshold for your specific use case
