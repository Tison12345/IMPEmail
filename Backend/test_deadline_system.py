# test_deadline_system.py
from email_reader import EmailReader
from deadline_extractor import DeadlineExtractor
from deadline_storage import DeadlineStorage
from notification_engine import NotificationEngine
import json

# Email credentials from the code
EMAIL = "mominiiitdwd@gmail.com"
PASSWORD = "diqp shib zdex halu"

# Create a test notification handler
def print_notification(notification):
    print("\n=== NOTIFICATION ===")
    print(f"Subject: {notification['subject']}")
    print(f"Body: {notification['body']}")
    print("====================\n")

# Initialize components
print("Initializing components...")
storage = DeadlineStorage("test_deadlines.json")
extractor = DeadlineExtractor()
notification_engine = NotificationEngine(storage)
notification_engine.add_notification_handler(print_notification)

# Connect to email and fetch recent messages
print(f"Connecting to email {EMAIL}...")
reader = EmailReader(EMAIL, PASSWORD)
emails = reader.get_recent_emails(days=30, limit=50)  # Get more emails for testing
print(f"Found {len(emails)} recent emails")

# Process each email
print("Processing emails for deadlines...")
total_deadlines = 0
new_deadlines = 0

for i, email_data in enumerate(emails):
    print(f"\nEmail {i+1}/{len(emails)}: {email_data['subject']}")
    deadlines = extractor.extract_deadlines(email_data)
    total_deadlines += len(deadlines)
    
    if deadlines:
        count = storage.add_multiple_deadlines(deadlines)
        new_deadlines += count
        print(f"  Found {len(deadlines)} deadlines, {count} new ones added")
        
        for dl in deadlines:
            print(f"  - Task: {dl['task']}")
            print(f"    Due: {dl['deadline']}")
            print(f"    Confidence: {dl.get('confidence', 'unknown')}")
    else:
        print("  No deadlines found")

print(f"\nTotal deadlines found: {total_deadlines}")
print(f"New deadlines added: {new_deadlines}")

# Display all stored deadlines
all_deadlines = storage.get_all_deadlines()
print(f"\nAll stored deadlines ({len(all_deadlines)}):")
for dl in all_deadlines:
    print(f"- {dl['task']} (Due: {dl['deadline']})")

# Check upcoming deadlines
print("\nChecking for upcoming deadlines...")
notification_engine.check_upcoming_deadlines()