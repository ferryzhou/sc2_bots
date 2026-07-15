"""Download replays from spawningtool.com by id, to grow the study set.

spawningtool exposes each replay at ``https://lotv.spawningtool.com/<id>/download/``.
Replay ids are roughly contiguous within an uploaded collection, so a range
around a known-good block pulls more games of similar provenance. Non-replay
responses (404 HTML) are skipped; existing files are not re-downloaded.

    python analysis/spawningtool_download.py <out_dir> <start_id> <end_id>

Respects HTTPS_PROXY (the agent proxy). Be polite: a short delay between
requests. Verify quality afterwards with a name/league check before trusting the
sample (see analysis/replay_quality.py).
"""
import os
import sys
import time
import urllib.request

BASE = "https://lotv.spawningtool.com/{}/download/"
UA = "Mozilla/5.0 (replay-study)"


def looks_like_replay(data: bytes) -> bool:
    # SC2Replay is an MPQ archive: it starts with the 'MPQ' magic (user-data
    # header 'MPQ\x1b' or archive header 'MPQ\x1a'). 404 pages are HTML.
    return len(data) > 2000 and data[:3] == b"MPQ"


def download(out_dir: str, start: int, end: int, delay: float = 0.3) -> None:
    os.makedirs(out_dir, exist_ok=True)
    got = skipped = failed = 0
    for rid in range(start, end + 1):
        dest = os.path.join(out_dir, f"pro_{rid}.SC2Replay")
        if os.path.exists(dest):
            skipped += 1
            continue
        try:
            req = urllib.request.Request(BASE.format(rid), headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
        except Exception:
            failed += 1
            continue
        if looks_like_replay(data):
            with open(dest, "wb") as f:
                f.write(data)
            got += 1
        else:
            failed += 1
        if (got + failed) % 25 == 0:
            print(f"  ... id={rid} got={got} skipped={skipped} failed={failed}",
                  flush=True)
        time.sleep(delay)
    print(f"done: downloaded {got}, skipped {skipped} existing, {failed} not-a-replay")


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    out_dir, start, end = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    download(out_dir, start, end)


if __name__ == "__main__":
    main()
