# 🚀 AI Agent Quick Reference Card

## 🎯 Copy-Paste Starters for Each Agent

### Frontend Agent:
```
cd /Users/studio/hardcard-frontend-ai && pwd
# You are the Frontend AI working on TypeScript migration
# Your branch: ai/frontend-specialist
# Check AI_AGENT_TASKS.md for your tasks
```

### Backend Agent:
```
cd /Users/studio/hardcard-backend-ai && pwd
# You are the Backend AI working on API types
# Your branch: ai/backend-specialist  
# Check AI_AGENT_TASKS.md for your tasks
```

### Testing Agent:
```
cd /Users/studio/hardcard-testing-ai && pwd
# You are the Testing AI creating comprehensive tests
# Your branch: ai/testing-specialist
# Check AI_AGENT_TASKS.md for your tasks
```

### Docs Agent:
```
cd /Users/studio/hardcard-docs-ai && pwd
# You are the Documentation AI updating all docs
# Your branch: ai/documentation
# Check AI_AGENT_TASKS.md for your tasks
```

### Security Agent:
```
cd /Users/studio/hardcard-security-ai && pwd
# You are the Security AI auditing for vulnerabilities
# Your branch: ai/security-audit
# Check AI_AGENT_TASKS.md for your tasks
```

---

## 🎮 Your Coordinator Commands

```bash
# Check all agents
./scripts/agent-coordinator.sh status

# Merge completed work
./scripts/agent-coordinator.sh merge frontend-ai

# View specific agent workspace
cd ../hardcard-frontend-ai && git status

# Return to main
cd /Users/studio/hardcard
```

---

## 📝 Example Full Agent Prompt

```
You are the Frontend Specialist AI for the HardCard project.

CRITICAL: Your working directory is /Users/studio/hardcard-frontend-ai
First command must be: cd /Users/studio/hardcard-frontend-ai

Your current task: Enable TypeScript strict mode incrementally
- Start with noImplicitAny
- Fix type errors in Dashboard.tsx
- Update component props interfaces
- Commit after each component is fixed

Rules:
1. Work ONLY in your directory
2. Focus ONLY on frontend/ files  
3. Update STATUS.md with progress
4. Commit with clear messages
5. Do NOT touch backend/ or docs/

Begin by checking your current directory and reviewing the task list.
```

---

## 🔥 Quick Status Check

Run this to see all agents at a glance:
```bash
watch -n 30 './scripts/agent-coordinator.sh status'
```

This updates every 30 seconds showing all agent progress!