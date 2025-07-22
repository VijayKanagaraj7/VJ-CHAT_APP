// VIJAY'S CHAT APP JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initializeCharacterCounter();
    initializeFormHandling();
    initializeRefreshButton();
    initializeAutoRefresh();
    
    // Initialize feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
    
    // Scroll to bottom of messages on load
    scrollToBottom();
});

/**
 * Initialize character counter for message input
 */
function initializeCharacterCounter() {
    const messageTextarea = document.getElementById('content');
    const charCount = document.getElementById('char-count');
    
    if (messageTextarea && charCount) {
        messageTextarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            charCount.textContent = currentLength;
            
            // Change color based on character count
            if (currentLength > 900) {
                charCount.style.color = 'var(--bs-danger)';
            } else if (currentLength > 800) {
                charCount.style.color = 'var(--bs-warning)';
            } else {
                charCount.style.color = 'var(--bs-info)';
            }
        });
    }
}

/**
 * Initialize form handling with loading states
 */
function initializeFormHandling() {
    const messageForm = document.getElementById('message-form');
    const sendButton = document.getElementById('send-btn');
    const loadingOverlay = document.getElementById('loading-overlay');
    
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            const messageInput = document.getElementById('content');
            const message = messageInput.value.trim();
            
            // Validate message
            if (!message) {
                e.preventDefault();
                showAlert('Please enter a message before sending.', 'error');
                return;
            }
            
            if (message.length > 1000) {
                e.preventDefault();
                showAlert('Message is too long. Maximum 1000 characters allowed.', 'error');
                return;
            }
            
            // Show loading state
            showLoadingState();
        });
    }
}

/**
 * Initialize refresh button functionality
 */
function initializeRefreshButton() {
    const refreshButton = document.getElementById('refresh-btn');
    
    if (refreshButton) {
        refreshButton.addEventListener('click', function() {
            refreshMessages();
        });
    }
}

/**
 * Initialize auto-refresh functionality (polls every 10 seconds)
 */
function initializeAutoRefresh() {
    // Auto-refresh messages every 10 seconds
    setInterval(function() {
        refreshMessages(true);
    }, 10000);
}

/**
 * Refresh messages from server
 */
function refreshMessages(silent = false) {
    if (!silent) {
        showSpinner('refresh-btn');
    }
    
    // Simple page reload for now (following guidelines to avoid fetch)
    if (!silent) {
        window.location.reload();
    }
}

/**
 * Show loading overlay
 */
function showLoadingState() {
    const overlay = document.getElementById('loading-overlay');
    const sendButton = document.getElementById('send-btn');
    
    if (overlay) {
        overlay.classList.remove('d-none');
    }
    
    if (sendButton) {
        sendButton.classList.add('btn-loading');
        sendButton.disabled = true;
    }
}

/**
 * Hide loading overlay
 */
function hideLoadingState() {
    const overlay = document.getElementById('loading-overlay');
    const sendButton = document.getElementById('send-btn');
    
    if (overlay) {
        overlay.classList.add('d-none');
    }
    
    if (sendButton) {
        sendButton.classList.remove('btn-loading');
        sendButton.disabled = false;
    }
}

/**
 * Show spinner on button
 */
function showSpinner(buttonId) {
    const button = document.getElementById(buttonId);
    if (button) {
        const icon = button.querySelector('[data-feather]');
        if (icon) {
            icon.style.animation = 'spin 1s linear infinite';
            setTimeout(() => {
                icon.style.animation = '';
            }, 1000);
        }
    }
}

/**
 * Scroll to bottom of messages container
 */
function scrollToBottom() {
    const messagesContainer = document.getElementById('messages-container');
    if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    // Create alert element
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <i data-feather="${type === 'error' ? 'alert-circle' : 'info'}" class="me-2" style="width: 18px; height: 18px;"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert at top of container
    const container = document.querySelector('.container');
    if (container) {
        const firstChild = container.firstElementChild;
        if (firstChild) {
            container.insertBefore(alertDiv, firstChild.nextSibling);
        } else {
            container.appendChild(alertDiv);
        }
        
        // Replace feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

/**
 * Handle keyboard shortcuts
 */
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to send message
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const messageForm = document.getElementById('message-form');
        if (messageForm) {
            messageForm.requestSubmit();
        }
    }
    
    // Escape to clear message input
    if (e.key === 'Escape') {
        const messageInput = document.getElementById('content');
        if (messageInput && document.activeElement === messageInput) {
            messageInput.value = '';
            document.getElementById('char-count').textContent = '0';
        }
    }
});

/**
 * Handle window beforeunload to warn about unsent messages
 */
window.addEventListener('beforeunload', function(e) {
    const messageInput = document.getElementById('content');
    if (messageInput && messageInput.value.trim()) {
        e.preventDefault();
        e.returnValue = '';
    }
});

/**
 * Initialize tooltips if Bootstrap is available
 */
if (typeof bootstrap !== 'undefined') {
    document.addEventListener('DOMContentLoaded', function() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[title]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    });
}
