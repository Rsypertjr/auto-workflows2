import asyncio
import pandas as pd
from tasks.data_automation import pipeline_dataframe_to_sql

async def test_live_pipeline():
    # All keys explicitly match MasterInvoice variable properties
    sample_data = {
        'user_id': [2041, 2042, 2043, 2044, 2041],
        'signup_date': ['2026-07-15', '2026-07-16', '2026-07-17', '2026-07-18', '2026-07-15'],
        'billing': [1250.00, 4300.50, 2210.00, 99.99, 1250.00],
        'source_file': [
            'invoice_20260722_044348.csv', 'invoice_20260722_044348.csv', 
            'invoice_20260722_044348.csv', 'invoice_20260722_044348.csv', 
            'invoice_20260721_212023.csv'
        ],
        'email_message_id': [
            '19f8823256f31ac6', '19f8823256f31ac6', '19f8823256f31ac6', 
            '19f8823256f31ac6', '19f868d2cb2a4d2e'
        ]
    }
    
    df = pd.DataFrame(sample_data)
    
    # Clean string date metrics converting them to true datetime structures for Postgres
    df['signup_date'] = pd.to_datetime(df['signup_date']).dt.date

    # Run the transaction
    await pipeline_dataframe_to_sql(df)

if __name__ == "__main__":
    asyncio.run(test_live_pipeline())
