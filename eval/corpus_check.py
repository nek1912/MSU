#!/usr/bin/env python3
"""Corpus quality checker for seed .md files."""
import os
import re
import json
import sys

REQUIRED_FIELDS = [
    "source_id", "title", "organization", "domain",
    "jurisdiction", "url", "verified_date"
]
ALLOWED_DOMAINS = [
    "cooperative", "pacs", "schemes", "pmfby",
    "agriculture", "finlit", "grievance"
]
ALLOWED_JURISDICTIONS = ["central", "state"]
PLACEHOLDERS = [
    "PASTE VERBATIM TEXT HERE", "TODO", "TBD",
    "Lorem ipsum", "Wikipedia"
]

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

def check_file(filepath):
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
        errors, placeholders = check_file(fpath)
        all_errors.extend(errors)
        all_placeholders.extend(placeholders)

        meta, _ = parse_frontmatter(open(fpath, 'r', encoding='utf-8').read())
        if meta and 'source_id' in meta:
            sid = meta['source_id']
            if sid in all_source_ids:
                all_errors.append({
                    "file": fname,
                    "error": f"Duplicate source_id: '{sid}' (also in {all_source_ids[sid]})",
                    "severity": "error"
                })
            else:
                all_source_ids[sid] = fname

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

    sys.exit(1 if files_failed > 0 else 0)

if __name__ == '__main__':
    main()
