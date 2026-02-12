import uuid
import re
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
import databutton as db

router = APIRouter()

class FileUploadResponse(BaseModel):
    reference_id: str
    file_name: str
    content_type: str
    size: int

def sanitize_filename_for_key(filename: str) -> str:
    """Sanitize filename to be part of a storage key.
    Removes special characters, replaces spaces with underscores,
    and limits length.
    """
    # Remove non-alphanumeric characters (except dots and underscores)
    s = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    # Replace multiple dots/underscores with single one
    s = re.sub(r'[._-]+', '_', s)
    # Limit length
    return s[:50] # Keep it reasonably short for a key component

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile):
    """
    Uploads a file to db.storage.binary and returns a reference ID (storage key).
    The storage key is a combination of a UUID and a sanitized version of the original filename.
    """
    try:
        contents = await file.read()
        original_filename = file.filename if file.filename else "unknown_file"
        sanitized_part = sanitize_filename_for_key(original_filename)
        
        # Generate a unique key for storage
        unique_id = uuid.uuid4()
        storage_key = f"event_tag_ref__{unique_id}__{sanitized_part}"
        
        db.storage.binary.put(storage_key, contents)
        
        print(f"File '{original_filename}' uploaded with key: {storage_key}")
        
        return FileUploadResponse(
            reference_id=storage_key, 
            file_name=original_filename,
            content_type=file.content_type if file.content_type else "application/octet-stream",
            size=len(contents)
        )
    except Exception as e:
        print(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"Could not upload file: {str(e)}") from e

# To consider for future:
# - Mime type validation/restriction if needed
# - File size limits
# - More robust error handling around db.storage operations
