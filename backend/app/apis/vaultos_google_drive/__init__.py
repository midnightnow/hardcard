"""VaultOS Google Drive API

This API provides Google Drive integration for VaultOS, including:
1. Mirroring the VaultOS folder structure in Google Drive
2. Automated backup functionality
3. Synchronization between local and cloud storage

The API creates a Google Drive folder structure that mirrors both the user-facing
organizational structure and the technical system architecture of VaultOS.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import json
import datetime
import time
import databutton as db
import re

# Google API imports
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Local imports
from app.apis.vaultos_folder_structure import get_folder_structure
from app.apis.vaultos_architecture import get_vaultos_architecture

router = APIRouter()

# Models
class GoogleDriveConfig(BaseModel):
    """Configuration for Google Drive integration"""
    enabled: bool = False
    sync_interval_minutes: int = 60
    user_folders_path: str = "Legacy Vault User Data"
    system_folders_path: str = "Legacy Vault System"
    backup_logs: bool = True
    last_sync: Optional[str] = None

class GoogleDriveCredentials(BaseModel):
    """Google Drive credentials"""
    token: Dict[str, Any]
    refresh_token: str
    token_uri: str
    client_id: str
    client_secret: str
    scopes: List[str]

class DriveOperationResult(BaseModel):
    """Result of a Google Drive operation"""
    success: bool
    message: str
    details: Optional[Dict[str, Any]] = None

class SyncStatus(BaseModel):
    """Status of the Google Drive sync"""
    enabled: bool
    last_sync: Optional[str] = None
    next_sync: Optional[str] = None
    status: str
    folders_synced: int = 0
    files_synced: int = 0

# Constants
DRIVE_CONFIG_KEY = "google_drive_config"
DRIVE_CREDENTIALS_KEY = "google_drive_credentials"
DRIVE_LAST_BACKUP_LOG_KEY = "google_drive_last_backup_log"

# Helper functions
def get_drive_service():
    """Get an authenticated Google Drive service instance"""
    try:
        # Get stored credentials
        credentials_dict = db.storage.json.get(DRIVE_CREDENTIALS_KEY, None)
        
        if not credentials_dict:
            raise HTTPException(status_code=400, detail="Google Drive credentials not found")
            
        credentials = Credentials(
            token=credentials_dict.get("token"),
            refresh_token=credentials_dict.get("refresh_token"),
            token_uri=credentials_dict.get("token_uri"),
            client_id=credentials_dict.get("client_id"),
            client_secret=credentials_dict.get("client_secret"),
            scopes=credentials_dict.get("scopes")
        )
        
        return build('drive', 'v3', credentials=credentials)
    except Exception as e:
        print(f"Error getting Drive service: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize Google Drive service: {str(e)}")

def get_or_create_folder(service, name, parent_id=None):
    """Get a folder by name, or create it if it doesn't exist"""
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    query += " and trashed=false"
    
    response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = response.get('files', [])
    
    if files:
        return files[0]['id']
    else:
        # Create the folder
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
            
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

def save_file_to_drive(service, name, content, mime_type, parent_id):
    """Save a file to Google Drive"""
    from googleapiclient.http import MediaInMemoryUpload
    
    # Check if file already exists in the folder
    query = f"name='{name}' and '{parent_id}' in parents and trashed=false"
    response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = response.get('files', [])
    
    media = MediaInMemoryUpload(content.encode('utf-8'), mimetype=mime_type)
    
    if files:
        # Update existing file
        file_id = files[0]['id']
        updated_file = service.files().update(
            fileId=file_id,
            media_body=media,
            fields='id'
        ).execute()
        return updated_file.get('id')
    else:
        # Create new file
        file_metadata = {
            'name': name,
            'parents': [parent_id]
        }
        new_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        return new_file.get('id')

def sanitize_filename(filename):
    """Make a filename safe for use in Google Drive"""
    # Replace problematic characters
    return re.sub(r'[\\/*?:|<>"\[\]]', '_', filename)

def get_config():
    """Get the Google Drive configuration"""
    try:
        config = db.storage.json.get(DRIVE_CONFIG_KEY, None)
        if not config:
            # Create default config
            config = GoogleDriveConfig().dict()
            db.storage.json.put(DRIVE_CONFIG_KEY, config)
        return config
    except Exception as e:
        print(f"Error getting Google Drive config: {str(e)}")
        return GoogleDriveConfig().dict()

