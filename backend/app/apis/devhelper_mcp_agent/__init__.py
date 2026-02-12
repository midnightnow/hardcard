
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import databutton as db
import yaml
import asyncio
import os
import tempfile # Added for temp file creation
import re # Added for sanitize_storage_key

# MCP Agent specific imports
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM # Keep for other potential agent functions
# from mcp_agent.schemas import Message, FunctionCall # Commented out due to ModuleNotFoundError
import firebase_admin
from firebase_admin import credentials as admin_credentials, firestore # Added firestore import
import json
from typing import List, Optional
from app.libs.firebase_admin_service import get_firestore_client # For Firestore access
from app.libs.memory_service import MemoryFrame, MemoryService, MemoryType
from app.apis.vector_utils import cosine_similarity
from datetime import datetime
import numpy as np # For cosine similarity if direct array ops were needed, though encapsulated now

router = APIRouter(prefix="/api/v1/devhelper-mcp", tags=["DevHelper MCP Agent"])

# Helper function for sanitizing storage keys
def sanitize_storage_key(key: str) -> str:
    """Sanitize storage key to only allow alphanumeric and ._- symbols."""
    return re.sub(r'[^a-zA-Z0-9._-]', '', key)

class ContextualSuggestionRequest(BaseModel):
    query: str
    max_visual_memories: int = 3
    max_textual_memories: int = 3

class ContextualSuggestionResponse(BaseModel):
    suggestion: str
    retrieved_visual_context_count: int
    retrieved_textual_context_count: int
    error: Optional[str] = None

# --- Pydantic Models ---
class SummarizeDocumentRequest(BaseModel):
    url: str

class SummarizeDocumentResponse(BaseModel):
    summary: str
    
class InitializeAgentResponse(BaseModel):
    message: str
    agent_name: str | None = None
    llm_attached: bool = False

# --- Agent Configuration and Setup ---
AGENT_CONFIG_KEY = "mcp-agent.config.yaml"
_finder_agent: Agent | None = None
_llm_workflow: OpenAIAugmentedLLM | None = None
_app_instance: MCPApp | None = None

# async def get_mcp_config_and_write_to_temp_file(use_simplified_config_for_diag: bool = True) -> str:
#     """Fetches MCP config and secrets, writes them to temp files, and returns the config file path."""
#     try:
#         config_str_original = db.storage.text.get(AGENT_CONFIG_KEY)
#         if not config_str_original:
#             raise FileNotFoundError(f"MCP agent configuration not found in db.storage.text with key '{AGENT_CONFIG_KEY}'")
        
#         config_to_write = config_str_original
#         if use_simplified_config_for_diag:
#             print("[DIAGNOSTIC] Using simplified MCP config with only 'fetch' server.")
#             config_data = yaml.safe_load(config_str_original)
#             if 'mcp' in config_data and 'servers' in config_data['mcp']:
#                 original_servers = config_data['mcp']['servers']
#                 # Preserve other top-level keys
#                 simplified_config_data = {
#                     key: value for key, value in config_data.items() if key not in ['mcp']
#                 }
#                 # Simplify only the servers part under 'mcp'
#                 simplified_config_data['mcp'] = {
#                     'servers': {
#                         'fetch': original_servers.get('fetch')
#                     }
#                 }
                
#                 if not simplified_config_data['mcp']['servers']['fetch']:
#                     print("[DIAGNOSTIC] Error: 'fetch' server definition not found in original config to simplify.")
#                     # Fallback to original if something is wrong with this simplification logic
#                     config_to_write = config_str_original
#                 else:
#                     config_to_write = yaml.dump(simplified_config_data)
#                 print(f"--- [DIAGNOSTIC] Final config_to_write (simplified path) ---\n{config_to_write}\n-------------------------------------------------")
#             else:
#                 print("[DIAGNOSTIC] Could not parse original config to simplify, using original.")
#                 config_to_write = config_str_original
#             print(f"[DIAGNOSTIC] Simplified config to write:\n{config_to_write}")
        
#         openai_api_key = db.secrets.get("OPENAI_API_KEY")
#         if not openai_api_key:
#             raise ValueError("OPENAI_API_KEY secret not found.")

#         temp_dir = tempfile.gettempdir()
        
