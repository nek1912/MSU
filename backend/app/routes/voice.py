"""Voice I/O route — Sarvam (primary) → Azure (fallback) → text-only.

Pipeline: audio → STT → text → existing chat RAG → answer → TTS → audio
"""

import logging
import base64

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import Response

from app.providers.sarvam_voice import SarvamSTTProvider, SarvamTTSProvider
from app.providers.azure_stt import AzureSTTProvider
from app.providers.azure_tts import AzureTTSProvider
from app.config import get_settings
from app.routes.chat import chat as chat_handler
from app.routes.chat import ChatRequest

_log = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["voice"])


def _lang_short(lang: str) -> str:
    """'hi-IN' → 'hi', 'en-IN' → 'en'."""
    return lang.split("-")[0] if "-" in lang else lang


async def _stt(audio_bytes: bytes, language: str) -> str:
    """STT with fallback: Sarvam → Azure."""
    # Try Sarvam first
    sarvam = SarvamSTTProvider()
    if sarvam.enabled:
        try:
            return await sarvam.transcribe(audio_bytes, language)
        except Exception as e:
            _log.warning("Sarvam STT failed, trying Azure: %s", e)

    # Fallback to Azure
    settings = get_settings()
    azure = AzureSTTProvider(settings)
    if azure.configured:
        try:
            return azure.transcribe(audio_bytes, language)
        except Exception as e:
            _log.warning("Azure STT failed: %s", e)

    return ""


async def _tts(text: str, language: str) -> bytes | None:
    """TTS with fallback: Sarvam → Azure → None."""
    # Try Sarvam first
    sarvam = SarvamTTSProvider()
    if sarvam.enabled:
        try:
            return await sarvam.synthesize(text, language)
        except Exception as e:
            _log.warning("Sarvam TTS failed, trying Azure: %s", e)

    # Fallback to Azure
    settings = get_settings()
    azure = AzureTTSProvider(settings)
    if azure.configured:
        try:
            return azure.synthesize(text, language)
        except Exception as e:
            _log.warning("Azure TTS failed: %s", e)

    return None


@router.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str = Form(default="hi"),
) -> dict:
    """STT: Convert uploaded audio to text (no RAG)."""
    audio_bytes = await audio.read()
    text = await _stt(audio_bytes, language)
    return {"text": text, "language": language, "error": None if text else "no_speech"}


@router.post("/speak")
async def speak_text(
    text: str = Form(...),
    language: str = Form(default="hi"),
) -> Response:
    """TTS: Convert text to speech audio (no RAG). Returns WAV."""
    audio = await _tts(text, language)
    if audio:
        return Response(content=audio, media_type="audio/wav")
    return Response(content=b"", media_type="audio/wav", status_code=503)


@router.post("")
async def voice_chat(
    audio: UploadFile = File(...),
    language: str = Form(default="hi"),
    session_id: str = Form(default=""),
    state: str | None = Form(default=None),
) -> dict:
    """Full voice pipeline: audio → STT → RAG → TTS → audio."""
    audio_bytes = await audio.read()
    transcribed = await _stt(audio_bytes, language)

    if not transcribed:
        return {
            "answer": "Could not understand the audio. Please try again.",
            "transcribed_text": "",
            "audio_base64": None,
            "error": "no_speech",
        }

    # RAG via existing chat pipeline
    chat_request = ChatRequest(
        question=transcribed,
        language=_lang_short(language),
        session_id=session_id,
        state=state,
    )
    rag_result = chat_handler(chat_request)

    # TTS
    answer_text = rag_result.get("answer", "")
    audio_b64 = None
    if answer_text:
        answer_audio = await _tts(answer_text, _lang_short(language))
        if answer_audio:
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
