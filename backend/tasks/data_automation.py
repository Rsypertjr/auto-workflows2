import os
import io
import json
import asyncio
import pandas as pd
from datetime import datetime
from datetime import date
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import BigInteger, Date, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from google import genai

# 1. Retrieve the API key from environment variables
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY environment variable not found. Please set it before running."
    )

# 2. Configure the library with your API key
client = genai.Client(api_key=api_key)


from sqlalchemy.ext.asyncio import create_async_engine

# FIX: Add '+asyncpg' to your hardcoded fallback string as well
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://production_user:SecureProdPassword2026!@postgres-db:5432/production_db",
)
# Initialize the async client engine safely
engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)


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


def generate_ai_narrative_summary(metrics: dict, df_head: str) -> str:
    """Passes financial calculations into Gemini to synthesize real-time performance insights."""

    # 4. Generate content
    prompt = f"""
    You are an automated financial controller AI agent analyzing the current system operational activity.
    Review the data metrics structure below and compile a concise 2-sentence executive summary report.
    Hightlight the revenue velocity and point out any transaction anomalies or structural observations.
    
    Calculated System Metrics:
        - Target Processing Date:  {metrics['report_date']}
        - Identified Active Invoices: {metrics['total_active_users']}
        - Total Gross Extracted Value: ${metrics['total_revenue_usd']:,}
        
    Sample Invoice File Row Architecture:
    {df_head}
    """

    try:
        # Execute streaming prompt against the recommended Gemini 3.6 Flash architecture model
        response = client.models.generate_content(
            model="gemini-3.6-flash", contents=prompt
        )

        return response.text

    except Exception as e:
        return f"AI generation trace failed during execution: {e}"


def automate_monthly_report():
    """Core data orchestration orchestrator coordinating ingestion, transformation, and AI reporting layers."""
    try:
        print("🚀 Starting automated ingestion pipeline loop...")

        # 1. ATTEMPT THIRD-PARTY INGESTION THROUGH INBOX stream
        df = get_invoices()
        print("Dataframe of invoices:", df)

        if df is not None:
            # Clean incoming invoice rows automatically using data rules
            df.columns = df.columns.str.strip().str.lower()
            if "billing" in df.columns:
                df["billing"] = pd.to_numeric(df["billing"], errors="coerce").fillna(
                    0.0
                )
            else:
                df["billing"] = 0.0
        else:
            print("ℹ️ Falling back to default baseline file system parameters.")
            # Local fallback mock dataframe execution path matching expected database attributes
            raw_fallback = [
                {"user_id": 101, "billing": 1250.00},
                {"user_id": 102, "billing": 3400.00},
                {"user_id": 103, "billing": 4120.00},
            ]
            df = pd.DataFrame(raw_fallback)

        # 2. RUN SYSTEM INFRASTRUCTURE CALCULATIONS
        total_accounts = int(df.shape[0])
        total_sum = float(df["billing"].sum()) if "billing" in df.columns else 0.0
        anomaly_flag = True if total_sum > 10000.0 else False

        metrics = {
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "total_active_users": total_accounts,
            "total_revenue_usd": round(total_sum, 2),
            "anomaly_detected": anomaly_flag,
            "ai_written_summary": "Processing engine summary context initialization pending...",
        }

        # 3. INTERSECT AI GENERATIVE ANALYTICS ENGINE LAYER
        sample_rows_string = df.head(2).to_string()
        ai_narrative = generate_ai_narrative_summary(metrics, sample_rows_string)
        metrics["ai_written_summary"] = ai_narrative

        # 4. ATOMICALLY OVERWRITE CACHE PERSISTENCE FRAMEWORK
        os.makedirs("./cache", exist_ok=True)
        with open("./cache/latest_report.json", "w") as f:
            json.dump(metrics, f, indent=4)

        print("✅ Production Data Automation Complete. System Cache Synced.")
        from tasks.parse_invoices import get_invoices
        master_df = get_invoices()
        print("📤 Pipelining data to Postgres SQL data store!")
        asyncio.run(pipeline_dataframe_to_sql(master_df))

    except Exception as e:
        print(f"❌ PIPELINE ERROR ALERT: {e}")


async def pipeline_dataframe_to_sql(df: pd.DataFrame):
    """Parses a structured metrics DataFrame and pipes rows asynchronously into PostgreSQL."""
    if df.empty:
        print("⚠️ Pipeline Execution Aborted:  Incoming DataFrame contains no rows.")
        return

    print(" 🚀 Initializing DataFrame to SQL Database pipeline context...")
    # 1. AUTOMATED COLUMN SANITIZATION
    # Strips accidental trailing whitespace and forces lowercasing to match definitions
    df.columns = df.columns.str.strip().str.lower()

    # 2. DATA CONVERSION LAYER
    # Ensures string dates are cast to native datetime.date objects for Postgres compliance
    if "signup_date" in df.columns:
        df["signup_date"] = pd.to_datetime(df["signup_date"]).dt.date

    # 3.  Automated Schema Initiallization
    # Generates the target 'master_invoices' table autmatically if it does not exist yet
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 4.  Convert Dataframe Rows into a Pure Python Dictionary Grid
    # Truncates Pandas datatypes to match native JSON/Python standard formats
    # records = df.to_dict(orient="records")

    # 4. FIX: Build an explicitly bound parameter List matching cless fields
    # This guarantees SQLALlchemy maps the valuesl to the right parameters
    bound_records = [
        {
            "user_id": int(row["user_id"]),
            "signup_date": row["signup_date"],
            "billing": float(row["billing"]),
            "source_file": str(row["source_file"]),
            "email_message_id": str(row["email_message_id"]),
        }
        for _, row in df.iterrows()
    ]

    # 5. Stream Records Directly across the Isolated Docker Bridge Network
    try:
        async with AsyncSession(engine) as session:
            async with session.begin():
                # Prepares a high-performance hatch insert mapping statement
                stmt = insert(MasterInvoice).values(bound_records)
                await session.execute(stmt)
        print(f"✅ Pipeline Completed! Successfully pushed {len(bound_records)}")
    except Exception as e:
        print(f"❌ DATABASE PIPEPINE WRITE ERROR: {e}")
        print(
            " 💡 Tip: Verify your Database column names which the table mapping exactly."
        )


if __name__ == "__main__":
    # Do your processing, math operations, or export pipelines here
    automate_monthly_report()
