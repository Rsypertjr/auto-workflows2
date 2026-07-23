import os
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import threading
import time

SCOPES = ['https://mail.google.com/']

def get_creds():
    creds = None 
    # token.json stores the user's access and refresh tokens 
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Inside Docker, Local server auth will fail unless ports are mapped    
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            
            creds = flow.run_local_server(
                port=8080,
                open_browser=False,
                prompt='consent'
            )
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds
            

def main():
   
    creds =   get_creds()  
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    
    print("Gmail Connection Successful.  Labels:")
    for label in labels:
        print(f" - {label['name']}")
        
        
if __name__ == '__main__':
    main()