#         # Write mcp-agent.config.yaml
#         temp_config_file_path = os.path.join(temp_dir, "mcp-agent.config.yaml")
#         with open(temp_config_file_path, "w") as f:
#             f.write(config_to_write)
#         print(f"MCP agent configuration written to temporary file: {temp_config_file_path}")

#         # Write mcp_agent.secrets.yaml
#         # Ensure the secrets file is in the same directory as the config for auto-discovery by mcp-agent
#         secrets_content = {
#             "OPENAI_API_KEY": openai_api_key
#         }
#         temp_secrets_file_path = os.path.join(temp_dir, "mcp_agent.secrets.yaml")
#         with open(temp_secrets_file_path, "w") as f:
#             yaml.dump(secrets_content, f)
#         print(f"MCP agent secrets written to temporary file: {temp_secrets_file_path}")
        
#         return temp_config_file_path # The MCP_AGENT_CONFIG_PATH should point to the config file
#     except FileNotFoundError as e:
#         print(f"Error: {e}")
#         raise HTTPException(status_code=500, detail=str(e)) from e
#     except ValueError as e:
#         print(f"Error: {e}")
#         raise HTTPException(status_code=500, detail=str(e)) from e
#     except Exception as e:
#         print(f"Unexpected error getting MCP config/secrets or writing to temp files: {e}")
#         raise HTTPException(status_code=500, detail=f"Unexpected error with MCP setup: {e}") from e

# async def setup_agent_instance():
#     """
#     Initializes the MCPApp, the finder_agent, and attaches the LLM.
#     Agent initialization and LLM attachment are performed within an app.run() context.
#     """
#     # global _finder_agent, _llm_workflow, _app_instance

#     # if _finder_agent and _llm_workflow and _app_instance: # Check if already set up
#     #      print("Agent and LLM seem to be already initialized.")
#     #      return _finder_agent, _llm_workflow, _app_instance

#     # Always re-initialize for now to debug OpenAISettings issue with generate_str
#     print("[setup_agent_instance] Forcing re-initialization of agent, LLM, and app instance.")
#     # Temporarily set global variables to None to ensure re-initialization
#     # These globals might be problematic if not handled carefully across concurrent requests in a real scenario
#     # but for single-threaded diagnostic testing, this ensures they are reset.
#     global _finder_agent, _llm_workflow, _app_instance
#     _finder_agent = None
#     _llm_workflow = None
#     _app_instance = None

#     try:
#         temp_config_file_path = await get_mcp_config_and_write_to_temp_file(use_simplified_config_for_diag=False)
#         os.environ['MCP_AGENT_CONFIG_PATH'] = temp_config_file_path
#         print(f"Set MCP_AGENT_CONFIG_PATH to: {temp_config_file_path}")
        
#         app_to_setup_with = MCPApp(name="DevHelperMCP", config_file_path=temp_config_file_path)
#         print(f"MCPApp initialized with explicit config_file_path: {temp_config_file_path}")

#         async with app_to_setup_with.run() as engine_interface:
#             print(f"MCPApp context entered for agent setup. Engine: {engine_interface}")
            
#             # Since setup_agent_instance currently calls get_mcp_config_and_write_to_temp_file with use_simplified_config_for_diag=False,
#             # we are in "full config mode".
#             agent_server_names = ["fetch", "filesystem"]
#             print(f"[DIAGNOSTIC] Agent will be configured with server_names: {agent_server_names} (full config mode)")

#             finder_agent_being_setup = Agent(
#                 name="finder",
#                 instruction="You can read local files or fetch URLs. Return the requested information when asked.",
#                 server_names=agent_server_names
#             )
            
#             await finder_agent_being_setup.initialize() 
#             # Updated print statement to be more generic based on agent_server_names
#             print(f"Agent '{finder_agent_being_setup.name}' initialized within app.run() context (requesting servers: {agent_server_names}).")

#             # openai_api_key = db.secrets.get("OPENAI_API_KEY") # Now handled by mcp_agent.secrets.yaml
#             # if not openai_api_key:
#             #     raise ValueError("OPENAI_API_KEY secret not found.")
            
#             original_openai_model = os.environ.get("OPENAI_MODEL_NAME")
#             # OPENAI_API_KEY is now expected to be picked up from mcp_agent.secrets.yaml
#             # which is created by get_mcp_config_and_write_to_temp_file() and placed in the
#             # same directory as the MCP_AGENT_CONFIG_PATH file.
            
