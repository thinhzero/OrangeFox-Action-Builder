#!/usr/bin/env python3
"""Stage a small, sanitized diagnostic allowlist; never copy raw environment logs."""

import argparse
import json
import os
from pathlib import Path
import re


MAX_FILE_BYTES = 32 * 1024 * 1024
SENSITIVE_NAME = re.compile(r"TOKEN|PASSWORD|SECRET|CREDENTIAL|AUTHORIZATION|PRIVATE_KEY", re.I)
# Installation tokens can contain dot-separated/base64url segments as well as
# alphanumerics. Matching only the prefix would leave most of the token exposed.
GITHUB_TOKEN = re.compile(r"\b(?:gh[pousr]_|github_pat_)[A-Za-z0-9_.-]+")
URL_CREDENTIALS = re.compile(r"(https?://)[^/\s@]+@", re.I)


def sanitize(text, environment):
    # Soong's Environment line is unbounded and may include arbitrary secrets.
    text = "".join("[environment dump omitted]\n" if "Environment: [" in line else line
                   for line in text.splitlines(keepends=True))
    values = {value for name, value in environment.items()
              if SENSITIVE_NAME.search(name) and len(value) >= 8}
    for value in sorted(values, key=len, reverse=True):
        text = text.replace(value, "[REDACTED]")
    text = GITHUB_TOKEN.sub("[REDACTED]", text)
    return URL_CREDENTIALS.sub(r"\1[REDACTED]@", text)


def collect(workspace, branch, environment):
    if branch not in ("11.0", "12.1"):
        raise ValueError("Unsupported manifest branch")
    workspace = workspace.resolve()
    output = workspace / "build-diagnostics"
    # A new staging directory prevents publishing stale or user-supplied files.
    output.mkdir()
    names = (
        "build.log", "source-defaults-report.json", "source-libraries-report.json",
        f"OrangeFox/fox_{branch}/out/error.log", "boot-test-release/SHA256SUMS",
    )
    collected = []
    for name in names:
        source = workspace / name
        for component in (source, *source.parents):
            if component == workspace:
                break
            if component.is_symlink():
                raise ValueError("Refusing a symlink in diagnostic inputs")
        if not source.exists():
            continue
        if not source.is_file() or source.stat().st_size > MAX_FILE_BYTES:
            raise ValueError("Diagnostic input is not a bounded regular file")
        with source.open("rb") as stream:
            data = stream.read(MAX_FILE_BYTES + 1)
        if len(data) > MAX_FILE_BYTES:
            raise ValueError("Diagnostic input is not a bounded regular file")
        text = sanitize(data.decode("utf-8", errors="replace"), environment)
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        collected.append(name)
    return collected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--manifest-branch", required=True)
    args = parser.parse_args()
    files = collect(args.workspace, args.manifest_branch, os.environ)
    print(json.dumps({"sanitized_diagnostic_files": files}))


if __name__ == "__main__":
    main()
