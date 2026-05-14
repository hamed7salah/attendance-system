"""
Database operations for attendance system

Handles:
- User management (add, update, delete)
- Face embedding storage
- Vector similarity search for face matching
- Attendance logging
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class Database:
    """PostgreSQL database connection and operations"""
    
    def __init__(self, database_url: str):
        """
        Initialize database connection
        
        Args:
            database_url: PostgreSQL connection string
                         Format: postgresql://user:password@host:port/dbname
        """
        self.database_url = database_url
        self.conn = None
        self.cursor = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(self.database_url)
            self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            logger.info("✅ Connected to database successfully!")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            raise
    
    def _ensure_connection(self):
        """Reconnect if connection is lost"""
        try:
            if self.conn is None or self.conn.closed:
                self._connect()
            else:
                # Test connection
                self.cursor.execute("SELECT 1")
        except:
            self._connect()
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Database connection closed")
    
    # ==========================================
    # USER OPERATIONS
    # ==========================================
    
    def add_user(self, name: str, email: Optional[str] = None, 
                 employee_id: Optional[str] = None) -> int:
        """
        Add new user to database
        
        Args:
            name: User's full name
            email: User's email (optional)
            employee_id: Employee ID (optional)
            
        Returns:
            user_id: ID of newly created user
        """
        self._ensure_connection()
        
        try:
            self.cursor.execute(
                """
                INSERT INTO users (name, email, employee_id)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (name, email, employee_id)
            )
            user_id = self.cursor.fetchone()['id']
            self.conn.commit()
            logger.info(f"✅ User '{name}' added with ID {user_id}")
            return user_id
        except Exception as e:
            self.conn.rollback()
            logger.error(f"❌ Error adding user: {e}")
            raise
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        self._ensure_connection()
        
        try:
            self.cursor.execute(
                """
                SELECT u.*, COUNT(fe.id) as embedding_count
                FROM users u
                LEFT JOIN face_embeddings fe ON u.id = fe.user_id
                WHERE u.id = %s
                GROUP BY u.id
                """,
                (user_id,)
            )
            return self.cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users with embedding counts"""
        self._ensure_connection()
        
        try:
            self.cursor.execute(
                """
                SELECT u.*, COUNT(fe.id) as embedding_count
                FROM users u
                LEFT JOIN face_embeddings fe ON u.id = fe.user_id
                GROUP BY u.id
                ORDER BY u.created_at DESC
                """
            )
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def update_user(self, user_id: int, name: Optional[str] = None, 
                   email: Optional[str] = None, employee_id: Optional[str] = None):
        """Update user information"""
        self._ensure_connection()
        
        try:
            updates = []
            values = []
            
            if name is not None:
                updates.append("name = %s")
                values.append(name)
            if email is not None:
                updates.append("email = %s")
                values.append(email)
            if employee_id is not None:
                updates.append("employee_id = %s")
                values.append(employee_id)
            
            if not updates:
                return
            
            values.append(user_id)
            
            self.cursor.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE id = %s",
                tuple(values)
            )
            self.conn.commit()
            logger.info(f"✅ User {user_id} updated")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error updating user: {e}")
            raise
    
    def delete_user(self, user_id: int):
        """Delete user and all associated data"""
        self._ensure_connection()
        
        try:
            self.cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            self.conn.commit()
            logger.info(f"✅ User {user_id} deleted")
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error deleting user: {e}")
            raise
    
    # ==========================================
    # FACE EMBEDDING OPERATIONS
    # ==========================================
    
    def add_face_embedding(self, user_id: int, embedding: np.ndarray, 
                          quality_score: Optional[float] = None) -> int:
        """
        Store face embedding in database
        
        Args:
            user_id: User ID
            embedding: Face embedding vector (512-dimensional)
            quality_score: Optional quality metric (0-1)
            
        Returns:
            embedding_id: ID of stored embedding
        """
        self._ensure_connection()
        
        try:
            # Convert embedding to list for storage
            embedding_list = embedding.tolist()
            
            self.cursor.execute(
                """
                INSERT INTO face_embeddings (user_id, embedding, quality_score)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (user_id, embedding_list, quality_score)
            )
            embedding_id = self.cursor.fetchone()['id']
            self.conn.commit()
            logger.info(f"✅ Embedding stored for user {user_id}")
            return embedding_id
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error storing embedding: {e}")
            raise
    
    def get_user_embeddings(self, user_id: int) -> List[np.ndarray]:
        """Get all embeddings for a user"""
        self._ensure_connection()
        
        try:
            self.cursor.execute(
                """
                SELECT embedding
                FROM face_embeddings
                WHERE user_id = %s
                ORDER BY created_at DESC
                """,
                (user_id,)
            )
            rows = self.cursor.fetchall()
            return [np.array(row['embedding']) for row in rows]
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            return []
    
    def find_matching_user(self, query_embedding: np.ndarray, 
                          threshold: float = 0.55) -> Optional[Dict[str, Any]]:
        """
        Find user matching the query embedding using pgvector similarity search
        
        LEARNING: This uses PostgreSQL's pgvector extension to find the most
        similar face embedding in the database using cosine similarity.
        
        The <=> operator calculates distance (1 - similarity).
        ORDER BY embedding <=> query finds closest matches efficiently.
        
        Args:
            query_embedding: Face embedding to search for
            threshold: Minimum similarity score (0-1)
            
        Returns:
            Dictionary with user info and similarity score, or None if no match
        """
        self._ensure_connection()
        
        try:
            embedding_list = query_embedding.tolist()
            
            # Use pgvector cosine similarity search
            self.cursor.execute(
                """
                SELECT 
                    u.id as user_id,
                    u.name,
                    u.email,
                    u.employee_id,
                    1 - (fe.embedding <=> %s::vector) as similarity
                FROM users u
                JOIN face_embeddings fe ON u.id = fe.user_id
                ORDER BY fe.embedding <=> %s::vector
                LIMIT 1
                """,
                (embedding_list, embedding_list)
            )
            
            result = self.cursor.fetchone()
            
            if result and result['similarity'] >= threshold:
                return {
                    'user_id': result['user_id'],
                    'name': result['name'],
                    'email': result['email'],
                    'employee_id': result['employee_id'],
                    'confidence': float(result['similarity'])
                }
            
            return None
        except Exception as e:
            logger.error(f"Error finding matching user: {e}")
            return None
    
    def find_similar_faces(self, query_embedding: np.ndarray, 
                          limit: int = 5, threshold: float = 0.0) -> List[Dict[str, Any]]:
        """
        Find similar faces ordered by similarity score
        
        Args:
            query_embedding: Query face embedding
            limit: Maximum results to return
            threshold: Minimum similarity threshold
            
        Returns:
            List of similar faces with scores
        """
        self._ensure_connection()
        
        try:
            embedding_list = query_embedding.tolist()
            
            self.cursor.execute(
                """
                SELECT 
                    u.id as user_id,
                    u.name,
                    fe.id as embedding_id,
                    1 - (fe.embedding <=> %s::vector) as similarity
                FROM users u
                JOIN face_embeddings fe ON u.id = fe.user_id
                WHERE 1 - (fe.embedding <=> %s::vector) >= %s
                ORDER BY fe.embedding <=> %s::vector
                LIMIT %s
                """,
                (embedding_list, embedding_list, threshold, embedding_list, limit)
            )
            
            results = self.cursor.fetchall()
            return [
                {
                    'user_id': r['user_id'],
                    'name': r['name'],
                    'embedding_id': r['embedding_id'],
                    'similarity': float(r['similarity'])
                }
                for r in results
            ]
        except Exception as e:
            logger.error(f"Error finding similar faces: {e}")
            return []
    
    # ==========================================
    # ATTENDANCE LOGGING
    # ==========================================
    
    def log_attendance(self, user_id: int, confidence: float, 
                      camera_id: int = 0) -> Optional[int]:
        """
        Log attendance for a user
        
        Args:
            user_id: User ID
            confidence: Recognition confidence score
            camera_id: Camera ID (default 0)
            
        Returns:
            log_id: ID of attendance log entry
        """
        self._ensure_connection()
        
        try:
            self.cursor.execute(
                """
                INSERT INTO attendance_logs (user_id, confidence, camera_id)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (user_id, confidence, camera_id)
            )
            log_id = self.cursor.fetchone()['id']
            self.conn.commit()
            logger.info(f"✅ Attendance logged for user {user_id}")
            return log_id
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error logging attendance: {e}")
            return None
    
    def get_attendance_logs(self, start_date: Optional[date] = None, 
                           end_date: Optional[date] = None,
                           user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get attendance logs for date range
        
        Args:
            start_date: Start date (default: 7 days ago)
            end_date: End date (default: today)
            user_id: Optional filter by user ID
            
        Returns:
            List of attendance logs
        """
        self._ensure_connection()
        
        if start_date is None:
            start_date = date.today() - timedelta(days=7)
        if end_date is None:
            end_date = date.today()
        
        try:
            if user_id:
                self.cursor.execute(
                    """
                    SELECT 
                        al.id,
                        al.user_id,
                        u.name,
                        u.employee_id,
                        al.timestamp,
                        al.confidence,
                        al.camera_id
                    FROM attendance_logs al
                    JOIN users u ON al.user_id = u.id
                    WHERE DATE(al.timestamp) BETWEEN %s AND %s
                    AND al.user_id = %s
                    ORDER BY al.timestamp DESC
                    """,
                    (start_date, end_date, user_id)
                )
            else:
                self.cursor.execute(
                    """
                    SELECT 
                        al.id,
                        al.user_id,
                        u.name,
                        u.employee_id,
                        al.timestamp,
                        al.confidence,
                        al.camera_id
                    FROM attendance_logs al
                    JOIN users u ON al.user_id = u.id
                    WHERE DATE(al.timestamp) BETWEEN %s AND %s
                    ORDER BY al.timestamp DESC
                    """,
                    (start_date, end_date)
                )
            
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting attendance logs: {e}")
            return []
    
    def get_daily_summary(self, target_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Get attendance summary for a specific day
        
        Args:
            target_date: Date to summarize (default: today)
            
        Returns:
            List with user attendance status for the day
        """
        self._ensure_connection()
        
        if target_date is None:
            target_date = date.today()
        
        try:
            self.cursor.execute(
                """
                SELECT 
                    u.id,
                    u.name,
                    u.employee_id,
                    MIN(al.timestamp) as first_entry,
                    MAX(al.timestamp) as last_entry,
                    COUNT(*) as entry_count,
                    AVG(al.confidence) as avg_confidence
                FROM users u
                LEFT JOIN attendance_logs al 
                    ON u.id = al.user_id 
                    AND DATE(al.timestamp) = %s
                GROUP BY u.id, u.name, u.employee_id
                ORDER BY u.name
                """,
                (target_date,)
            )
            
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting daily summary: {e}")
            return []
    
    def check_duplicate_entry(self, user_id: int, minutes: int = 5) -> bool:
        """
        Check if user was logged recently (within N minutes)
        
        Useful to prevent duplicate entries in quick succession
        
        Args:
            user_id: User ID
            minutes: Time window in minutes
            
        Returns:
            True if user logged within the time window
        """
        self._ensure_connection()
        
        try:
            self.cursor.execute(
                """
                SELECT COUNT(*) as count
                FROM attendance_logs
                WHERE user_id = %s
                AND timestamp > NOW() - INTERVAL '%s minutes'
                """,
                (user_id, minutes)
            )
            
            result = self.cursor.fetchone()
            return result['count'] > 0
        except Exception as e:
            logger.error(f"Error checking duplicate entry: {e}")
            return False
    
    # ==========================================
    # STATISTICS
    # ==========================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        self._ensure_connection()
        
        try:
            # Total users
            self.cursor.execute("SELECT COUNT(*) as count FROM users")
            total_users = self.cursor.fetchone()['count']
            
            # Total embeddings
            self.cursor.execute("SELECT COUNT(*) as count FROM face_embeddings")
            total_embeddings = self.cursor.fetchone()['count']
            
            # Total attendance logs
            self.cursor.execute("SELECT COUNT(*) as count FROM attendance_logs")
            total_logs = self.cursor.fetchone()['count']
            
            # Today's attendance
            self.cursor.execute(
                """
                SELECT COUNT(DISTINCT user_id) as count
                FROM attendance_logs
                WHERE DATE(timestamp) = CURRENT_DATE
                """
            )
            today_attendance = self.cursor.fetchone()['count']
            
            # Average confidence
            self.cursor.execute("SELECT AVG(confidence) as avg_conf FROM attendance_logs")
            result = self.cursor.fetchone()
            avg_confidence = result['avg_conf'] if result['avg_conf'] else 0
            
            return {
                'total_users': total_users,
                'total_embeddings': total_embeddings,
                'total_logs': total_logs,
                'today_attendance': today_attendance,
                'avg_confidence': float(avg_confidence)
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
