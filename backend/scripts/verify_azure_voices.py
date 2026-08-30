"""Validate that configured Azure TTS voice NAMES exist in the Azure catalog.

NAME-VALIDATION ONLY. This script does NOT synthesize audio (live audio
verification requires real credentials + a playback device and is a separate
boundary step). Run manually with AZURE_SPEECH_KEY set:

    python backend/scripts/verify_azure_voices.py

Exits 0 if all configured voices are valid (or if skipped due to missing
credentials/SDK), 1 if a configured voice name is not found in the catalog.
"""
from __future__ import annotations

import os
import sys

# Allow running as a standalone script from the repo root.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def main() -> int:
    from app.config import get_settings

    settings = get_settings()
    key = getattr(settings, "azure_speech_key", "") or os.getenv("AZURE_SPEECH_KEY", "")
    region = getattr(settings, "azure_speech_region", "centralindia") or os.getenv(
        "AZURE_SPEECH_REGION", "centralindia"
    )

    if not key:
        print("SKIP: AZURE_SPEECH_KEY not set — cannot verify live voice names.")
        print("      Set AZURE_SPEECH_KEY (and AZURE_SPEECH_REGION) to validate names.")
        return 0

    try:
        import azure.cognitiveservices.speech as speechsdk
    except (ImportError, ModuleNotFoundError):
        print("SKIP: azure-cognitiveservices-speech SDK not installed; cannot verify.")
        return 0

    config = speechsdk.SpeechConfig(subscription=key, region=region)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=config, audio_config=None)
    voices = synthesizer.get_voice_info_list()
    available = {v.name for v in voices}

    tts_voices = getattr(settings, "tts_voices", {}) or {}
    if not tts_voices:
        print("No tts_voices configured; nothing to verify.")
        return 0

    missing = []
    print("Validating configured Azure TTS voice names (name check only):")
    for lang, name in tts_voices.items():
        ok = name in available
        status = "OK" if ok else "MISSING"
        if not ok:
            missing.append((lang, name))
        print(f"  {lang}: {name} [{status}]")

    if missing:
        print(f"\n{len(missing)} configured voice name(s) NOT found in Azure catalog.")
        return 1

    print("\nAll configured Azure voice names are valid (name check only).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
