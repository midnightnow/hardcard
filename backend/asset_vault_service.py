"""
Asset Vault Service for HardCard Members Area
Handles secure storage and retrieval of business documents
"""

import os
import json
import hashlib
import datetime
from typing import List, Dict, Optional
from pathlib import Path
import shutil
from cryptography.fernet import Fernet
from fastapi import HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import aiofiles

class AssetVaultService:
    """Secure document storage service with encryption"""
    
    def __init__(self, vault_path: str = "./vault"):
        self.vault_path = Path(vault_path)
        self.metadata_path = self.vault_path / "metadata"
        self.files_path = self.vault_path / "files"
        
        # Create directories if they don't exist
        self.vault_path.mkdir(exist_ok=True)
        self.metadata_path.mkdir(exist_ok=True)
        self.files_path.mkdir(exist_ok=True)
        
        # Initialize encryption
        self.encryption_key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Asset categories
        self.categories = {
            "financial": {
                "name": "Financial Documents",
                "icon": "file-invoice-dollar",
                "color": "green"
            },
            "business": {
                "name": "Business Documents",
                "icon": "briefcase",
                "color": "blue"
            },
            "legal": {
                "name": "Legal & Contracts",
                "icon": "gavel",
                "color": "purple"
            },
            "strategic": {
                "name": "Strategic Plans",
                "icon": "chess",
                "color": "yellow"
            }
        }
    
    def _get_or_create_key(self) -> bytes:
        """Get or create encryption key"""
        key_file = self.vault_path / ".key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def _generate_file_id(self, filename: str) -> str:
        """Generate unique file ID"""
        timestamp = datetime.datetime.now().isoformat()
        return hashlib.sha256(f"{filename}{timestamp}".encode()).hexdigest()[:16]
    
    async def upload_file(
        self,
        file: UploadFile,
        category: str,
        user_id: str,
        description: Optional[str] = None
    ) -> Dict:
        """Upload and encrypt a file"""
        
        if category not in self.categories:
            raise HTTPException(status_code=400, detail="Invalid category")
        
        # Generate file ID and paths
        file_id = self._generate_file_id(file.filename)
        encrypted_filename = f"{file_id}.enc"
        file_path = self.files_path / encrypted_filename
        
        # Read and encrypt file content
        content = await file.read()
        encrypted_content = self.cipher_suite.encrypt(content)
        
        # Save encrypted file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(encrypted_content)
        
        # Create metadata
        metadata = {
            "id": file_id,
            "original_name": file.filename,
            "category": category,
            "size": len(content),
            "mime_type": file.content_type,
            "user_id": user_id,
            "description": description,
            "uploaded_at": datetime.datetime.now().isoformat(),
            "last_accessed": None,
            "access_count": 0,
            "shared_with": []
        }
        
        # Save metadata
        metadata_file = self.metadata_path / f"{file_id}.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "id": file_id,
            "filename": file.filename,
            "category": category,
            "size": len(content),
            "uploaded_at": metadata["uploaded_at"]
        }
    
    async def download_file(self, file_id: str, user_id: str) -> FileResponse:
        """Download and decrypt a file"""
        
        # Load metadata
        metadata_file = self.metadata_path / f"{file_id}.json"
        if not metadata_file.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Check access
        if metadata["user_id"] != user_id and user_id not in metadata["shared_with"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Load and decrypt file
        encrypted_file = self.files_path / f"{file_id}.enc"
        with open(encrypted_file, 'rb') as f:
            encrypted_content = f.read()
        
        decrypted_content = self.cipher_suite.decrypt(encrypted_content)
        
        # Update access metadata
        metadata["last_accessed"] = datetime.datetime.now().isoformat()
        metadata["access_count"] += 1
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Create temporary file for download
        temp_file = self.vault_path / "temp" / metadata["original_name"]
        temp_file.parent.mkdir(exist_ok=True)
        
        with open(temp_file, 'wb') as f:
            f.write(decrypted_content)
        
        return FileResponse(
            path=temp_file,
            filename=metadata["original_name"],
            media_type=metadata["mime_type"]
        )
    
    def list_files(self, user_id: str, category: Optional[str] = None) -> List[Dict]:
        """List user's files"""
        files = []
        
        for metadata_file in self.metadata_path.glob("*.json"):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Check access
            if metadata["user_id"] == user_id or user_id in metadata["shared_with"]:
                if category is None or metadata["category"] == category:
                    files.append({
                        "id": metadata["id"],
                        "filename": metadata["original_name"],
                        "category": metadata["category"],
                        "size": metadata["size"],
                        "uploaded_at": metadata["uploaded_at"],
                        "last_accessed": metadata["last_accessed"],
                        "description": metadata["description"]
                    })
        
        # Sort by upload date (newest first)
        files.sort(key=lambda x: x["uploaded_at"], reverse=True)
        
        return files
    
    def get_category_stats(self, user_id: str) -> Dict[str, Dict]:
        """Get file count and size by category"""
        stats = {cat: {"count": 0, "size": 0} for cat in self.categories}
        
        for metadata_file in self.metadata_path.glob("*.json"):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            if metadata["user_id"] == user_id:
                cat = metadata["category"]
                stats[cat]["count"] += 1
                stats[cat]["size"] += metadata["size"]
        
        return stats
    
    def delete_file(self, file_id: str, user_id: str) -> bool:
        """Delete a file"""
        
        # Check metadata
        metadata_file = self.metadata_path / f"{file_id}.json"
        if not metadata_file.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Check ownership
        if metadata["user_id"] != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete files
        encrypted_file = self.files_path / f"{file_id}.enc"
        if encrypted_file.exists():
            encrypted_file.unlink()
        metadata_file.unlink()
        
        return True
    
    def share_file(self, file_id: str, owner_id: str, share_with: str) -> bool:
        """Share file with another user"""
        
        metadata_file = self.metadata_path / f"{file_id}.json"
        if not metadata_file.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        # Check ownership
        if metadata["user_id"] != owner_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Add to shared list
        if share_with not in metadata["shared_with"]:
            metadata["shared_with"].append(share_with)
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return True
    
    def search_files(self, user_id: str, query: str) -> List[Dict]:
        """Search files by name or description"""
        results = []
        query_lower = query.lower()
        
        for metadata_file in self.metadata_path.glob("*.json"):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            # Check access
            if metadata["user_id"] == user_id or user_id in metadata["shared_with"]:
                # Search in filename and description
                if (query_lower in metadata["original_name"].lower() or 
                    (metadata["description"] and query_lower in metadata["description"].lower())):
                    
                    results.append({
                        "id": metadata["id"],
                        "filename": metadata["original_name"],
                        "category": metadata["category"],
                        "size": metadata["size"],
                        "uploaded_at": metadata["uploaded_at"],
                        "description": metadata["description"]
                    })
        
        return results
    
    def get_storage_usage(self, user_id: str) -> Dict:
        """Get user's storage usage statistics"""
        total_size = 0
        file_count = 0
        
        for metadata_file in self.metadata_path.glob("*.json"):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            
            if metadata["user_id"] == user_id:
                total_size += metadata["size"]
                file_count += 1
        
        # Convert to MB
        total_size_mb = total_size / (1024 * 1024)
        
        return {
            "total_files": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size_mb, 2),
            "storage_limit_mb": 5000,  # 5GB limit
            "usage_percentage": round((total_size_mb / 5000) * 100, 2)
        }


