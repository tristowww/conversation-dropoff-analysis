"""Download the official public release at a pinned revision; no credentials."""
import argparse
import hashlib
import json
from pathlib import Path
import urllib.request

REVISION = 'c9e1ec1e6b093712b9c42235c7303ece647490e9'
BASE = 'https://huggingface.co/datasets/Anthropic/AnthropicInterviewer'
EXPECTED = {
    'workforce': '09ff307d42ebc8ed0b0ba25f41ffe2e50e9baa0b3c1ab4133ee528118817aab4',
    'creatives': 'd4e865b9959671990ceb51089c7494dbeed7560f9a623da873e6eb0f1b6506b4',
    'scientists': '338677e4a4ec17824cb5bfbc9242c8a37e7041157d34fb65e7e6fb58ea3f407a',
}

def download(destination):
    destination.mkdir(parents=True, exist_ok=True)
    manifest = {'dataset': 'Anthropic/AnthropicInterviewer', 'revision': REVISION, 'files': [],
                'data_license': 'CC-BY according to the dataset card; version is not stated there.',
                'card_url': BASE + '/blob/' + REVISION + '/README.md'}
    for cohort, expected in EXPECTED.items():
        url = f'{BASE}/resolve/{REVISION}/interview_transcripts/{cohort}_transcripts.csv'
        path = destination / f'{cohort}.csv'
        raw = path.read_bytes() if path.exists() else urllib.request.urlopen(url, timeout=60).read()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != expected:
            raise ValueError('Dataset checksum mismatch: ' + cohort)
        path.write_bytes(raw)
        manifest['files'].append({'cohort': cohort, 'sha256': digest, 'bytes': len(raw), 'url': url})
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print('Verified three public source files at revision ' + REVISION)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, default=Path('.local-data/anthropic'))
    download(p.parse_args().output)
