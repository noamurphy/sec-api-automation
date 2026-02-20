from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


SEC_BASE = "https://www.sec.gov"
SEC_DATA_BASE = "https://data.sec.gov"


@dataclass
class FilingMeta:
    form: str
    filing_date: str
    accession: str
    primary_document: str


class SecClient:
    def __init__(self, user_agent: str, timeout_seconds: int = 20, min_interval_seconds: float = 0.2) -> None:
        self.timeout_seconds = timeout_seconds
        self.min_interval_seconds = min_interval_seconds
        self.last_request_at = 0.0
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    def _throttle(self) -> None:
        now = time.time()
        elapsed = now - self.last_request_at
        if elapsed < self.min_interval_seconds:
            time.sleep(self.min_interval_seconds - elapsed)
        self.last_request_at = time.time()

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=16),
        retry=retry_if_exception_type(requests.RequestException),
    )
    def _get(self, url: str) -> requests.Response:
        self._throttle()
        response = self.session.get(url, timeout=self.timeout_seconds)
        response.raise_for_status()
        return response

    def get_json(self, url: str) -> dict[str, Any]:
        response = self._get(url)
        return response.json()

    def get_bytes(self, url: str) -> bytes:
        response = self._get(url)
        return response.content

    def get_company_tickers(self) -> dict[str, dict[str, Any]]:
        return self.get_json(f"{SEC_BASE}/files/company_tickers.json")

    def ticker_to_cik_map(self) -> dict[str, str]:
        payload = self.get_company_tickers()
        return {
            item["ticker"].upper(): str(item["cik_str"]).zfill(10)
            for item in payload.values()
        }

    def get_submissions(self, cik: str) -> dict[str, Any]:
        return self.get_json(f"{SEC_DATA_BASE}/submissions/CIK{cik}.json")

    def get_filing_index(self, cik: str, accession: str) -> dict[str, Any]:
        acc_nodash = accession.replace("-", "")
        return self.get_json(
            f"{SEC_BASE}/Archives/edgar/data/{int(cik)}/{acc_nodash}/index.json"
        )

    def sec_archive_url(self, cik: str, accession: str, filename: str) -> str:
        acc_nodash = accession.replace("-", "")
        return f"{SEC_BASE}/Archives/edgar/data/{int(cik)}/{acc_nodash}/{filename}"


def list_filings(submissions_json: dict[str, Any], form_types: set[str]) -> list[FilingMeta]:
    recent = submissions_json.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])

    result: list[FilingMeta] = []
    for idx, form in enumerate(forms):
        if form not in form_types:
            continue
        result.append(
            FilingMeta(
                form=form,
                filing_date=dates[idx],
                accession=accessions[idx],
                primary_document=primary_docs[idx],
            )
        )

    result.sort(key=lambda item: item.filing_date, reverse=True)
    return result