#             # We still set OPENAI_MODEL_NAME as an environment variable, as OpenAISettings might pick it up.
#             original_openai_model = os.environ.get("OPENAI_MODEL_NAME")
            
#             # OPENAI_API_KEY is now expected to be picked up from mcp_agent.secrets.yaml
#             # which is created by get_mcp_config_and_write_to_temp_file() and placed in the
#             # same directory as the MCP_AGENT_CONFIG_PATH file.
            
#             # We still set OPENAI_MODEL_NAME as an environment variable, as OpenAISettings might pick it up.
#             original_openai_model = os.environ.get("OPENAI_MODEL_NAME")
            
#             # Explicitly set OPENAI_API_KEY in environment before attach_llm
#             # This is to ensure that if OpenAIAugmentedLLM or its dependencies (like LiteLLM)
#             # prioritize environment variables for API key discovery, it's available.
#             openai_api_key_val = db.secrets.get("OPENAI_API_KEY")
#             if not openai_api_key_val:
#                 # This should have been caught by get_mcp_config_and_write_to_temp_file, but as a safeguard:
#                 raise ValueError("OPENAI_API_KEY secret not found when trying to set it in environment for attach_llm.")
            
#             original_openai_api_key_env = os.environ.get("OPENAI_API_KEY")
#             os.environ["OPENAI_API_KEY"] = openai_api_key_val
#             print(f"Temporarily set OPENAI_API_KEY environment variable for attach_llm.")

#             os.environ["OPENAI_MODEL_NAME"] = "gpt-4o-mini"
#             print(f"Set OPENAI_MODEL_NAME to 'gpt-4o-mini'. OPENAI_API_KEY set in env and also in mcp_agent.secrets.yaml.")
            
#             try:
#                 # Pass the LLM class. attach_llm should instantiate it and it should pick up
#                 # its configuration (including API key from secrets.yaml and model from env var).
#                 llm_being_setup = await finder_agent_being_setup.attach_llm(
#                     OpenAIAugmentedLLM
#                 )
#                 print(f"LLM class passed to attach_llm for agent '{finder_agent_being_setup.name}' within app.run() context.")
#             finally:
#                 # Restore original environment variables
#                 if original_openai_api_key_env is not None:
#                     os.environ["OPENAI_API_KEY"] = original_openai_api_key_env
#                     print("Restored original OPENAI_API_KEY environment variable.")
#                 elif "OPENAI_API_KEY" in os.environ: # Only delete if we set it and there wasn't one before
#                     del os.environ["OPENAI_API_KEY"]
#                     print("Removed temporarily set OPENAI_API_KEY environment variable.")

#                 if original_openai_model is not None:
#                     os.environ["OPENAI_MODEL_NAME"] = original_openai_model
#                 elif "OPENAI_MODEL_NAME" in os.environ: # Only delete if we set it and there wasn't one before
#                     del os.environ["OPENAI_MODEL_NAME"]
#                 print("Restored original OPENAI_MODEL_NAME environment variable (if any).")
            
#             _finder_agent = finder_agent_being_setup
#             _llm_workflow = llm_being_setup
#             _app_instance = app_to_setup_with

#         print(f"Finder agent '{_finder_agent.name}' and LLM setup complete. MCPApp instance stored.")
#         return _finder_agent, _llm_workflow, _app_instance

#     except Exception as e:
#         print(f"Error during agent setup: {e}")
#         _finder_agent = None
#         _llm_workflow = None
#         _app_instance = None
#         raise HTTPException(status_code=500, detail=f"Failed to setup agent: {e}") from e


@router.post("/initialize-agent", response_model=InitializeAgentResponse)
async def trigger_finder_agent_initialization():
    """
    Manually triggers the initialization of the Finder agent and its LLM.
    This is more for testing the setup process.
    """
    return InitializeAgentResponse(
        message="Agent initialization is currently disabled.",
        agent_name=None,
        llm_attached=False
    )


import requests
from bs4 import BeautifulSoup
from openai import OpenAI

