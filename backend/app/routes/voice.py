"""Voice routes for STT and TTS."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.voice_service import VoiceService, VoiceUnavailableError

router = APIRouter()
voice_service = VoiceService()


class TranscribeRequest(BaseModel):
    audio: bytes
    language: str = "en"


class SpeakRequest(BaseModel):
    text: str
    language: str = "en"


@router.post("/voice/transcribe")
async def transcribe(req: TranscribeRequest) -> dict:
    """Convert speech to text."""
    try:
        text = await voice_service.speech_to_text(req.audio, req.language)
        return {"text": text, "language": req.language}
    except VoiceUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/voice/speak")
async def speak(req: SpeakRequest) -> dict:
    """Convert text to speech."""
    try:
        audio = await voice_service.text_to_speech(req.text, req.language)
        return {"audio": audio.hex(), "language": req.language}
    except VoiceUnavailableError as e:
        raise HTTPException(status_code=503, detail=str(e))
