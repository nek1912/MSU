"""PHASE 13: Voice I/O route.

Architecture: One RAG core, no separate voice RAG.
Pipeline: audio → STT → text → existing chat RAG → answer → TTS → audio

The voice route is a thin adapter around the same RAG pipeline used by /chat.
It does NOT duplicate retrieval, generation, or evidence gating logic.
"""
import logging

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import Response

from app.config import get_settings
from app.providers.azure_stt import AzureSTTProvider
from app.providers.azure_tts import AzureTTSProvider
from app.routes.chat import chat as chat_handler
from app.routes.chat import ChatRequest

_log = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form(default="en-IN"),
) -> dict:
    """STT: Convert uploaded audio to text.

    This is a pure STT endpoint — no RAG, no generation.
    Returns the transcribed text for the client to use.
    """
    settings = get_settings()
    stt = AzureSTTProvider(settings)

    if not stt.configured:
        return {
            "text": "",
            "error": "Azure Speech Services not configured",
            "language": language,
        }

    audio_bytes = await audio.read()
    text = stt.transcribe(audio_bytes, language)

    return {"text": text, "language": language, "error": None}


@router.post("/speak")
async def speak_text(
    text: str = Form(...),
    language: str = Form(default="en"),
) -> Response:
    """TTS: Convert text to speech audio.

    This is a pure TTS endpoint — no RAG, no generation.
    Returns WAV audio bytes.
    """
    settings = get_settings()
    tts = AzureTTSProvider(settings)

    if not tts.configured:
        return Response(content=b"", media_type="audio/wav", status_code=503)

    audio_bytes = tts.synthesize(text, language)
    return Response(content=audio_bytes, media_type="audio/wav")


@router.post("")
async def voice_chat(
    audio: UploadFile = File(...),
    language: str = Form(default="en-IN"),
    session_id: str = Form(default=""),
    state: str | None = Form(default=None),
) -> dict:
    """Full voice pipeline: audio → STT → RAG → TTS → audio.

    One RAG core (same as /chat), no separate voice RAG.
    Pipeline: STT → chat handler → TTS
    """
    settings = get_settings()
    stt = AzureSTTProvider(settings)
    tts = AzureTTSProvider(settings)

    if not stt.configured:
        return {
            "answer": "Voice input is not configured.",
            "transcribed_text": "",
            "audio_base64": None,
            "error": "Azure Speech Services not configured",
        }

    # Step 1: STT — convert audio to text
    audio_bytes = await audio.read()
    transcribed = stt.transcribe(audio_bytes, language)

    if not transcribed:
        return {
            "answer": "Could not understand the audio. Please try again.",
            "transcribed_text": "",
            "audio_base64": None,
            "error": "no_speech",
        }

    # Step 2: RAG — pass transcribed text through existing chat pipeline
    chat_request = ChatRequest(
        question=transcribed,
        language=language.split("-")[0],  # "en-IN" → "en"
        session_id=session_id,
        state=state,
    )
    rag_result = chat_handler(chat_request)

    # Step 3: TTS — convert answer to speech
    answer_text = rag_result.get("answer", "")
    audio_b64 = None
    if tts.configured and answer_text:
        answer_audio = tts.synthesize(answer_text, language.split("-")[0])
        if answer_audio:
            import base64
            audio_b64 = base64.b64encode(answer_audio).decode("ascii")

    return {
        "answer": answer_text,
        "transcribed_text": transcribed,
        "audio_base64": audio_b64,
        "language": rag_result.get("language", language),
        "domain": rag_result.get("domain", "unknown"),
        "confidence": rag_result.get("confidence", 0.0),
        "confidence_level": rag_result.get("confidence_level", "none"),
        "citations": rag_result.get("citations", []),
        "abstained": rag_result.get("abstained", False),
        "error": None,
    }
