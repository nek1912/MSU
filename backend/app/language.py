"""Language detection — loads all configuration from data/language_config.json.

No hardcoded script ranges, stopwords, or language lists in this file.
"""
import json
from functools import lru_cache
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data"


@lru_cache(maxsize=1)
def _load_config() -> dict:
    """Load language config from JSON (cached)."""
    path = DATA_DIR / "language_config.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    # Convert script ranges to sets for O(1) lookup
    scripts = {}
    for name, (start, end) in raw["scripts"].items():
        scripts[name] = set(range(start, end + 1))
    # Convert stopwords to sets
    stopwords = {lang: set(words) for lang, words in raw["stopwords"].items()}
    return {
        "scripts": scripts,
        "stopwords": stopwords,
        "supported": set(raw["supported_languages"]),
        "script_threshold": raw["script_threshold"],
        "latin_threshold": raw["latin_threshold"],
    }


def _script_ratios(text: str) -> tuple[float, float]:
    """Return (devanagari_ratio, gujarati_ratio) among alphabetic chars."""
    cfg = _load_config()
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0, 0.0
    dev = sum(1 for c in letters if ord(c) in cfg["scripts"]["devanagari"]) / len(letters)
    guj = sum(1 for c in letters if ord(c) in cfg["scripts"]["gujarati"]) / len(letters)
    return dev, guj


def _latin_stopword_bias(text: str, hi_sw: set, gu_sw: set) -> tuple[int, int]:
    cfg = _load_config()
    en_sw = cfg["stopwords"]["en"]
    words = {w.lower() for w in text.split()}
    return (len(words & hi_sw) - len(words & en_sw),
            len(words & gu_sw) - len(words & en_sw))


def normalize_language(selected: str, text: str) -> str:
    """Detect actual language from text, using selection as a hint.
    
    All thresholds and language lists loaded from data/language_config.json.
    The original query is preserved — this only classifies the language.
    """
    cfg = _load_config()
    if selected not in cfg["supported"]:
        raise ValueError(f"unsupported language: {selected}")
    dev_ratio, guj_ratio = _script_ratios(text)
    hi_sw = cfg["stopwords"]["hi"]
    gu_sw = cfg["stopwords"]["gu"]
    hi_bias, gu_bias = _latin_stopword_bias(text, hi_sw, gu_sw)
    threshold = cfg["script_threshold"]
    latin_thresh = cfg["latin_threshold"]

    # Devanagari script → Hindi
    if dev_ratio >= threshold:
        return "hi"
    # Gujarati script → Gujarati
    if guj_ratio >= threshold:
        return "gu"
    # Latin script with Hindi stopword bias → Hindi
    if selected == "hi" and dev_ratio <= latin_thresh and hi_bias > 0:
        return "hi"
    # Latin script with Gujarati stopword bias → Gujarati
    if selected == "gu" and dev_ratio <= latin_thresh and guj_ratio <= latin_thresh and gu_bias > 0:
        return "gu"
    return selected
