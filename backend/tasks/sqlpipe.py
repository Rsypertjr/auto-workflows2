import os
import base64
import io
import pandas as pd
import psycopg2
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def export_to_postgres_psycopg2(df):
    """Inserts the Master DataFrame into PostgreSQL using a raw psycopg2 connection."""
    if df.empty:
        print("DataFrame is empty. Skipping database insert.")
        return

    # Clean data: Replace Pandas NaN with Python None so psycopg2 converts them to SQL NULL
    cleaned_df = df.where(pd.notnull(df), None)

    # 1. Establish the explicit connection to the database
    connection = None
    try:
        connection = psycopg2.connect(
            host="127.0.0.1",  # Server address (or your remote Docker host IP)
            database="postgres",  # Name of your specific database
            user="postgres",  # Your PostgreSQL username
            password="SecureProdPassword2026!",  # Your PostgreSQL password
            port="5432",  # Your custom PostgreSQL port
        )

        cursor = connection.cursor()

        # 2. Prepare the dynamic insert query based on DataFrame column names
        columns = list(cleaned_df.columns)
        table_name = "invoice_records"

        # Generates: "INSERT INTO invoice_records (col1, col2) VALUES (%s, %s)"
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(['%s'] * len(columns))})"

        # 3. Convert rows into a tuple format required by psycopg2
        records_to_insert = [tuple(row) for row in cleaned_df.values]

        # 4. Perform an optimized batch execution bulk insert
        cursor.executemany(query, records_to_insert)

        # 5. Commit changes and cleanly wrap up contexts
        connection.commit()
        print(
            f"Successfully batch inserted {len(records_to_insert)} records into table '{table_name}'."
        )

        cursor.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error while connecting or inserting into PostgreSQL: {error}")
        if connection:
            connection.rollback()

    finally:
        if connection:
            connection.close()
            print("PostgreSQL connection is closed.")
