// Chat functionality
class TravelChatbot {
    constructor() {
        this.chatContainer = document.getElementById('chatContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.loading = document.getElementById('loading');
        this.status = document.getElementById('status');
        
        this.initializeEventListeners();
        this.checkHealth();
    }
    
    initializeEventListeners() {
        // Send button click
        this.sendButton.addEventListener('click', () => this.sendMessage());
        
        // Enter key press
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Quick suggestion buttons
        document.querySelectorAll('.suggestion-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.dataset.message;
                this.messageInput.value = message;
                this.sendMessage();
            });
        });
        
        // Auto-resize input
        this.messageInput.addEventListener('input', () => {
            this.sendButton.disabled = !this.messageInput.value.trim();
        });
    }
    
    async checkHealth() {
        try {
            const response = await fetch('/api/health');
            const data = await response.json();
            
            if (data.chatbot_ready) {
                this.updateStatus('online', 'Online');
            } else {
                this.updateStatus('offline', 'Connecting...');
            }
        } catch (error) {
            this.updateStatus('offline', 'Offline');
            console.error('Health check failed:', error);
        }
    }
    
    updateStatus(type, text) {
        const statusIcon = this.status.querySelector('.fa-circle');
        const statusText = this.status.childNodes[2];
        
        statusIcon.className = `fas fa-circle ${type}`;
        statusText.textContent = ` ${text}`;
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // Clear input and disable button
        this.messageInput.value = '';
        this.sendButton.disabled = true;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        
        // Show loading
        this.showLoading();
        
        try {
            // Send to API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            
            // Hide loading
            this.hideLoading();
            
            if (data.success) {
                // Add assistant response
                this.addMessage(data.response, 'assistant');
            } else {
                // Add error message
                this.addMessage('Oops! Something went wrong. Try again? 🤔', 'assistant');
            }
            
        } catch (error) {
            this.hideLoading();
            this.addMessage('Connection error. Please check your internet! 📶', 'assistant');
            console.error('Chat error:', error);
        }
        
        // Scroll to bottom
        this.scrollToBottom();
    }
    
    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${sender === 'user' ? 'fa-user' : 'fa-robot'}"></i>
            </div>
            <div class="message-content">
                <p>${this.formatMessage(content)}</p>
                <div class="message-time">${timeString}</div>
            </div>
        `;
        
        this.chatContainer.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(text) {
        // Simple formatting for emojis and basic markdown
        return text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }
    
    showLoading() {
        this.loading.style.display = 'flex';
    }
    
    hideLoading() {
        this.loading.style.display = 'none';
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
        }, 100);
    }
}

// Initialize the chatbot when page loads
document.addEventListener('DOMContentLoaded', () => {
    new TravelChatbot();
});

// Add some extra visual feedback
document.addEventListener('click', (e) => {
    if (e.target.matches('.suggestion-btn')) {
        e.target.style.transform = 'scale(0.95)';
        setTimeout(() => {
            e.target.style.transform = '';
        }, 150);
    }
});

// Auto-focus input on page load
window.addEventListener('load', () => {
    document.getElementById('messageInput').focus();
}); 