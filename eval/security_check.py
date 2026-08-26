#!/usr/bin/env python3
"""Security scan for the project."""
import os
import re
import json
import subprocess
import sys

API_KEY_PATTERNS = [
    re.compile(r'sk-[A-Za-z0-9]{20,}'),
    re.compile(r'api_key\s*=\s*["\'][^"\']{10,}["\']', re.IGNORECASE),
    re.compile(r'Bearer\s+[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE),
]
NEXT_PUBLIC_SECRET_PATTERNS = [
    re.compile(r'NEXT_PUBLIC_\w*(KEY|SECRET|TOKEN)\w*\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
]
CREDENTIAL_URL_PATTERNS = [
    re.compile(r'https?://[^@\s]+:[^@\s]+@[^\s]+'),
]

def check_git_env_tracked():
    """Check if .env is tracked by git."""
    try:
        result = subprocess.run(
            ['git', 'ls-files', '.env'],
            capture_output=True, text=True, cwd=os.path.join(os.path.dirname(__file__), '..')
        )
        tracked = result.stdout.strip()
        return {
            "name": ".env not tracked by git",
            "passed": len(tracked) == 0,
            "details": f"Tracked: {tracked}" if tracked else "Not tracked (good)"
        }
    except Exception as e:
        return {
            "name": ".env not tracked by git",
            "passed": False,
            "details": f"Error: {e}"
        }

def check_gitignore_env():
    """Check .gitignore includes .env."""
    gitignore = os.path.join(os.path.dirname(__file__), '..', '.gitignore')
    try:
        with open(gitignore, 'r') as f:
            content = f.read()
        has_env = any(line.strip() == '.env' for line in content.splitlines())
        return {
            "name": ".gitignore includes .env",
            "passed": has_env,
            "details": "Present" if has_env else "Missing"
        }
    except Exception as e:
        return {
            "name": ".gitignore includes .env",
            "passed": False,
            "details": f"Error: {e}"
        }

def scan_python_for_api_keys():
    """Scan backend Python files for API key patterns."""
    backend_dir = os.path.join(os.path.dirname(__file__), '..', 'backend', 'app')
    findings = []
    exclude_files = {'config.py'}
    for root, dirs, files in os.walk(backend_dir):
        for fname in files:
            if not fname.endswith('.py') or fname in exclude_files:
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    for pattern in API_KEY_PATTERNS:
                        if pattern.search(line):
                            findings.append(f"{os.path.relpath(fpath, backend_dir)}:{i}: {line.strip()[:100]}")
            except Exception:
                pass
    return {
        "name": "No API keys in backend source",
        "passed": len(findings) == 0,
        "details": findings if findings else "Clean"
    }

def scan_frontend_next_public():
    """Scan frontend for NEXT_PUBLIC_ secrets."""
    frontend_dir = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'src')
    findings = []
    if not os.path.isdir(frontend_dir):
        return {
            "name": "No NEXT_PUBLIC_ secrets in frontend",
            "passed": True,
            "details": "Frontend src directory not found"
        }
    for root, dirs, files in os.walk(frontend_dir):
        for fname in files:
            if not (fname.endswith('.ts') or fname.endswith('.tsx') or fname.endswith('.js')):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    for pattern in NEXT_PUBLIC_SECRET_PATTERNS:
                        if pattern.search(line):
                            findings.append(f"{os.path.relpath(fpath, frontend_dir)}:{i}: {line.strip()[:100]}")
            except Exception:
                pass
    return {
        "name": "No NEXT_PUBLIC_ secrets in frontend",
        "passed": len(findings) == 0,
        "details": findings if findings else "Clean"
    }

def scan_credential_urls():
    """Scan source files for URLs with embedded credentials."""
    project_root = os.path.join(os.path.dirname(__file__), '..')
    findings = []
    scan_dirs = ['backend', 'frontend', 'scripts']
    scan_extensions = {'.py', '.ts', '.tsx', '.js', '.yaml', '.yml'}
    for scan_dir in scan_dirs:
        dir_path = os.path.join(project_root, scan_dir)
        if not os.path.isdir(dir_path):
            continue
        for fname in os.listdir(dir_path):
            fpath = os.path.join(dir_path, fname)
            if not os.path.isfile(fpath):
                continue
            ext = os.path.splitext(fname)[1]
            if ext not in scan_extensions:
                continue
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    for pattern in CREDENTIAL_URL_PATTERNS:
                        if pattern.search(line):
                            findings.append(f"{scan_dir}/{fname}:{i}")
            except Exception:
                pass
    return {
        "name": "No hardcoded URLs with credentials",
        "passed": len(findings) == 0,
        "details": findings if findings else "Clean"
    }

def main():
    checks = [
        check_git_env_tracked(),
        check_gitignore_env(),
        scan_python_for_api_keys(),
        scan_frontend_next_public(),
        scan_credential_urls(),
    ]

    all_passed = all(c["passed"] for c in checks)
    report = {"checks": checks}

    os.makedirs(os.path.join(os.path.dirname(__file__), 'reports'), exist_ok=True)
    out_path = os.path.join(os.path.dirname(__file__), 'reports', 'security_check.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    for check in checks:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"[{status}] {check['name']}: {check['details']}")
    print(f"\nReport written to {out_path}")
    sys.exit(0 if all_passed else 1)

if __name__ == '__main__':
    main()
