// HARDCARD Memory Assistant - Popup Script
console.log('HARDCARD Memory popup loaded');

// DOM elements
let authSection, statusSection, loadingSection, errorMessage;
let signInBtn, dashboardBtn, settingsBtn, toggleMemoryBtn;
let memoryStatus, memoriesCount, autoSaveStatus, currentPlatform;

// Initialize popup when DOM is loaded
document.addEventListener('DOMContentLoaded', async () => {
    initializeElements();
    await checkAuthenticationStatus();
    setupEventListeners();
});

function initializeElements() {
    // Sections
    authSection = document.getElementById('authSection');
    statusSection = document.getElementById('statusSection');
    loadingSection = document.getElementById('loadingSection');
    errorMessage = document.getElementById('errorMessage');
    
    // Buttons
    signInBtn = document.getElementById('signInBtn');
    dashboardBtn = document.getElementById('dashboardBtn');
    settingsBtn = document.getElementById('settingsBtn');
    toggleMemoryBtn = document.getElementById('toggleMemoryBtn');
    
    // Status elements
    memoryStatus = document.getElementById('memoryStatus');
    memoriesCount = document.getElementById('memoriesCount');
    autoSaveStatus = document.getElementById('autoSaveStatus');
    currentPlatform = document.getElementById('currentPlatform');
}

async function checkAuthenticationStatus() {
    showLoading(true);
    
    try {
        const { hardcard_api_key, hardcard_user_id, hardcard_user_profile } = 
            await chrome.storage.sync.get(['hardcard_api_key', 'hardcard_user_id', 'hardcard_user_profile']);
        
        if (hardcard_api_key && hardcard_user_id) {
            // User is authenticated
            await showStatusSection();
            await loadUserStatus();
        } else {
            // User needs to authenticate
            showAuthSection();
        }
    } catch (error) {
        console.error('Error checking authentication:', error);
        showError('Failed to check authentication status');
        showAuthSection();
    }
    
    showLoading(false);
}

async function loadUserStatus() {
    try {
        // Get current tab to determine platform
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        const platform = getPlatformFromUrl(tab?.url);
        currentPlatform.textContent = capitalizeFirst(platform);
        
        // Get memory settings
        const { 
            hardcard_memory_enabled, 
            hardcard_auto_save,
            hardcard_memory_count 
        } = await chrome.storage.sync.get([
            'hardcard_memory_enabled', 
            'hardcard_auto_save',
            'hardcard_memory_count'
        ]);
        
        // Update status display
        memoryStatus.textContent = hardcard_memory_enabled ? 'Active' : 'Disabled';
        memoryStatus.className = `status-value ${hardcard_memory_enabled ? 'status-enabled' : 'status-disabled'}`;
        
        autoSaveStatus.textContent = hardcard_auto_save ? 'On' : 'Off';
        autoSaveStatus.className = `status-value ${hardcard_auto_save ? 'status-enabled' : 'status-disabled'}`;
        
        memoriesCount.textContent = hardcard_memory_count || '0';
        
        // Update toggle button text
        toggleMemoryBtn.textContent = hardcard_memory_enabled ? 'Disable Memory' : 'Enable Memory';
        
        // Check if user is on a supported AI platform
        if (platform === 'unknown') {
            showError('Navigate to an AI platform (Claude, ChatGPT, etc.) to use memory features');
        }
        
    } catch (error) {
        console.error('Error loading user status:', error);
        showError('Failed to load status');
    }
}

function setupEventListeners() {
    // Sign in button
    signInBtn?.addEventListener('click', handleSignIn);
    
    // Dashboard button
    dashboardBtn?.addEventListener('click', () => {
        chrome.runtime.sendMessage({ 
            action: 'openDashboard',
            url: 'https://hardcard.ai/memory-dashboard'
        });
        window.close();
    });
    
    // Settings button
    settingsBtn?.addEventListener('click', () => {
        chrome.runtime.sendMessage({ 
            action: 'openDashboard',
            url: 'https://hardcard.ai/memory-settings'
        });
        window.close();
    });
    
    // Toggle memory button
    toggleMemoryBtn?.addEventListener('click', handleToggleMemory);
}

async function handleSignIn() {
    try {
        showLoading(true);
        
        // Generate a unique user ID for this session
        const userId = `hardcard_extension_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        
        // Store temporary user ID
        await chrome.storage.sync.set({ hardcard_temp_user_id: userId });
        
        // Check if user is already logged in by opening the extension page
        const authUrl = 'https://hardcard.ai/extension-auth?source=chrome-extension&userId=' + encodeURIComponent(userId);
        
        chrome.tabs.create({ url: authUrl }, (tab) => {
            // Close popup after opening auth tab
            window.close();
        });
        
    } catch (error) {
        console.error('Error during sign in:', error);
        showError('Failed to initiate sign in. Please try again.');
        showLoading(false);
    }
}

async function handleToggleMemory() {
    try {
        const { hardcard_memory_enabled } = await chrome.storage.sync.get(['hardcard_memory_enabled']);
        const newState = !hardcard_memory_enabled;
        
        await chrome.storage.sync.set({ hardcard_memory_enabled: newState });
        
        // Update UI
        memoryStatus.textContent = newState ? 'Active' : 'Disabled';
        memoryStatus.className = `status-value ${newState ? 'status-enabled' : 'status-disabled'}`;
        toggleMemoryBtn.textContent = newState ? 'Disable Memory' : 'Enable Memory';
        
        // Notify content scripts of the change
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        if (tab?.id) {
            chrome.tabs.sendMessage(tab.id, {
                action: 'memoryToggled',
                enabled: newState
            }).catch(() => {
                // Ignore errors if content script not available
            });
        }
        
    } catch (error) {
        console.error('Error toggling memory:', error);
        showError('Failed to toggle memory');
    }
}

function showAuthSection() {
    authSection.style.display = 'block';
    statusSection.style.display = 'none';
    loadingSection.style.display = 'none';
}

function showStatusSection() {
    authSection.style.display = 'none';
    statusSection.style.display = 'block';
    loadingSection.style.display = 'none';
}

function showLoading(show) {
    loadingSection.style.display = show ? 'block' : 'none';
    if (show) {
        authSection.style.display = 'none';
        statusSection.style.display = 'none';
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

function getPlatformFromUrl(url) {
    if (!url) return 'unknown';
    
    if (url.includes('claude.ai')) return 'claude';
    if (url.includes('chat.openai.com') || url.includes('chatgpt.com')) return 'chatgpt';
    if (url.includes('perplexity.ai')) return 'perplexity';
    if (url.includes('gemini.google.com')) return 'gemini';
    if (url.includes('poe.com')) return 'poe';
    if (url.includes('you.com')) return 'you';
    if (url.includes('character.ai')) return 'character';
    
    return 'unknown';
}

function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Listen for authentication completion
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'authenticationComplete') {
        checkAuthenticationStatus();
    }
});