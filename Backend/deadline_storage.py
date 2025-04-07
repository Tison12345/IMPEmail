import json
import os
import datetime
from typing import List, Dict, Any, Optional
import threading

class DeadlineStorage:
    def __init__(self, storage_file="deadlines.json"):
        """Initialize storage with the path to the storage file."""
        self.storage_file = storage_file
        self.lock = threading.Lock()  # For thread safety
        
        # Create storage file if it doesn't exist
        if not os.path.exists(storage_file):
            with open(storage_file, 'w') as f:
                json.dump([], f)
    
    def get_all_deadlines(self) -> List[Dict[str, Any]]:
        """Get all stored deadlines."""
        with self.lock:
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error reading deadlines: {e}")
                return []
    
    def add_deadline(self, deadline: Dict[str, Any]) -> bool:
        """Add a new deadline to storage."""
        if not self._is_valid_deadline(deadline):
            return False
        
        # Check if this is a duplicate
        if self._is_duplicate(deadline):
            return False
        
        # Add unique ID if not present
        if 'id' not in deadline:
            deadline['id'] = f"dl_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{id(deadline)}"
        
        # Add to storage
        with self.lock:
            deadlines = self.get_all_deadlines()
            deadlines.append(deadline)
            return self._save_deadlines(deadlines)
    
    def add_multiple_deadlines(self, deadlines: List[Dict[str, Any]]) -> int:
        """Add multiple deadlines, returns count of added items."""
        if not deadlines:
            return 0
        
        count = 0
        current_deadlines = self.get_all_deadlines()
        
        for deadline in deadlines:
            if not self._is_valid_deadline(deadline):
                continue
                
            # Check for duplicates
            if any(self._are_similar_deadlines(deadline, existing) for existing in current_deadlines):
                continue
            
            # Add unique ID
            deadline['id'] = f"dl_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{id(deadline)}"
            current_deadlines.append(deadline)
            count += 1
        
        if count > 0:
            with self.lock:
                self._save_deadlines(current_deadlines)
        
        return count
    
    def update_deadline(self, deadline_id: str, updated_data: Dict[str, Any]) -> bool:
        """Update an existing deadline by ID."""
        with self.lock:
            deadlines = self.get_all_deadlines()
            
            for i, deadline in enumerate(deadlines):
                if deadline.get('id') == deadline_id:
                    # Preserve ID and source info
                    updated_data['id'] = deadline_id
                    if 'source_email_id' in deadline:
                        updated_data['source_email_id'] = deadline['source_email_id']
                    if 'source_email_subject' in deadline:
                        updated_data['source_email_subject'] = deadline['source_email_subject']
                    
                    deadlines[i] = updated_data
                    return self._save_deadlines(deadlines)
            
            return False
    
    def delete_deadline(self, deadline_id: str) -> bool:
        """Delete a deadline by ID."""
        with self.lock:
            deadlines = self.get_all_deadlines()
            initial_count = len(deadlines)
            
            deadlines = [d for d in deadlines if d.get('id') != deadline_id]
            
            if len(deadlines) < initial_count:
                return self._save_deadlines(deadlines)
            return False
    
    def get_upcoming_deadlines(self, hours_ahead=24) -> List[Dict[str, Any]]:
        """Get deadlines coming up within specified hours."""
        all_deadlines = self.get_all_deadlines()
        upcoming = []
        
        now = datetime.datetime.now()
        cutoff = now + datetime.timedelta(hours=hours_ahead)
        
        for deadline in all_deadlines:
            deadline_date = self._parse_deadline_date(deadline.get('deadline'))
            
            if deadline_date and now <= deadline_date <= cutoff:
                upcoming.append(deadline)
        
        return upcoming
    
    def _save_deadlines(self, deadlines: List[Dict[str, Any]]) -> bool:
        """Save deadlines to storage file."""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(deadlines, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving deadlines: {e}")
            return False
    
    def _is_valid_deadline(self, deadline: Dict[str, Any]) -> bool:
        """Check if deadline has required fields."""
        return (
            isinstance(deadline, dict) and
            'task' in deadline and
            'deadline' in deadline
        )
    
    def _is_duplicate(self, new_deadline: Dict[str, Any]) -> bool:
        """Check if a similar deadline already exists."""
        existing_deadlines = self.get_all_deadlines()
        return any(self._are_similar_deadlines(new_deadline, existing) 
                  for existing in existing_deadlines)
    
    def _are_similar_deadlines(self, deadline1: Dict[str, Any], deadline2: Dict[str, Any]) -> bool:
        """Check if two deadlines are similar (likely the same task)."""
        # If they have the same source email, similar task name, and same deadline date
        same_source = (deadline1.get('source_email_id') == deadline2.get('source_email_id') and
                       deadline1.get('source_email_id') is not None)
        
        # Compare task names (if one is substring of the other or very similar)
        task1 = deadline1.get('task', '').lower()
        task2 = deadline2.get('task', '').lower()
        similar_task = (task1 in task2 or task2 in task1) or self._similarity_score(task1, task2) > 0.7
        
        # Compare dates (if they're the same day)
        date1 = self._parse_deadline_date(deadline1.get('deadline'))
        date2 = self._parse_deadline_date(deadline2.get('deadline'))
        same_day = (date1 and date2 and 
                   date1.year == date2.year and 
                   date1.month == date2.month and 
                   date1.day == date2.day)
        
        return (same_source and similar_task) or (similar_task and same_day)
    
    def _similarity_score(self, str1: str, str2: str) -> float:
        """Calculate a simple similarity score between two strings."""
        if not str1 or not str2:
            return 0.0
            
        # Simple case: one is substring of the other
        if str1 in str2 or str2 in str1:
            return 0.8
            
        # Count common words
        words1 = set(str1.split())
        words2 = set(str2.split())
        
        if not words1 or not words2:
            return 0.0
            
        common_words = words1.intersection(words2)
        return len(common_words) / max(len(words1), len(words2))
    
    def _parse_deadline_date(self, date_str: Optional[str]) -> Optional[datetime.datetime]:
        """Parse deadline string to datetime object."""
        if not date_str:
            return None
            
        try:
            # Try direct parsing (ISO format)
            return datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            # Try with dateutil for more flexible parsing
            try:
                import dateutil.parser
                return dateutil.parser.parse(date_str)
            except:
                return None

# Usage example
if __name__ == "__main__":
    storage = DeadlineStorage("test_deadlines.json")
    
    # Test adding a deadline
    test_deadline = {
        "task": "Submit project report",
        "deadline": "2023-03-20T17:00:00",
        "details": "Final version with all appendices",
        "confidence": "high",
        "source_email_subject": "Project deadline reminder"
    }
    
    storage.add_deadline(test_deadline)
    
    # Test retrieving deadlines
    all_deadlines = storage.get_all_deadlines()
    print(f"Total deadlines: {len(all_deadlines)}")
    
    # Test upcoming deadlines
    upcoming = storage.get_upcoming_deadlines(hours_ahead=168)  # Next 7 days
    print(f"Upcoming deadlines: {len(upcoming)}")