def update_config(config):
    """Update the Google Drive configuration"""
    try:
        db.storage.json.put(DRIVE_CONFIG_KEY, config)
        return True
    except Exception as e:
        print(f"Error updating Google Drive config: {str(e)}")
        return False

def log_backup_operation(log_data):
    """Log backup operation details"""
    try:
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            **log_data
        }
        
        # Get existing logs
        existing_logs = db.storage.json.get(DRIVE_LAST_BACKUP_LOG_KEY, [])
        if not isinstance(existing_logs, list):
            existing_logs = []
            
        # Add new log and keep only the last 100 entries
        existing_logs.append(log_entry)
        if len(existing_logs) > 100:
            existing_logs = existing_logs[-100:]
            
        db.storage.json.put(DRIVE_LAST_BACKUP_LOG_KEY, existing_logs)
        return True
    except Exception as e:
        print(f"Error logging backup operation: {str(e)}")
        return False

# API Endpoints
@router.get("/google-drive-config")
def get_google_drive_config() -> GoogleDriveConfig:
    """Get the current Google Drive configuration"""
    config = get_config()
    return GoogleDriveConfig(**config)

@router.post("/google-drive-config")
def update_google_drive_config(config: GoogleDriveConfig) -> DriveOperationResult:
    """Update the Google Drive configuration"""
    result = update_config(config.dict())
    return DriveOperationResult(
        success=result,
        message="Configuration updated successfully" if result else "Failed to update configuration"
    )

@router.post("/save-google-credentials")
def save_google_credentials(credentials: GoogleDriveCredentials) -> DriveOperationResult:
    """Save Google Drive API credentials"""
    try:
        db.storage.json.put(DRIVE_CREDENTIALS_KEY, credentials.dict())
        return DriveOperationResult(
            success=True,
            message="Google Drive credentials saved successfully"
        )
    except Exception as e:
        return DriveOperationResult(
            success=False,
            message=f"Failed to save Google Drive credentials: {str(e)}"
        )

@router.get("/test-google-drive-connection")
def test_google_drive_connection() -> DriveOperationResult:
    """Test the Google Drive connection"""
    try:
        service = get_drive_service()
        about = service.about().get(fields="user").execute()
        
        return DriveOperationResult(
            success=True,
            message="Successfully connected to Google Drive",
            details={"user": about.get("user", {})}
        )
    except Exception as e:
        return DriveOperationResult(
            success=False,
            message=f"Failed to connect to Google Drive: {str(e)}"
        )

@router.post("/create-vaultos-folder-structure")
def create_vaultos_folder_structure(background_tasks: BackgroundTasks) -> DriveOperationResult:
    """Create the VaultOS folder structure in Google Drive"""
    try:
        # Start the folder creation in the background
        background_tasks.add_task(create_user_folder_structure_task)
        background_tasks.add_task(create_system_folder_structure_task)
        
        return DriveOperationResult(
            success=True,
            message="Started creating VaultOS folder structure in Google Drive. This may take a few minutes."
        )
    except Exception as e:
        return DriveOperationResult(
            success=False,
            message=f"Failed to start folder structure creation: {str(e)}"
        )

def create_user_folder_structure_task():
    """Background task to create the user-facing folder structure in Google Drive"""
    try:
        config = get_config()
        service = get_drive_service()
        
        # Get the root folder or create it
        root_folder_id = get_or_create_folder(service, config['user_folders_path'])
        
        # Get the folder structure from the API
        folder_structure = get_folder_structure()
        
        # Create the root VaultOS folder
        vault_folder_id = get_or_create_folder(service, folder_structure.name, root_folder_id)
        
        # Track our progress for logging
        created_folders = 1  # Root folder
        created_files = 0
        
        # Create the folder structure recursively
        created_folders += create_folders_recursively(service, vault_folder_id, folder_structure.children, created_files)
        
        # Update last sync time
        config['last_sync'] = datetime.datetime.now().isoformat()
        update_config(config)
        
        # Log the operation
        log_backup_operation({
            "operation": "create_user_folder_structure",
            "folders_created": created_folders,
            "files_created": created_files,
            "status": "success"
        })
        
    except Exception as e:
        print(f"Error creating user folder structure: {str(e)}")
        log_backup_operation({
            "operation": "create_user_folder_structure",
            "status": "error",
            "error": str(e)
        })

