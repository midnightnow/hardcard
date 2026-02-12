// HARDCARD Memory Assistant - Claude Integration
console.log('HARDCARD Memory: Claude integration loaded');

class ClaudeMemoryIntegration {
    constructor() {
        this.isEnabled = true;
        this.sidebarVisible = false;
        this.lastMessageContent = '';
        this.conversationHistory = [];
        this.memoryKeywords = [];
        
        this.init();
    }
    
    async init() {
        // Check if memory is enabled
        const { hardcard_memory_enabled } = await chrome.storage.sync.get(['hardcard_memory_enabled']);
        this.isEnabled = hardcard_memory_enabled !== false;
        
        if (this.isEnabled) {
            this.setupMessageObserver();
            this.createMemoryInterface();
            this.loadMemoryKeywords();
            this.addMemoryShortcuts();
        }
        
        // Listen for messages from background script
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            this.handleMessage(message, sender, sendResponse);
        });
    }
    
    setupMessageObserver() {
        // Observe changes in Claude's conversation area
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
        
        // Start observing the conversation container
        const conversationContainer = this.findConversationContainer();
        if (conversationContainer) {
            observer.observe(conversationContainer, {
                childList: true,
                subtree: true
            });
        }
        
        // Retry finding container if not immediately available
        if (!conversationContainer) {
            setTimeout(() => this.setupMessageObserver(), 1000);
        }
    }
    
    findConversationContainer() {
        // Claude's conversation container selectors (may need updates as Claude UI changes)
        const selectors = [
            '[role="main"]',
            '.conversation',
            '.chat-container',
            '[data-testid="conversation"]'
        ];
        
        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element) return element;
        }
        
        return null;
    }
    
    processNewMessage(node) {
        // Look for assistant responses in Claude
        const assistantMessage = this.extractAssistantMessage(node);
        const userMessage = this.extractUserMessage(node);
        
        if (assistantMessage) {
            this.saveConversationMemory(assistantMessage, 'assistant');
            this.suggestRelevantMemories(assistantMessage);
        }
        
        if (userMessage) {
            this.saveConversationMemory(userMessage, 'user');
        }
    }
    
    extractAssistantMessage(node) {
        // Claude-specific selectors for assistant messages
        const assistantSelectors = [
            '[data-is-streaming="false"]',
            '.font-claude-message',
            '.prose',
            '[role="assistant"]'
        ];
        
        for (const selector of assistantSelectors) {
            const element = node.querySelector ? node.querySelector(selector) : 
                           node.matches && node.matches(selector) ? node : null;
            
            if (element) {
                const text = element.innerText || element.textContent;
                if (text && text.length > 10 && text !== this.lastMessageContent) {
                    this.lastMessageContent = text;
                    return text;
                }
            }
        }
        
        return null;
    }
    
    extractUserMessage(node) {
        // Look for user input messages
        const userSelectors = [
            '[data-role="user"]',
            '.user-message',
            '.whitespace-pre-wrap'
        ];
        
        for (const selector of userSelectors) {
            const element = node.querySelector ? node.querySelector(selector) : 
                           node.matches && node.matches(selector) ? node : null;
            
            if (element) {
                const text = element.innerText || element.textContent;
                if (text && text.length > 3) {
                    return text;
                }
            }
        }
        
        return null;
    }
    
    async saveConversationMemory(content, role) {
        if (!this.isEnabled || content.length < 10) return;
        
        // Extract key information and context
        const memoryData = {
            content: content,
            role: role,
            platform: 'claude',
            context: {
                conversationLength: this.conversationHistory.length,
                timestamp: new Date().toISOString(),
                pageTitle: document.title,
                url: window.location.href
            }
        };
        
        // Add to local conversation history
        this.conversationHistory.push(memoryData);
        
        // Send to background script for storage
        chrome.runtime.sendMessage({
            action: 'saveMemory',
            data: memoryData
        });
        
        // Update memory keywords
        this.updateMemoryKeywords(content);
    }
    
    async suggestRelevantMemories(content) {
        // Search for relevant memories based on current message
        chrome.runtime.sendMessage({
            action: 'getMemories',
            query: content.substring(0, 200) // Use first 200 chars for search
        }, (response) => {
            if (response?.memories?.length > 0) {
                this.displayMemorySuggestions(response.memories);
            }
        });
    }
    
    displayMemorySuggestions(memories) {
        // Create or update memory suggestions UI
        let suggestionBox = document.getElementById('hardcard-memory-suggestions');
        
        if (!suggestionBox) {
            suggestionBox = document.createElement('div');
            suggestionBox.id = 'hardcard-memory-suggestions';
            suggestionBox.className = 'hardcard-memory-suggestions';
            
            // Insert near the input area
            const inputArea = this.findInputArea();
            if (inputArea) {
                inputArea.parentNode.insertBefore(suggestionBox, inputArea);
            }
        }
        
        // Populate with memory suggestions
        suggestionBox.innerHTML = `
            <div class="memory-header">
                <span class="memory-icon">🧠</span>
                <span>Relevant Memories</span>
                <button class="memory-close" onclick="this.parentElement.parentElement.style.display='none'">×</button>
            </div>
            <div class="memory-list">
                ${memories.slice(0, 3).map((memory, index) => `
                    <div class="memory-item" data-memory-id="${memory.id}">
                        <div class="memory-content">${this.truncateText(memory.content, 100)}</div>
                        <div class="memory-meta">${this.formatDate(memory.timestamp)} • ${memory.platform}</div>
                    </div>
                `).join('')}
            </div>
        `;
        
        suggestionBox.style.display = 'block';
        
        // Auto-hide after 10 seconds
        setTimeout(() => {
            if (suggestionBox) {
                suggestionBox.style.display = 'none';
            }
        }, 10000);
    }
    
    findInputArea() {
        // Claude input area selectors
        const selectors = [
            '[contenteditable="true"]',
            'textarea',
            '.ProseMirror',
            '[role="textbox"]'
        ];
        
        for (const selector of selectors) {
            const element = document.querySelector(selector);
            if (element && element.offsetParent) { // Check if visible
                return element;
            }
        }
        
        return null;
    }
    
    createMemoryInterface() {
        // Add memory sidebar toggle button
        const toggleButton = document.createElement('button');
        toggleButton.id = 'hardcard-memory-toggle';
        toggleButton.className = 'hardcard-memory-toggle';
        toggleButton.innerHTML = '🧠';
        toggleButton.title = 'Toggle HARDCARD Memory';
        toggleButton.onclick = () => this.toggleMemorySidebar();
        
        // Insert button in header area
        const header = document.querySelector('header') || document.querySelector('nav');
        if (header) {
            header.appendChild(toggleButton);
        } else {
            document.body.appendChild(toggleButton);
        }
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
                    <button onclick="window.hardcardMemory.searchMemories()">🔍</button>
                </div>
                <div class="memory-categories">
                    <button class="category-btn active" data-category="all">All</button>
                    <button class="category-btn" data-category="recent">Recent</button>
                    <button class="category-btn" data-category="important">Important</button>
                </div>
                <div class="memory-list" id="sidebar-memory-list">
                    <div class="loading">Loading memories...</div>
                </div>
            </div>
        `;
        
        document.body.appendChild(sidebar);
        
        // Set up search functionality
        window.hardcardMemory = this;
        
        return sidebar;
    }
    
    async loadRecentMemories() {
        const memoryList = document.getElementById('sidebar-memory-list');
        if (!memoryList) return;
        
        chrome.runtime.sendMessage({
            action: 'getMemories',
            query: 'recent' // Get recent memories
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
                    <button onclick="window.hardcardMemory.insertMemory('${memory.id}')">Insert</button>
                    <button onclick="window.hardcardMemory.copyMemory('${memory.id}')">Copy</button>
                </div>
            </div>
        `).join('');
    }
    
    insertMemory(memoryId) {
        // Find the memory content and insert it into Claude's input
        const memoryItem = document.querySelector(`[data-memory-id="${memoryId}"]`);
        if (!memoryItem) return;
        
        const content = memoryItem.querySelector('.memory-content').textContent;
        const inputArea = this.findInputArea();
        
        if (inputArea) {
            // Insert memory content into input
            const currentValue = inputArea.value || inputArea.textContent || '';
            const newValue = currentValue + '\n\n[From Memory]: ' + content;
            
            if (inputArea.value !== undefined) {
                inputArea.value = newValue;
            } else {
                inputArea.textContent = newValue;
            }
            
            // Trigger input event
            inputArea.dispatchEvent(new Event('input', { bubbles: true }));
            inputArea.focus();
        }
    }
    
    copyMemory(memoryId) {
        const memoryItem = document.querySelector(`[data-memory-id="${memoryId}"]`);
        if (!memoryItem) return;
        
        const content = memoryItem.querySelector('.memory-content').textContent;
        navigator.clipboard.writeText(content).then(() => {
            // Show copy confirmation
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
        // Add keyboard shortcuts for memory functions
        document.addEventListener('keydown', (event) => {
            // Ctrl/Cmd + M to toggle memory sidebar
            if ((event.ctrlKey || event.metaKey) && event.key === 'm') {
                event.preventDefault();
                this.toggleMemorySidebar();
            }
            
            // Ctrl/Cmd + Shift + M to save current conversation as important memory
            if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'M') {
                event.preventDefault();
                this.saveCurrentConversationAsMemory();
            }
        });
    }
    
    saveCurrentConversationAsMemory() {
        // Get current conversation content
        const conversationElements = document.querySelectorAll('[role="main"] > div');
        const conversationText = Array.from(conversationElements)
            .map(el => el.textContent)
            .join('\n')
            .trim();
        
        if (conversationText.length > 50) {
            chrome.runtime.sendMessage({
                action: 'saveMemory',
                data: {
                    content: conversationText,
                    role: 'conversation',
                    platform: 'claude',
                    important: true,
                    context: {
                        saved_manually: true,
                        timestamp: new Date().toISOString(),
                        url: window.location.href
                    }
                }
            });
            
            // Show confirmation
            this.showNotification('Conversation saved to memory!');
        }
    }
    
    async loadMemoryKeywords() {
        // Load user's memory keywords for better context detection
        chrome.runtime.sendMessage({
            action: 'getMemories',
            query: 'keywords'
        }, (response) => {
            if (response?.memories) {
                this.memoryKeywords = response.memories
                    .map(m => m.content.split(' '))
                    .flat()
                    .filter(word => word.length > 3)
                    .slice(0, 100); // Keep top 100 keywords
            }
        });
    }
    
    updateMemoryKeywords(content) {
        // Extract important keywords from new content
        const words = content.toLowerCase()
            .split(/\W+/)
            .filter(word => word.length > 3 && !this.isCommonWord(word));
        
        words.forEach(word => {
            if (!this.memoryKeywords.includes(word)) {
                this.memoryKeywords.push(word);
            }
        });
        
        // Keep only most recent 100 keywords
        if (this.memoryKeywords.length > 100) {
            this.memoryKeywords = this.memoryKeywords.slice(-100);
        }
    }
    
    isCommonWord(word) {
        const commonWords = ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'man', 'end', 'few', 'got', 'let', 'say', 'she', 'too', 'use'];
        return commonWords.includes(word);
    }
    
    handleMessage(message, sender, sendResponse) {
        switch (message.action) {
            case 'toggleMemorySidebar':
                this.toggleMemorySidebar();
                break;
                
            case 'memoryToggled':
                this.isEnabled = message.enabled;
                if (!this.isEnabled) {
                    // Hide any visible memory UI
                    const sidebar = document.getElementById('hardcard-memory-sidebar');
                    const suggestions = document.getElementById('hardcard-memory-suggestions');
                    if (sidebar) sidebar.style.display = 'none';
                    if (suggestions) suggestions.style.display = 'none';
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
        // Create temporary notification
        const notification = document.createElement('div');
        notification.className = 'hardcard-notification';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #4f46e5;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 10000;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
        `;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
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

// Initialize Claude memory integration
const claudeMemory = new ClaudeMemoryIntegration();