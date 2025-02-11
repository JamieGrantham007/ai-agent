import subprocess
import streamlit as st
import pickle
import os
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request  
import spacy
import requests 
import time 
import threading

PUSH_NOTIFICATION_URL = 

nlp = spacy.load("en_core_web_sm")

# Gmail API setup
SCOPES = ['https://www.googleapis.com/auth/gmail.modify','https://www.googleapis.com/auth/gmail.readonly' ] 
CLIENT_SECRET_FILE = 
API_NAME = 'gmail'
API_VERSION = 'v1'

INTENTS = { 
    "fetch_emails": ["fetch emails", "check emails", "emails", "get emails", "check my emails"],
    "exit": ["exit", "goodbye", "bye", "close", "quit"],
    "chat": ["tell"]
}

IMPORTANT_SENDERS = ["19-salman@ewellcastle.co.uk", "19-mogg@ewellcastle.co.uk"]  # 🔹 Always lowercase for case-insensitive comparison

# Initialize the session state for 'last_notified_email' if it doesn't exist.
if "last_notified_email" not in st.session_state:
    st.session_state["last_notified_email"] = None  # Initialize with None or appropriate value.

if "conversation" not in st.session_state:
    st.session_state.conversation = [{"role": "system", "content": "You are a chatbot"}]

def authenticate_gmail():
    """Authenticate and get an access token."""
    creds = None
    
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=5001)  

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def send_notification(sender, subject):
    """Send a push notification to the iPhone using Pushcut."""
    message = {
        "text": f"📩 New Important Email!\nFrom: {sender}\nSubject: {subject}"
    }

    response = requests.post(PUSH_NOTIFICATION_URL, json=message)

    if response.status_code == 200:
        print("📲 Notification sent successfully")
    else:
        print("⚠️ Failed to send notification:", response.text)

def mark_email_as_read(service, email_id):
    """Mark email as read to prevent duplicate notifications."""
    service.users().messages().modify(userId='me', id=email_id, body={'removeLabelIds': ['UNREAD']}).execute()

def check_emails_loop():
    """Continuously check for important emails every 10 seconds."""
    while True:
        try:
            # Ensure session state is initialized within the thread context
            if "last_notified_email" not in st.session_state:
                st.session_state["last_notified_email"] = None
            fetch_emails()
        except Exception as e:
            print(f"Error fetching emails: {e}")
        time.sleep(2)

def fetch_emails():
    """Fetch unread emails and send notifications for important ones."""
    creds = authenticate_gmail()
    service = build(API_NAME, API_VERSION, credentials=creds)
    
    try:
        # Fetch only unread emails (modify query as needed)
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
        messages = results.get('messages', [])

        if not messages:
            return ["No new emails"]

        email_data = []
        new_email_found = False

        for message in messages[:5]: 
            email_id = message['id']
            

            # Avoid duplicate notifications by checking last notified email
            if st.session_state.last_notified_email == email_id:
                continue  

            try:
                # Get the email data for the given message ID
                msg = service.users().messages().get(userId='me', id=email_id).execute()
            except Exception as e:
                print(f"Error fetching email with ID {email_id}: {e}")
                continue  # Skip if email can't be fetched

            subject = next((header['value'] for header in msg['payload']['headers'] if header['name'] == 'Subject'), "No Subject")
            sender = next((header['value'] for header in msg['payload']['headers'] if header['name'] == 'From'), "Unknown Sender")

            email_data.append(f"From: {sender} | Subject: {subject}")

            # Normalize sender email to lowercase for case-insensitive matching
            sender_email = sender.lower()

            if any(important_sender in sender_email for important_sender in IMPORTANT_SENDERS):
                send_notification(sender, subject)
                new_email_found = True

                # Mark email as read to prevent repeated notifications
                mark_email_as_read(service, email_id)

                # Update last notified email ID
                st.session_state.last_notified_email = email_id

        return email_data if new_email_found else ["No important emails found."]
    
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return ["Error fetching emails."]

# Start the email checking loop in a background thread
if "thread_started" not in st.session_state:
    threading.Thread(target=check_emails_loop, daemon=True).start()
    st.session_state["thread_started"] = True

# Add the title to the app
st.title("Jarvis AI")

# Input box for user queries
user_input = st.text_input("You: ", key="user_input")

# Intent detection
def detect_intents(user_input):
    """Detect user intents based on predefined keywords."""
    doc = nlp(user_input.lower())
    detected_intents = set()

    for intent, keywords in INTENTS.items():
        if any(keyword in user_input.lower() for keyword in keywords):
            detected_intents.add(intent)
        
    for token in doc:
        if token.lemma_ in ["fetch", "check", "get", "read"] and "email" in user_input.lower():
            detected_intents.add("fetch_emails")

    return detected_intents if detected_intents else {"chat"}

def chat_with_ollama(prompt):
    st.session_state.conversation.append({"role": "user", "content": prompt})  
    formatted_prompt = "\n".join([f"{i['role']}: {i['content']}" for i in st.session_state.conversation])
    result = subprocess.run(['ollama', "run", "mistral", formatted_prompt], capture_output=True, text=True)  
    response = result.stdout.strip()

    st.session_state.conversation.append({"role": "ollama", "content": response})  
    return response
if user_input:
    detected_intents = detect_intents(user_input)

    for intent in detected_intents:
        if intent == "exit":
            st.write("Jarvis: Goodbye!")
            break
        elif intent == "fetch_emails":
            try:
                emails = fetch_emails()
                st.write("Emails:")
                for email in emails:
                    st.write(email)
            except Exception as e:
                st.write(f"Error fetching emails: {e}")
        else:
            prompt = user_input + " make it really short"
            response = chat_with_ollama(prompt)
            st.write("Jarvis: ", response)
