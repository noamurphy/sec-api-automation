# SEC API Automation (First Full Version)

This repository is a self-directed build of a real-world financial-document automation workflow based on a closed Upwork contract brief: [contract link](https://www.upwork.com/jobs/~021989661025868771778).

The goal was to deliver the same core requirements the contract requested, even though I was not selected for the engagement. This project was built as:
- A learning exercise in production-style SEC + Google Drive automation
- A proof-of-capability artifact for future data-engineering and API-automation contracts
- A practical reference implementation with runnable code, setup docs, and a validated 10-company demo

This repository now includes a runnable Python pipeline that:
- Maps ticker to CIK
- Pulls latest 10-K and 10-Q
- Finds a recent earnings-related 8-K with EX-99 exhibits
- Downloads and normalizes target documents to PDF filenames
- Creates a Google Drive folder per company, uploads files, and shares folder publicly
- Outputs a final CSV with availability flags and Drive link

Main entrypoint:
- `src/sec_api_automation/main.py`

Detailed instructions:
- `/Users/murphy/PythonProjects/UpWork/sec_api_automation/docs/runbook.md`
- `/Users/murphy/PythonProjects/UpWork/sec_api_automation/docs/google_oauth_setup.md`
- `/Users/murphy/PythonProjects/UpWork/sec_api_automation/docs/google_service_account_setup.md`
