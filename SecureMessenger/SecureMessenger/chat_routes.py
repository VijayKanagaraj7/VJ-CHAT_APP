import logging
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from auth_models import db, SecureMessage
from auth_forms import MessageForm
from crypto_utils import CryptoManager

chat_bp = Blueprint('chat', __name__)

# Initialize crypto manager
crypto_manager = CryptoManager()

# Verify encryption is working on startup
if not crypto_manager.verify_encryption():
    logging.error("Encryption verification failed!")
else:
    logging.info("Encryption system verified successfully")

@chat_bp.route('/')
def index():
    """Main chat interface - show landing page if not authenticated"""
    if not current_user.is_authenticated:
        return render_template('landing.html')
    
    form = MessageForm()
    
    try:
        # Load recent messages from database
        messages_query = SecureMessage.query.filter_by(is_deleted=False)\
                                          .order_by(SecureMessage.created_at.asc())\
                                          .limit(50)
        encrypted_messages = messages_query.all()
        
        decrypted_messages = []
        
        for msg in encrypted_messages:
            try:
                decrypted_content = crypto_manager.decrypt_message(msg.encrypted_content)
                
                decrypted_messages.append({
                    'id': msg.id,
                    'content': decrypted_content,
                    'author': msg.author.get_full_name(),
                    'author_username': msg.author.username,
                    'timestamp': msg.created_at.strftime("%H:%M:%S"),
                    'created_at': msg.created_at
                })
            except Exception as e:
                logging.error(f"Error decrypting message {msg.id}: {e}")
                continue
        
        # Get user statistics
        user_message_count = SecureMessage.query.filter_by(user_id=current_user.id, is_deleted=False).count()
        total_message_count = SecureMessage.query.filter_by(is_deleted=False).count()
        
        return render_template('chat/index.html', 
                             form=form,
                             messages=decrypted_messages,
                             user_message_count=user_message_count,
                             total_message_count=total_message_count)
                             
    except Exception as e:
        logging.error(f"Error loading messages: {e}")
        flash('Error loading messages. Please try again.', 'error')
        return render_template('chat/index.html', form=form, messages=[])

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """Handle sending a new message"""
    form = MessageForm()
    
    if form.validate_on_submit():
        try:
            message_content = form.content.data.strip() if form.content.data else ""
            
            # Additional server-side validation
            if len(message_content) > 1000:
                flash('Message too long! Maximum 1000 characters allowed.', 'error')
                return redirect(url_for('chat.index'))
            
            # Encrypt the message
            encrypted_content = crypto_manager.encrypt_message(message_content)
            
            # Create and store the message in database
            message = SecureMessage()
            message.content = message_content  # Store original for admin purposes if needed
            message.encrypted_content = encrypted_content
            message.user_id = current_user.id
            
            db.session.add(message)
            db.session.commit()
            
            flash('Message sent successfully!', 'success')
            logging.info(f"Message sent by user {current_user.username}: ID {message.id}")
            
        except ValueError as e:
            flash(f'Validation error: {str(e)}', 'error')
            logging.error(f"Validation error: {e}")
        except Exception as e:
            db.session.rollback()
            flash('Failed to send message. Please try again.', 'error')
            logging.error(f"Error sending message: {e}")
    else:
        # Form validation failed
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'error')
    
    return redirect(url_for('chat.index'))

@chat_bp.route('/api/messages')
@login_required
def api_messages():
    """API endpoint to get recent messages for real-time updates"""
    try:
        messages_query = SecureMessage.query.filter_by(is_deleted=False)\
                                          .order_by(SecureMessage.created_at.asc())\
                                          .limit(50)
        encrypted_messages = messages_query.all()
        
        decrypted_messages = []
        
        for msg in encrypted_messages:
            try:
                decrypted_content = crypto_manager.decrypt_message(msg.encrypted_content)
                
                decrypted_messages.append({
                    'id': msg.id,
                    'content': decrypted_content,
                    'author': msg.author.get_full_name(),
                    'author_username': msg.author.username,
                    'timestamp': msg.created_at.strftime("%H:%M:%S"),
                    'created_at': msg.created_at.isoformat()
                })
            except Exception as e:
                logging.error(f"Error decrypting message {msg.id}: {e}")
                continue
        
        return jsonify({
            'status': 'success',
            'messages': decrypted_messages,
            'total_count': len(decrypted_messages)
        })
        
    except Exception as e:
        logging.error(f"API error: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Failed to load messages'
        }), 500

@chat_bp.route('/clear', methods=['POST'])
@login_required
def clear_messages():
    """Clear all messages (soft delete for demo/testing purposes)"""
    try:
        # Soft delete all messages
        SecureMessage.query.update({'is_deleted': True})
        db.session.commit()
        
        flash('All messages cleared successfully!', 'info')
        logging.info(f"All messages cleared by user: {current_user.username}")
        
    except Exception as e:
        db.session.rollback()
        flash('Failed to clear messages.', 'error')
        logging.error(f"Error clearing messages: {e}")
    
    return redirect(url_for('chat.index'))

@chat_bp.route('/my-messages')
@login_required
def my_messages():
    """Display current user's messages"""
    try:
        messages_query = SecureMessage.query.filter_by(user_id=current_user.id, is_deleted=False)\
                                          .order_by(SecureMessage.created_at.desc())
        encrypted_messages = messages_query.all()
        
        decrypted_messages = []
        
        for msg in encrypted_messages:
            try:
                decrypted_content = crypto_manager.decrypt_message(msg.encrypted_content)
                
                decrypted_messages.append({
                    'id': msg.id,
                    'content': decrypted_content,
                    'timestamp': msg.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    'created_at': msg.created_at
                })
            except Exception as e:
                logging.error(f"Error decrypting message {msg.id}: {e}")
                continue
        
        return render_template('chat/my_messages.html', messages=decrypted_messages)
        
    except Exception as e:
        logging.error(f"Error loading user messages: {e}")
        flash('Error loading your messages.', 'error')
        return render_template('chat/my_messages.html', messages=[])

@chat_bp.route('/delete-message/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    """Delete a specific message (only by the author)"""
    try:
        message = SecureMessage.query.get_or_404(message_id)
        
        # Check if user owns this message
        if message.user_id != current_user.id:
            flash('You can only delete your own messages.', 'error')
            return redirect(url_for('chat.index'))
        
        message.soft_delete()
        flash('Message deleted successfully.', 'success')
        logging.info(f"Message {message_id} deleted by user {current_user.username}")
        
    except Exception as e:
        flash('Error deleting message.', 'error')
        logging.error(f"Error deleting message {message_id}: {e}")
    
    return redirect(url_for('chat.index'))

@chat_bp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@chat_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logging.error(f"Internal server error: {error}")
    return render_template('errors/500.html'), 500