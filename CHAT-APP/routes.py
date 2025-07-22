import logging
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, jsonify
from app import app
from models import Message, MessageStore
from crypto_utils import CryptoManager

# Initialize components
crypto_manager = CryptoManager()
message_store = MessageStore()

# Verify encryption is working on startup
if not crypto_manager.verify_encryption():
    logging.error("Encryption verification failed!")
else:
    logging.info("Encryption system verified successfully")

@app.route('/')
def index():
    """Main chat interface"""
    try:
        # Load recent messages and decrypt them
        encrypted_messages = message_store.get_recent_messages(50)
        decrypted_messages = []
        
        for msg in encrypted_messages:
            try:
                decrypted_content = crypto_manager.decrypt_message(msg.encrypted_content)
                # Parse timestamp for display
                timestamp = datetime.fromisoformat(msg.timestamp)
                formatted_time = timestamp.strftime("%H:%M:%S")
                
                decrypted_messages.append({
                    'content': decrypted_content,
                    'timestamp': formatted_time,
                    'message_id': msg.message_id
                })
            except Exception as e:
                logging.error(f"Error decrypting message {msg.message_id}: {e}")
                # Skip corrupted messages
                continue
        
        return render_template('index.html', messages=decrypted_messages)
    except Exception as e:
        logging.error(f"Error loading messages: {e}")
        flash('Error loading messages. Please try again.', 'error')
        return render_template('index.html', messages=[])

@app.route('/send', methods=['POST'])
def send_message():
    """Handle sending a new message"""
    try:
        message_content = request.form.get('message', '').strip()
        
        # Validate input
        if not message_content:
            flash('Message cannot be empty!', 'error')
            return redirect(url_for('index'))
        
        if len(message_content) > 1000:
            flash('Message too long! Maximum 1000 characters allowed.', 'error')
            return redirect(url_for('index'))
        
        # Encrypt the message
        encrypted_content = crypto_manager.encrypt_message(message_content)
        
        # Create and store the message
        message = Message(
            content=message_content,
            encrypted_content=encrypted_content
        )
        
        message_store.add_message(message)
        
        flash('Message sent successfully!', 'success')
        logging.info(f"Message sent and encrypted successfully: ID {message.message_id}")
        
    except ValueError as e:
        flash(f'Validation error: {str(e)}', 'error')
        logging.error(f"Validation error: {e}")
    except Exception as e:
        flash('Failed to send message. Please try again.', 'error')
        logging.error(f"Error sending message: {e}")
    
    return redirect(url_for('index'))

@app.route('/api/messages')
def api_messages():
    """API endpoint to get recent messages for real-time updates"""
    try:
        encrypted_messages = message_store.get_recent_messages(50)
        decrypted_messages = []
        
        for msg in encrypted_messages:
            try:
                decrypted_content = crypto_manager.decrypt_message(msg.encrypted_content)
                timestamp = datetime.fromisoformat(msg.timestamp)
                formatted_time = timestamp.strftime("%H:%M:%S")
                
                decrypted_messages.append({
                    'content': decrypted_content,
                    'timestamp': formatted_time,
                    'message_id': msg.message_id
                })
            except Exception as e:
                logging.error(f"Error decrypting message {msg.message_id}: {e}")
                continue
        
        return jsonify({
            'status': 'success',
            'messages': decrypted_messages
        })
    except Exception as e:
        logging.error(f"API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load messages'
        }), 500

@app.route('/clear', methods=['POST'])
def clear_messages():
    """Clear all messages (for demo/testing purposes)"""
    try:
        message_store.save_messages([])
        flash('All messages cleared successfully!', 'info')
        logging.info("All messages cleared")
    except Exception as e:
        flash('Failed to clear messages.', 'error')
        logging.error(f"Error clearing messages: {e}")
    
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html', messages=[]), 404

@app.errorhandler(500)
def internal_error(error):
    logging.error(f"Internal server error: {error}")
    flash('An internal error occurred. Please try again.', 'error')
    return render_template('index.html', messages=[]), 500
