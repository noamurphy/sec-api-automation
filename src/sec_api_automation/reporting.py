from __future__ import annotations

import csv
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class CompanyResult:
    company_name: str
    ticker: str
    drive_folder_link: str
    has_10k: bool
    has_10q: bool
    has_deck: bool
    has_transcript: bool


def read_completed_tickers(csv_path: Path) -> set[str]:
    if not csv_path.exists():
        return set()
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return {row["ticker"].upper() for row in reader if row.get("ticker")}


def append_result(csv_path: Path, result: CompanyResult) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "company_name",
                "ticker",
                "drive_folder_link",
                "has_10k",
                "has_10q",
                "has_deck",
                "has_transcript",
            ],
        )
        if write_header:
            writer.writeheader()
        writer.writerow(asdict(result))
