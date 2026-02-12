// HARDCARD Memory Assistant - Background Script
console.log('HARDCARD Memory Assistant background script loaded');

// Handle extension icon click
chrome.action.onClicked.addListener(async (tab) => {
  console.log('Extension icon clicked on tab:', tab.url);
  
  try {
    // Check if user is authenticated
    const { hardcard_api_key, hardcard_user_id } = await chrome.storage.sync.get(['hardcard_api_key', 'hardcard_user_id']);
    
    if (hardcard_api_key && hardcard_user_id) {
      // User is authenticated, toggle memory sidebar
      await chrome.tabs.sendMessage(tab.id, { 
        action: 'toggleMemorySidebar',
        userId: hardcard_user_id,
        apiKey: hardcard_api_key
      });
    } else {
      // User not authenticated, open popup for login
      chrome.action.openPopup();
    }
  } catch (error) {
    console.error('Error handling icon click:', error);
    // Fallback to popup if content script not available
    chrome.action.openPopup();
  }
});

// Handle extension installation/update
chrome.runtime.onInstalled.addListener(async (details) => {
  console.log('HARDCARD Memory Assistant installed/updated:', details.reason);
  
  // Enable memory by default
  await chrome.storage.sync.set({ 
    hardcard_memory_enabled: true,
    hardcard_auto_save: true,
    hardcard_context_sharing: true
  });
  
  // Show welcome message on first install
  if (details.reason === 'install') {
    chrome.tabs.create({
      url: 'https://hardcard.ai/memory-extension-welcome'
    });
  }
});

// Handle messages from content scripts and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Background received message:', message);
  
  switch (message.action) {
    case 'saveMemory':
      handleSaveMemory(message.data, sender.tab);
      break;
      
    case 'getMemories':
      handleGetMemories(message.query, sender.tab).then(sendResponse);
      return true; // Will respond asynchronously
      
    case 'openDashboard':
      chrome.tabs.create({ url: message.url || 'https://hardcard.ai/memory-dashboard' });
      break;
      
    case 'updateSettings':
      chrome.storage.sync.set(message.settings);
      break;
      
    case 'authenticate':
      handleAuthentication(message.credentials).then(sendResponse);
      return true; // Will respond asynchronously
      
    default:
      console.warn('Unknown message action:', message.action);
  }
});

// Save memory to HARDCARD backend
async function handleSaveMemory(memoryData, tab) {
  try {
    const { hardcard_api_key, hardcard_user_id } = await chrome.storage.sync.get(['hardcard_api_key', 'hardcard_user_id']);
    
    if (!hardcard_api_key || !hardcard_user_id) {
      console.error('User not authenticated');
      return;
    }
    
    const response = await fetch('https://api.hardcard.ai/v1/memory/save', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${hardcard_api_key}`,
        'X-User-ID': hardcard_user_id
      },
      body: JSON.stringify({
        content: memoryData.content,
        context: memoryData.context,
        platform: memoryData.platform,
        url: tab?.url,
        timestamp: new Date().toISOString(),
        metadata: {
          tab_title: tab?.title,
          user_agent: navigator.userAgent
        }
      })
    });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }
    
    const result = await response.json();
    console.log('Memory saved successfully:', result);
    
    // Notify content script of successful save
    if (tab?.id) {
      chrome.tabs.sendMessage(tab.id, {
        action: 'memorySaved',
        success: true,
        memoryId: result.memory_id
      });
    }
    
  } catch (error) {
    console.error('Error saving memory:', error);
    
    // Store locally as fallback
    const localMemories = await chrome.storage.local.get(['hardcard_local_memories']) || { hardcard_local_memories: [] };
    localMemories.hardcard_local_memories.push({
      ...memoryData,
      timestamp: new Date().toISOString(),
      synced: false
    });
    await chrome.storage.local.set(localMemories);
  }
}

// Retrieve memories from HARDCARD backend
async function handleGetMemories(query, tab) {
  try {
    const { hardcard_api_key, hardcard_user_id } = await chrome.storage.sync.get(['hardcard_api_key', 'hardcard_user_id']);
    
    if (!hardcard_api_key || !hardcard_user_id) {
      console.error('User not authenticated');
      return { memories: [], error: 'Not authenticated' };
    }
    
    const response = await fetch('https://api.hardcard.ai/v1/memory/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${hardcard_api_key}`,
        'X-User-ID': hardcard_user_id
      },
      body: JSON.stringify({
        query: query,
        context: {
          platform: getPlatformFromUrl(tab?.url),
          url: tab?.url
        },
        limit: 10
      })
    });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status}`);
    }
    
    const result = await response.json();
    return { memories: result.memories || [], success: true };
    
  } catch (error) {
    console.error('Error retrieving memories:', error);
    
    // Fallback to local storage
    const localMemories = await chrome.storage.local.get(['hardcard_local_memories']);
    return { 
      memories: localMemories.hardcard_local_memories || [], 
      error: 'Using local storage',
      success: false 
    };
  }
}

// Handle user authentication
async function handleAuthentication(credentials) {
  try {
    const response = await fetch('https://api.hardcard.ai/v1/auth/extension', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(credentials)
    });
    
    if (!response.ok) {
      throw new Error(`Authentication failed: ${response.status}`);
    }
    
    const result = await response.json();
    
    // Store authentication data
    await chrome.storage.sync.set({
      hardcard_api_key: result.api_key,
      hardcard_user_id: result.user_id,
      hardcard_user_profile: result.profile
    });
    
    console.log('Authentication successful');
    return { success: true, user: result.profile };
    
  } catch (error) {
    console.error('Authentication error:', error);
    return { success: false, error: error.message };
  }
}

// Sync local memories when online
async function syncLocalMemories() {
  try {
    const { hardcard_api_key, hardcard_user_id } = await chrome.storage.sync.get(['hardcard_api_key', 'hardcard_user_id']);
    const { hardcard_local_memories } = await chrome.storage.local.get(['hardcard_local_memories']);
    
    if (!hardcard_api_key || !hardcard_user_id || !hardcard_local_memories?.length) {
      return;
    }
    
    const unsyncedMemories = hardcard_local_memories.filter(memory => !memory.synced);
    
    for (const memory of unsyncedMemories) {
      const response = await fetch('https://api.hardcard.ai/v1/memory/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${hardcard_api_key}`,
          'X-User-ID': hardcard_user_id
        },
        body: JSON.stringify(memory)
      });
      
      if (response.ok) {
        memory.synced = true;
      }
    }
    
    // Update local storage
    await chrome.storage.local.set({ hardcard_local_memories });
    console.log('Local memories synced successfully');
    
  } catch (error) {
    console.error('Error syncing local memories:', error);
  }
}

// Utility function to get platform from URL
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

// Periodic sync of local memories
setInterval(syncLocalMemories, 5 * 60 * 1000); // Every 5 minutes