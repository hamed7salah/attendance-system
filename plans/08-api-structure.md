# API Structure & Endpoints

## 🌐 API DESIGN PRINCIPLES

- **RESTful:** Standard HTTP methods (GET, POST, PUT, DELETE)
- **Versioned:** `/api/v1/...` for future compatibility
- **Consistent:** Uniform response format
- **Documented:** Auto-generated OpenAPI/Swagger docs
- **Secure:** JWT authentication, rate limiting
- **Real-time:** WebSocket for live updates

---

## 📋 API STRUCTURE OVERVIEW

```
/api/v1/
├── /auth/              # Authentication
├── /users/             # User management
├── /cameras/           # Camera management
├── /attendance/        # Attendance operations
├── /recognition/       # Face recognition
├── /analytics/         # Reports & analytics
├── /system/            # System configuration
└── /health/            # Health checks

/ws/                    # WebSocket endpoints
├── /attendance         # Real-time attendance updates
└── /camera/{id}        # Live camera feed
```

---

## 🔐 AUTHENTICATION ENDPOINTS

### **POST /api/v1/auth/login**
User login with email/password.

**Request:**
```json
{
  "email": "john.doe@company.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid",
    "email": "john.doe@company.com",
    "full_name": "John Doe",
    "role": "employee"
  }
}
```

**Status Codes:**
- `200`: Success
- `401`: Invalid credentials
- `422`: Validation error

---

### **POST /api/v1/auth/refresh**
Refresh access token.

**Request:**
```json
{
  "refresh_token": "..."
}
```

