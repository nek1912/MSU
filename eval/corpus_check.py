#!/usr/bin/env python3
"""Corpus quality checker for seed .md files."""
import os
import re
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

REQUIRED_FIELDS = [
    "source_id", "title", "organization", "domain",
    "jurisdiction", "url", "verified_date",
    "source_type", "official_domain"
]
ALLOWED_DOMAINS = [
    "cooperative", "pacs", "schemes", "pmfby",
    "agriculture", "finlit", "grievance"
]
ALLOWED_JURISDICTIONS = ["central", "state", "central_and_state"]
PLACEHOLDERS = [
    "PASTE VERBATIM TEXT HERE", "TODO", "TBD",
    "Lorem ipsum", "Wikipedia"
]
ALLOWED_SOURCE_TYPES = [
    "official_web_source", "legislation", "legislation_repository",
    "guidelines", "faq", "financial_literacy", "model_bylaw"
]
APPROVED_OFFICIAL_DOMAINS = [
    "gov.in", "cooperation.gov.in", "pmfby.gov.in",
    "rbi.org.in", "pmjdy.gov.in", "indiacode.nic.in",
    "gujaratlegislature.nic.in"
]


def _official_domain_matches(url, declared_domain):
    """Check if the URL's domain matches or is a subdomain of the declared official domain."""
    try:
        parsed = urlparse(url)
        host = parsed.hostname or ""
        return host == declared_domain or host.endswith("." + declared_domain)
    except Exception:
        return False


def parse_frontmatter(content):
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return None, content
    raw = match.group(1)
    meta = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        kv = re.match(r'^(\w+):\s*(.+)$', line)
        if kv:
            key = kv.group(1)
            val = kv.group(2).strip().strip('"').strip("'")
            meta[key] = val
    body = content[match.end():]
    return meta, body

def check_file(filepath, seen_source_ids=None):
    errors = []
    placeholders = []
    basename = os.path.basename(filepath)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        errors.append({"file": basename, "error": f"Cannot read: {e}", "severity": "error"})
        return errors, placeholders

    meta, body = parse_frontmatter(content)
    if meta is None:
        errors.append({"file": basename, "error": "No YAML frontmatter found", "severity": "error"})
        return errors, placeholders

    for field in REQUIRED_FIELDS:
        if field not in meta or not meta[field]:
            errors.append({"file": basename, "error": f"Missing required field: {field}", "severity": "error"})

    if meta.get("domain") and meta["domain"] not in ALLOWED_DOMAINS:
        errors.append({"file": basename, "error": f"Invalid domain: {meta['domain']}", "severity": "error"})
    if meta.get("jurisdiction") and meta["jurisdiction"] not in ALLOWED_JURISDICTIONS:
        errors.append({"file": basename, "error": f"Invalid jurisdiction: {meta['jurisdiction']}", "severity": "error"})
    if meta.get("url") and not meta["url"].startswith("https://"):
        errors.append({"file": basename, "error": "URL does not start with https://", "severity": "warning"})

    if meta.get("source_type") and meta["source_type"] not in ALLOWED_SOURCE_TYPES:
        errors.append({"file": basename, "error": f"Invalid source_type: {meta['source_type']}", "severity": "error"})

    if meta.get("official_domain") and meta["official_domain"] not in APPROVED_OFFICIAL_DOMAINS:
        errors.append({"file": basename, "error": f"official_domain not in approved registry: {meta['official_domain']}", "severity": "error"})

    if meta.get("url") and meta.get("official_domain"):
        if not _official_domain_matches(meta["url"], meta["official_domain"]):
            errors.append({"file": basename, "error": f"URL domain does not match declared official_domain '{meta['official_domain']}'", "severity": "error"})

    current_source_id = meta.get("source_id")
    if current_source_id:
        if seen_source_ids is not None:
            if current_source_id in seen_source_ids:
                errors.append({"file": basename, "error": f"Duplicate source_id: '{current_source_id}' (also in {seen_source_ids[current_source_id]})", "severity": "error"})
            else:
                seen_source_ids[current_source_id] = basename
        else:
            dirpath = os.path.dirname(filepath)
            for other in os.listdir(dirpath):
                if other.endswith('.md') and other != basename:
                    other_path = os.path.join(dirpath, other)
                    try:
                        with open(other_path, 'r', encoding='utf-8') as f:
                            other_content = f.read()
                        other_meta, _ = parse_frontmatter(other_content)
                        if other_meta and other_meta.get('source_id') == current_source_id:
                            errors.append({"file": basename, "error": f"Duplicate source_id: '{current_source_id}' (also in {other})", "severity": "error"})
                            break
                    except Exception:
                        pass

    if not body.strip():
        errors.append({"file": basename, "error": "Empty content after frontmatter", "severity": "error"})

    lines = content.splitlines()
    for i, line in enumerate(lines, 1):
        for ph in PLACEHOLDERS:
            if ph.lower() in line.lower():
                placeholders.append({"file": basename, "line": i})
                break

    return errors, placeholders