@router.post("/summarize-document", response_model=SummarizeDocumentResponse)
async def trigger_summarize_document(request: SummarizeDocumentRequest):
    """
    Retrieves and summarizes a document from the given URL using direct OpenAI calls.
    """
    print(f"Received request to summarize URL: {request.url}")
    openai_api_key = db.secrets.get("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY secret not found.")
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY secret not found.")

    client = OpenAI(api_key=openai_api_key)

    # Ensure Firebase is initialized for this API
    try:
        firebase_app_instance = firebase_admin.get_app()
        print(f"[DevHelper MCP Agent] Firebase app already initialized: {firebase_app_instance.name}")
    except ValueError:
        print("[DevHelper MCP Agent] Firebase app not found, initializing...")
        try:
            firebase_secret_key = db.secrets.get("FIREBASE_SERVICE_ACCOUNT_KEY")
            if not firebase_secret_key:
                raise ValueError("FIREBASE_SERVICE_ACCOUNT_KEY secret not found.")
            
            cred_json = json.loads(firebase_secret_key)
            cred = admin_credentials.Certificate(cred_json)
            project_id = cred_json.get('project_id', None) # or cred.project_id after Certificate creation
            if not project_id: # Fallback if not in JSON, though firebase_admin.credentials.Certificate might populate it
                # This part is a bit tricky as project_id might not be directly in the parsed cert before initialize_app
                # For bucket name, usually it's better if the project_id is known.
                # Let's assume the SDK handles it or it's available post-cred creation.
                # A common pattern for bucket name is <project_id>.appspot.com
                # If cred.project_id is available:
                # storage_bucket_name = f"{cred.project_id}.appspot.com"
                # firebase_admin.initialize_app(cred, {'storageBucket': storage_bucket_name})
                # For now, initialize without explicit storage bucket if project_id is not easily derived pre-init
                 firebase_admin.initialize_app(cred) # Simpler initialization
            else:
                firebase_admin.initialize_app(cred, {
                    'storageBucket': f"{project_id}.appspot.com"
                })
            print("[DevHelper MCP Agent] Firebase app initialized successfully.")
        except Exception as e:
            print(f"[DevHelper MCP Agent] Error initializing Firebase: {e}")

    try:
        # Fetch content from URL
        response = requests.get(request.url, timeout=10) # Added timeout
        response.raise_for_status() # Raise an exception for bad status codes
        
        # Parse HTML and extract text
        soup = BeautifulSoup(response.content, 'html.parser')
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose() # Remove script and style elements
        text_content = soup.get_text(separator='\n', strip=True)
        
        if not text_content.strip():
            print(f"No text content found at URL: {request.url}")
            raise HTTPException(status_code=404, detail="No text content found at URL.")

        print(f"Fetched text content from {request.url}, length: {len(text_content)}")

        # Summarize text using OpenAI
        # Truncate if too long for the model (adjust max_tokens and prompt as needed)
        max_prompt_length = 12000  # Rough estimate for gpt-4o-mini context window with some buffer
        if len(text_content) > max_prompt_length:
            text_content = text_content[:max_prompt_length]
            print(f"Content truncated to {max_prompt_length} characters for summarization.")

        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant designed to summarize web content."},
                {"role": "user", "content": f"Please provide a concise summary of the following text from the URL {request.url}:\n\n{text_content}"}
            ]
        )
        
        summary_result = completion.choices[0].message.content

        if not summary_result:
            print(f"OpenAI did not return a summary for {request.url}")
            raise HTTPException(status_code=500, detail="Could not generate summary using OpenAI.")

        try:
            db.storage.text.put(f"summary_{sanitize_storage_key(request.url)}.txt", summary_result)
            print(f"Successfully stored summary for {request.url} in db.storage.text")
        except Exception as e_mem:
            print(f"Error saving summary to Databutton Storage: {e_mem}")
            # Not raising an exception here, as summarization itself was successful

        return SummarizeDocumentResponse(summary=summary_result)

    except requests.exceptions.RequestException as e_req:
        print(f"Error fetching URL {request.url}: {e_req}")
        raise HTTPException(status_code=500, detail=f"Error fetching URL: {str(e_req)}") from e_req
    except HTTPException as e_http: # Re-raise HTTPExceptions from parsing/validation
        raise e_http
    except Exception as e_gen:
        print(f"General error summarizing document {request.url}: {type(e_gen).__name__} - {e_gen}")
        raise HTTPException(status_code=500, detail=f"Failed to summarize document: {str(e_gen)}") from e_gen

class MCPToolTestRequest(BaseModel):
    prompt: str

class MCPToolTestResponse(BaseModel):
    result: str
    error: Optional[str] = None

