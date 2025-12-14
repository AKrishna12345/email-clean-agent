"""
Gmail API Service
Handles fetching emails from Gmail API
"""
from googleapiclient.discovery import build
from google.auth.transport.requests import Request as GoogleRequest
from datetime import datetime
import base64
import re
from typing import List, Dict, Optional
from database import User
from auth import get_user_credentials, refresh_user_token


def get_gmail_service(user: User, db) -> Optional[object]:
    """
    Get authenticated Gmail service for a user
    Refreshes token if needed
    """
    try:
        # Refresh token if expired
        refresh_user_token(user, db)
        
        # Get credentials
        credentials = get_user_credentials(user)
        
        # Build Gmail service
        service = build('gmail', 'v1', credentials=credentials)
        return service
    except Exception as e:
        print(f"Error building Gmail service: {e}")
        return None


def get_email_ids(user: User, count: int, db) -> List[str]:
    """
    Phase 1: Fetch email IDs from Gmail
    Returns list of message IDs
    """
    print(f"\n{'='*60}")
    print(f"PHASE 1: Fetching email IDs (count: {count})")
    print(f"{'='*60}")
    
    service = get_gmail_service(user, db)
    if not service:
        raise Exception("Failed to get Gmail service")
    
    try:
        # Fetch message list - only from Primary inbox (excludes Promotions, Social, Updates, etc.)
        # Note: CATEGORY_PRIMARY cannot be used in labelIds, must use query parameter instead
        results = service.users().messages().list(
            userId='me',
            maxResults=count,
            labelIds=['INBOX'],  # Only inbox emails
            q='in:inbox category:primary'  # Filter for Primary tab only (excludes Promotions, Social, Updates)
        ).execute()
        
        messages = results.get('messages', [])
        message_ids = [msg['id'] for msg in messages]
        
        print(f"✅ Successfully fetched {len(message_ids)} email IDs")
        print(f"Message IDs: {message_ids[:5]}..." if len(message_ids) > 5 else f"Message IDs: {message_ids}")
        
        return message_ids
    except Exception as e:
        print(f"❌ Error fetching email IDs: {e}")
        raise


def decode_email_body(data: str) -> str:
    """
    Decode base64 email body
    """
    try:
        # Remove any whitespace/newlines
        data = data.replace('-', '+').replace('_', '/')
        # Add padding if needed
        missing_padding = len(data) % 4
        if missing_padding:
            data += '=' * (4 - missing_padding)
        decoded = base64.urlsafe_b64decode(data)
        return decoded.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Warning: Error decoding email body: {e}")
        return ""


def parse_email_headers(headers: List[Dict]) -> Dict[str, str]:
    """
    Parse email headers into a dictionary
    """
    parsed = {}
    for header in headers:
        name = header.get('name', '').lower()
        value = header.get('value', '')
        parsed[name] = value
    return parsed


def extract_email_body(message_data: Dict) -> str:
    """
    Extract email body from message data
    Handles both plain text and HTML
    """
    body = ""
    
    # Check if message has payload
    payload = message_data.get('payload', {})
    
    # Get body from payload
    body_data = payload.get('body', {})
    if body_data.get('data'):
        body = decode_email_body(body_data['data'])
    
    # If no body in main payload, check parts (for multipart messages)
    if not body and 'parts' in payload:
        for part in payload['parts']:
            mime_type = part.get('mimeType', '')
            if mime_type == 'text/plain':
                body_data = part.get('body', {})
                if body_data.get('data'):
                    body = decode_email_body(body_data['data'])
                    break
            elif mime_type == 'text/html' and not body:
                # Fallback to HTML if no plain text
                body_data = part.get('body', {})
                if body_data.get('data'):
                    body = decode_email_body(body_data['data'])
    
    return body


