import imaplib
import email
from email.header import decode_header
import datetime
import dateutil.parser
import re
import os
from typing import List, Dict, Any, Tuple

class EmailReader:
    def __init__(self, email_address, password, imap_server="imap.gmail.com", imap_port=993):
        """Initialize email reader with credentials."""
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.connection = None
    
    def connect(self) -> bool:
        """Establish connection to the IMAP server."""
        try:
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.connection.login(self.email_address, self.password)
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Close the IMAP connection."""
        if self.connection:
            try:
                self.connection.close()
                self.connection.logout()
            except:
                pass
    
    def get_recent_emails(self, folder="INBOX", days=7, limit=50) -> List[Dict[str, Any]]:
        """Fetch recent emails from specified folder."""
        if not self.connection:
            if not self.connect():
                return []
        
        emails_data = []
        try:
            status, messages = self.connection.select(folder)
            if status != "OK":
                print(f"Error selecting folder: {status}")
                return []
            
            # Calculate date from days ago
            date_since = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%d-%b-%Y")
            status, data = self.connection.search(None, f'(SINCE "{date_since}")')
            
            if status != "OK":
                print("No messages found!")
                return []
            
            # Get message IDs and process the most recent ones first (up to limit)
            message_ids = data[0].split()
            message_ids = message_ids[-limit:] if limit and len(message_ids) > limit else message_ids
            
            for message_id in reversed(message_ids):
                status, msg_data = self.connection.fetch(message_id, "(RFC822)")
                if status != "OK":
                    continue
                
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                # Extract basic email information
                subject = self._decode_email_header(email_message.get("Subject", ""))
                from_address = self._decode_email_header(email_message.get("From", ""))
                date_str = email_message.get("Date", "")
                
                try:
                    date = dateutil.parser.parse(date_str) if date_str else None
                except:
                    date = None
                
                # Extract email body
                body = self._get_email_body(email_message)
                
                emails_data.append({
                    "id": message_id.decode(),
                    "subject": subject,
                    "from": from_address,
                    "date": date,
                    "body": body
                })
            
            return emails_data
        
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
        finally:
            self.disconnect()
    
    def _decode_email_header(self, header):
        """Decode email header to readable format."""
        if not header:
            return ""
        
        decoded_parts = []
        for part, encoding in decode_header(header):
            if isinstance(part, bytes):
                try:
                    if encoding:
                        decoded_parts.append(part.decode(encoding))
                    else:
                        decoded_parts.append(part.decode())
                except:
                    decoded_parts.append(part.decode('utf-8', errors='replace'))
            else:
                decoded_parts.append(part)
        
        return ''.join([str(part) for part in decoded_parts])
    
    def _get_email_body(self, email_message):
        """Extract email body, preferring plain text over HTML."""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Skip attachments
                if "attachment" in content_disposition:
                    continue
                
                # Get text content
                if content_type == "text/plain":
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        body = part.get_payload(decode=True).decode(charset, errors='replace')
                        break  # Prefer plain text
                    except:
                        continue
                
                # Fallback to HTML if no plain text
                elif content_type == "text/html" and not body:
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        body = part.get_payload(decode=True).decode(charset, errors='replace')
                    except:
                        continue
        else:
            # Not multipart - get payload directly
            content_type = email_message.get_content_type()
            try:
                charset = email_message.get_content_charset() or 'utf-8'
                body = email_message.get_payload(decode=True).decode(charset, errors='replace')
            except:
                body = ""
        
        return body

# Usage example
if __name__ == "__main__":
    # Test the email reader (do not store credentials in code for production)
    reader = EmailReader("mominiiitdwd@gmail.com", "diqp shib zdex halu")
    emails = reader.get_recent_emails(days=3, limit=10)
    for email in emails:
        print(f"Subject: {email['subject']}")
        print(f"From: {email['from']}")
        print(f"Date: {email['date']}")
        print("=" * 50)