@router.post("/test-mcp-fetch-tool", response_model=MCPToolTestResponse, summary="Test MCP agent's ability to use a configured tool (e.g., fetch).")
async def test_mcp_fetch_tool(request: MCPToolTestRequest):
    """
    Tests if the initialized MCP agent (finder_agent) can use its configured tools (e.g., 'fetch')
    by providing a prompt that should trigger tool use.
    """
    print(f"Received request for MCP tool test with prompt: {request.prompt}")
    return MCPToolTestResponse(result="MCP agent is currently disabled.", error=None)

# --- Generic Key-Value Storage for Agent's Operational Data ---
class SaveItemRequest(BaseModel):
    key: str
    value: dict # Expecting a JSON serializable dictionary

class GetItemResponse(BaseModel):
    key: str
    value: dict | None = None

@router.post("/save-item", summary="Save a generic JSON item to storage")
async def save_generic_item(request: SaveItemRequest):
    """
    Saves a generic JSON serializable dictionary to db.storage.json under the provided key
    and also stores its content with an embedding in Firestore for RAG.
    The key will be sanitized for db.storage.json.
    """
    sanitized_storage_key = sanitize_storage_key(request.key)
    original_key = request.key # Preserve original key for Firestore document ID if suitable, or for metadata
    content_dict = request.value

    # 1. Save to db.storage.json (existing behavior)
    try:
        db.storage.json.put(sanitized_storage_key, content_dict)
        print(f"Successfully stored item with key '{sanitized_storage_key}' in db.storage.json")
    except Exception as e:
        print(f"Error saving item with key '{sanitized_storage_key}' to db.storage.json: {e}")
        # Decide if this error should prevent Firestore saving or be logged only
        # For now, we'll let it raise if critical, or log and continue if desired.
        # raise HTTPException(status_code=500, detail=f"Failed to save item to JSON storage: {str(e)}")

    # 2. Generate embedding and save to Firestore
    try:
        # Convert dictionary to JSON string for embedding
        content_str_for_embedding = json.dumps(content_dict, sort_keys=True)
        
        # Sanitize Firestore document ID
        firestore_doc_id = original_key.replace('/', '_').replace('.', '-')
        if not firestore_doc_id: # handle empty key
            import uuid
            firestore_doc_id = str(uuid.uuid4())
            
        memory_service = MemoryService()
        embedding = await memory_service.generate_and_store_embedding(
            memory_id=firestore_doc_id,
            text=content_str_for_embedding
        )
        
        if not embedding:
            raise ValueError("Failed to generate embedding for textual memory.")

        textual_memory_data = MemoryFrame(
            id=firestore_doc_id,
            memory_type=MemoryType.TEXT,
            content=str(content_dict),
            embedding=embedding,
            timestamp=datetime.utcnow().isoformat(),
            metadata={
                "original_key": original_key,
                "content_dict": content_dict
            }
        )
        
        # Save to Firestore
        # Ensure firestore_db is initialized (typically done at app startup or via a dependency)
        # Re-checking Firebase initialization here, as it was done in summarize_document
        try:
            firebase_admin.get_app()
        except ValueError: # Firebase app not initialized
            print("[DevHelper MCP Agent - save_item] Firebase app not found, attempting to initialize...")
            try:
                firebase_secret_key_str = db.secrets.get("FIREBASE_SERVICE_ACCOUNT_KEY")
                if not firebase_secret_key_str:
                    raise ValueError("FIREBASE_SERVICE_ACCOUNT_KEY secret not found.")
                
                cred_json_obj = json.loads(firebase_secret_key_str)
                cred_obj = admin_credentials.Certificate(cred_json_obj)
                project_id_val = cred_json_obj.get('project_id')
                
                if project_id_val:
                    firebase_admin.initialize_app(cred_obj, {'storageBucket': f"{project_id_val}.appspot.com"})
                else:
                    firebase_admin.initialize_app(cred_obj) # Simpler init if project_id not easily found
                print("[DevHelper MCP Agent - save_item] Firebase app initialized successfully.")
            except Exception as fb_init_e:
                print(f"[DevHelper MCP Agent - save_item] Critical: Firebase initialization failed: {fb_init_e}")
                # This is critical for saving to Firestore, so raise an error
                raise HTTPException(status_code=500, detail=f"Firestore not available: Firebase init failed: {fb_init_e}") from fb_init_e
        
        textual_memories_ref = get_firestore_client().collection('textual_memories')
        textual_memories_ref.document(textual_memory_data.id).set(textual_memory_data.model_dump()) # Use model_dump for Pydantic v2
        
        print(f"Successfully generated embedding and stored textual memory '{textual_memory_data.id}' in Firestore.")
        
        return {
            "message": "Item saved to JSON storage and textual memory stored in Firestore.",
            "json_storage_key": sanitized_storage_key,
            "firestore_memory_id": textual_memory_data.id
        }

    except HTTPException as e_http: # Re-raise HTTPExceptions
        raise e_http
    except Exception as e:
        print(f"Error processing textual memory for key '{original_key}': {e}")
        # If JSON storage succeeded, we might not want to throw a 500 for the whole endpoint
        # but indicate partial success or log the error. For now, return a 500.
        raise HTTPException(status_code=500, detail=f"Failed to process and store textual memory: {str(e)}")