# FastAPI router integration
from fastapi import APIRouter, Depends, UploadFile, File
from typing import Optional

router = APIRouter(prefix="/api/vault", tags=["Asset Vault"])
vault_service = AssetVaultService()

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    category: str = "business",
    description: Optional[str] = None,
    user_id: str = "admin"  # TODO: Get from auth
):
    """Upload a file to the vault"""
    return await vault_service.upload_file(file, category, user_id, description)

@router.get("/files")
async def list_files(
    category: Optional[str] = None,
    user_id: str = "admin"  # TODO: Get from auth
):
    """List user's files"""
    return vault_service.list_files(user_id, category)

@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    user_id: str = "admin"  # TODO: Get from auth
):
    """Download a file"""
    return await vault_service.download_file(file_id, user_id)

@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    user_id: str = "admin"  # TODO: Get from auth
):
    """Delete a file"""
    success = vault_service.delete_file(file_id, user_id)
    return {"success": success}

@router.get("/stats")
async def get_stats(
    user_id: str = "admin"  # TODO: Get from auth
):
    """Get storage statistics"""
    return {
        "categories": vault_service.get_category_stats(user_id),
        "storage": vault_service.get_storage_usage(user_id)
    }

@router.get("/search")
async def search_files(
    query: str,
    user_id: str = "admin"  # TODO: Get from auth
):
    """Search files"""
    return vault_service.search_files(user_id, query)