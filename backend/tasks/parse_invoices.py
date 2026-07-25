import os
import base64
import io
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build

# API Permissions requested
SCOPES = ["https://mail.google.com/"]


def get_creds():
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    # It is created automatically when the authorization flow completes for the first time.
    if os.path.exists("./token.json"):
        creds = Credentials.from_authorized_user_file("./token.json", SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "./credentials.json", SCOPES
            )
            # Opens a local server to handle the browser authentication redirect
            creds = flow.run_local_server(
                host="localhost",
                port=8080,
                authorization_prompt_message="Please visit this URL to authorize this application: {url}",
                success_message="The authentication flow has completed. You may close this window.",
                open_browser=False,  # This stops the script from looking for a browser
            )

        # Save the credentials for the next run
        with open("./token.json", "w") as token:
            token.write(creds.to_json())
    return creds


def get_gmail_service():
    """Initializes the Gmail API service using Application Default Credentials."""
    try:
        # Automatically detects file path from GOOGLE_APPLICATION_CREDENTIALS env variable
        # service = build('gmail','v1')
        creds = get_creds()
        service = build("gmail", "v1", credentials=creds)
        return service
    except Exception as e:
        print(f"Error intializing Gmail clientr: {e}")


def fetch_unread_invoice_emails(service, user_id="me"):
    """Queries Gmail for unread emails matching 'invoice' or CSV hints."""
    try:
        # Search query looking for unread messages with CSV attachments or invoice keywords
        # If using Domain-Wide Delegation, swap 'me' for target user's email string
        query = "is:unread has:attachment filename:csv"

        response = service.users().messages().list(userId=user_id, q=query).execute()
        messages = response.get("messages", [])
        return messages
    except HttpError as error:
        print(f"An API error occurred: {error}")
        return []


def extract_csv_attachments(service, message_id, user_id="me"):
    """Finds, decodes, and parses CSV file attachments into Pandas DataFrames."""
    dataframes = {}
    try:
        message = (
            service.users().messages().get(userId=user_id, id=message_id).execute()
        )
        payload = message.get("payload", {})
        parts = payload.get("parts", [])

        # Walk through multi-part email structure to find attachements
        for part in parts:
            filename = part.get("filename")
            mime_type = part.get("mimeType")

            # Target CSV attachements specifically
            if filename and (filename.endswith(".csv") or mime_type == "text/csv"):
                attachment_id = part["body"].get("attachmentId")

                if attachment_id:
                    # Fetch raw binary chunk data for the attachment block
                    attachment = (
                        service.users()
                        .messages()
                        .attachments()
                        .get(userId=user_id, messageId=message_id, id=attachment_id)
                        .execute()
                    )

                    # Decode base64 bytes payload
                    file_data = base64.urlsafe_b64decode(
                        attachment["data"].encode("UTF-8")
                    )

                    # Convert raw bytes streams seamlessly into a Pandas DataFrame
                    df = pd.read_csv(io.BytesIO(file_data))
                    dataframes[filename] = df
                    print(
                        f"Successfully processed attachment: {filename} ({len(df)} rows found)"
                    )

                    # OPTIONAL: Mark message as read by removing the UNREAD Label
                    # service.user().messages().batchModify(
                    #   userId = user_id,
                    #   body={'ids': [message_id], 'removeLabelIds': ['UNREAD']}
                    # ).execute()

    except HttpError as error:
        print(f"Error extracting attachments from message {message_id}: {error}")

    return dataframes


def get_invoices():
    service = get_gmail_service()
    if not service:
        return

    print("Searching for unread invoice emails....")
    messages = fetch_unread_invoice_emails(service)

    if not messages:
        print("No matching unread emails with CSV attachements found.")

    all_invoice_dfs = []

    for msg in messages:
        print(f"Processing Message ID: {msg['id']}")
        dfs = extract_csv_attachments(service, msg["id"])

        for name, df in dfs.items():
            # Attach source metadata directly to the DataFrame raw records
            df["source_file"] = name
            df["email_message_id"] = msg["id"]
            all_invoice_dfs.append(df)

        # Master frame compilation example
        if all_invoice_dfs:
            master_df = pd.concat(all_invoice_dfs, ignore_index=True)
            print("\n--- Master Invoice DataFrame Sample ---")
            print(master_df.head())

    return master_df


async def pipeline_to_sql(df):
    from tasks.data_automation import pipeline_dataframe_to_sql

    await pipeline_dataframe_to_sql(df)
