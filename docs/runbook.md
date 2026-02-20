# SEC Automation Runbook

## 1) Setup

1. Use Python 3.10+
2. Create and activate a virtual environment
3. Install package

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

4. Set environment variables (see `.env.example`)

```bash
export SEC_USER_AGENT="First Last email@domain.com"
export GOOGLE_DRIVE_AUTH_MODE="oauth"
export GOOGLE_OAUTH_CLIENT_SECRETS="/absolute/path/to/oauth-client-secrets.json"
export GOOGLE_OAUTH_TOKEN_PATH="/absolute/path/to/google_oauth_token.json"
export GOOGLE_DRIVE_PARENT_FOLDER_ID="optional_parent_folder_id"
```

OAuth setup guide:
- `/Users/murphy/PythonProjects/UpWork/sec_api_automation/docs/google_oauth_setup.md`

## 2) Input CSV format

The input CSV must include:
- `ticker`

Optional:
- `company_name` (if omitted, SEC submissions company name is used)

Example file: `examples/tickers_10_demo.csv`

## 3) Run 10-company demo

```bash
sec-api-automation \
  --tickers-csv examples/tickers_10_demo.csv \
  --output-dir output_demo
```

Expected outputs:
- Local PDFs under `output_demo/<TICKER>/`
- Result CSV at `output_demo/results.csv`
- Google Drive folder for each company, link captured in CSV

## 4) Run full list (500 companies)

```bash
sec-api-automation \
  --tickers-csv path/to/tickers_500.csv \
  --output-dir output_full
```

If interrupted, resume without reprocessing completed companies:

```bash
sec-api-automation \
  --tickers-csv path/to/tickers_500.csv \
  --output-dir output_full \
  --resume
```

## 5) Output CSV schema

- `company_name`
- `ticker`
- `drive_folder_link`
- `has_10k`
- `has_10q`
- `has_deck`
- `has_transcript`
