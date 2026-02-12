// AI Agent Context Bookmarklets
// Save these as bookmarks in your browser for one-click context copying

// Instructions:
// 1. Create a new bookmark in your browser
// 2. Set the name to "Frontend AI Agent"  
// 3. Set the URL to the javascript code below (including javascript: prefix)
// 4. Click the bookmark to copy context to clipboard

// Frontend AI Agent
javascript:(function(){
  const context = `I am the Frontend AI Agent for HardCard.
My working directory is: /Users/studio/hardcard-frontend-ai
My branch is: ai/frontend-specialist
My focus is: frontend/ files only

I'll start by initializing my workspace:

\`\`\`bash
cd /Users/studio/hardcard-frontend-ai
pwd
git status
ls -la
\`\`\``;
  navigator.clipboard.writeText(context).then(() => {
    alert('Frontend AI context copied! Paste into your AI chat.');
  });
})();

// Backend AI Agent
javascript:(function(){
  const context = `I am the Backend AI Agent for HardCard.
My working directory is: /Users/studio/hardcard-backend-ai
My branch is: ai/backend-specialist
My focus is: backend/ files only

I'll start by initializing my workspace:

\`\`\`bash
cd /Users/studio/hardcard-backend-ai
pwd
git status
ls -la
\`\`\``;
  navigator.clipboard.writeText(context).then(() => {
    alert('Backend AI context copied! Paste into your AI chat.');
  });
})();

// Testing AI Agent
javascript:(function(){
  const context = `I am the Testing AI Agent for HardCard.
My working directory is: /Users/studio/hardcard-testing-ai
My branch is: ai/testing-specialist
My focus is: test files only

I'll start by initializing my workspace:

\`\`\`bash
cd /Users/studio/hardcard-testing-ai
pwd
git status
ls -la
\`\`\``;
  navigator.clipboard.writeText(context).then(() => {
    alert('Testing AI context copied! Paste into your AI chat.');
  });
})();

// Documentation AI Agent
javascript:(function(){
  const context = `I am the Documentation AI Agent for HardCard.
My working directory is: /Users/studio/hardcard-docs-ai
My branch is: ai/documentation
My focus is: *.md files only

I'll start by initializing my workspace:

\`\`\`bash
cd /Users/studio/hardcard-docs-ai
pwd
git status
ls -la
\`\`\``;
  navigator.clipboard.writeText(context).then(() => {
    alert('Documentation AI context copied! Paste into your AI chat.');
  });
})();

// Security AI Agent
javascript:(function(){
  const context = `I am the Security AI Agent for HardCard.
My working directory is: /Users/studio/hardcard-security-ai
My branch is: ai/security-audit
My focus is: security analysis

I'll start by initializing my workspace:

\`\`\`bash
cd /Users/studio/hardcard-security-ai
pwd
git status
ls -la
\`\`\``;
  navigator.clipboard.writeText(context).then(() => {
    alert('Security AI context copied! Paste into your AI chat.');
  });
})();