import importlib.util
import os
import sys

import pytest

_SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "scripts",
    "verify_azure_voices.py",
)


def _load_module():
    spec = importlib.util.spec_from_file_location("verify_azure_voices", _SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_script_runs_and_skips_without_creds(monkeypatch):
    monkeypatch.delenv("AZURE_SPEECH_KEY", raising=False)
    monkeypatch.delenv("AZURE_SPEECH_REGION", raising=False)
    # Ensure settings don't carry a key from elsewhere for this check.
    module = _load_module()
    # Force no key path by patching get_settings if needed.
    import app.config as cfg

    class _Fake:
        azure_speech_key = ""
        azure_speech_region = "centralindia"
        tts_voices = {}

    monkeypatch.setattr(cfg, "get_settings", lambda: _Fake())
    assert module.main() == 0
