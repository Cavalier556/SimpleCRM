import base64
import os.path
import pickle
import threading
from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup
from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Define the SCOPES. If modifying it, delete the token.pickle file.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Thread-local storage for Gmail service instances
thread_local = threading.local()


def get_credentials():
    creds = None
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:

            try:
                creds.refresh(Request())
            except RefreshError:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)

        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
            
    return creds


def get_service():
    """Returns a thread-specific Gmail service instance."""
    if not hasattr(thread_local, "service"):
        creds = get_credentials()
        thread_local.service = build("gmail", "v1", credentials=creds)
    return thread_local.service


def get_message_body(payload):
    """Recursively search for the best message body (HTML preferred)."""
    parts = []

    def collect_parts(p):
        if "parts" in p:
            for part in p["parts"]:
                collect_parts(part)
        elif "body" in p and "data" in p["body"]:
            parts.append(p)

    collect_parts(payload)
    # 1. Try to find HTML
    for p in parts:
        if p.get("mimeType") == "text/html":
            return base64.urlsafe_b64decode(p["body"]["data"]), "text/html"

    # 2. Fallback to plain text
    for p in parts:
        if p.get("mimeType") == "text/plain":
            return base64.urlsafe_b64decode(p["body"]["data"]), "text/plain"

    # 3. Fallback to first available part
    if parts:
        return base64.urlsafe_b64decode(parts[0]["body"]["data"]), parts[0].get(
            "mimeType"
        )

    return None, None


def process_single_message(msg):
    """Fetch and process a single message from Gmail."""
    service = get_service()
    try:
        # Optimization: Use 'fields' to fetch only necessary data
        # 'payload(headers,parts)' is needed for get_message_body and header extraction
        txt = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=msg["id"],
                fields="id,threadId,payload(headers,parts,body)",
            )
            .execute()
        )
        payload = txt.get("payload", {})
        headers = payload.get("headers", [])

        subject = "No Subject"
        sender = "Unknown Sender"
        recipient = "Unknown Recipient"
        date = "Unknown Date"
        for d in headers:
            if d["name"] == "Subject":
                subject = d["value"]
            if d["name"] == "From":
                sender = d["value"]
            if d["name"] == "To":
                recipient = d["value"]
            if d["name"] == "Date":
                date = d["value"]

        decoded_data, mime_type = get_message_body(payload)

        if decoded_data:
            soup = BeautifulSoup(decoded_data, "lxml")
            # Plain text summary
            text_summary = soup.get_text(separator=" ", strip=True)[:150] + "..."

            if mime_type == "text/html":
                # Extract body contents to avoid nested <html> tags
                if soup.body:
                    html_body = "".join([str(item) for item in soup.body.contents])
                else:
                    html_body = decoded_data.decode("utf-8", errors="ignore")
            else:
                # For plain text, convert newlines to <br> for basic HTML rendering
                html_body = decoded_data.decode("utf-8", errors="ignore").replace(
                    "\n", "<br>"
                )
        else:
            text_summary = "[No Body Content Found]"
            html_body = text_summary

        return {
            "id": msg["id"],
            "threadId": msg.get("threadId"),
            "subject": subject,
            "from": sender,
            "to": recipient,
            "date": date,
            "body": text_summary,
            "html_body": html_body,
        }

    except Exception as e:
        print(f"Error processing message {msg['id']}: {e}")
        return None


def extract_messages_data(messages):
    """Fetch all messages in parallel using a ThreadPoolExecutor."""
    if not messages:
        return []

    # Use ThreadPoolExecutor to fetch messages concurrently
    # max_workers=10 is a safe default for Gmail API
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(process_single_message, messages))

    # Filter out failed results
    return [r for r in results if r is not None]


def getEmails(max_results=10):
    service = get_service()
    result = (
        service.users().messages().list(userId="me", maxResults=max_results).execute()
    )
    messages = result.get("messages", [])
    return extract_messages_data(messages)


def getEmailsForAddress(address):
    service = get_service()

    # Query both sent to and received from the address
    query = f"from:{address} OR to:{address}"
    messages = []

    result = service.users().messages().list(userId="me", q=query).execute()
    messages.extend(result.get("messages", []))

    # Handle pagination
    while "nextPageToken" in result:
        page_token = result["nextPageToken"]
        result = (
            service.users()
            .messages()
            .list(userId="me", q=query, pageToken=page_token)
            .execute()
        )
        messages.extend(result.get("messages", []))

    # Sort messages by date might be needed, but Gmail API usually returns them descending
    return extract_messages_data(messages)


if __name__ == "__main__":
    pass
