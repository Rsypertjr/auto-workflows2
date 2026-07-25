import os
import io
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from datetime import datetime
import pandas as pd

# --- GOOGLE SECURE WEB OAUTH COMPONENT CLIENTS ---
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Define the strict security clearance required to transmit data via Gmail API
SCOPES = ["https://mail.google.com/"]


def get_creds():
    creds = None
    # token.json stores the user's access and refresh tokens
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Inside Docker, Local server auth will fail unless ports are mapped
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)

            creds = flow.run_local_server(
                port=8080, open_browser=False, prompt="consent"
            )
        with open("token.json", "w") as token:
            token.write(creds.to_json())
            print(f"💾 Fresh access parameters cached to token.json successfully.")
    return creds


def generate_mock_invoice_csv() -> bytes:
    """Create a temporary, valid CSV invoice dataframe in memory."""
    print("📊 Generating dynamic mock invoice records...")

    mock_data = [
        {"user_id": 2041, "signup_date": "2026-07-15", "billing": 1250.00},
        {"user_id": 2042, "signup_date": "2026-07-16", "billing": 4300.50},
        {"user_id": 2043, "signup_date": "2026-07-17", "billing": 2210.00},
        {"user_id": 2044, "signup_date": "2026-07-18", "billing": 99.99},
    ]

    df = pd.DataFrame(mock_data)
    csv_buffer = io.BytesIO()
    df.to_csv(csv_buffer, index=False)
    return csv_buffer.getvalue()


def build_raw_mime_message() -> str:
    """Complies standard email layout rules into a base64 web-compatible string."""
    target_user = os.getenv("EMAIL_USER", "your_automated_billing_inbox@gmail.com")

    msg = MIMEMultipart()
    msg["From"] = target_user
    msg["To"] = target_user  # Loops back directly to yourself for isolation validation
    msg["Subject"] = (
        f"Automated Production Invoice Data - {datetime.now().strftime('%Y-%m-%d')}"
    )

    body = "System Notice: Please find attached the raw CSV processing invoice dataset matching today's production run."
    msg.attach(MIMEText(body, "plain"))

    # Inject the CSV stream attachment asset
    csv_bytes = generate_mock_invoice_csv()
    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(csv_bytes)
    encode_base64(attachment)

    attachment.add_header(
        "Content-Disposition",
        f'attachment; filename="invoice_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"',
    )
    msg.attach(attachment)

    # Gmail Web API expects transmission blocks stringified in urlsafe base64 structure
    raw_string = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
    return {"raw": raw_string}


def send_test_invoice_email():
    """Authenticates via Web OAuth and posts the data message to the Gmail API router."""
    #token_path = "token.json"# Resolve the absolute path to your key file inside the container
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    service_account_json = os.path.join(base_dir, 'service_account.json')
    
    #credentials_json = "credentials.json"  # App credentials from Google Cloud Console
    creds = None

    # 1. Look for existing saved authentication configurations
    #if os.path.exists(token_path):
        #creds = Credentials.from_authorized_user_file(token_path, SCOPES)           
    
    if not os.path.exists(service_account_json):
        print(f"❌ Error: Automated key missing at path: {service_account_json}")
        return

    # 2. Trigger the requested Login server challenge flow if no cache tokens exit
    #creds = get_creds()
    try:
        # Load the credentials directly without opening any browser servers
        creds = service_account.Credentials.from_service_account_file(
            service_account_json, 
            scopes=SCOPES
        ).with_subject('richardsypertjr@gmail.com')
        
        print(" 📡 Connecting to Gmail REST API Engine over Port 443...")
        service = build("gmail", "v1", credentials=creds)

        email_payload = build_raw_mime_message()
        print(" 📤 Sending encrypted transmission block...")

        service.users().messages().send(userId="me", body=email_payload).execute()
        print("✅ Success! Test web-invoice sent safely via Google API.")
    except Exception as e:
        print(f"❌ Gmaill Web API Transmission Error: {e}")


if __name__ == "__main__":
    send_test_invoice_email()
