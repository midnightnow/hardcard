// HARDCARD Memory Assistant - ChatGPT Integration
console.log('HARDCARD Memory: ChatGPT integration loaded');

class ChatGPTMemoryIntegration {
    constructor() {
        this.isEnabled = true;
        this.sidebarVisible = false;
        this.lastMessageContent = '';
        this.conversationHistory = [];
        this.observerActive = false;
        
        this.init();
    }
    
    async init() {
        // Set platform identifier
        document.body.setAttribute('data-platform', 'chatgpt');
        
        // Check if memory is enabled
        const { hardcard_memory_enabled } = await chrome.storage.sync.get(['hardcard_memory_enabled']);
        this.isEnabled = hardcard_memory_enabled !== false;
        
        if (this.isEnabled) {
            this.setupMessageObserver();
            this.createMemoryInterface();
            this.addMemoryShortcuts();
        }
        
        // Listen for messages from background script
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse);
        });
    }
    
    setupMessageObserver() {
        if (this.observerActive) return;
        
        // ChatGPT conversation observer
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            this.processNewMessage(node);
                        }
                    });
                }
            });
        });
        
        // Find ChatGPT conversation container
        const conversationContainer = this.findConversationContainer();
        if (conversationContainer) {
            observer.observe(conversationContainer, {
                childList: true,
                subtree: true
            });
            this.observerActive = true;
        }
        
        // Retry if container not found
        if (!conversationContainer) {
            setTimeout(() => this.setupMessageObserver(), 1000);
        }
    }
    
    findConversationContainer() {
        // ChatGPT conversation container selectors
        const selectors = [
            '[role="main"]',
            '.conversation-content',
            '[data-testid="conversation-turn"]',
            '.text-base'
        ];
        
        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element) return element.closest('main') || element.parentElement;
        }
        
        // Fallback: look for common ChatGPT structure
        const main = document.querySelector('main');
        if (main) return main;
        
        return null;
    }
    
    processNewMessage(node) {
        // Look for ChatGPT assistant responses
        const assistantMessage = this.extractAssistantMessage(node);
        const userMessage = this.extractUserMessage(node);
        
        if (assistantMessage && assistantMessage !== this.lastMessageContent) {
            this.lastMessageContent = assistantMessage;
            this.saveConversationMemory(assistantMessage, 'assistant');
            this.suggestRelevantMemories(assistantMessage);
        }
        
        if (userMessage) {
            this.saveConversationMemory(userMessage, 'user');
        }
    }
    
    extractAssistantMessage(node) {
        // ChatGPT-specific selectors for assistant messages
        const assistantSelectors = [
            '[data-message-author-role="assistant"]',
            '.markdown.prose',
            '[data-testid="conversation-turn"] .text-base',
            '.text-gray-800.w-full'
        ];
        
        for (const selector of assistantSelectors) {
            let element = node.querySelector ? node.querySelector(selector) : null;
            
            // Check if the node itself matches
            if (!element && node.matches && node.matches(selector)) {
                element = node;
            }
            
            // Check if parent contains assistant message
            if (!element && node.closest) {
                element = node.closest(selector);
            }
            
            if (element) {
                const text = element.innerText || element.textContent;
                if (text && text.length > 10 && !text.includes('Copy code')) {
                    return text.trim();
                }
            }
        }
        
        // Alternative approach: look for elements with specific ChatGPT classes
        const possibleElements = node.querySelectorAll 
            ? node.querySelectorAll('div, p, span') 
            : [node];
            
        for (const el of possibleElements) {
            if (el.textContent && 
                el.textContent.length > 50 && 
                !el.querySelector('button') && // Exclude UI elements
                !el.textContent.includes('Regenerate') &&
                !el.textContent.includes('Copy code')) {
                
                // Check if this looks like an assistant response
                const parent = el.closest('[data-message-author-role="assistant"]');
                if (parent) {
                    return el.textContent.trim();
                }
            }
        }
        
        return null;
    }
    
    extractUserMessage(node) {
        // ChatGPT user message selectors
        const userSelectors = [
            '[data-message-author-role="user"]',
            '.whitespace-pre-wrap'
        ];
        
        for (const selector of userSelectors) {
            let element = node.querySelector ? node.querySelector(selector) : null;
            
            if (!element && node.matches && node.matches(selector)) {
                element = node;
            }
            
            if (element) {
                const text = element.innerText || element.textContent;
                if (text && text.length > 3) {
                    return text.trim();
                }
            }
        }
        
        return null;
    }
    
    async saveConversationMemory(content, role) {
        if (!this.isEnabled || content.length < 10) return;
        
        // Extract meaningful content and avoid duplicates
        if (this.conversationHistory.some(item => 
            item.content === content && item.role === role)) {
            return; // Avoid duplicate saves
        }
        
        const memoryData = {
            content: content,
            role: role,
            platform: 'chatgpt',
            context: {
                conversationLength: this.conversationHistory.length,
                timestamp: new Date().toISOString(),
                pageTitle: document.title,
                url: window.location.href,
                conversationId: this.extractConversationId()
            }
        };
        
        // Add to local conversation history
        this.conversationHistory.push(memoryData);
        
        // Send to background script for storage
        chrome.runtime.sendMessage({
            action: 'saveMemory',
            data: memoryData
        });
    }
    
    extractConversationId() {
        // Try to extract ChatGPT conversation ID from URL
        const urlMatch = window.location.pathname.match(/\/c\/([a-f0-9-]+)/);
        return urlMatch ? urlMatch[1] : null;
    }
    
    async suggestRelevantMemories(content) {
        // Search for relevant memories
        chrome.runtime.sendMessage({
            action: 'getMemories',
            query: content.substring(0, 200)
        }, (response) => {
            if (response?.memories?.length > 0) {
                this.displayMemorySuggestions(response.memories);
            }
        });
    }
    
    displayMemorySuggestions(memories) {
        // Remove existing suggestions
        const existingSuggestions = document.getElementById('hardcard-memory-suggestions');
        if (existingSuggestions) {
            existingSuggestions.remove();
        }
        
        // Create new suggestion box
        const suggestionBox = document.createElement('div');
        suggestionBox.id = 'hardcard-memory-suggestions';
        suggestionBox.className = 'hardcard-memory-suggestions';
        
        suggestionBox.innerHTML = `
            <div class="memory-header">
                <span class="memory-icon">🧠</span>
                <span>Relevant Memories Found</span>
                <button class="memory-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
            <div class="memory-list">
                ${memories.slice(0, 3).map((memory, index) => `
                    <div class="memory-item" data-memory-id="${memory.id}">
                        <div class="memory-content">${this.truncateText(memory.content, 120)}</div>
                        <div class="memory-meta">${this.formatDate(memory.timestamp)} • ${memory.platform}</div>
                    </div>
                `).join('')}
            </div>
        `;
        
        // Insert into ChatGPT interface
        const insertLocation = this.findSuggestionInsertLocation();
        if (insertLocation) {
            insertLocation.insertAdjacentElement('beforebegin', suggestionBox);
        } else {
            document.body.appendChild(suggestionBox);
        }
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (suggestionBox.parentNode) {
                suggestionBox.remove();
            }
        }, 10000);
    }
    
    findSuggestionInsertLocation() {
        // Find good location to insert suggestions in ChatGPT
        const selectors = [
            'form[class*="stretch"]', // ChatGPT input form
            '[data-testid="send-button"]',
            'textarea[placeholder*="message"]',
            '.text-base textarea'
        ];
        
        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element) {
                return element.closest('form') || element.parentElement;
            }
        }
        
        return null;
    }
    
    createMemoryInterface() {
        // Add memory toggle button
        const toggleButton = document.createElement('button');
        toggleButton.id = 'hardcard-memory-toggle';
        toggleButton.className = 'hardcard-memory-toggle';
        toggleButton.innerHTML = '🧠';
        toggleButton.title = 'Toggle HARDCARD Memory';
        toggleButton.onclick = () => this.toggleMemorySidebar();
        
        document.body.appendChild(toggleButton);
    }
    
    toggleMemorySidebar() {
        this.sidebarVisible = !this.sidebarVisible;
        
        let sidebar = document.getElementById('hardcard-memory-sidebar');
        
        if (!sidebar) {
            sidebar = this.createMemorySidebar();
        }
        
        sidebar.style.display = this.sidebarVisible ? 'block' : 'none';
        
        if (this.sidebarVisible) {
            this.loadRecentMemories();
        }
    }
    
    createMemorySidebar() {
        const sidebar = document.createElement('div');
        sidebar.id = 'hardcard-memory-sidebar';
        sidebar.className = 'hardcard-memory-sidebar';
        
        sidebar.innerHTML = `
            <div class="memory-sidebar-header">
                <h3>🧠 HARDCARD Memory</h3>
                <button class="memory-sidebar-close" onclick="this.parentElement.parentElement.style.display='none'">×</button>
            </div>
            <div class="memory-sidebar-content">
                <div class="memory-search">
                    <input type="text" placeholder="Search memories..." id="memory-search-input">
                    <button onclick="window.chatgptMemory.searchMemories()">🔍</button>
                </div>
                <div class="memory-categories">
                    <button class="category-btn active" data-category="all">All</button>
                    <button class="category-btn" data-category="recent">Recent</button>
                    <button class="category-btn" data-category="chatgpt">ChatGPT</button>
                </div>
                <div class="memory-list" id="sidebar-memory-list">
                    <div class="loading">Loading memories...</div>
                </div>
            </div>
        `;
        
        document.body.appendChild(sidebar);
        
        // Set up global reference for search
        window.chatgptMemory = this;
        
        return sidebar;
    }
    
    async loadRecentMemories() {
        const memoryList = document.getElementById('sidebar-memory-list');
        if (!memoryList) return;
        
        chrome.runtime.sendMessage({
            action: 'getMemories',
            query: 'recent'
        }, (response) => {
            if (response?.memories) {
                this.displayMemoriesInSidebar(response.memories);
            } else {
                memoryList.innerHTML = '<div class="no-memories">No memories found</div>';
            }
        });
    }
    
    displayMemoriesInSidebar(memories) {
        const memoryList = document.getElementById('sidebar-memory-list');
        if (!memoryList) return;
        
        memoryList.innerHTML = memories.map(memory => `
            <div class="sidebar-memory-item" data-memory-id="${memory.id}">
                <div class="memory-content">${this.truncateText(memory.content, 150)}</div>
                <div class="memory-meta">
                    <span class="memory-date">${this.formatDate(memory.timestamp)}</span>
                    <span class="memory-platform">${memory.platform}</span>
                </div>
                <div class="memory-actions">
                    <button onclick="window.chatgptMemory.insertMemory('${memory.id}')">Insert</button>
                    <button onclick="window.chatgptMemory.copyMemory('${memory.id}')">Copy</button>
                </div>
            </div>
        `).join('');
    }
    
    insertMemory(memoryId) {
        // Find memory content and insert into ChatGPT input
        const memoryItem = document.querySelector(`[data-memory-id="${memoryId}"]`);
        if (!memoryItem) return;
        
        const content = memoryItem.querySelector('.memory-content').textContent;
        const inputArea = this.findInputArea();
        
        if (inputArea) {
            const currentValue = inputArea.value || '';
            const newValue = currentValue + '\n\n[From Memory]: ' + content;
            
            inputArea.value = newValue;
            
            // Trigger input events to notify ChatGPT
            inputArea.dispatchEvent(new Event('input', { bubbles: true }));
            inputArea.dispatchEvent(new Event('change', { bubbles: true }));
            inputArea.focus();
            
            // Adjust textarea height if needed
            inputArea.style.height = 'auto';
            inputArea.style.height = inputArea.scrollHeight + 'px';
        }
    }
    
    findInputArea() {
        // ChatGPT input area selectors
        const selectors = [
            'textarea[placeholder*="message"]',
            '#prompt-textarea',
            '.text-base textarea',
            'form textarea'
        ];
        
        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element && element.offsetParent) {
                return element;
            }
        }
        
        return null;
    }
    
    copyMemory(memoryId) {
        const memoryItem = document.querySelector(`[data-memory-id="${memoryId}"]`);
        if (!memoryItem) return;
        
        const content = memoryItem.querySelector('.memory-content').textContent;
        navigator.clipboard.writeText(content).then(() => {
            const button = memoryItem.querySelector('button');
            const originalText = button.textContent;
            button.textContent = 'Copied!';
            setTimeout(() => {
                button.textContent = originalText;
            }, 1000);
        });
    }
    
    searchMemories() {
        const searchInput = document.getElementById('memory-search-input');
        if (!searchInput) return;
        
        const query = searchInput.value.trim();
        if (!query) {
            this.loadRecentMemories();
            return;
        }
        
        chrome.runtime.sendMessage({
            action: 'getMemories',
            query: query
        }, (response) => {
            if (response?.memories) {
                this.displayMemoriesInSidebar(response.memories);
            }
        });
    }
    
    addMemoryShortcuts() {
        // Keyboard shortcuts for ChatGPT
        document.addEventListener('keydown', (event) => {
            // Ctrl/Cmd + M to toggle memory sidebar
            if ((event.ctrlKey || event.metaKey) && event.key === 'm') {
                event.preventDefault();
                this.toggleMemorySidebar();
            }
            
            // Ctrl/Cmd + Shift + M to save conversation
            if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'M') {
                event.preventDefault();
                this.saveCurrentConversation();
            }
        });
    }
    
    saveCurrentConversation() {
        // Get current conversation from ChatGPT
        const conversationElements = document.querySelectorAll('[data-testid="conversation-turn"]');
        const conversationText = Array.from(conversationElements)
            .map(el => el.textContent)
            .filter(text => text && text.length > 10)
            .join('\n\n')
            .trim();
        
        if (conversationText.length > 50) {
            chrome.runtime.sendMessage({
                action: 'saveMemory',
                data: {
                    content: conversationText,
                    role: 'conversation',
                    platform: 'chatgpt',
                    important: true,
                    context: {
                        saved_manually: true,
                        timestamp: new Date().toISOString(),
                        url: window.location.href,
                        conversationId: this.extractConversationId()
                    }
                }
            });
            
            this.showNotification('Conversation saved to memory!');
        }
    }
    
    handleMessage(message, sender, sendResponse) {
        switch (message.action) {
            case 'toggleMemorySidebar':
                this.toggleMemorySidebar();
                break;
                
            case 'memoryToggled':
                this.isEnabled = message.enabled;
                if (!this.isEnabled) {
                    const sidebar = document.getElementById('hardcard-memory-sidebar');
                    const suggestions = document.getElementById('hardcard-memory-suggestions');
                    if (sidebar) sidebar.style.display = 'none';
                    if (suggestions) suggestions.remove();
                }
                break;
                
            case 'memorySaved':
                if (message.success) {
                    this.showNotification('Memory saved successfully!');
                }
                break;
        }
    }
    
    showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'hardcard-notification';
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }
    
    // Utility functions
    truncateText(text, maxLength) {
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
    }
    
    formatDate(timestamp) {
        const date = new Date(timestamp);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
}

// Initialize ChatGPT memory integration
const chatgptMemory = new ChatGPTMemoryIntegration();