📩 Jarvis AI – Gmail Email Notifier & Chatbot

Jarvis AI is a Streamlit-based personal assistant that:

Connects to Gmail using the Gmail API.

Continuously checks for important emails in the background.

Sends push notifications (via webhook/URL) for important senders.

Summarizes email content using Mistral (via Ollama).

Provides a chat interface with intent detection (email checking or general chat).

🚀 Features

✅ Gmail API Authentication (OAuth2 with token storage).

✅ Background email monitoring with threading.

✅ Push notifications to a custom URL when important emails arrive.

✅ Summarized emails in 10 words or fewer.

✅ Streamlit UI for interaction.

✅ Keyword-based intent detection (fetch emails, chat, exit).

📦 Requirements

Install dependencies:

pip install streamlit google-auth google-auth-oauthlib google-api-python-client spacy requests
python -m spacy download en_core_web_sm


You also need:

Ollama
 installed locally (for Mistral summarization & chatbot).

A Gmail OAuth2 client secret JSON file from Google Cloud.

A Push Notification endpoint URL (e.g., Discord, Slack, Teams webhook, or custom API).

⚙️ Setup

Clone the repo (or copy the script):

git clone <your-repo-url>
cd <your-project>


Add credentials & config:

Place your Gmail credentials.json in the project root.

Edit the script and set:

CLIENT_SECRET_FILE = "credentials.json"
PUSH_NOTIFICATION_URL = "https://your-webhook-url"


Run the app:

streamlit run app.py


On first run, the app will open a Google login page in your browser.

Sign in with the Gmail account you want to monitor.

A token.pickle file will be saved for future sessions.

🔑 Configuration
Important Senders

Edit the list in the script:

IMPORTANT_SENDERS = [
    "example1@email.com",
    "example2@email.com"
]

Intents (chat commands)
INTENTS = {
    "fetch_emails": ["fetch emails", "check emails", "get emails"],
    "exit": ["exit", "goodbye", "quit"],
    "chat": ["tell"]
}

🖥️ Usage

Launch the app with:

streamlit run app.py


In the chat box, type:

"check emails" → fetches and summarizes recent important emails.

"exit" → closes the assistant.

Anything else → sends to Ollama (Mistral) for chat.

New important emails trigger a push notification and display inside Streamlit.

📌 Example Notification
📩 New Important Email!
From: john@example.com
Subject: Meeting Update
📌 Summary: Meeting rescheduled to tomorrow at 10am

⚠️ Known Issues / Notes

If Ollama or Mistral is not running, summaries and chat won’t work.

Emails with only HTML bodies may not summarize correctly.

Push notifications require a valid PUSH_NOTIFICATION_URL.

Gmail API quota limits may apply.

📜 License

MIT License – free to use and modify.
