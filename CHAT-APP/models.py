import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional

class Message:
    def __init__(self, content: str, encrypted_content: str, timestamp: Optional[str] = None, message_id: Optional[str] = None):
        self.content = content
        self.encrypted_content = encrypted_content
        self.timestamp = timestamp or datetime.now().isoformat()
        self.message_id = message_id or self._generate_id()
    
    def _generate_id(self) -> str:
        """Generate a simple message ID based on timestamp"""
        return str(int(datetime.now().timestamp() * 1000000))
    
    def to_dict(self) -> Dict:
        return {
            'content': self.content,
            'encrypted_content': self.encrypted_content,
            'timestamp': self.timestamp,
            'message_id': self.message_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Message':
        return cls(
            content=data.get('content', ''),
            encrypted_content=data.get('encrypted_content', ''),
            timestamp=data.get('timestamp', None),
            message_id=data.get('message_id', None)
        )

class MessageStore:
    def __init__(self, file_path: str = 'data/messages.json'):
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create the messages file if it doesn't exist"""
        if not os.path.exists(self.file_path):
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
            self.save_messages([])
    
    def load_messages(self) -> List[Message]:
        """Load messages from the JSON file"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return [Message.from_dict(msg_data) for msg_data in data]
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error loading messages: {e}")
            return []
    
    def save_messages(self, messages: List[Message]):
        """Save messages to the JSON file"""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([msg.to_dict() for msg in messages], f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Error saving messages: {e}")
            raise
    
    def add_message(self, message: Message):
        """Add a new message and save to file"""
        messages = self.load_messages()
        messages.append(message)
        self.save_messages(messages)
    
    def get_recent_messages(self, limit: int = 50) -> List[Message]:
        """Get the most recent messages"""
        messages = self.load_messages()
        return messages[-limit:] if len(messages) > limit else messages
