"""Resolve open-access PDFs for bibliography entries and download them.

Pipeline per reference:
1) If existing url looks like a PDF, try to download.
2) Extract DOI from raw text (or url) if present.
3) If no DOI, query Crossref by title (and year if available) to get best DOI guess.
4) Query Unpaywall for OA locations and pick a PDF URL.
5) Apply small publisher shortcuts when possible (e.g., MDPI / Royal Society).

Outputs:
- resolved_downloads.csv: per reference resolution details + download status
- downloads/: downloaded PDF files

Usage:
  python3 resolve_and_download.py --email davy.janssens@uhasselt.be

Notes:
- This makes many external HTTP requests. Expect some failures (rate limiting, paywalls, captchas).
- Focuses on OA downloads; it does not bypass paywalls.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import mimetypes
import re
import time
import urllib.parse
from pathlib import Path
from typing import Any, Iterable

import requests

BASE = Path(__file__).resolve().parent
CSV_PATH = BASE / "references.csv"
DOWNLOAD_DIR = BASE / "downloads"
DEFAULT_OUT_CSV = BASE / "resolved_downloads.csv"

HEADERS = {
    "User-Agent": "cascade-papers-downloader/1.0 (mailto: davy.janssens@uhasselt.be)",
    "Accept": "text/html,application/pdf,application/json;q=0.9,*/*;q=0.8",
}

DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[^\s\]\)\}" + '"' + r"'<>,;]+", re.IGNORECASE)
URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)


def _looks_like_scholar_block(html: str) -> bool:
    h = (html or "").lower()
    return (
        "unusual traffic" in h
        or "systems have detected unusual traffic" in h
        or "not a robot" in h
        or "/sorry/" in h
        or "recaptcha" in h
    )


def scholar_pdf_candidates(query: str) -> tuple[list[str], str]:
    """Attempt to fetch Scholar results page and extract direct PDF links.

    Returns (pdf_urls, info).
    """
    if not query:
        return [], "scholar:no_query"

    q = urllib.parse.quote_plus(query)
    url = f"https://scholar.google.com/scholar?q={q}"
    try:
        resp = http_get(url, stream=False, timeout=25)
        if resp.status_code != 200:
            return [], f"scholar_http_{resp.status_code}"
        html = resp.text or ""
        if _looks_like_scholar_block(html):
            return [], "scholar_blocked"

        # Heuristic extraction:
        # - look for any direct .pdf links
        # - prefer links that appear near '[PDF]'
        pdf_links = []
        for m in re.finditer(r'href="(https?://[^"]+)"', html, flags=re.IGNORECASE):
            link = m.group(1)
            if ".pdf" in link.lower():
                pdf_links.append(link)

        # De-dup
        seen = set()
        out = []
        for l in pdf_links:
            if l in seen:
                continue
            seen.add(l)
            out.append(l)
        return out[:5], "scholar_ok" if out else "scholar_no_pdf_links"
    except Exception as exc:  # pragma: no cover
        return [], f"scholar_error_{exc}"


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    return name[:180] if name else "file"


def sha8(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:8]


def extract_doi(text: str) -> str:
    m = DOI_PATTERN.search(text or "")
    return m.group(0).rstrip(".") if m else ""


def extract_first_url(text: str) -> str:
    m = URL_PATTERN.search(text or "")
    return m.group(0).rstrip(".,)") if m else ""


def looks_like_pdf(url: str, content_type: str | None) -> bool:
    if url.lower().endswith(".pdf"):
        return True
    if content_type and "pdf" in content_type.lower():
        return True
    return False


def http_get(url: str, *, stream: bool = False, timeout: int = 25) -> requests.Response:
    return requests.get(url, headers=HEADERS, stream=stream, timeout=timeout, allow_redirects=True)


def download_pdf(url: str, target: Path) -> tuple[bool, str, str]:
    """Returns ok, status, content_type."""
    try:
        with http_get(url, stream=True) as resp:
            ct = resp.headers.get("Content-Type", "")
            if resp.status_code != 200:
                return False, f"http {resp.status_code}", ct
            if not looks_like_pdf(url, ct):
                guessed_ext = mimetypes.guess_extension(ct.split(";")[0].strip()) if ct else None
                if not (guessed_ext and guessed_ext.lower() == ".pdf"):
                    return False, f"non-pdf content-type {ct or 'unknown'}", ct
            target.parent.mkdir(exist_ok=True)
            with target.open("wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True, "downloaded", ct
    except Exception as exc:  # pragma: no cover
        return False, f"error {exc}", ""


def crossref_lookup(title: str, year: str | None) -> tuple[str, str]:
    """Return (doi, score_info)."""
    if not title:
        return "", "no_title"
    params = {
        "query.bibliographic": title,
        "rows": 1,
    }
    # year filter is tricky; keep it lightweight
    try:
        r = requests.get("https://api.crossref.org/works", params=params, headers=HEADERS, timeout=25)
        if r.status_code != 200:
            return "", f"crossref_http_{r.status_code}"
        data = r.json()
        items = (data.get("message") or {}).get("items") or []
        if not items:
            return "", "crossref_no_items"
        doi = (items[0].get("DOI") or "").strip()
        score = str(items[0].get("score") or "")
        # Optional: crude year check (don’t reject hard)
        if year:
            issued = items[0].get("issued")
            if isinstance(issued, dict):
                parts = issued.get("date-parts")
                if isinstance(parts, list) and parts and isinstance(parts[0], list) and parts[0]:
                    cr_year = str(parts[0][0])
                    return doi, f"crossref_score_{score}_year_{cr_year}"
        return doi, f"crossref_score_{score}"
    except Exception as exc:  # pragma: no cover
        return "", f"crossref_error_{exc}"


def openalex_lookup(title: str, year: str | None) -> tuple[str, str, str]:
    """Return (doi, oa_url, info) via OpenAlex.

    OpenAlex can provide:
    - ids.doi (as https://doi.org/...)
    - primary_location.pdf_url / landing_page_url
    - best_oa_location.pdf_url
    """
    if not title:
        return "", "", "openalex:no_title"
    params = {
        "search": title,
        "per-page": 5,
    }
    try:
        r = requests.get("https://api.openalex.org/works", params=params, headers=HEADERS, timeout=25)
        if r.status_code != 200:
            return "", "", f"openalex_http_{r.status_code}"
        data = r.json()
        results = data.get("results") or []
        if not results:
            return "", "", "openalex_no_results"

        # Pick first result; lightly prefer year match if available
        chosen = results[0]
        if year:
            for cand in results:
                py = cand.get("publication_year")
                if py and str(py) == str(year).rstrip("abcdefghijklmnopqrstuvwxyz"):
                    chosen = cand
                    break

        ids = chosen.get("ids") or {}
        doi_url = (ids.get("doi") or "").strip()  # typically https://doi.org/...
        doi = ""
        if doi_url:
            doi = doi_url.replace("https://doi.org/", "").replace("http://doi.org/", "")

        oa_url = ""
        primary = chosen.get("primary_location") or {}
        best = chosen.get("best_oa_location") or {}

        for key in ("pdf_url",):
            oa_url = (primary.get(key) or "").strip()
            if oa_url:
                break
        if not oa_url:
            oa_url = (best.get("pdf_url") or "").strip()
        if not oa_url:
            oa_url = (primary.get("landing_page_url") or "").strip()
        if not oa_url:
            oa = chosen.get("open_access") or {}
            oa_url = (oa.get("oa_url") or "").strip()

        info = "openalex_ok"
        if chosen.get("openalex_id"):
            info += f";id={chosen.get('openalex_id')}"
        if chosen.get("publication_year"):
            info += f";year={chosen.get('publication_year')}"
        return doi, oa_url, info
    except Exception as exc:  # pragma: no cover
        return "", "", f"openalex_error_{exc}"


def unpaywall_lookup(doi: str, email: str) -> tuple[str, dict[str, Any] | None, str]:
    """Return (pdf_url, raw_json, info)."""
    if not doi:
        return "", None, "no_doi"
    url = f"https://api.unpaywall.org/v2/{doi}"
    try:
        r = requests.get(url, params={"email": email}, headers=HEADERS, timeout=25)
        if r.status_code != 200:
            return "", None, f"unpaywall_http_{r.status_code}"
        data = r.json()
        best = data.get("best_oa_location") or {}
        pdf = (best.get("url_for_pdf") or "").strip()
        if not pdf:
            # fallback: scan oa_locations
            for loc in data.get("oa_locations") or []:
                cand = (loc.get("url_for_pdf") or "").strip()
                if cand:
                    pdf = cand
                    break
        return pdf, data, "unpaywall_ok" if pdf else "unpaywall_no_pdf"
    except Exception as exc:  # pragma: no cover
        return "", None, f"unpaywall_error_{exc}"


def publisher_shortcuts(url: str, doi: str) -> list[str]:
    """Return candidate PDF URLs derived from known patterns."""
    cands: list[str] = []
    if url and "mdpi.com" in url:
        # MDPI articles typically have a /pdf endpoint.
        # Example: https://www.mdpi.com/1660-4601/15/12/2828 -> .../pdf
        base = url.split("?")[0].rstrip("/")
        if not base.endswith("/pdf"):
            cands.append(base + "/pdf")
    if doi and doi.lower().startswith("10.1098/"):
        # Royal Society: /doi/pdf/<doi>
        cands.append(f"https://royalsocietypublishing.org/doi/pdf/{doi}")
    return cands


def iter_rows() -> Iterable[dict[str, str]]:
    if not CSV_PATH.exists():
        raise SystemExit("references.csv not found")
    with CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield {k: (v or "") for k, v in row.items()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", required=True)
    ap.add_argument("--sleep", type=float, default=1.0, help="seconds between requests")
    ap.add_argument("--enable-openalex", action="store_true", help="use OpenAlex fallback for DOI/OA links")
    ap.add_argument("--enable-scholar", action="store_true", help="use Google Scholar fallback (may be blocked)")
    ap.add_argument("--scholar-sleep", type=float, default=6.0, help="seconds between Scholar requests")
    ap.add_argument("--log-every", type=int, default=10, help="print progress every N rows")
    ap.add_argument("--out", default=str(DEFAULT_OUT_CSV), help="output CSV path")
    ap.add_argument("--skip", type=int, default=0, help="skip first N rows (for batching)")
    ap.add_argument("--max", type=int, default=0, help="process at most N rows (0 = all)")
    args = ap.parse_args()

    DOWNLOAD_DIR.mkdir(exist_ok=True)

    out_rows: list[dict[str, Any]] = []

    for i, row in enumerate(iter_rows(), start=1):
        if args.skip and i <= args.skip:
            continue
        if args.max and i > args.max:
            break

        if args.log_every and i % args.log_every == 0:
            print(f"Progress: {i} rows processed...")

        raw = row.get("raw", "")
        title = row.get("title", "")
        year = row.get("year", "")
        existing_url = (row.get("url") or "").strip()

        doi = extract_doi(raw) or extract_doi(existing_url)
        resolved_doi = ""
        crossref_info = ""
        openalex_info = ""

        candidate_urls: list[str] = []
        if existing_url:
            candidate_urls.append(existing_url)

        # Try publisher shortcut if we have a URL early
        candidate_urls.extend(publisher_shortcuts(existing_url, doi))

        # If no DOI, try Crossref on title
        if not doi:
            doi, crossref_info = crossref_lookup(title, year or None)
            resolved_doi = doi
        else:
            resolved_doi = doi

        # OpenAlex fallback (helpful if Crossref fails, or to get OA link candidates)
        openalex_oa_url = ""
        if args.enable_openalex:
            if not resolved_doi or resolved_doi.strip() == "":
                oa_doi, oa_url, openalex_info = openalex_lookup(title, year or None)
                if oa_doi:
                    resolved_doi = oa_doi
                openalex_oa_url = oa_url
            else:
                # Even with DOI, OpenAlex may provide a direct PDF URL
                _oa_doi, oa_url, openalex_info = openalex_lookup(title, year or None)
                openalex_oa_url = oa_url

        if openalex_oa_url:
            candidate_urls.append(openalex_oa_url)

        # Add shortcut candidates derived from DOI
        candidate_urls.extend(publisher_shortcuts(existing_url, resolved_doi))

        unpaywall_pdf = ""
        unpaywall_info = ""
        if resolved_doi:
            unpaywall_pdf, _unpaywall_json, unpaywall_info = unpaywall_lookup(resolved_doi, args.email)
            if unpaywall_pdf:
                candidate_urls.append(unpaywall_pdf)

        # De-dup while preserving order
        seen = set()
        unique_urls = []
        for u in candidate_urls:
            u = (u or "").strip()
            if not u:
                continue
            if u in seen:
                continue
            seen.add(u)
            unique_urls.append(u)

        status = "unresolved"
        downloaded_file = ""
        used_url = ""
        used_ct = ""

        # Try to download from the first working candidate
        attempted_any = False
        if unique_urls:
            for cand in unique_urls:
                attempted_any = True
                used_url = cand
                fname_base = sanitize_filename(title) if title else sanitize_filename(raw)
                target = DOWNLOAD_DIR / f"{row.get('id','')}_{fname_base}_{sha8(cand)}.pdf"
                ok, st, ct = download_pdf(cand, target)
                used_ct = ct
                if ok:
                    status = "downloaded"
                    downloaded_file = str(target)
                    break
                status = f"fail:{st}"
                time.sleep(args.sleep)

        # Scholar fallback (only if nothing succeeded)
        scholar_info = ""
        if status != "downloaded" and args.enable_scholar:
            # Build query from title + year if available
            query = title.strip() if title else raw.strip()
            if year and year not in query:
                query = f"{query} {year}"
            pdf_cands, scholar_info = scholar_pdf_candidates(query)
            for cand in pdf_cands:
                attempted_any = True
                used_url = cand
                fname_base = sanitize_filename(title) if title else sanitize_filename(raw)
                target = DOWNLOAD_DIR / f"{row.get('id','')}_{fname_base}_{sha8(cand)}.pdf"
                ok, st, ct = download_pdf(cand, target)
                used_ct = ct
                if ok:
                    status = "downloaded"
                    downloaded_file = str(target)
                    break
                status = f"fail:{st}"
                time.sleep(args.scholar_sleep)
            if not pdf_cands and status != "downloaded" and not attempted_any:
                status = f"skip:scholar:{scholar_info}"

        if not attempted_any and status == "unresolved":
            status = "skip:no_candidates"

        out_rows.append(
            {
                **row,
                "doi": resolved_doi,
                "crossref_info": crossref_info,
                "unpaywall_info": unpaywall_info,
                "openalex_info": openalex_info,
                "scholar_info": scholar_info,
                "candidate_urls_json": json.dumps(unique_urls),
                "used_url": used_url,
                "used_content_type": used_ct,
                "download_status": status,
                "downloaded_file": downloaded_file,
            }
        )

        # Gentle pacing even if no download attempts
        time.sleep(args.sleep)

    if out_rows:
        fieldnames = list(out_rows[0].keys())
    else:
        fieldnames = []

    out_csv = Path(args.out)
    if not out_csv.is_absolute():
        out_csv = (BASE / out_csv).resolve()

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)

    print(f"Wrote {len(out_rows)} rows -> {out_csv}")


if __name__ == "__main__":
    main()
