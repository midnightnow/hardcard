from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

# VaultOS Streamlit Application Launcher

router = APIRouter(prefix="/vaultos-launcher")

@router.get("/", response_class=HTMLResponse)
def launch_vaultos():
    """Launch the VaultOS Streamlit application. This endpoint serves as the main entry point
    for the VaultOS platform, providing access to the family trust fund management system."""
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Launching VaultOS</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #0f172a;
                color: #e2e8f0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
                padding: 0;
            }
            .loading-container {
                text-align: center;
            }
            h1 {
                font-size: 2.5rem;
                margin-bottom: 1rem;
            }
            .vault-icon {
                font-size: 4rem;
                margin-bottom: 1rem;
            }
            .loading-spinner {
                width: 50px;
                height: 50px;
                border: 5px solid rgba(255, 255, 255, 0.3);
                border-radius: 50%;
                border-top-color: #4f46e5;
                animation: spin 1s ease-in-out infinite;
                margin: 20px auto;
            }
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            .redirect-message {
                margin-top: 20px;
                font-size: 1.2rem;
            }
        </style>
    </head>
    <body>
        <div class="loading-container">
            <div class="vault-icon">🛡️</div>
            <h1>Legacy Vault OS</h1>
            <div class="loading-spinner"></div>
            <div class="redirect-message">Initializing secure environment...</div>
        </div>
        
        <script>
            // Redirect to the actual VaultOS dashboard after a brief delay
            setTimeout(() => {
                window.location.href = '/vaultos-streamlit/';
            }, 2000);
        </script>
    </body>
    </html>
    """

@router.get("/redirect", response_class=RedirectResponse)
def redirect_to_vaultos():
    """Redirect to the VaultOS Streamlit application."""
    return RedirectResponse(url="/vaultos-streamlit/")