def create_system_folder_structure_task():
    """Background task to create the system architecture folder structure in Google Drive"""
    try:
        config = get_config()
        service = get_drive_service()
        
        # Get the root folder or create it
        root_folder_id = get_or_create_folder(service, config['system_folders_path'])
        
        # Get the architecture from the API
        architecture = get_vaultos_architecture()
        
        # Create folders for each component
        created_folders = 0
        created_files = 0
        
        # Get the root component
        root_component = architecture.components.get(architecture.root_component)
        if not root_component:
            raise ValueError("Root component not found in architecture")
            
        # Create the root folder
        vaultos_folder_id = get_or_create_folder(service, root_component.name, root_folder_id)
        created_folders += 1
        
        # Add README if present
        if root_component.readme:
            save_file_to_drive(service, "README.md", root_component.readme, "text/markdown", vaultos_folder_id)
            created_files += 1
        
        # Create component folders and READMEs
        component_folders = {architecture.root_component: vaultos_folder_id}
        
        # First pass: create all folders
        for component_id, component in architecture.components.items():
            if component_id == architecture.root_component:
                continue  # Already created the root folder
                
            # Get the parent folder ID
            parent_folder_id = root_folder_id
            if component.parent and component.parent in component_folders:
                parent_folder_id = component_folders[component.parent]
                
            # Create the component folder
            folder_id = get_or_create_folder(service, component.name, parent_folder_id)
            component_folders[component_id] = folder_id
            created_folders += 1
            
            # Add README if present
            if component.readme:
                save_file_to_drive(service, "README.md", component.readme, "text/markdown", folder_id)
                created_files += 1
                
            # Add config template if present
            if component.config_template:
                config_content = json.dumps(component.config_template.dict(), indent=2)
                save_file_to_drive(service, "config_template.json", config_content, "application/json", folder_id)
                created_files += 1
        
        # Update last sync time
        config['last_sync'] = datetime.datetime.now().isoformat()
        update_config(config)
        
        # Log the operation
        log_backup_operation({
            "operation": "create_system_folder_structure",
            "folders_created": created_folders,
            "files_created": created_files,
            "status": "success"
        })
        
    except Exception as e:
        print(f"Error creating system folder structure: {str(e)}")
        log_backup_operation({
            "operation": "create_system_folder_structure",
            "status": "error",
            "error": str(e)
        })

def create_folders_recursively(service, parent_id, folders, file_count):
    """Recursively create folders and their children"""
    created_count = 0
    
    for folder in folders:
        # Create the folder
        folder_id = get_or_create_folder(service, folder.name, parent_id)
        created_count += 1
        
        # Add files if present
        if folder.files:
            for file in folder.files:
                # Create a placeholder file with description
                file_content = f"# {file.name}\n\n{file.description}\n\nThis is a placeholder file for demonstration purposes."
                save_file_to_drive(service, file.name, file_content, "text/plain", folder_id)
                file_count += 1
        
        # Recursively process child folders
        if folder.children:
            created_count += create_folders_recursively(service, folder_id, folder.children, file_count)
    
    return created_count

@router.post("/sync-vaultos-files")
def sync_vaultos_files(background_tasks: BackgroundTasks) -> DriveOperationResult:
    """Sync VaultOS files to Google Drive"""
    try:
        # Start the sync in the background
        background_tasks.add_task(sync_vaultos_files_task)
        
        return DriveOperationResult(
            success=True,
            message="Started syncing VaultOS files to Google Drive. This may take a few minutes."
        )
    except Exception as e:
        return DriveOperationResult(
            success=False,
            message=f"Failed to start file sync: {str(e)}"
        )

