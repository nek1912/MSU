import numpy as np

from app.domains import AnchorStore


class FakeProvider:
    """Deterministic fake: identical text -> identical vector; different -> orthogonal-ish."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        out = []
        for i, t in enumerate(texts):
            v = [0.0] * 16
            v[i % 16] = 1.0
            out.append(v)
        return out


RULES = {"pmfby": ["pmfby"], "finlit": ["jan dhan"]}
ANCHORS = {"pmfby": ["crop insurance claim"], "finlit": ["open a bank account"]}


def test_keyword_rule_short_circuits():
    store = AnchorStore(rules=RULES, anchors=ANCHORS, vectors=np.zeros((2, 16)))
    assert store.classify("tell me about PMFBY", [0.0] * 16)[0] == "pmfby"


def test_anchor_match_by_cosine():
    q = [1.0] + [0.0] * 15  # matches FakeProvider vector index 0
    store = AnchorStore(rules={}, anchors={"finlit": ["open a bank account", "second"]},
                        vectors=np.array([[1.0] + [0.0] * 15, [0.0, 1.0] + [0.0] * 14]))
    domain, score = store.classify("bank account help", q)
    assert domain == "finlit" and score > 0.9


def test_out_of_scope_floor():
    store = AnchorStore(rules={}, anchors={"finlit": ["open a bank account"]},
                        vectors=np.zeros((1, 16)))
    assert store.classify("who won the cricket match", [0.0] * 16)[0] == "out_of_scope"
