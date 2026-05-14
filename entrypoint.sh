#!/bin/bash
set -e

echo "🔄 Starting Attendance System..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until pg_isready -h postgres -p 5432 -U attendance; do
  echo "   PostgreSQL is unavailable - sleeping"
  sleep 2
done

echo "✅ PostgreSQL is ready!"

# Wait a bit more to ensure database is fully initialized
sleep 3

# Test database connection
echo "🔍 Testing database connection..."
export PGPASSWORD=attendance123
psql -h postgres -U attendance -d attendance_db -c "SELECT 1;" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Database connection successful!"
else
    echo "❌ Database connection failed!"
    exit 1
fi

# Check if pgvector extension is enabled
echo "🔍 Checking pgvector extension..."
psql -h postgres -U attendance -d attendance_db -c "SELECT * FROM pg_extension WHERE extname='vector';" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ pgvector extension is enabled!"
else
    echo "⚠️  pgvector extension not found, but schema.sql should handle it"
fi

echo "🚀 Starting Streamlit application..."
exec streamlit run app.py --server.address=0.0.0.0 --server.port=8501
