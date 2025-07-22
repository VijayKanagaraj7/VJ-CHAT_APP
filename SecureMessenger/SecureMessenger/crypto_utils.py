import os
import logging
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken

class CryptoManager:
    def __init__(self, key_file: str = 'data/secret.key'):
        self.key_file = key_file
        self.cipher = self._initialize_cipher()
    
    def _initialize_cipher(self) -> Fernet:
        """Initialize the Fernet cipher with key from file or generate new one"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
            
            # Load existing key or generate new one
            if os.path.exists(self.key_file):
                with open(self.key_file, 'rb') as key_file:
                    key = key_file.read()
                logging.info("Loaded existing encryption key")
            else:
                key = Fernet.generate_key()
                with open(self.key_file, 'wb') as key_file:
                    key_file.write(key)
                logging.info("Generated new encryption key")
            
            return Fernet(key)
        except Exception as e:
            logging.error(f"Error initializing cipher: {e}")
            raise
    
    def encrypt_message(self, message: str) -> str:
        """Encrypt a message and return base64 encoded string"""
        try:
            if not message.strip():
                raise ValueError("Message cannot be empty")
            
            encrypted_bytes = self.cipher.encrypt(message.encode('utf-8'))
            return encrypted_bytes.decode('utf-8')
        except Exception as e:
            logging.error(f"Encryption error: {e}")
            raise
    
    def decrypt_message(self, encrypted_message: str) -> str:
        """Decrypt a base64 encoded encrypted message"""
        try:
            if not encrypted_message.strip():
                raise ValueError("Encrypted message cannot be empty")
            
            decrypted_bytes = self.cipher.decrypt(encrypted_message.encode('utf-8'))
            return decrypted_bytes.decode('utf-8')
        except InvalidToken:
            logging.error("Invalid token - message cannot be decrypted")
            raise ValueError("Message decryption failed - invalid token")
        except Exception as e:
            logging.error(f"Decryption error: {e}")
            raise
    
    def verify_encryption(self) -> bool:
        """Verify that encryption/decryption is working correctly"""
        try:
            test_message = "CryptoChatTest123"
            encrypted = self.encrypt_message(test_message)
            decrypted = self.decrypt_message(encrypted)
            return decrypted == test_message
        except Exception as e:
            logging.error(f"Encryption verification failed: {e}")
            return False