def sync_vaultos_files_task():
    """Background task to sync VaultOS files to Google Drive"""
    try:
        config = get_config()
        service = get_drive_service()
        
        # TODO: Implement actual file syncing based on VaultOS file storage
        # For now, we'll create a backup of system logs and configuration
        
        # Get the system folder
        system_folder_id = get_or_create_folder(service, config['system_folders_path'])
        vaultos_folder_id = get_or_create_folder(service, "VaultOS", system_folder_id)
        logs_folder_id = get_or_create_folder(service, "Logs", vaultos_folder_id)
        
        # Create a timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Create a backup of the backup logs if enabled
        files_synced = 0
        if config.get('backup_logs', True):
            backup_logs = db.storage.json.get(DRIVE_LAST_BACKUP_LOG_KEY, [])
            logs_content = json.dumps(backup_logs, indent=2)
            save_file_to_drive(
                service, 
                f"backup_logs_{timestamp}.json", 
                logs_content, 
                "application/json", 
                logs_folder_id
            )
            files_synced += 1
        
        # Create a backup of the Google Drive configuration
        config_content = json.dumps(config, indent=2)
        save_file_to_drive(
            service, 
            f"drive_config_{timestamp}.json", 
            config_content, 
            "application/json", 
            logs_folder_id
        )
        files_synced += 1
        
        # Update last sync time
        config['last_sync'] = datetime.datetime.now().isoformat()
        update_config(config)
        
        # Log the operation
        log_backup_operation({
            "operation": "sync_vaultos_files",
            "files_synced": files_synced,
            "status": "success"
        })
        
    except Exception as e:
        print(f"Error syncing VaultOS files: {str(e)}")
        log_backup_operation({
            "operation": "sync_vaultos_files",
            "status": "error",
            "error": str(e)
        })

@router.get("/google-drive-sync-status")
def get_google_drive_sync_status() -> SyncStatus:
    """Get the current Google Drive sync status"""
    config = get_config()
    
    last_sync = None
    if config.get('last_sync'):
        last_sync = config['last_sync']
    
    next_sync = None
    if last_sync:
        try:
            last_sync_dt = datetime.datetime.fromisoformat(last_sync)
            interval_minutes = config.get('sync_interval_minutes', 60)
            next_sync_dt = last_sync_dt + datetime.timedelta(minutes=interval_minutes)
            next_sync = next_sync_dt.isoformat()
        except Exception as e:
            print(f"Error calculating next sync: {str(e)}")
    
    # Get the last log entry
    logs = db.storage.json.get(DRIVE_LAST_BACKUP_LOG_KEY, [])
    folders_synced = 0
    files_synced = 0
    status = "Not started"
    
    if logs and isinstance(logs, list) and len(logs) > 0:
        last_log = logs[-1]
        folders_synced = last_log.get('folders_created', 0) + last_log.get('folders_synced', 0)
        files_synced = last_log.get('files_created', 0) + last_log.get('files_synced', 0)
        if last_log.get('status') == 'success':
            status = "Completed successfully"
        elif last_log.get('status') == 'error':
            status = f"Error: {last_log.get('error', 'Unknown error')}"
        else:
            status = "In progress"
    
    return SyncStatus(
        enabled=config.get('enabled', False),
        last_sync=last_sync,
        next_sync=next_sync,
        status=status,
        folders_synced=folders_synced,
        files_synced=files_synced
    )

@router.get("/backup-logs")
def get_backup_logs() -> List[Dict[str, Any]]:
    """Get the Google Drive backup logs"""
    logs = db.storage.json.get(DRIVE_LAST_BACKUP_LOG_KEY, [])
    return logs

@router.post("/schedule-backup")
def schedule_backup(background_tasks: BackgroundTasks) -> DriveOperationResult:
    """Schedule a backup to run at the configured interval"""
    try:
        config = get_config()
        
        # Make sure backups are enabled
        if not config.get('enabled', False):
            return DriveOperationResult(
                success=False,
                message="Backup is not enabled. Please enable it in the configuration."
            )
        
        # Start the scheduler task
        background_tasks.add_task(backup_scheduler_task)
        
        return DriveOperationResult(
            success=True,
            message="Scheduled backup task started. Backups will run at the configured interval."
        )
    except Exception as e:
        return DriveOperationResult(
            success=False,
            message=f"Failed to schedule backup: {str(e)}"
        )

def backup_scheduler_task():
    """Background task to run backups at the configured interval"""
    try:
        while True:
            # Get the latest config
            config = get_config()
            
            # Check if backups are enabled
            if not config.get('enabled', False):
                print("Backup scheduler: Backups are disabled, stopping scheduler.")
                break
            
            # Run the backup tasks
            print("Backup scheduler: Running backup tasks...")
            sync_vaultos_files_task()
            
            # Calculate the next run time
            interval_minutes = config.get('sync_interval_minutes', 60)
            print(f"Backup scheduler: Sleeping for {interval_minutes} minutes until next backup...")
            
            # Sleep until the next run
            time.sleep(interval_minutes * 60)
    except Exception as e:
        print(f"Error in backup scheduler: {str(e)}")
        log_backup_operation({
            "operation": "backup_scheduler",
            "status": "error",
            "error": str(e)
        })
