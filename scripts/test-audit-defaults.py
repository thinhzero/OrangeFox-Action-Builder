#!/usr/bin/env python3
"""Regression tests for the advisory source scan; no Android checkout needed."""

import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest


sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location("audit", Path(__file__).with_name("audit-defaults.py"))
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class LiteralTests(unittest.TestCase):
    def test_literals(self):
        names, refs, dynamic = AUDIT.literals('cc_defaults { name: "base" }\n'
                                            'cc_library { defaults: ["base", "absent",], }')
        self.assertEqual(names, {"base"})
        self.assertEqual(refs, [("base", 2), ("absent", 2)])
        self.assertEqual(dynamic, 0)

    def test_comments_and_strings(self):
        text = '// name: "fake"\n/* defaults: ["fake"] */\n'
        text += 'cc_defaults { name: "real", note: "defaults: [\\\"fake\\\"]", }'
        self.assertEqual(AUDIT.literals(text), ({"real"}, [], 0))

    def test_dynamic_expressions_not_reported(self):
        for expression in ('variable', '["partial"] + variable', '["partial", variable]',
                           'variable + ["partial"]'):
            with self.subTest(expression=expression):
                self.assertEqual(AUDIT.literals('cc_library { defaults: ' + expression + ', }'),
                                 (set(), [], 1))

    def test_empty_list(self):
        self.assertEqual(AUDIT.literals('cc_library { defaults: [], }'), (set(), [], 0))

    def test_malformed_list_not_reported(self):
        self.assertEqual(AUDIT.literals('cc_library { defaults: ["a" "b"], }'),
                         (set(), [], 1))

    def test_line_numbers(self):
        self.assertEqual(AUDIT.literals('/*\ncomment\n*/\ndefaults: [\n"absent",\n],')[1],
                         [("absent", 5)])


class TreeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, path, text):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text)
        return file

    def test_cross_file_and_read_only(self):
        first = self.write('a/Android.bp', 'cc_library { defaults: ["base", "absent"], }')
        self.write('b/Android.bp', 'cc_defaults { name: "base", }')
        before = first.read_bytes()
        report = AUDIT.audit(self.root)
        self.assertEqual(report['candidate_count'], 1)
        self.assertEqual(report['candidates'][0]['name'], 'absent')
        self.assertEqual(first.read_bytes(), before)

    def test_skip_generated_and_marked_trees(self):
        for directory in ('.git', '.repo', 'out', 'ignored', 'generated'):
            self.write(directory + '/Android.bp', 'defaults: ["excluded"],')
        self.write('ignored/.find-ignore', '')
        self.write('generated/.out-dir', '')
        self.assertEqual(AUDIT.audit(self.root)['files_scanned'], 0)

    def test_symlink_directory_not_followed(self):
        self.write('out/Android.bp', 'defaults: ["excluded"],')
        (self.root / 'link').symlink_to(self.root / 'out', target_is_directory=True)
        self.assertEqual(AUDIT.audit(self.root)['files_scanned'], 0)

    def test_symlink_file_not_read(self):
        source = self.write('out/source', 'defaults: ["excluded"],')
        (self.root / 'Android.bp').symlink_to(source)
        report = AUDIT.audit(self.root)
        self.assertEqual(report['files_scanned'], 0)
        self.assertEqual(report['unreadable_file_count'], 1)

    def test_bounded_candidates(self):
        text = 'defaults: [' + ','.join(f'"missing{i:04}"' for i in range(250)) + '],'
        self.write('Android.bp', text)
        report = AUDIT.audit(self.root)
        self.assertEqual(report['candidate_count'], 250)
        self.assertEqual(len(report['candidates']), AUDIT.MAX_CANDIDATES)
        self.assertTrue(report['truncated'])

    def test_bounded_references(self):
        self.write('Android.bp', 'defaults: ["absent"],\n' * 10)
        candidate = AUDIT.audit(self.root)['candidates'][0]
        self.assertEqual(candidate['reference_count'], 10)
        self.assertEqual(len(candidate['references']), AUDIT.MAX_REFERENCES)

    def test_unreadable_input_is_advisory(self):
        self.write('Android.bp', '').write_bytes(b'\xff')
        self.assertEqual(AUDIT.audit(self.root)['unreadable_file_count'], 1)


if __name__ == "__main__":
    unittest.main()
