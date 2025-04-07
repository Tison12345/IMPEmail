import requests
import json
import os
import re
import datetime
from typing import List, Dict, Any, Optional

class DeadlineExtractor:
    def __init__(self, llm_api_url="http://localhost:11434/api/generate"):
        """Initialize with the LLM API endpoint."""
        self.llm_api_url = llm_api_url
        self.model_name = "mistral"  # Default model
    
    def extract_deadlines(self, email_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract deadlines from email content using LLM."""
        prompt = self._create_extraction_prompt(email_data)
        llm_response = self._query_llm(prompt)
        
        if not llm_response:
            return []
        
        # Extract the JSON part from the response
        deadlines = self._parse_llm_response(llm_response)
        
        # Add metadata and normalize dates
        return self._process_deadlines(deadlines, email_data)
    
    def _create_extraction_prompt(self, email_data: Dict[str, Any]) -> str:
        """Create a prompt for the LLM to extract deadlines."""
        return f"""
        Analyze the following email and extract any deadlines, due dates, or time-sensitive tasks.
        
        SUBJECT: {email_data.get('subject', 'No Subject')}
        FROM: {email_data.get('from', 'Unknown')}
        DATE: {email_data.get('date', 'Unknown')}
        
        EMAIL CONTENT:
        {email_data.get('body', '')}
        
        Extract ALL deadlines mentioned in this email. For each deadline, identify:
        1. The task or what is due
        2. The exact deadline date and time (if specified)
        3. Any additional important details
        
        Format your response as a JSON array of deadlines. Each deadline should be a JSON object with these fields:
        - "task": The name or description of the task
        - "deadline": The date and time in ISO format (YYYY-MM-DDTHH:MM:SS) or just the date (YYYY-MM-DD) if no time is specified
        - "details": Any additional context about the deadline
        - "confidence": Your confidence level (high, medium, low) that this is actually a deadline
        
        If no deadlines are found, return an empty array [].
        
        Response should be valid JSON only, with no explanations or other text.
        """
    
    def _query_llm(self, prompt: str) -> Optional[str]:
        """Send a prompt to the LLM API and get the response."""
        try:
            response = requests.post(
                self.llm_api_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                print(f"API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"LLM query error: {e}")
            return None
    
    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Extract and parse JSON from LLM response."""
        try:
            # Find JSON in the response (handle cases where LLM adds extra text)
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                deadlines = json.loads(json_str)
                return deadlines if isinstance(deadlines, list) else []
            return []
        except json.JSONDecodeError:
            print("Failed to parse LLM response as JSON")
            return []
    
    def _process_deadlines(self, deadlines: List[Dict[str, Any]], email_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process and normalize extracted deadlines."""
        processed = []
        
        for deadline in deadlines:
            # Try to normalize the date format
            deadline_date = None
            date_str = deadline.get("deadline", "")
            
            if date_str:
                try:
                    # Handle various date formats
                    deadline_date = self._normalize_date(date_str)
                except:
                    # Keep original if parsing fails
                    deadline_date = date_str
            
            # Add metadata
            processed_deadline = {
                "task": deadline.get("task", "Unknown task"),
                "deadline": deadline_date,
                "details": deadline.get("details", ""),
                "confidence": deadline.get("confidence", "medium"),
                "source_email_id": email_data.get("id", ""),
                "source_email_subject": email_data.get("subject", ""),
                "source_email_from": email_data.get("from", ""),
                "extraction_time": datetime.datetime.now().isoformat()
            }
            
            processed.append(processed_deadline)
        
        return processed
    
    def _normalize_date(self, date_str: str) -> str:
        """Attempt to normalize date to ISO format."""
        # Try direct parsing first
        try:
            parsed_date = datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return parsed_date.isoformat()
        except ValueError:
            pass
        
        # Use dateutil for more flexible parsing
        try:
            import dateutil.parser
            parsed_date = dateutil.parser.parse(date_str)
            return parsed_date.isoformat()
        except:
            # Return original if all parsing fails
            return date_str

# Usage example
if __name__ == "__main__":
    extractor = DeadlineExtractor()
    test_email = {
        "id": "test123",
        "subject": "Project deadline reminder",
        "from": "manager@example.com",
        "date": "2023-03-15T10:00:00",
        "body": "Hi team, Just a reminder that the final report is due next Friday at 5pm. Please also submit your timesheet by Monday noon. Thanks, Manager"
    }
    
    deadlines = extractor.extract_deadlines(test_email)
    print(json.dumps(deadlines, indent=2))