**Response:**
```json
{
  "access_token": "...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

---

### **POST /api/v1/auth/logout**
Logout (invalidate token).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

---

## 👤 USER MANAGEMENT ENDPOINTS

### **GET /api/v1/users**
List all users (paginated).

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)
- `search`: Search by name/email
- `department`: Filter by department
- `is_active`: Filter by active status

**Response:**
```json
{
  "users": [
    {
      "id": "uuid",
      "email": "john.doe@company.com",
      "full_name": "John Doe",
      "employee_id": "EMP001",
      "department": "Engineering",
      "role": "employee",
      "is_active": true,
      "face_count": 3,
      "created_at": "2026-05-01T10:00:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 8
}
```

---

### **GET /api/v1/users/{user_id}**
Get user details.

**Response:**
```json
{
  "id": "uuid",
  "email": "john.doe@company.com",
  "full_name": "John Doe",
  "employee_id": "EMP001",
  "department": "Engineering",
  "role": "employee",
  "phone": "+1234567890",
  "is_active": true,
  "face_embeddings": [
    {
      "id": "uuid",
      "quality_score": 0.95,
      "is_primary": true,
      "created_at": "2026-05-01T10:00:00Z"
    }
  ],
  "attendance_stats": {
    "total_days": 45,
    "present_days": 42,
    "attendance_rate": 0.93
  },
  "created_at": "2026-05-01T10:00:00Z"
}
```

---

### **POST /api/v1/users**
Create new user.

**Request:**
```json
{
  "email": "jane.smith@company.com",
  "full_name": "Jane Smith",
  "employee_id": "EMP002",
  "department": "Marketing",
  "phone": "+1234567890",
  "role": "employee"
}
```

**Response:**
```json
{
  "id": "uuid",
  "email": "jane.smith@company.com",
  "full_name": "Jane Smith",
  "message": "User created successfully. Please enroll face."
}
```

**Status Codes:**
- `201`: Created
- `400`: Invalid data
- `409`: Email already exists

---

### **PUT /api/v1/users/{user_id}**
Update user information.

**Request:**
```json
{
  "full_name": "Jane Smith-Johnson",
  "department": "Sales",
  "phone": "+0987654321"
}
```

**Response:**
```json
{
  "id": "uuid",
  "message": "User updated successfully"
}
```

---

### **DELETE /api/v1/users/{user_id}**
Soft delete user (set is_active = false).

**Response:**
```json
{
  "message": "User deactivated successfully"
}
```

---

## 🎥 CAMERA MANAGEMENT ENDPOINTS

### **GET /api/v1/cameras**
List all cameras.

**Response:**
```json
{
  "cameras": [
    {
      "id": "uuid",
      "name": "Main Entrance",
      "location": "Building A - Floor 1",
      "camera_type": "rtsp",
      "is_active": true,
      "status": "online",
      "last_activity": "2026-05-11T12:30:00Z",
      "config": {
        "resolution": [1920, 1080],
        "fps": 30
      }
    }
  ]
}
```

---

### **POST /api/v1/cameras**
Add new camera.

**Request:**
```json
{
  "name": "Back Entrance",
  "location": "Building B - Floor 1",
  "camera_type": "rtsp",
  "rtsp_url": "rtsp://192.168.1.100:554/stream",
  "config": {
    "resolution": [1920, 1080],
    "fps": 30,
    "recognition_threshold": 0.55
  }
}
```

**Response:**
```json
{
  "id": "uuid",
  "message": "Camera added successfully"
}
```

---

### **PUT /api/v1/cameras/{camera_id}**
Update camera configuration.

---

### **DELETE /api/v1/cameras/{camera_id}**
Remove camera.

---

### **POST /api/v1/cameras/{camera_id}/start**
Start camera processing.

**Response:**
```json
{
  "message": "Camera started successfully",
  "status": "running"
}
```

---

### **POST /api/v1/cameras/{camera_id}/stop**
Stop camera processing.

---

## 📸 FACE ENROLLMENT ENDPOINTS

### **POST /api/v1/users/{user_id}/enroll**
Enroll user face (upload image or capture from camera).

**Request (multipart/form-data):**
```
image: <file>
quality_threshold: 0.8 (optional)
```

**Response:**
```json
{
  "embedding_id": "uuid",
  "quality_score": 0.92,
  "message": "Face enrolled successfully",
  "total_embeddings": 1
}
```

**Status Codes:**
- `201`: Face enrolled
- `400`: Poor quality image
- `404`: User not found
- `409`: Face already exists (duplicate detection)

---

### **GET /api/v1/users/{user_id}/faces**
Get all face embeddings for user.

**Response:**
```json
{
  "embeddings": [
    {
      "id": "uuid",
      "quality_score": 0.95,
      "is_primary": true,
      "image_url": "/storage/faces/uuid.jpg",
      "created_at": "2026-05-01T10:00:00Z"
    }
  ]
}
```

---

### **DELETE /api/v1/users/{user_id}/faces/{embedding_id}**
Delete specific face embedding.

---

### **POST /api/v1/users/{user_id}/faces/{embedding_id}/set-primary**
Set embedding as primary.

---

## 🔍 FACE RECOGNITION ENDPOINTS

### **POST /api/v1/recognition/identify**
Identify person from image (for testing/manual verification).

**Request (multipart/form-data):**
```
image: <file>
threshold: 0.55 (optional)
```

**Response:**
```json
{
  "recognized": true,
  "user": {
    "id": "uuid",
    "full_name": "John Doe",
    "employee_id": "EMP001"
  },
  "confidence": 0.87,
  "processing_time_ms": 145
}
```

**If not recognized:**
```json
{
  "recognized": false,
  "message": "No matching user found",
  "confidence": 0.32
}
```

---

### **POST /api/v1/recognition/verify**
Verify if image matches specific user (1:1 verification).

**Request:**
```json
{
  "user_id": "uuid",
  "image": "<base64_encoded_image>"
}
```

**Response:**
```json
{
  "verified": true,
  "confidence": 0.89,
  "threshold": 0.55
}
```

---

## 📊 ATTENDANCE ENDPOINTS

### **GET /api/v1/attendance**
Get attendance logs (paginated, filterable).

**Query Parameters:**
- `user_id`: Filter by user
- `camera_id`: Filter by camera
- `start_date`: Start date (YYYY-MM-DD)
- `end_date`: End date (YYYY-MM-DD)
- `page`: Page number
- `limit`: Items per page

**Response:**
```json
{
  "logs": [
    {
      "id": "uuid",
      "user": {
        "id": "uuid",
        "full_name": "John Doe",
        "employee_id": "EMP001"
      },
      "camera": {
        "id": "uuid",
        "name": "Main Entrance",
        "location": "Building A"
      },
      "timestamp": "2026-05-11T08:30:15Z",
      "confidence": 0.87,
      "status": "present",
      "image_url": "/storage/attendance/uuid.jpg"
    }
  ],
  "total": 1250,
  "page": 1,
  "pages": 63
}
```

---

### **GET /api/v1/attendance/today**
Get today's attendance summary.

**Response:**
```json
{
  "date": "2026-05-11",
  "total_employees": 150,
  "present": 142,
  "absent": 8,
  "attendance_rate": 0.947,
  "by_department": [
    {
      "department": "Engineering",
      "total": 50,
      "present": 48,
      "rate": 0.96
    }
  ]
}
```

---

### **GET /api/v1/attendance/user/{user_id}**
Get attendance history for specific user.

**Query Parameters:**
- `start_date`: Start date
- `end_date`: End date
- `page`: Page number

**Response:**
```json
{
  "user": {
    "id": "uuid",
    "full_name": "John Doe"
  },
  "period": {
    "start": "2026-05-01",
    "end": "2026-05-11"
  },
  "stats": {
    "total_days": 11,
    "present_days": 10,
    "absent_days": 1,
    "attendance_rate": 0.91
  },
  "logs": [
    {
      "date": "2026-05-11",
      "first_entry": "08:30:15",
      "last_exit": "17:45:30",
      "total_entries": 3,
      "status": "present"
    }
  ]
}
```

---

### **POST /api/v1/attendance/manual**
Manual attendance entry (for admin/corrections).

**Request:**
```json
{
  "user_id": "uuid",
  "timestamp": "2026-05-11T08:30:00Z",
  "status": "present",
  "notes": "Manual entry - system was down"
}
```

**Response:**
```json
{
  "id": "uuid",
  "message": "Manual attendance logged successfully"
}
```

---

### **DELETE /api/v1/attendance/{log_id}**
Delete attendance log (admin only).

---

## 📈 ANALYTICS ENDPOINTS

### **GET /api/v1/analytics/summary**
Overall system analytics.

**Query Parameters:**
- `start_date`: Start date
- `end_date`: End date

**Response:**
```json
{
  "period": {
    "start": "2026-05-01",
    "end": "2026-05-11"
  },
  "overview": {
    "total_logs": 1580,
    "unique_users": 142,
    "avg_daily_attendance": 143.6,
    "avg_confidence": 0.86
  },
  "by_department": [...],
  "by_camera": [...],
  "by_hour": [
    {
      "hour": 8,
      "count": 120,
      "avg_confidence": 0.88
    }
  ],
  "trends": {
    "attendance_rate_trend": [0.94, 0.95, 0.93, ...]
  }
}
```

---

### **GET /api/v1/analytics/user/{user_id}/report**
Detailed user attendance report.

---

### **GET /api/v1/analytics/department/{department}/report**
Department-wise attendance report.

---

### **GET /api/v1/analytics/export**
Export attendance data (CSV/Excel).

**Query Parameters:**
- `format`: 'csv' or 'excel'
- `start_date`: Start date
- `end_date`: End date
- `user_ids`: Comma-separated user IDs (optional)

**Response:**
- File download (CSV/Excel)

---

## 🔧 SYSTEM ENDPOINTS

### **GET /api/v1/system/config**
Get system configuration.

**Response:**
```json
{
  "recognition_threshold": 0.55,
  "duplicate_window_hours": 24,
  "max_embeddings_per_user": 5,
  "enable_liveness_detection": false
}
```

---

### **PUT /api/v1/system/config**
Update system configuration (admin only).

**Request:**
```json
{
  "recognition_threshold": 0.60,
  "enable_liveness_detection": true
}
```

---

### **GET /api/v1/system/stats**
System statistics.

**Response:**
```json
{
  "total_users": 150,
  "active_users": 142,
  "total_cameras": 5,
  "active_cameras": 4,
  "total_attendance_logs": 15680,
  "total_unknown_faces": 23,
  "database_size_mb": 245,
  "uptime_seconds": 86400
}
```

---

### **GET /api/v1/health**
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-05-11T12:30:00Z",
  "services": {
    "database": "healthy",
    "cv_pipeline": "healthy",
    "cameras": {
      "total": 5,
      "active": 4,
      "inactive": 1
    }
  },
  "version": "1.0.0"
}
```

---

## 🔌 WEBSOCKET ENDPOINTS

### **WS /ws/attendance**
Real-time attendance updates.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/attendance?token=<jwt_token>');
```

**Server Messages:**
```json
{
  "event": "attendance_logged",
  "data": {
    "id": "uuid",
    "user": {
      "id": "uuid",
      "full_name": "John Doe",
      "employee_id": "EMP001"
    },
    "camera": {
      "id": "uuid",
      "name": "Main Entrance"
    },
    "timestamp": "2026-05-11T08:30:15Z",
    "confidence": 0.87
  }
}
```

```json
{
  "event": "unknown_face",
  "data": {
    "camera_id": "uuid",
    "camera_name": "Main Entrance",
    "timestamp": "2026-05-11T08:35:20Z",
    "image_url": "/storage/unknown/uuid.jpg"
  }
}
```

---

### **WS /ws/camera/{camera_id}**
Live camera feed (MJPEG stream or frame updates).

**Server Messages:**
```json
{
  "event": "frame",
  "data": {
    "camera_id": "uuid",
    "timestamp": "2026-05-11T08:30:15.123Z",
    "frame": "<base64_encoded_jpeg>",
    "detections": [
      {
        "bbox": [100, 150, 300, 400],
        "confidence": 0.95,
        "user_id": "uuid",
        "user_name": "John Doe"
      }
    ]
  }
}
```

---

## 📝 RESPONSE FORMAT STANDARDS

### **Success Response**
```json
{
  "success": true,
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### **Error Response**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["Invalid email format"]
    }
  }
}
```

### **Pagination Metadata**
```json
{
  "data": [...],
  "pagination": {
    "total": 150,
    "page": 1,
    "limit": 20,
    "pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## 🔒 AUTHENTICATION & AUTHORIZATION

### **JWT Token Structure**
```json
{
  "sub": "user_id",
  "email": "john.doe@company.com",
  "role": "employee",
  "exp": 1715432400,
  "iat": 1715428800
}
```

### **Role-Based Access Control (RBAC)**

| Endpoint | Employee | Admin | Security |
|----------|----------|-------|----------|
| GET /users | Own only | All | All |
| POST /users | ❌ | ✅ | ✅ |
| DELETE /users | ❌ | ✅ | ❌ |
| GET /attendance | Own only | All | All |
| POST /attendance/manual | ❌ | ✅ | ✅ |
| PUT /system/config | ❌ | ✅ | ❌ |
| GET /analytics | Limited | All | All |

---

## 🚀 RATE LIMITING

```python
# Per endpoint rate limits
RATE_LIMITS = {
    "/api/v1/recognition/identify": "10/minute",
    "/api/v1/users": "100/minute",
    "/api/v1/attendance": "100/minute",
    "/api/v1/analytics/export": "5/hour"
}
```

---

## 📊 API METRICS & MONITORING

### **Prometheus Metrics Endpoint**
```
GET /metrics
```

**Metrics:**
- `api_requests_total{method, endpoint, status}`
- `api_request_duration_seconds{method, endpoint}`
- `recognition_requests_total{result}`
- `recognition_confidence{quantile}`
- `active_cameras{status}`
- `attendance_logs_total`

---

## 🎯 NEXT STEPS

Now we have:
- ✅ Database schema
- ✅ API structure
- ✅ WebSocket design

Next, we'll create:
1. **Project structure** (directory layout)
2. **Phase-by-phase implementation roadmap**
3. **Initial setup instructions**

Ready to proceed?
