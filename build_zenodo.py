#!/usr/bin/env python3
"""Propose, verify and build a local, manifest-pinned Zenodo release (stdlib only)."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tempfile
import zipfile

SCHEMA = 'osmoflux-release-3'
GROUPS = ('code', 'run-data', 'analysis')
RESERVED_RUN_DIRS = {'release', 'zenodo'}
EXCLUDED_NAMES = {'.DS_Store', '.ipynb_checkpoints', '__pycache__'}


def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False) + '\n').encode()


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def safe_path(root, relative):
    p = PurePosixPath(relative)
    if not relative or p.is_absolute() or '..' in p.parts or '\\' in relative or str(p) != relative:
        raise ValueError(f'Unsafe relative path: {relative}')
    current = root
    for part in p.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f'Symlink not permitted: {relative}')
    if not current.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Path escapes project: {relative}')
    return current


def load_config(root, relative):
    config = json.loads(safe_path(root, relative).read_text())
    if config.get('schema') != 'osmoflux-release-config-2':
        raise ValueError('Unsupported release configuration schema.')
    if config.get('deposit_scope') != 'data-and-code' or 'papers' in config:
        raise ValueError('Configuration must describe a data-and-code deposit without papers.')
    code = config['code_files']
    if not code or len(set(code)) != len(code):
        raise ValueError('Code files must be a nonempty, unique list.')
    for name in code:
        safe_path(root, name)
        if name.startswith(('archive/', 'runs/', 'runs_dev/')) or Path(name).suffix.lower() in {'.docx', '.doc', '.pdf'}:
            raise ValueError('Code inventory cannot include archives, run files or paper documents.')
    reproduction = config['reproduction']
    for key in ['analysis_notebook', 'simulation_notebook', 'requirements']:
        if reproduction[key] not in code:
            raise ValueError(f'Reproduction file missing from code_files: {key}')
    if not re.fullmatch(r'\d+\.\d+(?:\.\d+)?', reproduction['python']):
        raise ValueError('Python version must be major.minor or major.minor.patch.')
    figures = config['required_figures']
    if not figures or len(set(figures)) != len(figures):
        raise ValueError('Required figures must be a nonempty, unique list.')
    for figure in figures:
        safe_path(root, figure)
        if not figure.startswith('figures/') or not figure.endswith('.png'):
            raise ValueError('Figures must be explicit PNG paths under figures/.')
    return config


def run_path(run_id):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', run_id):
        raise ValueError('Run ID must be a single directory name.')
    return f'runs/REPRO/{run_id}'


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def provenance(root):
    return {'commit': git(root, 'rev-parse', 'HEAD'),
            'origin': git(root, 'remote', 'get-url', 'origin'),
            'working_tree_changes': git(root, 'status', '--porcelain', '--untracked-files=all').splitlines()}


def inventory(root, run_id, config, config_path):
    """Full selected run, with generated analysis separated; no other runs or caches."""
    result = {name: 'code' for name in [*config['code_files'], config_path]}
    base = safe_path(root, run_path(run_id))
    if not base.is_dir():
        raise ValueError(f'Missing run: {base}')
    for directory, dirs, files in os.walk(base, followlinks=False):
        here = Path(directory)
        # Approval records and upload archives are outputs, never scientific inputs.
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDED_NAMES and not (here == base and d in RESERVED_RUN_DIRS))
        for d in dirs:
            if (here / d).is_symlink():
                raise ValueError(f'Symlink in run: {here / d}')
        for name in sorted(files):
            if name in EXCLUDED_NAMES:
                continue
            p = here / name
            if p.suffix.lower() in {'.docx', '.doc'}:
                raise ValueError(f'Unexpected document in data inventory: {p}')
            rel = p.relative_to(root).as_posix()
            safe_path(root, rel)
            result[rel] = 'analysis' if p.relative_to(base).parts[0] == 'derived_analysis' else 'run-data'
    return result


def analysis_checks(root, run_id, config):
    base = safe_path(root, run_path(run_id)) / 'derived_analysis'
    im = json.loads((base / 'INPUT_MANIFEST.json').read_text())
    om = json.loads((base / 'OUTPUT_MANIFEST.json').read_text())
    v = json.loads((base / 'VERIFICATION.json').read_text())
    if im['run_id'] != run_id or v['run_id'] != run_id or v['status'] != 'ANALYSIS_COMPLETE':
        raise ValueError('Analysis is incomplete or belongs to another run.')
    for rel, expected in im['inputs_sha256'].items():
        p = safe_path(root, rel)
        if not p.is_relative_to(safe_path(root, run_path(run_id))) or p.is_relative_to(base) or any(p.is_relative_to(base.parent / d) for d in RESERVED_RUN_DIRS):
            raise ValueError(f'Unexpected analysis input: {rel}')
        if digest(p) != expected:
            raise ValueError(f'Analysis input changed: {rel}')
    for rel, expected in om['files_sha256'].items():
        if digest(safe_path(base, rel)) != expected:
            raise ValueError(f'Analysis output changed: {rel}')
    n = json.loads(safe_path(root, config['reproduction']['analysis_notebook']).read_text())
    code = [''.join(c['source']) for c in n['cells'] if c['cell_type'] == 'code']
    h = hashlib.sha256(json.dumps(code, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
    if h != im['analysis_code_sha256']:
        raise ValueError('Notebook code differs from the executed analysis.')
    return {'input_set_sha256': im['input_set_sha256'], 'analysis_code_sha256': h,
            'paper_regression': v['paper_regression'], 'input_files': len(im['inputs_sha256'])}


def figure_checks(root, run_id, config):
    """Require analysis exports; paper documents are not release inputs."""
    base = safe_path(root, run_path(run_id)) / 'derived_analysis'
    rows = []
    for relative in config['required_figures']:
        p = safe_path(base, relative)
        if not p.is_file() or not p.stat().st_size:
            raise ValueError(f'Missing required figure: {relative}')
        rows.append({'figure': relative, 'sha256': digest(p)})
    return rows


def propose(root, run_id, config_path, destination):
    if destination.exists():
        raise ValueError('Proposal directory already exists; choose a new --out directory.')
    config = load_config(root, config_path)
    analyses = analysis_checks(root, run_id, config)
    sources = inventory(root, run_id, config, config_path)
    records = []
    for i, (rel, group) in enumerate(sorted(sources.items()), 1):
        p = safe_path(root, rel)
        records.append({'path': rel, 'group': group, 'bytes': p.stat().st_size, 'sha256': digest(p)})
        if i % 10000 == 0:
            print(f'Inventoried {i:,} files', flush=True)
    g = provenance(root)
    figures = figure_checks(root, run_id, config)
    blockers = []
    if g['working_tree_changes']:
        blockers.append('Commit the intended code changes, then generate a fresh proposal from a clean checkout.')
    manifest = {'schema': SCHEMA, 'run_id': run_id, 'git': g, 'analysis': analyses,
                'configuration': {'path': config_path, 'sha256': digest(safe_path(root, config_path)), 'content': config}, 'files': records, 'figure_checks': figures, 'release_blockers': blockers,
                'exclusions': ['Other runs and _grid_cache', 'Selected run release/ and zenodo/ (approval records and package outputs)', 'Manuscript and supplement documents',
                               '.DS_Store, .ipynb_checkpoints, __pycache__'],
                'archive_format': 'ZIP_STORED; sorted paths; fixed 1980 timestamp; regular files mode 0644'}
    destination.mkdir(parents=True)
    path = destination / 'release-manifest.proposed.json'
    path.write_bytes(encoded(manifest))
    fingerprint = digest(path)
    (destination / 'release-manifest.proposed.sha256').write_text(f'{fingerprint}  {path.name}\n')
    lines = [f'# Proposed release: {run_id}', '', 'This is an inventory for review, not an approved release.', '',
             f'Git commit currently checked out: `{g["commit"]}`', f'Manifest SHA-256: `{fingerprint}`', '',
             '| Archive group | Files | Source bytes |', '|---|---:|---:|']
    for group in GROUPS:
        subset = [r for r in records if r['group'] == group]
        lines.append(f'| {group} | {len(subset):,} | {sum(r["bytes"] for r in subset):,} |')
    lines += ['', 'Archives are uncompressed for deterministic bytes across compression-library versions.',
              'ZIP headers add a small amount to these source sizes.', '', '## Before approval', '']
    lines += ['- ' + b for b in blockers] or ['- No automated release blockers. Review and approve the inventory.']
    lines += ['', 'No upload files have been built. No manifest has been frozen or saved inside the run.',
              'The analysis regression flag records whether manuscript-value tests were requested; it is not a claim of experimental validation.']
    (destination / 'REVIEW.md').write_text('\n'.join(lines) + '\n')
    print(f'Proposal: {path}\nManifest SHA-256: {fingerprint}\nRelease blockers: {len(blockers)}')


def load_manifest(path, expected):
    if digest(path) != expected:
        raise ValueError('Manifest fingerprint does not match --manifest-sha256.')
    m = json.loads(path.read_text())
    if m.get('schema') != SCHEMA:
        raise ValueError('Unsupported manifest schema.')
    return m


def verify(root, m):
    if m['release_blockers'] or m['git']['working_tree_changes']:
        raise ValueError('This proposal is not release-ready. Resolve REVIEW.md items and propose again.')
    g = provenance(root)
    if g != m['git']:
        raise ValueError('Git commit, origin or working-tree state differs from the manifest.')
    cfg = m['configuration']
    config = load_config(root, cfg['path'])
    if config != cfg['content'] or digest(safe_path(root, cfg['path'])) != cfg['sha256']:
        raise ValueError('Release configuration changed.')
    actual = inventory(root, m['run_id'], config, cfg['path'])
    records = m['files']
    if len({r['path'] for r in records}) != len(records):
        raise ValueError('Duplicate manifest paths.')
    if actual != {r['path']: r['group'] for r in records}:
        raise ValueError('Inventory changed: files added, removed or regrouped.')
    for r in records:
        p = safe_path(root, r['path'])
        if p.stat().st_size != r['bytes'] or digest(p) != r['sha256']:
            raise ValueError(f'File changed: {r["path"]}')
    if analysis_checks(root, m['run_id'], config) != m['analysis']:
        raise ValueError('Analysis provenance differs.')
    if figure_checks(root, m['run_id'], config) != m['figure_checks']:
        raise ValueError('Required analysis figures differ.')


def write_archive(root, records, destination):
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_STORED, allowZip64=True) as z:
        for r in sorted(records, key=lambda x: x['path']):
            info = zipfile.ZipInfo('osmoflux/' + r['path'], date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            h = hashlib.sha256()
            size = 0
            with safe_path(root, r['path']).open('rb') as src, z.open(info, 'w', force_zip64=True) as dst:
                for chunk in iter(lambda: src.read(1024 * 1024), b''):
                    h.update(chunk); size += len(chunk); dst.write(chunk)
            if size != r['bytes'] or h.hexdigest() != r['sha256']:
                raise ValueError(f'File changed during archive creation: {r["path"]}')


def build(root, manifest_path, expected):
    m = load_manifest(manifest_path, expected)
    verify(root, m)
    base = safe_path(root, run_path(m['run_id']))
    destination = safe_path(root, run_path(m['run_id']) + '/zenodo')
    release = safe_path(root, run_path(m['run_id']) + '/release')
    if destination.exists() and (not destination.is_dir() or any(destination.iterdir())):
        raise ValueError('Upload directory must be absent or empty; existing packages are never overwritten.')
    release.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.zenodo-build-', dir=release) as temp:
        stage = Path(temp)
        for group in GROUPS:
            write_archive(root, [r for r in m['files'] if r['group'] == group], stage / (group + '.zip'))
        shutil.copyfile(manifest_path, stage / 'release-manifest.json')
        reproduction = m['configuration']['content']['reproduction']
        readme = f'''# OsmoFlux reproducibility release

Run ID: {m['run_id']}
Git commit: {m['git']['commit']}
Repository: {m['git']['origin']}
Release manifest SHA-256: {expected}

## Reproduce the figures

1. Verify SHA256SUMS.txt against the downloaded files.
2. Extract code.zip, run-data.zip and analysis.zip into the same directory.
   All archives share an osmoflux/ root; retain their relative paths.
3. Create a Python {reproduction['python']} environment and install {reproduction['requirements']}.
4. In osmoflux/, open {reproduction['analysis_notebook']}, select that environment,
   restart the kernel and run all cells. The selected run ID must be {m['run_id']}.
5. Outputs are regenerated in runs/REPRO/{m['run_id']}/derived_analysis/.
   The archived outputs provide the release reference. Only derived_analysis/
   may be removed for a clean analysis rerun; retain uppercase ANALYSIS/.

The analysis reads saved simulation results; it does not rerun simulations.
{reproduction['simulation_notebook']} contains the simulation workflow and embedded source.
See the project README before launching a fresh simulation run.

The manifest hashes every included file. Original inputs, generated analysis,
and code are separate groups. Manuscript and supplement documents are excluded.
This data/code deposit has its own DOI; link it to the separate journal article
DOI when available. The manuscript is not needed to reproduce the analysis. Historical absolute paths inside simulation
receipts remain provenance; the analysis discovers its project root at runtime.
The MIT license applies to code; consult source attribution for benchmark data.
This package does not imply a reserved or published Zenodo DOI.
'''
        (stage / 'README.md').write_text(readme)
        files = sorted(stage.iterdir())
        (stage / 'SHA256SUMS.txt').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in files))
        # Validate archive CRCs and paths after writing, before exposing upload files.
        for p in stage.glob('*.zip'):
            with zipfile.ZipFile(p) as z:
                if z.testzip() is not None:
                    raise ValueError(f'Archive integrity failure: {p.name}')
        if destination.exists():
            destination.rmdir()  # Empty directory only; no user files are deleted.
        stage.rename(destination)
    print(f'Upload files ready: {destination}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parent)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('propose', help='Read and hash files; write a review inventory only.')
    p.add_argument('--run-id', required=True)
    p.add_argument('--config', required=True, help='Project-relative release configuration JSON.')
    p.add_argument('--out', type=Path, required=True, help='New proposal directory, outside the selected run.')
    for name in ('verify', 'build'):
        p = sub.add_parser(name)
        p.add_argument('--manifest', type=Path, required=True)
        p.add_argument('--manifest-sha256', required=True)
    a = parser.parse_args()
    root = a.project.resolve()
    try:
        if a.command == 'propose':
            destination = a.out.resolve()
            if destination.is_relative_to(safe_path(root, run_path(a.run_id))):
                raise ValueError('Write proposals outside the run; save only the approved manifest inside release/.')
            propose(root, a.run_id, a.config, destination)
        elif a.command == 'verify':
            verify(root, load_manifest(a.manifest, a.manifest_sha256)); print('All release files verified.')
        else:
            build(root, a.manifest, a.manifest_sha256)
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError, zipfile.BadZipFile) as e:
        parser.exit(1, f'ERROR: {e}\n')


if __name__ == '__main__':
    main()
