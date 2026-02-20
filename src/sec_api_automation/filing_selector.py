from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from .sec_client import FilingMeta, SecClient


EX99_PATTERN = re.compile(r"(exhibit|ex)[-_]?99([._-]?\d+)?", re.IGNORECASE)
EARNINGS_HINT_PATTERN = re.compile(
    r"(earnings|results|quarterly|q[1-4]|presentation|slides|conference|transcript)",
    re.IGNORECASE,
)


@dataclass
class EarningsExhibits:
    filing: FilingMeta
    deck_filename: str | None
    transcript_filename: str | None


def find_latest_form(filings: list[FilingMeta], form: str) -> FilingMeta | None:
    for filing in filings:
        if filing.form == form:
            return filing
    amended = f"{form}/A"
    for filing in filings:
        if filing.form == amended:
            return filing
    return None


def extract_ex99_filenames(index_json: dict[str, Any]) -> list[str]:
    files = index_json.get("directory", {}).get("item", [])
    names: list[str] = []
    for entry in files:
        filename = entry.get("name", "")
        if EX99_PATTERN.search(filename):
            names.append(filename)
    return names


def _score_deck(name: str) -> int:
    name_lower = name.lower()
    score = 0
    if any(token in name_lower for token in ["deck", "slides", "presentation"]):
        score += 5
    if "99.2" in name_lower or "99-2" in name_lower or "992" in name_lower:
        score += 2
    if any(token in name_lower for token in ["transcript", "conference", "call"]):
        score -= 5
    return score


def _score_transcript(name: str) -> int:
    name_lower = name.lower()
    score = 0
    if any(token in name_lower for token in ["transcript", "conference", "call", "prepared"]):
        score += 5
    if "99.1" in name_lower or "99-1" in name_lower or "991" in name_lower:
        score += 1
    if any(token in name_lower for token in ["deck", "slides", "presentation"]):
        score -= 5
    return score


def _pick_best(candidates: list[str], scorer) -> str | None:
    if not candidates:
        return None
    ranked = sorted(((scorer(name), name) for name in candidates), reverse=True)
    best_score, best_name = ranked[0]
    if best_score < 1:
        return None
    return best_name


def identify_latest_earnings_8k(
    sec: SecClient,
    cik: str,
    eight_ks: list[FilingMeta],
) -> EarningsExhibits | None:
    for filing in eight_ks:
        index_json = sec.get_filing_index(cik=cik, accession=filing.accession)
        ex99_files = extract_ex99_filenames(index_json)
        if not ex99_files:
            continue

        earnings_candidates = [name for name in ex99_files if EARNINGS_HINT_PATTERN.search(name)]
        candidates = earnings_candidates or ex99_files

        deck = _pick_best(candidates, _score_deck)
        transcript = _pick_best(candidates, _score_transcript)

        if deck and transcript == deck:
            transcript = None

        return EarningsExhibits(
            filing=filing,
            deck_filename=deck,
            transcript_filename=transcript,
        )
    return None
