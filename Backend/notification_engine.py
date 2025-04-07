import datetime
import time
import schedule
import threading
import json
import os
import requests
from typing import Dict, Any, List, Optional, Callable

class NotificationEngine:
    def __init__(self, 
                 storage_instance, 
                 llm_api_url="http://localhost:11434/api/generate",
                 notification_file="notifications.json"):
        """Initialize notification engine with storage and API info."""
        self.storage = storage_instance
        self.llm_api_url = llm_api_url
        self.notification_file = notification_file
        self.model_name = "mistral"
        self.notification_schedules = {}  # Track scheduled notifications
        self.running = False
        self.notification_handlers = []  # Callbacks for notifications
        
        # Create notification file if it doesn't exist
        if not os.path.exists(notification_file):
            with open(notification_file, 'w') as f:
                json.dump([], f)
    
    def add_notification_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Add a callback function to handle notifications."""
        self.notification_handlers.append(handler)
    
    def start(self, check_interval_minutes=15):
        """Start the notification scheduler."""
        if self.running:
            return
        
        self.running = True
        
        # Schedule regular checks
        schedule.every(check_interval_minutes).minutes.do(self.check_upcoming_deadlines)
        
        # Start the scheduler in a background thread
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        print(f"Notification engine started, checking every {check_interval_minutes} minutes")
    
    def stop(self):
        """Stop the notification scheduler."""
        self.running = False
        schedule.clear()
        print("Notification engine stopped")
    
    def _run_scheduler(self):
        """Run the scheduler loop."""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def check_upcoming_deadlines(self):
        """Check for upcoming deadlines and schedule notifications."""
        print("Checking for upcoming deadlines...")
        
        # Get deadlines for the next 48 hours
        upcoming = self.storage.get_upcoming_deadlines(hours_ahead=48)
        
        if not upcoming:
            print("No upcoming deadlines found")
            return
        
        # Process each deadline
        for deadline in upcoming:
            self._process_deadline_notification(deadline)
    
    def _process_deadline_notification(self, deadline: Dict[str, Any]):
        """Process a single deadline for notification."""
        deadline_id = deadline.get('id')
        
        if not deadline_id:
            return
        
        # Skip if already processed recently
        if self._is_recently_notified(deadline_id):
            return
        
        # Get the deadline datetime
        deadline_date = self._parse_deadline_date(deadline.get('deadline'))
        if not deadline_date:
            return
        
        # Calculate time until deadline
        now = datetime.datetime.now()
        time_until = deadline_date - now
        
        # Skip if deadline has passed
        if time_until.total_seconds() <= 0:
            return
        
        hours_until = time_until.total_seconds() / 3600
        
        # Determine when to send notifications
        notification_times = self._get_notification_times(hours_until)
        
        for notification_time in notification_times:
            self._schedule_notification(deadline, notification_time)
    
    def _parse_deadline_date(self, date_str: Optional[str]) -> Optional[datetime.datetime]:
        """Parse a deadline date string into a datetime object."""
        if not date_str:
            return None
            
        try:
            return datetime.datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            try:
                # Try alternative format
                return datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                print(f"Could not parse deadline date: {date_str}")
                return None
    
    def _is_recently_notified(self, deadline_id: str) -> bool:
        """Check if a notification was recently sent for this deadline."""
        try:
            # Load existing notifications
            with open(self.notification_file, 'r') as f:
                notifications = json.load(f)
            
            # Check for recent notifications for this deadline
            now = datetime.datetime.now()
            for notification in notifications:
                if notification.get('deadline_id') == deadline_id:
                    # Check if notification was sent in the last hour
                    notification_time = datetime.datetime.fromisoformat(notification.get('timestamp'))
                    if (now - notification_time).total_seconds() < 3600:
                        return True
                        
            return False
        except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
            print(f"Error checking recent notifications: {e}")
            return False
    
    def _get_notification_times(self, hours_until: float) -> List[float]:
        """Determine appropriate notification times based on time until deadline."""
        notification_times = []
        
        # Notification thresholds in hours
        thresholds = [1, 3, 24, 48]
        
        for threshold in thresholds:
            # If deadline is beyond this threshold, notify at this point
            if hours_until > threshold and hours_until - threshold < 1:
                notification_times.append(threshold)
        
        # If very close to deadline (< 1 hour), notify immediately
        if 0 < hours_until < 1:
            notification_times.append(0)  # 0 means immediately
        
        return notification_times
    
    def _schedule_notification(self, deadline: Dict[str, Any], hours_before: float):
        """Schedule a notification for a deadline."""
        deadline_id = deadline.get('id')
        
        # If immediate notification
        if hours_before == 0:
            self._send_notification(deadline)
            return
        
        # Calculate notification time
        deadline_date = self._parse_deadline_date(deadline.get('deadline'))
        if not deadline_date:
            return
            
        notification_time = deadline_date - datetime.timedelta(hours=hours_before)
        
        # Skip if notification time has passed
        if notification_time < datetime.datetime.now():
            return
        
        # Create a unique key for this notification
        notification_key = f"{deadline_id}_{hours_before}"
        
        # Skip if already scheduled
        if notification_key in self.notification_schedules:
            return
        
        # Schedule the notification
        job = schedule.every().day.at(notification_time.strftime("%H:%M")).do(
            self._send_notification, deadline, hours_before
        )
        
        self.notification_schedules[notification_key] = job
        print(f"Scheduled notification for '{deadline.get('task')}' at {notification_time}")
    
    def _send_notification(self, deadline: Dict[str, Any], hours_before: Optional[float] = None):
        """Generate and send a notification for a deadline."""
        notification_content = self._generate_notification_content(deadline, hours_before)
        
        # Record that we've sent a notification
        self._record_notification(deadline.get('id'), notification_content)
        
        # Call notification handlers
        for handler in self.notification_handlers:
            try:
                handler(notification_content)
            except Exception as e:
                print(f"Error in notification handler: {e}")
        
        print(f"Notification sent for: {deadline.get('task')}")
        
        # Remove from schedule if it exists
        if hours_before is not None:
            notification_key = f"{deadline.get('id')}_{hours_before}"
            if notification_key in self.notification_schedules:
                schedule.cancel_job(self.notification_schedules[notification_key])
                del self.notification_schedules[notification_key]
    
    def _generate_notification_content(self, deadline: Dict[str, Any], hours_before: Optional[float] = None) -> Dict[str, Any]:
        """Generate the content for a notification using the LLM."""
        task = deadline.get('task', 'Unknown task')
        deadline_date = self._parse_deadline_date(deadline.get('deadline'))
        deadline_str = deadline_date.strftime("%Y-%m-%d %H:%M") if deadline_date else "Unknown time"
        details = deadline.get('details', '')
        
        # Time context
        time_context = "approaching soon"
        if hours_before is not None:
            if hours_before == 1:
                time_context = "in 1 hour"
            elif hours_before == 3:
                time_context = "in 3 hours"
            elif hours_before == 24:
                time_context = "in 1 day"
            elif hours_before == 48:
                time_context = "in 2 days"
        
        # Try to use LLM for personalized message
        llm_content = self._get_llm_notification(task, deadline_str, time_context, details)
        
        if llm_content and 'subject' in llm_content and 'body' in llm_content:
            notification = {
                'id': f"notif_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                'deadline_id': deadline.get('id'),
                'task': task,
                'deadline_date': deadline_str,
                'time_context': time_context,
                'subject': llm_content['subject'],
                'body': llm_content['body'],
                'timestamp': datetime.datetime.now().isoformat()
            }
        else:
            # Fallback to template
            notification = {
                'id': f"notif_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                'deadline_id': deadline.get('id'),
                'task': task,
                'deadline_date': deadline_str,
                'time_context': time_context,
                'subject': f"REMINDER: {task} due {time_context}",
                'body': f"This is a reminder that '{task}' is due {time_context} ({deadline_str}).\n\n{details}"
            }
        
        return notification
    
    def _get_llm_notification(self, task: str, deadline_str: str, time_context: str, details: str) -> Optional[Dict[str, str]]:
        """Generate a personalized notification using the LLM API."""
        try:
            prompt = f"""
            Generate a friendly reminder notification for the following task:
            Task: {task}
            Deadline: {deadline_str}
            Time until deadline: {time_context}
            Additional details: {details}
            
            Please generate a JSON with 'subject' and 'body' fields for the notification.
            Keep the subject under 80 characters and the body concise but informative.
            The tone should be professional but friendly.
            """
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "temperature": 0.7,
                "max_tokens": 200
            }
            
            response = requests.post(self.llm_api_url, json=payload, timeout=5)
            
            if response.status_code == 200:
                result = response.json()
                # Extract the generated text from the API response
                generated_text = result.get('response', '')
                
                # Try to parse as JSON
                try:
                    # Find JSON in the response if it's embedded
                    import re
                    json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        content = json.loads(json_str)
                        
                        # Ensure required fields exist
                        if 'subject' in content and 'body' in content:
                            return content
                except (json.JSONDecodeError, AttributeError):
                    print("Failed to parse LLM response as JSON")
            
            return None
        except Exception as e:
            print(f"Error generating LLM notification: {e}")
            return None
    
    def _record_notification(self, deadline_id: str, notification: Dict[str, Any]):
        """Record a sent notification to the notifications file."""
        try:
            # Load existing notifications
            with open(self.notification_file, 'r') as f:
                notifications = json.load(f)
            
            # Add new notification
            notifications.append(notification)
            
            # Trim to last 100 notifications to prevent file growth
            if len(notifications) > 100:
                notifications = notifications[-100:]
            
            # Save updated notifications
            with open(self.notification_file, 'w') as f:
                json.dump(notifications, f, indent=2)
                
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error recording notification: {e}")
            # Create new file with just this notification
            with open(self.notification_file, 'w') as f:
                json.dump([notification], f, indent=2)