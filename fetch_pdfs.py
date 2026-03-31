"""Download PDFs from the `url` column in references.csv.

Current scope: only attempts direct URLs already present in the parsed references.
For each URL:
- issue HTTP GET with stream and modest timeout
- if content-type hints PDF or URL endswith .pdf, save under downloads/
- record status in downloads_report.csv

Use: python3 fetch_pdfs.py
"""
from __future__ import annotations

import csv
import mimetypes
import re
from pathlib import Path
from typing import Iterable

import requests

BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "references.csv"
DOWNLOAD_DIR = BASE / "downloads"
REPORT_PATH = BASE / "downloads_report.csv"

HEADERS = {
    "User-Agent": "cascade-papers-downloader/1.0",
}


def looks_like_pdf(url: str, content_type: str | None) -> bool:
    if url.lower().endswith(".pdf"):
        return True
    if content_type and "pdf" in content_type.lower():
        return True
    return False


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    return name[:180]


def download(url: str, target: Path) -> tuple[bool, str]:
    try:
        with requests.get(url, headers=HEADERS, stream=True, timeout=20) as resp:
            ct = resp.headers.get("Content-Type", "")
            if resp.status_code != 200:
                return False, f"http {resp.status_code}"
            if not looks_like_pdf(url, ct):
                guessed_ext = mimetypes.guess_extension(ct.split(";")[0].strip()) if ct else None
                if guessed_ext and guessed_ext.lower() == ".pdf":
                    pass
                else:
                    return False, f"non-pdf content-type {ct or 'unknown'}"
            with target.open("wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True, "downloaded"
    except Exception as exc:  # pragma: no cover - network path
        return False, f"error {exc}"


def iter_rows() -> Iterable[dict]:
    if not CSV_PATH.exists():
        raise SystemExit("references.csv not found")
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        yield from reader


def main() -> None:
    DOWNLOAD_DIR.mkdir(exist_ok=True)
    report_rows = []
    for row in iter_rows():
        url = (row.get("url") or "").strip()
        if not url:
            report_rows.append({**row, "status": "skip:no_url", "file": ""})
            continue
        filename = sanitize_filename(row.get("title") or row.get("raw") or str(row.get("id")))
        target = DOWNLOAD_DIR / f"{row.get('id','')}_{filename}.pdf"
        ok, status = download(url, target)
        report_rows.append({**row, "status": status if ok else f"fail:{status}", "file": str(target) if ok else ""})

    if report_rows:
        fieldnames = list(report_rows[0].keys())
    else:
        fieldnames = []

    with REPORT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_rows)

    print(f"Processed {len(report_rows)} rows. Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
