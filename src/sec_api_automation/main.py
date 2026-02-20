from __future__ import annotations

import argparse
import csv
import logging
from pathlib import Path

from .config import AppConfig
from .document_builder import download_optional
from .drive_client import DriveClient
from .filing_selector import find_latest_form, identify_latest_earnings_8k
from .reporting import CompanyResult, append_result, read_completed_tickers
from .sec_client import SecClient, list_filings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SEC filing to Google Drive automation")
    parser.add_argument(
        "--tickers-csv",
        required=True,
        help="CSV containing ticker column; company_name is optional",
    )
    parser.add_argument("--output-dir", default="output", help="Directory for local PDFs and result CSV")
    parser.add_argument("--result-csv", default="results.csv", help="Result CSV filename within output dir")
    parser.add_argument("--resume", action="store_true", help="Skip tickers already present in result CSV")
    return parser.parse_args()


def read_ticker_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    required = {"ticker"}
    if not rows:
        return []
    missing = required - set(rows[0].keys())
    if missing:
        raise ValueError(f"Input CSV is missing required columns: {sorted(missing)}")
    return rows


def process_one_company(
    sec: SecClient,
    drive: DriveClient,
    output_dir: Path,
    drive_parent_folder_id: str | None,
    ticker: str,
    company_name: str,
    ticker_to_cik: dict[str, str],
) -> CompanyResult:
    cik = ticker_to_cik.get(ticker.upper())
    if not cik:
        logging.warning("No CIK found for ticker=%s", ticker)
        fallback_name = company_name or ticker.upper()
        return CompanyResult(fallback_name, ticker, "", False, False, False, False)

    submissions = sec.get_submissions(cik)
    resolved_company_name = company_name or submissions.get("name", ticker.upper())

    filings = list_filings(submissions, {"10-K", "10-Q", "8-K", "8-K/A"})
    latest_10k = find_latest_form(filings, "10-K")
    latest_10q = find_latest_form(filings, "10-Q")
    latest_8ks = [f for f in filings if f.form in {"8-K", "8-K/A"}]
    earnings = identify_latest_earnings_8k(sec, cik, latest_8ks)

    company_output_dir = output_dir / ticker.upper()
    company_output_dir.mkdir(parents=True, exist_ok=True)

    ten_k_path = None
    if latest_10k:
        ten_k_url = sec.sec_archive_url(cik, latest_10k.accession, latest_10k.primary_document)
        ten_k_path = download_optional(sec, ten_k_url, company_output_dir / f"{ticker.upper()}_10K.pdf")

    ten_q_path = None
    if latest_10q:
        ten_q_url = sec.sec_archive_url(cik, latest_10q.accession, latest_10q.primary_document)
        ten_q_path = download_optional(sec, ten_q_url, company_output_dir / f"{ticker.upper()}_10Q.pdf")

    deck_path = None
    transcript_path = None
    if earnings:
        if earnings.deck_filename:
            deck_url = sec.sec_archive_url(cik, earnings.filing.accession, earnings.deck_filename)
            deck_path = download_optional(
                sec,
                deck_url,
                company_output_dir / f"{ticker.upper()}_EarningsDeck.pdf",
            )
        if earnings.transcript_filename:
            transcript_url = sec.sec_archive_url(cik, earnings.filing.accession, earnings.transcript_filename)
            transcript_path = download_optional(
                sec,
                transcript_url,
                company_output_dir / f"{ticker.upper()}_Transcript.pdf",
            )

    folder_id, folder_link = drive.create_company_folder(
        f"{ticker.upper()} - {resolved_company_name}",
        parent_folder_id=drive_parent_folder_id,
    )
    for file_path in [ten_k_path, ten_q_path, deck_path, transcript_path]:
        if file_path:
            drive.upload_file(folder_id, file_path)

    return CompanyResult(
        company_name=resolved_company_name,
        ticker=ticker.upper(),
        drive_folder_link=folder_link,
        has_10k=ten_k_path is not None,
        has_10q=ten_q_path is not None,
        has_deck=deck_path is not None,
        has_transcript=transcript_path is not None,
    )


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    result_csv = output_dir / args.result_csv
    if result_csv.exists() and not args.resume:
        result_csv.unlink()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    config = AppConfig.from_env(output_dir=output_dir, work_dir=output_dir / "work")
    sec = SecClient(
        user_agent=config.sec_user_agent,
        timeout_seconds=config.request_timeout_seconds,
        min_interval_seconds=config.min_request_interval_seconds,
    )
    if config.drive_auth_mode == "oauth":
        if config.drive_oauth_client_secrets_path is None:
            raise ValueError("Missing GOOGLE_OAUTH_CLIENT_SECRETS for OAuth mode")
        drive = DriveClient.from_oauth(
            client_secrets_path=config.drive_oauth_client_secrets_path,
            token_path=config.drive_oauth_token_path,
        )
    else:
        if config.drive_credentials_path is None:
            raise ValueError("Missing GOOGLE_APPLICATION_CREDENTIALS for service_account mode")
        drive = DriveClient.from_service_account(
            credentials_path=config.drive_credentials_path,
        )

    ticker_rows = read_ticker_rows(Path(args.tickers_csv))
    completed = read_completed_tickers(result_csv) if args.resume else set()
    ticker_to_cik = sec.ticker_to_cik_map()

    for row in ticker_rows:
        ticker = row["ticker"].strip().upper()
        company_name = row.get("company_name", "").strip()

        if not ticker:
            continue
        if ticker in completed:
            logging.info("Skipping ticker=%s due to --resume", ticker)
            continue

        try:
            logging.info("Processing ticker=%s company=%s", ticker, company_name)
            result = process_one_company(
                sec=sec,
                drive=drive,
                output_dir=output_dir,
                drive_parent_folder_id=config.drive_parent_folder_id,
                ticker=ticker,
                company_name=company_name,
                ticker_to_cik=ticker_to_cik,
            )
            append_result(result_csv, result)
        except Exception as exc:  # noqa: BLE001
            logging.exception("Failed ticker=%s: %s", ticker, exc)
            append_result(
                result_csv,
                CompanyResult(company_name or ticker, ticker, "", False, False, False, False),
            )


if __name__ == "__main__":
    main()
