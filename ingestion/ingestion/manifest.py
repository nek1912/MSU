from pathlib import Path

import yaml

# Required fields that must be non-null
MANIFEST_REQUIRED_NON_NULL = [
    "source_id", "path", "actual_title", "issuing_organization",
    "target_domain", "jurisdiction", "document_type", "official_source_url",
]

# Required fields that may be null
MANIFEST_REQUIRED_KEYS = [
    "state", "effective_date", "document_date",
]


def load_mvp_manifest(manifest_path: Path) -> list[dict]:
    """Load MVP sources from YAML manifest file."""
    with open(manifest_path, encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    return manifest.get("sources", [])


def load_hold_manifest(manifest_path: Path) -> list[dict]:
    """Load hold sources from YAML manifest file."""
    with open(manifest_path, encoding="utf-8") as f:
        manifest = yaml.safe_load(f)
    return manifest.get("sources", [])


def validate_manifest_files(sources: list[dict], base_dir: Path) -> tuple[list[dict], list[dict]]:
    """Validate that manifest files exist on disk.
    
    Returns:
        (valid_sources, missing_sources) tuple
    """
    valid = []
    missing = []
    for source in sources:
        file_path = base_dir / source.get("path", "")
        if file_path.exists():
            valid.append(source)
        else:
            missing.append(source)
    return valid, missing


def validate_manifest_fields(source: dict) -> list[str]:
    """Validate that manifest source has all required fields for DB insertion.
    
    Returns:
        List of missing/invalid field names (empty if valid)
    """
    errors = []
    
    # Check required non-null fields
    for field in MANIFEST_REQUIRED_NON_NULL:
        if field not in source or source[field] is None:
            errors.append(field)
    
    # Check required keys (may be null)
    for field in MANIFEST_REQUIRED_KEYS:
        if field not in source:
            errors.append(field)
    
    # Conditional validation: state required when jurisdiction is "state"
    if source.get("jurisdiction") == "state" and not source.get("state"):
        errors.append("state")
    
    return errors