def get_email_batch(service, message_ids: List[str]) -> List[Dict]:
    """
    Phase 2: Batch fetch full email messages
    Returns list of parsed email data
    """
    print(f"\n{'='*60}")
    print(f"PHASE 2: Fetching full email content ({len(message_ids)} emails)")
    print(f"{'='*60}")
    
    emails = []
    batch_size = 10  # Process in batches to avoid rate limits
    
    for i in range(0, len(message_ids), batch_size):
        batch = message_ids[i:i + batch_size]
        print(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} emails)...")
        
        for msg_id in batch:
            try:
                # Fetch full message
                message = service.users().messages().get(
                    userId='me',
                    id=msg_id,
                    format='full'
                ).execute()
                
                # Parse message
                email_data = parse_email_message(message)
                emails.append(email_data)
                
                print(f"  ✅ Fetched: {email_data.get('subject', 'No subject')[:50]}")
                
            except Exception as e:
                print(f"  ❌ Error fetching message {msg_id}: {e}")
                continue
    
    print(f"\n✅ Successfully fetched {len(emails)} full emails")
    return emails


def parse_email_message(message: Dict) -> Dict:
    """
    Parse a Gmail message into structured format
    """
    msg_id = message.get('id', '')
    payload = message.get('payload', {})
    headers = parse_email_headers(payload.get('headers', []))
    
    # Extract key fields
    subject = headers.get('subject', 'No Subject')
    sender = headers.get('from', 'Unknown Sender')
    date_str = headers.get('date', '')
    
    # Parse date
    try:
        # Try to parse the date string
        date = datetime.fromisoformat(date_str.replace('+', '+').replace('-', '-'))
    except:
        date = datetime.utcnow()
    
    # Extract email body
    body = extract_email_body(message)
    
    # Get snippet (preview)
    snippet = message.get('snippet', '')
    
    # Get labels
    label_ids = message.get('labelIds', [])
    
    # Extract email address from sender
    sender_email = sender
    if '<' in sender and '>' in sender:
        match = re.search(r'<([^>]+)>', sender)
        if match:
            sender_email = match.group(1)
    
    email_data = {
        'id': msg_id,
        'subject': subject,
        'from': sender_email,
        'from_name': sender.split('<')[0].strip() if '<' in sender else sender,
        'body': body,
        'snippet': snippet,
        'date': date.isoformat() if isinstance(date, datetime) else date,
        'labels': label_ids,
        'thread_id': message.get('threadId', '')
    }
    
    return email_data


def fetch_emails(user: User, count: int, db) -> Dict:
    """
    Main function to fetch emails from Gmail
    Returns structured email data
    """
    print(f"\n{'='*80}")
    print(f"FETCHING EMAILS FOR: {user.email}")
    print(f"Requested count: {count}")
    print(f"{'='*80}\n")
    
    try:
        # Phase 1: Get email IDs
        message_ids = get_email_ids(user, count, db)
        
        if not message_ids:
            print("⚠️  No emails found in inbox")
            return {
                'message': 'No emails found',
                'requested_count': count,
                'actual_count': 0,
                'emails': []
            }
        
        # Phase 2: Get full email content
        service = get_gmail_service(user, db)
        emails = get_email_batch(service, message_ids)
        
        # Print all email data for verification
        print(f"\n{'='*80}")
        print("ALL EMAIL DATA (for verification):")
        print(f"{'='*80}\n")
        
        for i, email in enumerate(emails, 1):
            print(f"\n--- Email {i}/{len(emails)} ---")
            print(f"ID: {email['id']}")
            print(f"Subject: {email['subject']}")
            print(f"From: {email['from']} ({email['from_name']})")
            print(f"Date: {email['date']}")
            print(f"Snippet: {email['snippet'][:100]}...")
            print(f"Body length: {len(email['body'])} characters")
            print(f"Body preview: {email['body'][:200]}...")
            print(f"Labels: {', '.join(email['labels'])}")
            print("-" * 80)
        
        print(f"\n{'='*80}")
        print(f"SUMMARY:")
        print(f"  Requested: {count} emails")
        print(f"  Fetched: {len(emails)} emails")
        print(f"  Success rate: {len(emails)/len(message_ids)*100:.1f}%")
        print(f"{'='*80}\n")
        
        return {
            'message': 'Emails fetched successfully',
            'requested_count': count,
            'actual_count': len(emails),
            'emails': emails
        }
        
    except Exception as e:
        print(f"\n❌ Error fetching emails: {e}")
        import traceback
        print(traceback.format_exc())
        raise

