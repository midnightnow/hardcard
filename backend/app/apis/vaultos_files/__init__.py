"""VaultOS Files API

This API provides endpoints to manage files and folders in the VaultOS file system.
It enables CRUD operations for files and folders, search functionality, and file type handling.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
import databutton as db
import re
import json
import time
import uuid
from datetime import datetime

# Initialize router
router = APIRouter()

# Helper function to sanitize storage keys
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

# Storage constants
FILES_INDEX_KEY = sanitize_storage_key("vaultos_files_index")
FOLDERS_INDEX_KEY = sanitize_storage_key("vaultos_folders_index")
USER_FILES_PREFIX = "vaultos_file_"
USER_FOLDERS_PREFIX = "vaultos_folder_"

# Models
class FileMetadata(BaseModel):
    """Metadata for a file"""
    id: str
    name: str
    description: Optional[str] = ""
    folder_id: str
    type: str
    size: int = 0
    created: str
    modified: str
    owner: Optional[str] = None
    permissions: Optional[List[str]] = []
    tags: Optional[List[str]] = []

class FolderMetadata(BaseModel):
    """Metadata for a folder"""
    id: str
    name: str
    description: Optional[str] = ""
    parent_id: Optional[str] = None
    created: str
    modified: str
    owner: Optional[str] = None
    permissions: Optional[List[str]] = []

class CreateFileRequest(BaseModel):
    """Request data for file creation"""
    name: str
    description: Optional[str] = ""
    folder_id: str
    type: str
    content: str
    tags: Optional[List[str]] = []

class UpdateFileRequest(BaseModel):
    """Request data for file update"""
    name: Optional[str] = None
    description: Optional[str] = None
    folder_id: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

class CreateFolderRequest(BaseModel):
    """Request data for folder creation"""
    name: str
    description: Optional[str] = ""
    parent_id: Optional[str] = None

class UpdateFolderRequest(BaseModel):
    """Request data for folder update"""
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None

class FileListResponse(BaseModel):
    """Response data for file listing"""
    files: List[FileMetadata]
    total: int

class FolderListResponse(BaseModel):
    """Response data for folder listing"""
    folders: List[FolderMetadata]
    total: int

class SearchResponse(BaseModel):
    """Response data for search results"""
    files: List[FileMetadata]
    folders: List[FolderMetadata]
    total_files: int
    total_folders: int

class FileResponse(BaseModel):
    """Response data for file operations"""
    metadata: FileMetadata
    content: Optional[str] = None

class FolderResponse(BaseModel):
    """Response data for folder operations"""
    metadata: FolderMetadata
    children: Optional[Dict[str, List[Union[FileMetadata, FolderMetadata]]]] = None

class MoveItemsRequest(BaseModel):
    """Request data for moving items"""
    file_ids: Optional[List[str]] = []
    folder_ids: Optional[List[str]] = []
    destination_folder_id: str

class BatchDeleteRequest(BaseModel):
    """Request data for batch delete operations"""
    file_ids: Optional[List[str]] = []
    folder_ids: Optional[List[str]] = []

# Initialize storage if not exists
def init_storage():
    """Initialize storage for files and folders if not already set up"""
    try:
        db.storage.json.get(FILES_INDEX_KEY)
    except:
        db.storage.json.put(FILES_INDEX_KEY, {})
    
    try:
        db.storage.json.get(FOLDERS_INDEX_KEY)
    except:
        # Initialize with root folder
        root_folder = {
            "root": {
                "id": "root",
                "name": "Root",
                "description": "Root folder",
                "parent_id": None,
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "owner": "system",
                "permissions": ["read", "write"]
            }
        }
        
        # Create base folders structure
        base_folders = [
            {"id": "personal", "name": "Personal", "description": "Personal data and documents"},
            {"id": "family", "name": "Family", "description": "Family trust management"},
            {"id": "investments", "name": "Investments", "description": "Investment portfolios and assets"},
            {"id": "legacy", "name": "Legacy", "description": "Legacy planning and generational wealth"},
            {"id": "core", "name": "Core", "description": "Core system functionality"}
        ]
        
        # Add base folders to root
        for folder in base_folders:
            folder_id = folder["id"]
            folder_data = {
                "id": folder_id,
                "name": folder["name"],
                "description": folder["description"],
                "parent_id": "root",
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "owner": "system",
                "permissions": ["read", "write"]
            }
            root_folder[folder_id] = folder_data
            
        db.storage.json.put(FOLDERS_INDEX_KEY, root_folder)

# Initialize storage
init_storage()

# Helper functions
def get_file_content(file_id: str) -> str:
    """Get content of a file"""
    try:
        file_key = sanitize_storage_key(f"{USER_FILES_PREFIX}{file_id}_content")
        content = db.storage.text.get(file_key)
        return content
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"File content not found: {str(e)}") from e

def save_file_content(file_id: str, content: str):
    """Save content of a file"""
    try:
        file_key = sanitize_storage_key(f"{USER_FILES_PREFIX}{file_id}_content")
        db.storage.text.put(file_key, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file content: {str(e)}") from e

def get_files_index() -> Dict[str, FileMetadata]:
    """Get the files index"""
    try:
        return db.storage.json.get(FILES_INDEX_KEY)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get files index: {str(e)}") from e

def get_folders_index() -> Dict[str, FolderMetadata]:
    """Get the folders index"""
    try:
        return db.storage.json.get(FOLDERS_INDEX_KEY)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get folders index: {str(e)}") from e

def update_files_index(files_index: Dict[str, FileMetadata]):
    """Update the files index"""
    try:
        db.storage.json.put(FILES_INDEX_KEY, files_index)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update files index: {str(e)}") from e

def update_folders_index(folders_index: Dict[str, FolderMetadata]):
    """Update the folders index"""
    try:
        db.storage.json.put(FOLDERS_INDEX_KEY, folders_index)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update folders index: {str(e)}") from e

# API Endpoints

# File endpoints
@router.post("/files", response_model=FileResponse)
def create_file(request: CreateFileRequest) -> FileResponse:
    """Create a new file"""
    # Generate a new file ID
    file_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    # Create file metadata
    file_metadata = FileMetadata(
        id=file_id,
        name=request.name,
        description=request.description,
        folder_id=request.folder_id,
        type=request.type,
        size=len(request.content),
        created=timestamp,
        modified=timestamp,
        owner="user",  # In a real app, this would be the authenticated user
        permissions=["read", "write"],
        tags=request.tags
    )
    
    # Save file content
    save_file_content(file_id, request.content)
    
    # Update files index
    files_index = get_files_index()
    files_index[file_id] = file_metadata.dict()
    update_files_index(files_index)
    
    return FileResponse(metadata=file_metadata, content=request.content)

@router.get("/files/{file_id}", response_model=FileResponse)
def get_file(file_id: str, include_content: bool = True) -> FileResponse:
    """Get a file by ID"""
    files_index = get_files_index()
    
    if file_id not in files_index:
        raise HTTPException(status_code=404, detail="File not found")
    
    file_metadata = FileMetadata(**files_index[file_id])
    content = None
    
    if include_content:
        content = get_file_content(file_id)
    
    return FileResponse(metadata=file_metadata, content=content)

@router.put("/files/{file_id}", response_model=FileResponse)
def update_file(file_id: str, request: UpdateFileRequest) -> FileResponse:
    """Update a file"""
    files_index = get_files_index()
    
    if file_id not in files_index:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Get existing metadata
    file_metadata_dict = files_index[file_id]
    
    # Update fields
    if request.name is not None:
        file_metadata_dict["name"] = request.name
    
    if request.description is not None:
        file_metadata_dict["description"] = request.description
    
    if request.folder_id is not None:
        file_metadata_dict["folder_id"] = request.folder_id
    
    if request.tags is not None:
        file_metadata_dict["tags"] = request.tags
    
    # Update content if provided
    if request.content is not None:
        save_file_content(file_id, request.content)
        file_metadata_dict["size"] = len(request.content)
    
    # Update timestamp
    file_metadata_dict["modified"] = datetime.now().isoformat()
    
    # Update files index
    files_index[file_id] = file_metadata_dict
    update_files_index(files_index)
    
    file_metadata = FileMetadata(**file_metadata_dict)
    content = get_file_content(file_id) if request.content is not None else None
    
    return FileResponse(metadata=file_metadata, content=content)

@router.delete("/files/{file_id}")
def delete_file(file_id: str):
    """Delete a file"""
    files_index = get_files_index()
    
    if file_id not in files_index:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Delete file content
    try:
        file_key = sanitize_storage_key(f"{USER_FILES_PREFIX}{file_id}_content")
        # If we had a delete method in the db.storage, we would use it here
        # For now, we'll just update the files index
    except Exception:
        pass
    
    # Remove from files index
    del files_index[file_id]
    update_files_index(files_index)
    
    return {"success": True, "message": "File deleted successfully"}

@router.get("/files", response_model=FileListResponse)
def list_files(
    folder_id: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> FileListResponse:
    """List files with optional filtering"""
    files_index = get_files_index()
    
    # Filter files
    filtered_files = []
    for file_id, file_data in files_index.items():
        match = True
        
        if folder_id is not None and file_data["folder_id"] != folder_id:
            match = False
        
        if type is not None and file_data["type"] != type:
            match = False
        
        if match:
            filtered_files.append(FileMetadata(**file_data))
    
    # Sort by modified date (newest first)
    filtered_files.sort(key=lambda x: x.modified, reverse=True)
    
    # Apply pagination
    paginated_files = filtered_files[offset:offset + limit]
    
    return FileListResponse(files=paginated_files, total=len(filtered_files))

# Folder endpoints
@router.post("/folders", response_model=FolderResponse)
def create_folder(request: CreateFolderRequest) -> FolderResponse:
    """Create a new folder"""
    # Generate a new folder ID
    folder_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    # Check if parent folder exists
    if request.parent_id is not None:
        folders_index = get_folders_index()
        if request.parent_id not in folders_index:
            raise HTTPException(status_code=404, detail="Parent folder not found")
    
    # Create folder metadata
    folder_metadata = FolderMetadata(
        id=folder_id,
        name=request.name,
        description=request.description,
        parent_id=request.parent_id if request.parent_id else "root",
        created=timestamp,
        modified=timestamp,
        owner="user",  # In a real app, this would be the authenticated user
        permissions=["read", "write"]
    )
    
    # Update folders index
    folders_index = get_folders_index()
    folders_index[folder_id] = folder_metadata.dict()
    update_folders_index(folders_index)
    
    return FolderResponse(metadata=folder_metadata)

@router.get("/folders/{folder_id}", response_model=FolderResponse)
def get_folder(folder_id: str, include_children: bool = False) -> FolderResponse:
    """Get a folder by ID"""
    folders_index = get_folders_index()
    
    if folder_id not in folders_index and folder_id != "root":
        raise HTTPException(status_code=404, detail="Folder not found")
    
    folder_metadata = FolderMetadata(**folders_index[folder_id])
    children = None
    
    if include_children:
        # Get child folders
        child_folders = []
        for fid, folder in folders_index.items():
            if folder["parent_id"] == folder_id:
                child_folders.append(FolderMetadata(**folder))
        
        # Get child files
        files_index = get_files_index()
        child_files = []
        for fid, file in files_index.items():
            if file["folder_id"] == folder_id:
                child_files.append(FileMetadata(**file))
        
        children = {
            "folders": child_folders,
            "files": child_files
        }
    
    return FolderResponse(metadata=folder_metadata, children=children)

@router.put("/folders/{folder_id}", response_model=FolderResponse)
def update_folder(folder_id: str, request: UpdateFolderRequest) -> FolderResponse:
    """Update a folder"""
    folders_index = get_folders_index()
    
    if folder_id not in folders_index and folder_id != "root":
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Get existing metadata
    folder_metadata_dict = folders_index[folder_id]
    
    # Prevent moving a folder to its own subfolder
    if request.parent_id is not None:
        current_parent = request.parent_id
        while current_parent is not None:
            if current_parent == folder_id:
                raise HTTPException(status_code=400, detail="Cannot move a folder to its own subfolder")
            
            if current_parent not in folders_index:
                break
                
            current_parent = folders_index[current_parent]["parent_id"]
    
    # Update fields
    if request.name is not None:
        folder_metadata_dict["name"] = request.name
    
    if request.description is not None:
        folder_metadata_dict["description"] = request.description
    
    if request.parent_id is not None:
        folder_metadata_dict["parent_id"] = request.parent_id
    
    # Update timestamp
    folder_metadata_dict["modified"] = datetime.now().isoformat()
    
    # Update folders index
    folders_index[folder_id] = folder_metadata_dict
    update_folders_index(folders_index)
    
    folder_metadata = FolderMetadata(**folder_metadata_dict)
    
    return FolderResponse(metadata=folder_metadata)

@router.delete("/folders/{folder_id}")
def delete_folder(folder_id: str, recursive: bool = False):
    """Delete a folder"""
    if folder_id == "root":
        raise HTTPException(status_code=400, detail="Cannot delete the root folder")
    
    folders_index = get_folders_index()
    
    if folder_id not in folders_index:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Check if folder has children
    has_subfolders = any(folder["parent_id"] == folder_id for folder in folders_index.values())
    
    files_index = get_files_index()
    has_files = any(file["folder_id"] == folder_id for file in files_index.values())
    
    if (has_subfolders or has_files) and not recursive:
        raise HTTPException(status_code=400, detail="Folder is not empty. Use recursive=true to delete it and its contents")
    
    if recursive:
        # Delete all subfolders recursively
        def delete_subfolder_recursive(parent_id):
            subfolder_ids = [fid for fid, folder in folders_index.items() if folder["parent_id"] == parent_id]
            
            for subfolder_id in subfolder_ids:
                delete_subfolder_recursive(subfolder_id)
                del folders_index[subfolder_id]
            
            # Delete all files in this folder
            file_ids_to_delete = [fid for fid, file in files_index.items() if file["folder_id"] == parent_id]
            for file_id in file_ids_to_delete:
                del files_index[file_id]
        
        delete_subfolder_recursive(folder_id)
    
    # Remove from folders index
    del folders_index[folder_id]
    
    # Update indexes
    update_folders_index(folders_index)
    update_files_index(files_index)
    
    return {"success": True, "message": "Folder deleted successfully"}

@router.get("/folders", response_model=FolderListResponse)
def list_folders(
    parent_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> FolderListResponse:
    """List folders with optional parent filtering"""
    folders_index = get_folders_index()
    
    # Filter folders
    filtered_folders = []
    for folder_id, folder_data in folders_index.items():
        if parent_id is None or folder_data["parent_id"] == parent_id:
            filtered_folders.append(FolderMetadata(**folder_data))
    
    # Sort by name
    filtered_folders.sort(key=lambda x: x.name)
    
    # Apply pagination
    paginated_folders = filtered_folders[offset:offset + limit]
    
    return FolderListResponse(folders=paginated_folders, total=len(filtered_folders))

# Advanced operations
@router.post("/search", response_model=SearchResponse)
def search(
    query: str,
    folder_id: Optional[str] = None,
    file_types: Optional[List[str]] = None,
    limit: int = 100
) -> SearchResponse:
    """Search for files and folders"""
    query = query.lower()
    
    # Search in files
    files_index = get_files_index()
    matched_files = []
    
    for file_id, file_data in files_index.items():
        if folder_id is not None and file_data["folder_id"] != folder_id:
            continue
            
        if file_types is not None and file_data["type"] not in file_types:
            continue
        
        # Search in name, description, and tags
        if (
            query in file_data["name"].lower() or 
            query in file_data["description"].lower() or
            any(query in tag.lower() for tag in file_data.get("tags", []))
        ):
            matched_files.append(FileMetadata(**file_data))
    
    # Search in folders
    folders_index = get_folders_index()
    matched_folders = []
    
    for folder_id, folder_data in folders_index.items():
        if folder_id == "root":
            continue
            
        # Filter by parent if specified
        if folder_id is not None and folder_data["parent_id"] != folder_id:
            continue
        
        # Search in name and description
        if (
            query in folder_data["name"].lower() or 
            query in folder_data["description"].lower()
        ):
            matched_folders.append(FolderMetadata(**folder_data))
    
    # Sort and limit results
    matched_files.sort(key=lambda x: x.modified, reverse=True)
    matched_folders.sort(key=lambda x: x.name)
    
    matched_files = matched_files[:limit]
    matched_folders = matched_folders[:limit]
    
    return SearchResponse(
        files=matched_files,
        folders=matched_folders,
        total_files=len(matched_files),
        total_folders=len(matched_folders)
    )

@router.post("/move")
def move_items(request: MoveItemsRequest):
    """Move files and folders to a destination folder"""
    folders_index = get_folders_index()
    files_index = get_files_index()
    
    # Check if destination folder exists
    if request.destination_folder_id not in folders_index and request.destination_folder_id != "root":
        raise HTTPException(status_code=404, detail="Destination folder not found")
    
    # Move files
    for file_id in request.file_ids:
        if file_id in files_index:
            files_index[file_id]["folder_id"] = request.destination_folder_id
            files_index[file_id]["modified"] = datetime.now().isoformat()
    
    # Move folders
    for folder_id in request.folder_ids:
        # Can't move root folder
        if folder_id == "root":
            continue
            
        if folder_id in folders_index:
            # Prevent moving a folder to its own subfolder
            current_parent = request.destination_folder_id
            invalid_move = False
            
            while current_parent is not None:
                if current_parent == folder_id:
                    invalid_move = True
                    break
                
                if current_parent not in folders_index:
                    break
                    
                current_parent = folders_index[current_parent]["parent_id"]
            
            if not invalid_move:
                folders_index[folder_id]["parent_id"] = request.destination_folder_id
                folders_index[folder_id]["modified"] = datetime.now().isoformat()
    
    # Update indexes
    update_files_index(files_index)
    update_folders_index(folders_index)
    
    return {"success": True, "message": "Items moved successfully"}

@router.post("/batch-delete")
def batch_delete(request: BatchDeleteRequest):
    """Delete multiple files and folders in one operation"""
    files_index = get_files_index()
    folders_index = get_folders_index()
    
    # Delete files
    for file_id in request.file_ids:
        if file_id in files_index:
            del files_index[file_id]
    
    # Delete folders (non-recursively for safety)
    for folder_id in request.folder_ids:
        # Can't delete root folder
        if folder_id == "root":
            continue
            
        if folder_id in folders_index:
            # Check if folder is empty
            has_subfolders = any(folder["parent_id"] == folder_id for folder in folders_index.values())
            has_files = any(file["folder_id"] == folder_id for file in files_index.values())
            
            if not has_subfolders and not has_files:
                del folders_index[folder_id]
    
    # Update indexes
    update_files_index(files_index)
    update_folders_index(folders_index)
    
    return {"success": True, "message": "Batch delete completed"}

@router.get("/tree")
def get_folder_tree(root_id: str = "root", depth: int = 2):
    """Get a hierarchical tree view of folders starting from the specified root"""
    folders_index = get_folders_index()
    
    if root_id not in folders_index and root_id != "root":
        raise HTTPException(status_code=404, detail="Root folder not found")
    
    def build_tree(folder_id, current_depth):
        if current_depth > depth:
            return None
            
        folder = folders_index.get(folder_id)
        if not folder:
            return None
            
        result = {
            "id": folder_id,
            "name": folder["name"],
            "description": folder["description"],
            "type": "folder"
        }
        
        # Add children if not at max depth
        if current_depth < depth:
            # Get subfolders
            children = []
            for fid, f in folders_index.items():
                if f["parent_id"] == folder_id:
                    child_tree = build_tree(fid, current_depth + 1)
                    if child_tree:
                        children.append(child_tree)
            
            # Get files at this level
            files_index = get_files_index()
            for fid, f in files_index.items():
                if f["folder_id"] == folder_id:
                    children.append({
                        "id": fid,
                        "name": f["name"],
                        "description": f["description"],
                        "type": "file",
                        "file_type": f["type"]
                    })
            
            # Sort children by name
            children.sort(key=lambda x: x["name"])
            result["children"] = children
        
        return result
    
    tree = build_tree(root_id, 1)
    return tree
