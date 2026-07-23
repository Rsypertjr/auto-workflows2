import os
import sys
import asyncio
import time
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Automatically inject the parent /app workspace directory to prevent import failures
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.main import engine, DATABASE_URL
except ImportError:
    print("❌ Critical: Could not find 'app.main'. Ensure this script is placed in 'backend/tasks/'")
    sys.exit(1)

async def verify_cluster_connection():
    """Performs an async network ping against the PostgreSQL container node."""
    print("📡 Initializing Database Verification Test...")
    print(f"🔗 Target Connection String: {DATABASE_URL.split('@')[-1]}")
    
    start_time = time.perf_counter()
    try:
        # Open an isolated session block explicitly for the test ping
        async with AsyncSession(engine) as session:
            # Execute standard low-overhead integrity check query
            result = await session.execute(text("SELECT version();"))
            db_version = result.scalar()
            
            end_time = time.perf_counter()
            latency_ms = round((end_time - start_time) * 1000, 2)
            
            print("\n✅ CONNECTIVITY MATCH SUCCESSFUL!")
            print(f"⏱️ Network Latency: {latency_ms} ms")
            print(f"📦 Engine Version:  {db_version}")
            
    except Exception as e:
        end_time = time.perf_counter()
        latency_ms = round((end_time - start_time) * 1000, 2)
        
        print("\n❌ DATABASE CONNECTION FAILED!")
        print(f"⏱️ Failure Timeout after: {latency_ms} ms")
        print(f"📝 Error Details: {e}\n")
        
        # Output architectural troubleshooting advice based on error footprint
        if "asyncpg" not in DATABASE_URL:
            print("💡 Tip: Missing '+asyncpg' driver modifier in your connection string.")
        elif "postgres-db" in DATABASE_URL:
            print("💡 Tip: Ensure this script runs INSIDE docker. Host machines cannot resolve 'postgres-db'.")
        elif "localhost" in DATABASE_URL:
            print("💡 Tip: Inside a container, 'localhost' looks inside itself, NOT the database container.")
            
        sys.exit(1)

if __name__ == "__main__":
    # Execute the non-blocking event loop framework task
    asyncio.run(verify_cluster_connection())