import yaml


def parse_chunk_file(path) -> dict:
    raw = path.read_text(encoding="utf-8")
    parts = raw.split("---\n", 2)
    meta = yaml.safe_load(parts[1]) or {}
    return {**meta, "content": parts[2].strip()}
