# SEC API Automation (First Full Version)

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