def main():
    seeds_dir = os.path.join(os.path.dirname(__file__), '..', 'corpus', 'seeds')
    if not os.path.isdir(seeds_dir):
        print(f"Seeds directory not found: {seeds_dir}", file=sys.stderr)
        sys.exit(1)

    md_files = sorted([f for f in os.listdir(seeds_dir) if f.endswith('.md')])
    if not md_files:
        print("No .md files found in seeds directory", file=sys.stderr)
        sys.exit(1)

    all_errors = []
    all_placeholders = []
    all_source_ids = {}
    files_passed = 0
    files_failed = 0

    for fname in md_files:
        fpath = os.path.join(seeds_dir, fname)
        errors, placeholders = check_file(fpath, seen_source_ids=all_source_ids)
        all_errors.extend(errors)
        all_placeholders.extend(placeholders)

        has_errors = any(e['severity'] == 'error' for e in errors if e['file'] == fname)
        if has_errors:
            files_failed += 1
        else:
            files_passed += 1

    report = {
        "files_checked": len(md_files),
        "files_passed": files_passed,
        "files_failed": files_failed,
        "errors": all_errors,
        "placeholders_found": all_placeholders
    }

    os.makedirs(os.path.join(os.path.dirname(__file__), 'reports'), exist_ok=True)
    out_path = os.path.join(os.path.dirname(__file__), 'reports', 'corpus_check.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"Checked {len(md_files)} files: {files_passed} passed, {files_failed} failed")
    if all_errors:
        print(f"Errors: {len(all_errors)}")
    if all_placeholders:
        print(f"Placeholders found: {len(all_placeholders)}")
    print(f"Report written to {out_path}")

    gold_result = validate_gold_cases()
    sys.exit(1 if files_failed > 0 or gold_result != 0 else 0)


def validate_gold_cases():
    """Validate that all source_ids in gold_cases.yaml exist in sources.yaml."""
    import yaml
    base = Path(__file__).resolve().parent.parent
    sources_path = base / "sources.yaml"
    gold_path = base / "eval" / "gold_cases.yaml"

    if not gold_path.exists():
        return 0

    with open(sources_path, encoding="utf-8") as f:
        sources = yaml.safe_load(f)
    source_ids = {s["id"] for s in sources.get("sources", [])}

    with open(gold_path, encoding="utf-8") as f:
        cases = yaml.safe_load(f)

    missing = set()
    for case in cases:
        for sid in case.get("relevant_source_ids", []):
            if sid not in source_ids:
                missing.add(sid)

    if missing:
        print(f"Gold cases reference missing source_ids: {missing}", file=sys.stderr)
        return 1
    print(f"Gold case validation passed: all {len(source_ids)} source_ids valid")
    return 0


if __name__ == '__main__':
    main()