@router.get("/get-item", response_model=GetItemResponse, summary="Get a generic JSON item from storage")
async def get_generic_item(key: str = Query(..., description="The key of the item to retrieve")) -> GetItemResponse:
    """
    Retrieves a generic JSON item from db.storage.json using the provided key.
    The key will be sanitized before lookup.
    Returns the item if found, otherwise returns a value of null.
    """
    sanitized_key = sanitize_storage_key(key)
    try:
        value = db.storage.json.get(sanitized_key, default=None)
        print(f"Retrieved item with key '{sanitized_key}' from db.storage.json. Found: {value is not None}")
        return GetItemResponse(key=sanitized_key, value=value)
    except Exception as e:
        print(f"Error retrieving item with key '{sanitized_key}' from db.storage.json: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve item: {str(e)}")

@router.post("/contextual-suggestion", response_model=ContextualSuggestionResponse)
async def contextual_suggestion(request: ContextualSuggestionRequest):
    visual_memories_data_for_prompt = []
    textual_memories_data_for_prompt = []
    retrieved_visual_count = 0
    retrieved_textual_count = 0
    firestore_client = get_firestore_client() # Get client once
    memory_service = MemoryService()

    if not firestore_client:
        return ContextualSuggestionResponse(
            suggestion="",
            retrieved_visual_context_count=0,
            retrieved_textual_context_count=0,
            error="Firestore client not available. Initialization might have failed."
        )
    
    try:
        # 1. Fetch Visual Memories from Firestore (existing logic)
        visual_memories_context_str = ""
        try:
            frames_ref = firestore_client.collection('memoryFrames').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(request.max_visual_memories)
            docs = frames_ref.stream()
            for doc in docs:
                frame_data = doc.to_dict()
                if frame_data:
                    frame = MemoryFrame(**frame_data)
                    visual_memories_data_for_prompt.append(f"Visual Memory (URL: {frame.pageUrl}, Context: {frame.taskContext}, Action: {frame.userAction}, Outcome: {frame.outcome}, Summary: {frame.summary or 'N/A'})")
            retrieved_visual_count = len(visual_memories_data_for_prompt)
            print(f"[CONTEXTUAL_SUGGESTION] Fetched {retrieved_visual_count} visual memories.")
            if visual_memories_data_for_prompt:
                visual_memories_context_str = "\n".join(visual_memories_data_for_prompt)
                # print(f"[CONTEXTUAL_SUGGESTION] Visual memories context for prompt: {visual_memories_context_str}") # Can be too verbose
            else:
                print("[CONTEXTUAL_SUGGESTION] No visual memories data formatted for prompt.")
        except Exception as e:
            print(f"[CONTEXTUAL_SUGGESTION] Error fetching visual memories: {type(e).__name__} - {e}")
            # Continue without visual memories if there's an error

        # 2. Fetch and Rank Textual Memories from Firestore using RAG
        textual_memories_context_str = ""
        try:
            # Generate embedding for the input query
            query_embedding = await memory_service.generate_and_store_embedding(
                memory_id="query",
                text=request.query
            )
            if not query_embedding:
                raise ValueError("Failed to generate embedding for the query.")

            # Fetch all textual memories
            textual_memories_ref = firestore_client.collection('textual_memories')
            all_textual_docs_stream = textual_memories_ref.stream()
            fetched_textual_docs_count = 0
            processed_for_ranking_count = 0
            ranked_textual_memories = []
            print(f"[CONTEXTUAL_SUGGESTION] Attempting to stream textual memories from Firestore collection '{textual_memories_ref.id}'")
            for doc in all_textual_docs_stream:
                fetched_textual_docs_count += 1
                mem_data = doc.to_dict()
                if mem_data and 'embedding' in mem_data and 'content_dict' in mem_data:
                    try:
                        textual_memory = MemoryFrame(**mem_data) # Validate with Pydantic model
                        similarity = cosine_similarity(np.array(query_embedding), np.array(textual_memory.embedding))
                        ranked_textual_memories.append({"memory": textual_memory, "similarity": similarity})
                        processed_for_ranking_count +=1
                    except Exception as pydantic_error: # Catch errors during Pydantic model instantiation
                        print(f"[CONTEXTUAL_SUGGESTION] Skipping textual memory due to Pydantic validation error: {pydantic_error} for doc ID {doc.id}")
                else:
                    print(f"[CONTEXTUAL_SUGGESTION] Skipping textual memory doc ID {doc.id} due to missing 'embedding' or 'content_dict'. Data: {mem_data}")
            print(f"[CONTEXTUAL_SUGGESTION] Fetched {fetched_textual_docs_count} total textual documents. Processed {processed_for_ranking_count} for ranking.")
            
            # Sort by similarity (descending)
            ranked_textual_memories.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Get top N memories
            top_textual_memories = ranked_textual_memories[:request.max_textual_memories]
            retrieved_textual_count = len(top_textual_memories)
            print(f"[CONTEXTUAL_SUGGESTION] Selected top {retrieved_textual_count} textual memories for prompt after ranking.")

            for item in top_textual_memories:
                mem = item["memory"]
                # Ensure content_dict is a string for the prompt, or handle complex dicts appropriately
                content_display = json.dumps(mem.content_dict) if isinstance(mem.content_dict, dict) else str(mem.content_dict)
                textual_memories_data_for_prompt.append(f"Textual Memory (Key: {mem.original_key}, Similarity: {item['similarity']:.2f}): {content_display}")
            
            if textual_memories_data_for_prompt:
                textual_memories_context_str = "\n".join(textual_memories_data_for_prompt)
                # print(f"[CONTEXTUAL_SUGGESTION] Textual memories context for prompt: {textual_memories_context_str}") # Can be too verbose
            else:
                print("[CONTEXTUAL_SUGGESTION] No textual memories data formatted for prompt.")

        except Exception as e:
            print(f"Error fetching or ranking textual memories: {e}")
            # Continue without textual memories if RAG part fails

        # 3. Construct Prompt (remains similar)
        combined_context = f"Visual Context:\n{visual_memories_context_str if visual_memories_data_for_prompt else 'No relevant visual context found.'}\n\nTextual Context (Retrieved via Semantic Search):\n{textual_memories_context_str if textual_memories_data_for_prompt else 'No relevant textual context found based on your query.'}"
        
        openai_api_key = db.secrets.get("OPENAI_API_KEY")
        if not openai_api_key:
            # This should ideally use proper error handling that get_firestore_client also uses
            # For now, direct check as it was.
            raise ValueError("OPENAI_API_KEY secret not found for contextual suggestion.")
        
        # Ensure client is OpenAI client, not some other global client if naming collides.
        oai_client = OpenAI(api_key=openai_api_key) # Explicitly create OpenAI client here
        
        prompt_messages = [
            {"role": "system", "content": "You are a helpful AI assistant. Based on the provided context from past visual memories and semantically similar textual memories, answer the user's query or provide a relevant suggestion."},
            {"role": "user", "content": f"Query: {request.query}\n\nCombined Context:\n{combined_context}"}
        ]
        
        # 4. Call OpenAI (remains similar)
        completion = oai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompt_messages
        )
        suggestion = completion.choices[0].message.content

        return ContextualSuggestionResponse(
            suggestion=suggestion,
            retrieved_visual_context_count=retrieved_visual_count,
            retrieved_textual_context_count=retrieved_textual_count
        )

    except Exception as e:
        print(f"Error in contextual_suggestion endpoint: {type(e).__name__} - {e}")
        # Ensure counts are accurate even in case of error before OpenAI call
        return ContextualSuggestionResponse(
            suggestion="",
            retrieved_visual_context_count=retrieved_visual_count,
            retrieved_textual_context_count=retrieved_textual_count,
            error=f"{type(e).__name__}: {str(e)}"
        )
