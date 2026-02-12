import databutton as db
import openai
from fastapi import APIRouter, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.auth import AuthorizedUser


router = APIRouter()

# --- Client Initialization ---

def get_openai_client():
    """Initializes and returns the OpenAI client using the secret key."""
    api_key = db.secrets.get("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    return openai.OpenAI(api_key=api_key)

# --- Pydantic Models ---

class TranscriptionResponse(BaseModel):
    text: str

class TextToSpeechRequest(BaseModel):
    text: str
    voice: str = "alloy"
    model: str = "tts-1"

# --- API Endpoints ---

@router.post("/transcribe-audio", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcribes audio using OpenAI's Whisper model.
    """
    client = get_openai_client()
    try:
        audio_bytes = await file.read()
        
        from io import BytesIO
        audio_io = BytesIO(audio_bytes)
        # It's important to name the file-like object for some APIs.
        audio_io.name = file.filename or "audio.wav"

        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_io,
        )
        return {"text": transcription.text}
    except Exception as e:
        print(f"Error during transcription: {e}")
        raise HTTPException(status_code=500, detail="Failed to transcribe audio.")

@router.post("/text-to-speech", tags=["stream"])
async def text_to_speech(request: TextToSpeechRequest):
    """
    Converts text to speech using OpenAI's TTS model and returns the audio.
    """
    client = get_openai_client()
    try:
        response = client.audio.speech.create(
            model=request.model,
            voice=request.voice,
            input=request.text,
        )
        return StreamingResponse(response.iter_bytes(), media_type="audio/mpeg")
    except Exception as e:
        print(f"Error during text-to-speech: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate audio.")

@router.websocket("/ws/voice-chat")
async def websocket_voice_chat(websocket: WebSocket, user: AuthorizedUser):
    """
    Handles WebSocket communication for real-time voice chat.
    Requires user authentication.
    """
    await websocket.accept(subprotocol="databutton.app")
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo for {user.sub}: {data}")
    except WebSocketDisconnect:
        print(f"Client {user.sub} disconnected from voice chat WebSocket.")
    except Exception as e:
        print(f"An error occurred in the voice chat WebSocket: {e}")
        await websocket.close(code=1011)
