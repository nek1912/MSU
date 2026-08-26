_DEVANAGARI = set(range(0x0900, 0x097F))
_HI_STOPWORDS = {"ka", "ki", "ke", "kaise", "kya", "hai", "mein", "meri", "mera",
                 "kitna", "nahi", "aur"}
_EN_STOPWORDS = {"the", "is", "at", "which", "on", "in", "how", "what", "do",
                 "does", "of", "and", "to", "for"}


def _script_ratios(text: str) -> float:
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if ord(c) in _DEVANAGARI) / len(letters)


def _latin_stopword_bias(text: str) -> float:
    words = {w.lower() for w in text.split()}
    return len(words & _HI_STOPWORDS) - len(words & _EN_STOPWORDS)


def normalize_language(selected: str, text: str) -> str:
    if selected not in ("en", "hi"):
        raise ValueError(f"unsupported language: {selected}")
    dev_ratio = _script_ratios(text)
    if selected == "en" and dev_ratio >= 0.7:
        return "hi"  # high-confidence mismatch only
    if selected == "hi" and dev_ratio <= 0.05 and _latin_stopword_bias(text) < 0:
        return "en"
    return selected
