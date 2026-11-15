#!/usr/bin/env python3
"""Report literal Blueprint defaults without changing or evaluating the build."""

import argparse
import json
import os
from pathlib import Path
import re


TOKEN = re.compile(
    r'(?P<space>\s+)|(?P<comment>//[^\n]*|/\*.*?\*/)|'
    r'(?P<string>"(?:\\.|[^"\\])*")|(?P<word>[A-Za-z_][A-Za-z_0-9]*)|'
    r'(?P<other>.)', re.S)
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_CANDIDATES = 200
MAX_REFERENCES = 5
SKIP_DIRS = {".git", ".repo", "out"}


def literals(text):
    """Extract literal name properties and complete literal defaults lists only."""
    tokens = []
    line = 1
    for match in TOKEN.finditer(text):
        kind, value = match.lastgroup, match.group()
        if kind not in ("space", "comment"):
            tokens.append((kind, value, line))
        line += value.count("\n")
    names, references, dynamic = set(), [], 0
    for index, (kind, value, line) in enumerate(tokens):
        if kind != "word" or value not in ("name", "defaults"):
            continue
        tail = tokens[index + 1:index + 3]
        if len(tail) != 2 or tail[0][1] != ":":
            continue
        if value == "name":
            if tail[1][0] == "string":
                names.add(json.loads(tail[1][1]))
            continue
        end = index + 2
        if tokens[end][1] != "[":
            dynamic += 1
            continue
        values = []
        end += 1
        expect_string = True
        while end < len(tokens):
            token_kind, token, token_line = tokens[end]
            if token == "]":
                break
            if expect_string and token_kind == "string":
                values.append((json.loads(token), token_line))
                expect_string = False
            elif not expect_string and token == ",":
                expect_string = True
            else:
                break
            end += 1
        if (end < len(tokens) and tokens[end][1] == "]"
                and (end + 1 == len(tokens) or tokens[end + 1][1] in (",", "}"))):
            references.extend(values)
        else:
            dynamic += 1
    return names, references, dynamic


def audit(root):
    root = root.resolve()
    definitions, references, errors = set(), {}, []
    files, dynamic = 0, 0
    for directory, dirs, filenames in os.walk(root, followlinks=False):
        if {".find-ignore", ".out-dir"}.intersection(filenames):
            dirs[:] = []
            continue
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS
                         and not (Path(directory) / d).is_symlink())
        if "Android.bp" not in filenames:
            continue
        path = Path(directory) / "Android.bp"
        relative = path.relative_to(root).as_posix()
        try:
            if path.is_symlink():
                raise ValueError("symlink not inspected")
            if path.stat().st_size > MAX_FILE_BYTES:
                raise ValueError("file exceeds inspection limit")
            names, defaults, skipped = literals(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            errors.append(relative)
            continue
        files += 1
        dynamic += skipped
        definitions.update(names)
        for name, line in defaults:
            references.setdefault(name, []).append({"file": relative, "line": line})
    missing = sorted(references.keys() - definitions)
    return {
        "scope": "Advisory literal-source scan, NOT Soong evaluation or dependency closure",
        "limitations": ["Namespaces, visibility, types, variants and generated modules are not evaluated",
                        "Variable/concatenated defaults expressions and non-Android.bp includes are not evaluated",
                        "Literal name properties may overapproximate module definitions"],
        "files_scanned": files, "literal_names": len(definitions),
        "dynamic_defaults_skipped": dynamic, "unreadable_files": errors[:MAX_CANDIDATES],
        "unreadable_file_count": len(errors), "candidate_count": len(missing),
        "candidates": [{"name": name, "references": references[name][:MAX_REFERENCES],
                        "reference_count": len(references[name])}
                       for name in missing[:MAX_CANDIDATES]],
        "truncated": len(missing) > MAX_CANDIDATES,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if not args.source_root.is_dir():
        parser.error("source root must be a directory")
    report = audit(args.source_root)
    args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(report["scope"])
    print(f"Scanned {report['files_scanned']} Android.bp files; "
          f"{report['candidate_count']} literal defaults candidates without literal definitions")
    for candidate in report["candidates"]:
        ref = candidate["references"][0]
        print(f"CANDIDATE {candidate['name']!r}: {ref['file']}:{ref['line']}")
    print("Build configuration and source files were not modified; strict Soong checks still apply.")


if __name__ == "__main__":
    main()
