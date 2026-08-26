import json
from functools import lru_cache
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).parent.parent / "data"
DOMAIN_FLOOR = 0.45  # provisional; calibrated in Phase 4 alongside retrieval gates


def load_rules(path: Path = DATA_DIR / "keyword_rules.json") -> dict[str, list[str]]:
    return json.loads(path.read_text(encoding="utf-8"))


class AnchorStore:
    def __init__(self, rules: dict[str, list[str]], domain_vectors: dict[str, np.ndarray]):
        self.rules = rules
        self.domains = sorted(domain_vectors)
        vecs = np.array([domain_vectors[d] for d in self.domains])
        self.vectors = vecs / np.maximum(np.linalg.norm(vecs, axis=1, keepdims=True), 1e-9)

    def classify(self, text: str, query_embedding: list[float]) -> tuple[str, float]:
        lowered = text.lower()
        for domain, keywords in self.rules.items():
            if any(kw in lowered for kw in keywords):
                return domain, 1.0
        q = np.asarray(query_embedding, dtype=float)
        q = q / max(np.linalg.norm(q), 1e-9)
        scores = self.vectors @ q
        best = int(scores.argmax())
        if scores[best] < DOMAIN_FLOOR:
            return "out_of_scope", float(scores[best])
        return self.domains[best], float(scores[best])


@lru_cache(maxsize=1)
def load_anchor_store(embed_texts, rules_path: Path = DATA_DIR / "keyword_rules.json",
                      anchors_path: Path = DATA_DIR / "domain_anchors.json") -> AnchorStore:
    anchors = json.loads(anchors_path.read_text(encoding="utf-8"))
    domain_vectors = {}
    for domain, phrases in anchors.items():
        vecs = np.asarray(embed_texts(phrases), dtype=float)
        domain_vectors[domain] = vecs.mean(axis=0)  # average per domain
    return AnchorStore(load_rules(rules_path), domain_vectors)


def get_anchor_store() -> AnchorStore:
    """Process-wide singleton. The route MUST call THIS, never
    `load_anchor_store(provider.embed_texts)` directly — a fresh bound method
    per request would defeat the cache and re-embed all ~70 anchors on every
    `/chat` (P0-1). First call costs ~70 embedding requests; the FastAPI
    startup hook (Task 11) warms it so no user request ever pays for it."""
    from app.providers.embeddings import get_embedding_provider
    return load_anchor_store(get_embedding_provider().embed_texts)
