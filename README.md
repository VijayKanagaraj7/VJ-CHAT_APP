# VJ-CHAT_APP
demo link - 
https://drive.google.com/file/d/1b2To0uQd2cSvwfZJCKv7L9RxMYDXN61q/view?usp=sharing
# VIJAY'S CHAT APP - Secure Messaging Application


VIJAY'S CHAT APP is a Flask-based web application that provides secure, encrypted messaging functionality. The application automatically encrypts all messages using Fernet symmetric encryption before storing them, ensuring that user communications remain private and secure. It features a simple chat room interface where users can send and receive encrypted messages in real-time.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a simple MVC (Model-View-Controller) architecture built on Flask:

- **Frontend**: HTML templates with Bootstrap CSS framework and vanilla JavaScript
- **Backend**: Flask web framework with Python
- **Storage**: File-based JSON storage for messages
- **Encryption**: Fernet symmetric encryption from the cryptography library
- **Session Management**: Flask sessions with configurable secret keys

The architecture prioritizes simplicity and security over scalability, making it ideal for small-scale secure messaging scenarios.

## Key Components

### 1. Flask Application (`app.py`, `main.py`)
- **Purpose**: Core Flask application setup and configuration
- **Decision**: Uses ProxyFix middleware for proper proxy handling in deployment environments
- **Key Features**: 
  - Configurable session secrets via environment variables
  - Debug logging enabled for development
  - Automatic data directory creation

### 2. Encryption System (`crypto_utils.py`)
- **Purpose**: Handles all cryptographic operations
- **Technology**: Fernet symmetric encryption from Python's cryptography library
- **Key Features**:
  - Automatic key generation and persistence
  - Secure message encryption/decryption
  - Error handling for corrupted or invalid encrypted data
- **Decision Rationale**: Fernet provides authenticated encryption, ensuring both confidentiality and integrity

### 3. Data Models (`models.py`)
- **Purpose**: Message data structures and file-based storage
- **Architecture**: Simple JSON file storage with in-memory object representation
- **Key Features**:
  - Message objects with content, encrypted content, timestamps, and unique IDs
  - File-based persistence using JSON format
  - Automatic file creation and directory management

### 4. Web Routes (`routes.py`)
- **Purpose**: HTTP request handling and business logic
- **Key Routes**:
  - `/` - Main chat interface with message display
  - `/send` - Message submission endpoint
  - Additional routes for message management (clear, refresh)
- **Security Features**: Automatic encryption before storage, decryption only for display

### 5. Frontend Interface
- **Templates**: Jinja2 templates with Bootstrap dark theme
- **Styling**: Custom CSS with responsive design
- **JavaScript**: Client-side functionality for form handling, auto-refresh, and UI enhancements
- **Design Decision**: Uses Bootstrap for rapid development and consistent UI components

## Data Flow

1. **Message Submission**:
   - User submits plaintext message via web form
   - Backend encrypts message using Fernet cipher
   - Encrypted message stored in JSON file with metadata
   - User redirected back to chat interface

2. **Message Display**:
   - Backend loads encrypted messages from JSON storage
   - Messages decrypted in real-time for display
   - Failed decryption attempts are logged and skipped
   - Formatted messages sent to template for rendering

3. **Encryption Key Management**:
   - Application checks for existing encryption key on startup
   - If no key exists, generates new Fernet key automatically
   - Key persisted to filesystem for consistent encryption/decryption

## External Dependencies

- **Flask**: Web framework for HTTP handling and templating
- **cryptography**: Provides Fernet encryption implementation
- **Werkzeug**: WSGI utilities including ProxyFix middleware
- **Bootstrap CDN**: Frontend CSS framework for styling
- **Feather Icons**: Icon library for UI elements

## Deployment Strategy

- **Development**: Flask development server with debug mode enabled
- **Configuration**: Environment-based configuration for session secrets
- **File Storage**: Local filesystem storage for messages and encryption keys
- **Hosting**: Designed for single-instance deployment (not horizontally scalable due to file-based storage)
- **Security**: ProxyFix middleware configured for reverse proxy deployments

### Current Limitations
- File-based storage limits scalability
- No user authentication or authorization
- Single encryption key for all messages
- No real-time messaging (polling-based updates)

The architecture prioritizes security and simplicity over advanced features, making it suitable for demonstration purposes or small-scale secure messaging needs.
