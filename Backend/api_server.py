from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from deadline_extractor import DeadlineExtractor
from deadline_storage import DeadlineStorage
from email_reader import EmailReader
from notification_engine import NotificationEngine
import json
import os
import threading

# Initialize the Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS to allow React Native to connect

# Initialize components
storage = DeadlineStorage("deadlines.json")
extractor = DeadlineExtractor()

# Set up the notification handler
def handle_notification(notification):
    # This will be used later with WebSockets
    pass

# Initialize notification engine
notification_engine = NotificationEngine(storage)
notification_engine.add_notification_handler(handle_notification)
notification_engine.start(check_interval_minutes=15)

# API Authentication (simple token for now)
API_TOKEN = "your-secure-token"  # Change this to a secure token

def require_token(f):
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token != f"Bearer {API_TOKEN}":
            return abort(401, description="Unauthorized")
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# API Routes
@app.route('/api/deadlines', methods=['GET'])
@require_token
def get_deadlines():
    deadlines = storage.get_all_deadlines()
    return jsonify(deadlines)

@app.route('/api/deadlines/upcoming', methods=['GET'])
@require_token
def get_upcoming_deadlines():
    hours = request.args.get('hours', default=24, type=int)
    deadlines = storage.get_upcoming_deadlines(hours_ahead=hours)
    return jsonify(deadlines)

@app.route('/api/deadlines/<deadline_id>', methods=['GET'])
@require_token
def get_deadline(deadline_id):
    deadlines = storage.get_all_deadlines()
    for deadline in deadlines:
        if deadline.get('id') == deadline_id:
            return jsonify(deadline)
    return abort(404, description="Deadline not found")

@app.route('/api/deadlines/<deadline_id>', methods=['PUT'])
@require_token
def update_deadline(deadline_id):
    updated_data = request.json
    success = storage.update_deadline(deadline_id, updated_data)
    if success:
        return jsonify({"success": True})
    return abort(404, description="Failed to update deadline")

@app.route('/api/deadlines/<deadline_id>', methods=['DELETE'])
@require_token
def delete_deadline(deadline_id):
    success = storage.delete_deadline(deadline_id)
    if success:
        return jsonify({"success": True})
    return abort(404, description="Failed to delete deadline")

@app.route('/api/extract/email', methods=['POST'])
@require_token
def extract_from_email():
    """Extract deadlines from a single email"""
    email_data = request.json
    deadlines = extractor.extract_deadlines(email_data)
    count = storage.add_multiple_deadlines(deadlines)
    return jsonify({"added": count, "deadlines": deadlines})

@app.route('/api/sync/emails', methods=['POST'])
@require_token
def sync_emails():
    """Sync emails from IMAP server and extract deadlines"""
    data = request.json
    email_address = data.get('email')
    password = data.get('password')
    imap_server = data.get('imap_server', 'imap.gmail.com')
    days = data.get('days', 7)
    
    if not email_address or not password:
        return abort(400, description="Email and password required")
    
    reader = EmailReader(email_address, password, imap_server=imap_server)
    emails = reader.get_recent_emails(days=days)
    
    added_count = 0
    extracted_deadlines = []
    
    for email_data in emails:
        deadlines = extractor.extract_deadlines(email_data)
        count = storage.add_multiple_deadlines(deadlines)
        added_count += count
        extracted_deadlines.extend(deadlines)
    
    return jsonify({
        "processed_emails": len(emails),
        "added_deadlines": added_count,
        "deadlines": extracted_deadlines
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)