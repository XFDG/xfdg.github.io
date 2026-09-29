"""Bounded HTTPS verification of published pages against local build bytes."""
from __future__ import annotations
import argparse
import hashlib
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://xfdg.github.io/'
PATHS = ('index.html', 'en/index.html', 'projects/iquest-q1.html',
         'en/projects/iquest-q1.html', 'opensource.html', 'en/opensource.html',
         'resume.html', 'en/resume.html', 'portfolio.css', 'script.js')


def verify(path: str) -> tuple[str, bool, str]:
    expected = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
    url = BASE + path + '?build=' + expected[:16]
    try:
        request = Request(url, headers={'User-Agent': 'Haoran-Portfolio-Release-Check/1.0', 'Cache-Control': 'no-cache'})
        with urlopen(request, timeout=12) as response:
            actual = hashlib.sha256(response.read()).hexdigest()
            status = response.status
        return path, status == 200 and actual == expected, f'HTTP {status}; content_match={actual == expected}'
    except (HTTPError, URLError, TimeoutError, OSError) as error:
        return path, False, str(error)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--timeout', type=int, default=240)
    args = parser.parse_args()
    deadline = time.monotonic() + args.timeout
    while True:
        with ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(verify, PATHS))
        for path, passed, detail in results:
            print(f'{"PASS" if passed else "WAIT"} {BASE}{path}: {detail}', flush=True)
        if all(passed for _, passed, _ in results):
            print('PASS: public Chinese/English pages and assets match this release', flush=True)
            return
        if time.monotonic() >= deadline:
            raise SystemExit('Public verification timed out. Check Pages build status; do not claim deployment success.')
        time.sleep(12)

if __name__ == '__main__':
    main()
