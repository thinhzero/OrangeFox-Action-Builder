#!/usr/bin/env python3
"""Host-only diagnostic redaction and workflow wiring regressions."""

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "diagnostics", Path(__file__).with_name("collect-build-diagnostics.py"))
DIAGNOSTICS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DIAGNOSTICS)


class DiagnosticChecks(unittest.TestCase):
    def setUp(self):
        self.work = tempfile.TemporaryDirectory(prefix="thyme-diagnostics-test-")
        self.addCleanup(self.work.cleanup)
        self.root = Path(self.work.name)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_entire_soong_environment_line_omitted(self):
        text = "before\n2026/11/16 Environment: [UNKNOWN=private-value GITHUB_TOKEN=fixture]\nafter\n"
        self.assertEqual(DIAGNOSTICS.sanitize(text, {}),
                         "before\n[environment dump omitted]\nafter\n")

    def test_token_shapes_url_auth_and_environment_values_redacted(self):
        secrets = ("ghp_fixturePERSONAL123", "ghs_fixtureJOB123", "ghs_" + "a" * 373,
                   "ghs_fixture.Header-0_payload.signature-9", "ghu_fixtureUSER123",
                   "gho_fixtureOAUTH123", "ghr_fixtureREFRESH123",
                   "github_pat_fixturePAT123", "owner-password-fixture")
        text = " ".join(secrets) + " https://user:pass@example.invalid/repo.git"
        cleaned = DIAGNOSTICS.sanitize(text, {"GIT_PASSWORD": secrets[-1]})
        for secret in secrets:
            self.assertNotIn(secret, cleaned)
        self.assertNotIn("user:pass", cleaned)
        self.assertIn("https://[REDACTED]@example.invalid/repo.git", cleaned)

    def test_dot_separated_token_does_not_leave_credential_segments(self):
        text = 'token="ghs_fixture.Header-0_payload.signature-9"\n'
        self.assertEqual(DIAGNOSTICS.sanitize(text, {}), 'token="[REDACTED]"\n')

    def test_environment_value_longest_first_and_sensitive_names(self):
        values = {name: "fixture-value-" + name for name in
                  ("GH_TOKEN", "PASSWORD", "CLIENT_SECRET", "CREDENTIAL", "AUTHORIZATION", "PRIVATE_KEY")}
        text = " ".join(values.values())
        self.assertEqual(DIAGNOSTICS.sanitize(text, values), " ".join(["[REDACTED]"] * len(values)))
        self.assertEqual(DIAGNOSTICS.sanitize("fixture-secret-long", {
            "TOKEN": "fixture-secret", "PASSWORD": "fixture-secret-long"}), "[REDACTED]")

    def test_only_allowlisted_files_staged_and_json_preserved(self):
        self.write("build.log", "error: missing fixture\nghs_fixtureJOB123\n")
        self.write("source-defaults-report.json", json.dumps({"name": "ghp_fixturePAT123"}))
        self.write("OrangeFox/fox_12.1/out/error.log", "undefined module\n")
        for name in ("OrangeFox/fox_12.1/out/soong.log", "OrangeFox/fox_12.1/out/verbose.log.gz",
                     "fox_env.sh", "private-token"):
            self.write(name, "must not be copied")
        names = DIAGNOSTICS.collect(self.root, "12.1", {})
        self.assertEqual(names, ["build.log", "source-defaults-report.json",
                                 "OrangeFox/fox_12.1/out/error.log"])
        output = self.root / "build-diagnostics"
        self.assertEqual(json.loads((output / "source-defaults-report.json").read_text()),
                         {"name": "[REDACTED]"})
        self.assertEqual(len([p for p in output.rglob("*") if p.is_file()]), 3)
        self.assertIn("undefined module", (output / names[-1]).read_text())

    def test_missing_logs_supported(self):
        self.assertEqual(DIAGNOSTICS.collect(self.root, "12.1", {}), [])

    def test_11_branch_allowlist_and_checksum(self):
        self.write("OrangeFox/fox_11.0/out/error.log", "old branch error\n")
        self.write("OrangeFox/fox_12.1/out/error.log", "wrong branch\n")
        self.write("source-libraries-report.json", '{"candidate": "example"}\n')
        self.write("boot-test-release/SHA256SUMS", "0" * 64 + "  recovery.img\n")
        names = DIAGNOSTICS.collect(self.root, "11.0", {})
        self.assertEqual(names, ["source-libraries-report.json", "OrangeFox/fox_11.0/out/error.log",
                                 "boot-test-release/SHA256SUMS"])

    def test_invalid_utf8_replaced_without_copying_binary_raw(self):
        path = self.write("build.log", "")
        path.write_bytes(b"error: \xff ghs_fixture.Header.sig-9\n")
        DIAGNOSTICS.collect(self.root, "12.1", {})
        self.assertEqual((self.root / "build-diagnostics/build.log").read_text(),
                         "error: \ufffd [REDACTED]\n")

    def test_existing_staging_directory_not_reused(self):
        (self.root / "build-diagnostics").mkdir()
        with self.assertRaises(FileExistsError):
            DIAGNOSTICS.collect(self.root, "12.1", {})

    def test_symlink_file_rejected(self):
        source = self.write("private", "do not upload")
        (self.root / "build.log").symlink_to(source)
        with self.assertRaisesRegex(ValueError, "symlink"):
            DIAGNOSTICS.collect(self.root, "12.1", {})

    def test_symlink_directory_rejected(self):
        source = self.root / "elsewhere"
        source.mkdir()
        (self.root / "OrangeFox").symlink_to(source, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            DIAGNOSTICS.collect(self.root, "12.1", {})

    def test_broken_symlink_rejected(self):
        (self.root / "build.log").symlink_to(self.root / "absent")
        with self.assertRaisesRegex(ValueError, "symlink"):
            DIAGNOSTICS.collect(self.root, "12.1", {})

    def test_staging_symlink_not_reused(self):
        (self.root / "build-diagnostics").symlink_to(self.root / "absent")
        with self.assertRaises(FileExistsError):
            DIAGNOSTICS.collect(self.root, "12.1", {})

    def test_fifo_rejected_without_blocking(self):
        os.mkfifo(self.root / "build.log")
        with self.assertRaisesRegex(ValueError, "bounded"):
            DIAGNOSTICS.collect(self.root, "12.1", {})

    def test_size_limit_rejected(self):
        self.write("build.log", "oversized fixture")
        with patch.object(DIAGNOSTICS, "MAX_FILE_BYTES", 4), \
                self.assertRaisesRegex(ValueError, "bounded"):
            DIAGNOSTICS.collect(self.root, "12.1", {})

    def test_branch_cannot_traverse_paths(self):
        with self.assertRaisesRegex(ValueError, "branch"):
            DIAGNOSTICS.collect(self.root, "../../elsewhere", {})

    def test_workflow_scopes_token_and_uploads_staging_only(self):
        # Wiring guard only, not a YAML evaluator or GitHub permission sandbox.
        workflow = (Path(__file__).resolve().parents[1] /
                    ".github/workflows/OrangeFox-Compile.yml").read_text()
        self.assertNotIn("GITHUB_TOKEN:", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertIn("unset GITHUB_TOKEN GH_TOKEN", workflow)
        self.assertEqual(workflow.count("token: ${{ github.token }}"), 2)
        upload = workflow.split("    - name: Upload build diagnostics\n", 1)[1].split("    - name:", 1)[0]
        self.assertIn("path: build-diagnostics/", upload)
        self.assertIn("if: ${{ always() && steps.prepare-diagnostics.outcome == 'success' }}", upload)
        prepare = workflow.split("    - name: Prepare sanitized build diagnostics\n", 1)[1].split("    - name:", 1)[0]
        self.assertIn("id: prepare-diagnostics", prepare)
        self.assertNotIn("out/soong.log", upload)
        self.assertNotIn("out/verbose.log.gz", upload)


if __name__ == "__main__":
    unittest.main()
