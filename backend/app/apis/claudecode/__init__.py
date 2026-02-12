from fastapi import APIRouter, HTTPException
import os
import json

router = APIRouter(prefix="/claudecode")

# Define the file structure and content
files_to_create = {
    "ui/package.json": {
        "name": "claudecode-app",
        "private": True,
        "version": "0.0.0",
        "type": "module",
        "scripts": {
            "dev": "vite",
            "build": "vite build",
            "preview": "vite preview"
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0"
        },
        "devDependencies": {
            "@types/react": "^18.2.15",
            "@types/react-dom": "^18.2.7",
            "@vitejs/plugin-react": "^4.0.3",
            "vite": "^4.4.5"
        }
    },
    "ui/vite.config.ts": """
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
})
""",
    "ui/src/main.tsx": """
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './pages/App.tsx'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
""",
    "ui/src/pages/App.tsx": """
function App() {
  return (
    <div>
      <h1>Hello World</h1>
    </div>
  )
}

export default App
"""
}

@router.post("/init")
async def init_claude_code():
    """
    Initializes a new ClaudeCode environment by creating the necessary files and directories.
    """
    try:
        for filepath, content in files_to_create.items():
            # Create directories if they don't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            # Write the file
            with open(filepath, "w") as f:
                if isinstance(content, dict):
                    json.dump(content, f, indent=2)
                else:
                    f.write(content)
        return {"message": "ClaudeCode environment initialized successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
