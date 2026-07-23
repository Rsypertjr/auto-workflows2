import time
from datetime import date
import pytest
import psycopg2
from typing import Dict, Any 
from fastapi import FastAPI, Response, status, BackgroundTasks 
from pydantic import BaseModel, Field 
import psutil 
import subprocess
import os
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

from sqlalchemy import BigInteger, Date, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class MasterInvoice(Base):
    __tablename__ = "master_invoices"    
    
    # Auto-incrementing primary key ID for structural safety
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    signup_date: Mapped[date] = mapped_column(Date, nullable=False)
    billing: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    source_file: Mapped[str] = mapped_column(String(255), nullable=False)
    email_message_id: Mapped[str] = mapped_column(String(64), nullable=False)
    

app = FastAPI(title="Production Monitoring API")
load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine

# FIX: Add '+asyncpg' to your hardcoded fallback string as well
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://production_user:SecureProdPassword2026!@postgres-db:5432/production_db"
)

# Initialize the async client engine safely
engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)

# --- PYDANTIC RESPONSE SCHEMAS --
class SystemMetrics(BaseModel):
    cpu_usage_percent: float = Field(..., description="Current system-wide CPU utilization")
    memory_usage_percent: float = Field(..., description="Ram utilization percentage")
    memory_used_gb: float = Field(..., description="Total active memory consumed in Gigabytes")
    
class HealthStatus(BaseModel):
    status: str 
    database: str 
    db_latency_ms: float 
    system_metrics: SystemMetrics
    
    
# --- LIVE HEALTH ENDPOINT ---
@app.get("/health", response_model=HealthStatus)
async def get_health_status(response: Response):
    """
    Comprehensive Live Health Endpoint.
    Validates physical DB infrastructure and collects server resource telemetry.
    """
    # 1. Measure Live Database Connectivity and Latency 
    start_time = time.perf_counter()
    db_connected = await verify_database_connected()
    print("Database Connected:", db_connected)
    end_time = time.perf_counter()
    
    db_latency = round((end_time - start_time) * 1000, 2) if db_connected else 0.0
    
    # 2. Gather Real-Time Server Telemetry via psutil 
    # interval=None provides an non-blocking instant snapshot calculation
    cpu_percent = psutil.cpu_percent(interval=None)
    virtual_mem = psutil.virtual_memory()
    mem_used_gb = round(virtual_mem.used / (1024 ** 3), 2)    
    
    metrics = SystemMetrics(
        cpu_usage_percent=cpu_percent,
        memory_usage_percent=virtual_mem.percent,
        memory_used_gb=mem_used_gb
    )
    
    # 3. Determine Overall Status 
    # If the database goes down or hardware resources melt, signal an unhealthy system 
    if not db_connected or cpu_percent > 95.0 or virtual_mem.percent > 90.0:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthStatus(
            status="unhealthy",
            database="disconnected" if not db_connected else "overloaded",
            db_latency_ms=db_latency,
            system_metrics=metrics            
        )
        
    return HealthStatus(
        status="healthy",
        database="connected",
        db_latency_ms=db_latency, 
        system_metrics=metrics
    )
    
async def verify_database_connected() -> bool:
    """Executes a low-overhead query to ensure the remote server is actively listening."""
    try:
       
        connection = psycopg2.connect(
            host="127.0.0.1",       # Server address (e.g., "127.0.0.1" or remote IP)
            database="postgres",     # Name of your specific database
            user="postgres",        # Your PostgreSQL username
            password="syp3rtjr2!",# Your PostgreSQL password
            port="5434"             # Default PostgreSQL port
        )
        return True 
    except Exception as error:
        print(f"Error connecting to database: {error}")
        # Capture all networkl timeouts, auth failures, or DNS drops here 
        return False

            