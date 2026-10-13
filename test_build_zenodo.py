"""Small synthetic fixtures: no real run data is modified or packaged."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import build_zenodo as b


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        self.root.mkdir()
        for name in ['README.md', 'OsmoFlux_analysis.ipynb', 'simulate.ipynb', 'requirements.txt']:
            (self.root / name).write_text('fixture\n')
        notebook = {'cells': [{'cell_type': 'code', 'source': ['print(1)\n']}]}
        (self.root / 'OsmoFlux_analysis.ipynb').write_text(json.dumps(notebook))
        self.run = self.root / 'runs/REPRO/test_run'
        self.out = self.run / 'derived_analysis'
        (self.out / 'figures').mkdir(parents=True)
        (self.run / 'input.csv').write_text('x\n1\n')
        code_hash = hashlib.sha256(json.dumps(['print(1)\n'], ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
        inputs = {'runs/REPRO/test_run/input.csv': b.digest(self.run / 'input.csv')}
        (self.out / 'INPUT_MANIFEST.json').write_bytes(b.encoded({'run_id': 'test_run', 'inputs_sha256': inputs,
            'input_set_sha256': hashlib.sha256(b.encoded(inputs)).hexdigest(), 'analysis_code_sha256': code_hash}))
        (self.out / 'VERIFICATION.json').write_bytes(b.encoded({'run_id': 'test_run', 'status': 'ANALYSIS_COMPLETE', 'paper_regression': 'NOT_RUN'}))
        figures = [f'figures/Fig{i:02}_fixture.png' for i in range(1, 4)] + ['figures/FigS1_fixture.png']
        for figure in figures:
            (self.out / figure).write_bytes(('image fixture ' + figure).encode())
        # Paper files exist locally, but must not be read or packaged.
        paper = self.root / 'archive/paper/private.docx'
        paper.parent.mkdir(parents=True)
        paper.write_bytes(b'private manuscript')
        self.config_path = 'release-test.json'
        self.config = {'schema': 'osmoflux-release-config-2', 'deposit_scope': 'data-and-code',
            'code_files': ['README.md', 'OsmoFlux_analysis.ipynb', 'simulate.ipynb', 'requirements.txt'],
            'reproduction': {'python': '3.12', 'analysis_notebook': 'OsmoFlux_analysis.ipynb',
                            'simulation_notebook': 'simulate.ipynb', 'requirements': 'requirements.txt'},
            'required_figures': figures}
        (self.root / self.config_path).write_bytes(b.encoded(self.config))
        outputs = {p.relative_to(self.out).as_posix(): b.digest(p) for p in self.out.rglob('*') if p.is_file()}
        (self.out / 'OUTPUT_MANIFEST.json').write_bytes(b.encoded({'files_sha256': outputs}))
        self.git = {'commit': 'a' * 40, 'origin': 'https://example.invalid/repo.git', 'working_tree_changes': []}
        self.mock = patch.object(b, 'provenance', return_value=self.git)
        self.mock.start()
        self.addCleanup(self.mock.stop)

    def proposal(self):
        target = Path(self.temp.name) / 'proposal'
        b.propose(self.root, 'test_run', self.config_path, target)
        p = target / 'release-manifest.proposed.json'
        return p, b.digest(p)

    def test_end_to_end_identical_builds_and_reproduction_paths(self):
        p, h = self.proposal()
        b.build(self.root, p, h)
        a = self.run / 'release/first-build'
        (self.run / 'zenodo').rename(a)
        # A prior package under release/ must not affect the next build.
        b.build(self.root, p, h)
        c = self.run / 'zenodo'
        self.assertEqual({p.name: b.digest(p) for p in a.iterdir()}, {p.name: b.digest(p) for p in c.iterdir()})
        self.assertIn('Python 3.12', (a / 'README.md').read_text())
        self.assertEqual({p.name for p in c.iterdir()}, {'code.zip', 'run-data.zip', 'analysis.zip', 'README.md', 'release-manifest.json', 'SHA256SUMS.txt'})
        with zipfile.ZipFile(c / 'run-data.zip') as z:
            self.assertFalse(any('/zenodo/' in n or '/release/' in n or n.endswith('.docx') for n in z.namelist()))
        with zipfile.ZipFile(a / 'code.zip') as z:
            self.assertIn('osmoflux/release-test.json', z.namelist())
        with zipfile.ZipFile(a / 'run-data.zip') as z:
            self.assertIn('osmoflux/runs/REPRO/test_run/input.csv', z.namelist())
        with self.assertRaises(ValueError):
            b.build(self.root, p, h)

    def test_tamper_and_new_file_rejected(self):
        p, h = self.proposal()
        m = b.load_manifest(p, h)
        (self.run / 'new.csv').write_text('extra')
        with self.assertRaisesRegex(ValueError, 'Inventory changed'):
            b.verify(self.root, m)
        (self.run / 'new.csv').unlink()
        (self.run / 'input.csv').write_text('x\n2\n')
        with self.assertRaisesRegex(ValueError, 'File changed'):
            b.verify(self.root, m)
        with self.assertRaisesRegex(ValueError, 'fingerprint'):
            b.load_manifest(p, '0' * 64)

    def test_reserved_approval_record_excluded_and_path_safety(self):
        before = b.inventory(self.root, 'test_run', self.config, self.config_path)
        (self.run / 'release').mkdir()
        (self.run / 'release/approved.json').write_text('{}')
        self.assertEqual(before, b.inventory(self.root, 'test_run', self.config, self.config_path))
        for path in ['../outside', '/absolute', 'a/../b', 'a\\b']:
            with self.assertRaises(ValueError):
                b.safe_path(self.root, path)
        (self.run / 'link').symlink_to(self.root / 'README.md')
        with self.assertRaisesRegex(ValueError, 'Symlink'):
            b.inventory(self.root, 'test_run', self.config, self.config_path)

    def test_dirty_checkout_blocks_release(self):
        self.git['working_tree_changes'] = [' M README.md']
        p, h = self.proposal()
        m = b.load_manifest(p, h)
        self.assertEqual(len(m['release_blockers']), 1)
        with self.assertRaisesRegex(ValueError, 'not release-ready'):
            b.verify(self.root, m)

    def test_papers_not_required_or_included(self):
        p, h = self.proposal()
        m = b.load_manifest(p, h)
        self.assertFalse(any(r['path'].endswith('.docx') or r['group'] == 'paper' for r in m['files']))
        (self.root / 'archive/paper/private.docx').unlink()
        b.verify(self.root, m)

    def test_upload_folder_never_changes_inventory(self):
        before = b.inventory(self.root, 'test_run', self.config, self.config_path)
        (self.run / 'zenodo').mkdir()
        (self.run / 'zenodo/old.zip').write_bytes(b'old upload')
        self.assertEqual(before, b.inventory(self.root, 'test_run', self.config, self.config_path))

    def test_code_list_cannot_include_manuscript(self):
        self.config['code_files'].append('archive/paper/private.docx')
        (self.root / self.config_path).write_bytes(b.encoded(self.config))
        with self.assertRaisesRegex(ValueError, 'paper documents'):
            b.load_config(self.root, self.config_path)

    def test_missing_required_figure_rejected(self):
        (self.out / self.config['required_figures'][0]).unlink()
        with self.assertRaisesRegex(ValueError, 'Missing required figure'):
            b.figure_checks(self.root, 'test_run', self.config)

    def test_changed_configuration_is_rejected(self):
        p, h = self.proposal()
        self.config['reproduction']['python'] = '3.13'
        (self.root / self.config_path).write_bytes(b.encoded(self.config))
        with self.assertRaisesRegex(ValueError, 'configuration changed'):
            b.verify(self.root, b.load_manifest(p, h))

    def test_unsafe_configuration_path_is_rejected(self):
        self.config['code_files'].append('../outside')
        (self.root / self.config_path).write_bytes(b.encoded(self.config))
        with self.assertRaisesRegex(ValueError, 'Unsafe relative path'):
            b.load_config(self.root, self.config_path)

    def test_archive_rechecks_content_while_writing(self):
        r = {'path': 'README.md', 'sha256': '0' * 64, 'bytes': 8}
        with self.assertRaisesRegex(ValueError, 'during archive creation'):
            b.write_archive(self.root, [r], Path(self.temp.name) / 'bad.zip')


if __name__ == '__main__':
    unittest.main()
