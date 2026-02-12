from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import databutton as db
from pydantic import BaseModel
from datetime import datetime
import re
import json

router = APIRouter()


def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols"""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)


class StoryMedia(BaseModel):
    """Model for story media metadata"""
    media_id: str
    media_type: str  # 'image', 'video', 'audio', 'document'
    filename: str
    upload_date: str
    description: Optional[str] = None


class FamilyStory(BaseModel):
    """Model for a family story"""
    story_id: str
    vault_id: str
    title: str
    content: str
    author: str
    created_at: str
    media: List[StoryMedia] = []
    tags: List[str] = []


class FamilyStoryCreate(BaseModel):
    """Model for creating a family story"""
    vault_id: str
    title: str
    content: str
    author: str
    tags: List[str] = []


class FamilyStoryUpdate(BaseModel):
    """Model for updating a family story"""
    title: Optional[str] = None
    content: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None


class FamilyStoriesResponse(BaseModel):
    """Response model for listing family stories"""
    stories: List[FamilyStory]


class MediaUploadResponse(BaseModel):
    """Response model for media uploads"""
    media_id: str
    media_type: str
    filename: str
    upload_date: str
    description: Optional[str] = None
    url: str


@router.get("/stories/{vault_id}", response_model=FamilyStoriesResponse)
def get_family_stories(vault_id: str):
    """Retrieve all family stories for a vault"""
    try:
        # Get the stories list for this vault
        storage_key = sanitize_storage_key(f"family_stories_{vault_id}")
        stories_data = db.storage.json.get(storage_key, default=[])
        return FamilyStoriesResponse(stories=stories_data)
    except Exception as e:
        print(f"Error retrieving family stories: {e}")
        return FamilyStoriesResponse(stories=[])


@router.get("/story/{story_id}", response_model=FamilyStory)
def get_family_story(story_id: str):
    """Retrieve a specific family story"""
    try:
        # Get the story data
        storage_key = sanitize_storage_key(f"family_story_{story_id}")
        story_data = db.storage.json.get(storage_key)
        return story_data
    except Exception as e:
        print(f"Error retrieving family story: {e}")
        raise HTTPException(status_code=404, detail="Story not found")


@router.post("/stories", response_model=FamilyStory)
def create_family_story(story: FamilyStoryCreate):
    """Create a new family story"""
    try:
        # Generate a unique ID for the story
        import uuid
        story_id = str(uuid.uuid4())
        
        # Create the story object
        new_story = FamilyStory(
            story_id=story_id,
            vault_id=story.vault_id,
            title=story.title,
            content=story.content,
            author=story.author,
            created_at=datetime.now().isoformat(),
            tags=story.tags,
            media=[]
        )
        
        # Save the individual story
        story_key = sanitize_storage_key(f"family_story_{story_id}")
        db.storage.json.put(story_key, new_story.dict())
        
        # Update the list of stories for this vault
        vault_stories_key = sanitize_storage_key(f"family_stories_{story.vault_id}")
        vault_stories = db.storage.json.get(vault_stories_key, default=[])
        vault_stories.append(new_story.dict())
        db.storage.json.put(vault_stories_key, vault_stories)
        
        # Update legacy score
        try:
            # Get current legacy score to recalculate with new content
            from app.apis.legacy_score import recalculate_legacy_score
            recalculate_legacy_score(story.vault_id)
        except Exception as score_error:
            print(f"Error updating legacy score: {score_error}")
        
        return new_story
    except Exception as e:
        print(f"Error creating family story: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/story/{story_id}", response_model=FamilyStory)
def update_family_story(story_id: str, update_data: FamilyStoryUpdate):
    """Update a family story"""
    try:
        # Get the current story
        storage_key = sanitize_storage_key(f"family_story_{story_id}")
        story_data = db.storage.json.get(storage_key)
        
        # Update the fields
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        story_data.update(update_dict)
        
        # Save the updated story
        db.storage.json.put(storage_key, story_data)
        
        # Update the story in the vault's story list
        vault_id = story_data.get("vault_id")
        if vault_id:
            vault_stories_key = sanitize_storage_key(f"family_stories_{vault_id}")
            vault_stories = db.storage.json.get(vault_stories_key, default=[])
            
            for i, story in enumerate(vault_stories):
                if story.get("story_id") == story_id:
                    vault_stories[i].update(update_dict)
                    break
            
            db.storage.json.put(vault_stories_key, vault_stories)
        
        return story_data
    except Exception as e:
        print(f"Error updating family story: {e}")
        raise HTTPException(status_code=404, detail="Story not found")


@router.delete("/story/{story_id}")
def delete_family_story(story_id: str):
    """Delete a family story"""
    try:
        # Get the story to find its vault_id
        story_key = sanitize_storage_key(f"family_story_{story_id}")
        story_data = db.storage.json.get(story_key)
        vault_id = story_data.get("vault_id")
        
        # Delete the individual story
        db.storage.json.delete(story_key)
        
        # Update the vault's story list
        if vault_id:
            vault_stories_key = sanitize_storage_key(f"family_stories_{vault_id}")
            vault_stories = db.storage.json.get(vault_stories_key, default=[])
            vault_stories = [s for s in vault_stories if s.get("story_id") != story_id]
            db.storage.json.put(vault_stories_key, vault_stories)
            
            # Update legacy score after deletion
            try:
                from app.apis.legacy_score import recalculate_legacy_score
                recalculate_legacy_score(vault_id)
            except Exception as score_error:
                print(f"Error updating legacy score: {score_error}")
        
        return {"success": True, "message": "Story deleted successfully"}
    except Exception as e:
        print(f"Error deleting family story: {e}")
        raise HTTPException(status_code=404, detail="Story not found")


@router.post("/media/upload", response_model=MediaUploadResponse)
def upload_story_media(
    story_id: str = Form(...),
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    media_type: Optional[str] = Form(None)  # 'image', 'video', 'audio', 'document'
):
    """Upload media for a family story"""
    try:
        # Generate a unique ID for the media
        import uuid
        media_id = str(uuid.uuid4())
        
        # Create filename with sanitization
        filename = sanitize_storage_key(file.filename)
        storage_key = f"family_story_media_{media_id}"
        
        # Auto-detect media type if not provided
        if not media_type:
            content_type = file.content_type.lower()
            if content_type.startswith('image/'):
                media_type = 'image'
            elif content_type.startswith('video/'):
                media_type = 'video'
            elif content_type.startswith('audio/'):
                media_type = 'audio'
            elif content_type in ['application/pdf', 'text/plain', 'application/msword', 
                              'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                media_type = 'document'
            else:
                media_type = 'document'  # Default to document for unknown types
        
        # Read file content
        content = file.file.read()
        
        # Store the file based on type
        if media_type in ['image', 'video', 'audio']:
            db.storage.binary.put(storage_key, content)
        elif media_type == 'document':
            if file.content_type == 'application/pdf':
                db.storage.binary.put(storage_key, content)
            else:
                # For text documents
                try:
                    text_content = content.decode('utf-8')
                    db.storage.text.put(storage_key, text_content)
                except UnicodeDecodeError:
                    # If it can't be decoded as text, store as binary
                    db.storage.binary.put(storage_key, content)
        
        # Create media metadata
        media_data = StoryMedia(
            media_id=media_id,
            media_type=media_type,
            filename=filename,
            upload_date=datetime.now().isoformat(),
            description=description
        )
        
        # Add media to the story
        story_key = sanitize_storage_key(f"family_story_{story_id}")
        story_data = db.storage.json.get(story_key)
        
        if "media" not in story_data:
            story_data["media"] = []
        
        story_data["media"].append(media_data.dict())
        db.storage.json.put(story_key, story_data)
        
        # Update the story in the vault's story list
        vault_id = story_data.get("vault_id")
        if vault_id:
            vault_stories_key = sanitize_storage_key(f"family_stories_{vault_id}")
            vault_stories = db.storage.json.get(vault_stories_key, default=[])
            
            for i, story in enumerate(vault_stories):
                if story.get("story_id") == story_id:
                    if "media" not in vault_stories[i]:
                        vault_stories[i]["media"] = []
                    vault_stories[i]["media"].append(media_data.dict())
                    break
            
            db.storage.json.put(vault_stories_key, vault_stories)
        
        # Generate URL for frontend access
        # For static assets, we need to create the proper URL format
        from app.env import Mode, mode
        
        # For images that can be displayed directly, we'll use static assets
        if media_type == 'image':
            import base64
            from app.env import project_id
            
            # Create a static asset for images so they can be displayed in the frontend
            asset_id = f"family_story_image_{media_id}"
            asset_metadata = {"content_type": file.content_type}
            db.storage.static_assets.put(asset_id, content, metadata=asset_metadata)
            url = f"https://static.databutton.com/public/{project_id}/{asset_id}"
        else:
            # For other types, we'll use our API endpoint
            url = f"/api/family-stories/media/{media_id}?type={media_type}"
        
        # Update legacy score with new media content
        try:
            from app.apis.legacy_score import recalculate_legacy_score
            recalculate_legacy_score(vault_id)
        except Exception as score_error:
            print(f"Error updating legacy score: {score_error}")
        
        return MediaUploadResponse(
            media_id=media_id,
            media_type=media_type,
            filename=filename,
            upload_date=media_data.upload_date,
            description=description,
            url=url
        )
    except Exception as e:
        print(f"Error uploading media: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/media/{media_id}")
def get_story_media(media_id: str, type: str):
    """Retrieve media for a family story"""
    try:
        storage_key = f"family_story_media_{media_id}"
        
        # Return the appropriate content based on type
        if type in ['image', 'video', 'audio', 'document']:
            try:
                # Try binary first
                content = db.storage.binary.get(storage_key)
                return content
            except:
                # If not in binary storage, try text storage
                try:
                    content = db.storage.text.get(storage_key)
                    return content
                except:
                    raise HTTPException(status_code=404, detail="Media not found")
        else:
            raise HTTPException(status_code=400, detail="Invalid media type")
    except Exception as e:
        print(f"Error retrieving media: {e}")
        raise HTTPException(status_code=404, detail="Media not found")
