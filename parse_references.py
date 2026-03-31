"""Utility to parse references.txt into a structured CSV.

Fields extracted:
- id: running number
- raw: full reference line
- year: first (YYYY or YYYY[a/b]) found in parentheses
- title: heuristic title guess (text after year up to next period)
- url: first URL/DOI-like token detected

This is heuristic but gives a workable table to drive lookups (e.g., Google Scholar / DOI).
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

YEAR_PATTERN = re.compile(r"\((\d{4}[a-z]?)\)")
URL_PATTERN = re.compile(r"https?://\S+", re.IGNORECASE)
# Allow parentheses in DOI suffix (e.g., 10.1016/0749-5978(91)90020-T)
DOI_PATTERN = re.compile(r"\b10\.\d{4,9}/[^\s\]\}" + '"' + r"'<>,;]+", re.IGNORECASE)

# Heuristic: a new reference typically starts with "Surname, ... (YYYY)".
REF_START_PATTERN = re.compile(
    r"^[A-ZÀ-ÖØ-Ý][^\n]{0,120}?\(\d{4}[a-z]?\)\.",
    re.UNICODE,
)


def extract_year(text: str) -> str:
    match = YEAR_PATTERN.search(text)
    return match.group(1) if match else ""


def extract_url(text: str) -> str:
    match = URL_PATTERN.search(text)
    return match.group(0).rstrip(".,)") if match else ""


def extract_doi(text: str) -> str:
    match = DOI_PATTERN.search(text)
    if not match:
        return ""
    return match.group(0).rstrip(".,)")


def strip_prefix(text: str) -> str:
    """Remove leading markers like '1→' or numbering and whitespace."""
    return re.sub(r"^\s*\d+\s*[→>.\-)]?\s*", "", text)


def guess_title(text: str, year: str) -> str:
    """Heuristic: take text after the year-closing paren up to the next period."""
    if not year:
        return ""
    year_match = YEAR_PATTERN.search(text)
    if not year_match:
        return ""
    start = year_match.end()
    remainder = text[start:]
    # Usually the year is followed by ". ", so remove leading punctuation/spaces
    remainder = remainder.lstrip(" .:-–—\t")
    period_idx = remainder.find(".")
    if period_idx == -1:
        return remainder.strip()
    return remainder[:period_idx].strip()


def extract_authors(text: str, year: str) -> str:
    if not year:
        return ""
    year_match = YEAR_PATTERN.search(text)
    if not year_match:
        return ""
    return text[: year_match.start()].strip().rstrip(".")


def group_references(lines: list[str]) -> list[str]:
    """Join wrapped lines into full reference strings.

    Strategy:
    - Strip leading numbering like '12→'
    - Start new record when line looks like a reference start
    - Otherwise, append as continuation
    """
    records: list[str] = []
    current: list[str] = []

    for raw_line in lines:
        line = strip_prefix(raw_line.rstrip())
        line = line.strip()
        if not line:
            continue

        is_new = bool(REF_START_PATTERN.match(line))
        if is_new and current:
            records.append(" ".join(current).strip())
            current = [line]
        else:
            current.append(line)

    if current:
        records.append(" ".join(current).strip())
    return records


def parse_lines(lines: list[str]) -> list[dict]:
    parsed = []
    grouped = group_references(lines)
    for idx, line in enumerate(grouped, start=1):
        year = extract_year(line)
        doi = extract_doi(line)
        url = extract_url(line)
        title = guess_title(line, year)
        authors = extract_authors(line, year)

        # Prefer DOI resolver URL if DOI exists
        if doi:
            url = f"https://doi.org/{doi}"

        parsed.append(
            {
                "id": idx,
                "authors": authors,
                "year": year,
                "title": title,
                "doi": doi,
                "url": url,
                "raw": line,
            }
        )
    return parsed


def write_csv(rows: list[dict], dest: Path) -> None:
    fieldnames = ["id", "authors", "year", "title", "doi", "url", "raw"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    base = Path(__file__).resolve().parent
    source = base / "references.txt"
    output = base / "references.csv"
    if not source.exists():
        raise SystemExit(f"Missing {source}")
    lines = source.read_text(encoding="utf-8").splitlines()
    rows = parse_lines(lines)
    write_csv(rows, output)
    print(f"Parsed {len(rows)} references -> {output}")


if __name__ == "__main__":
    main()
