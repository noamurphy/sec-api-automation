# Google OAuth Setup (Personal Google Drive)

Use this when you do not have Google Workspace Shared Drives.

## 1) Enable Drive API and create OAuth credentials

1. Open Google Cloud Console
2. Select or create your project
3. Enable **Google Drive API**
4. Go to **APIs & Services > OAuth consent screen**
5. Configure consent screen (External is fine for personal use)
6. Go to **APIs & Services > Credentials**
7. Create **OAuth client ID**
8. Choose **Desktop app**
9. Download the JSON (OAuth client secrets)

## 2) Set environment variables

```bash
export SEC_USER_AGENT="First Last email@domain.com"
export GOOGLE_DRIVE_AUTH_MODE="oauth"
export GOOGLE_OAUTH_CLIENT_SECRETS="/absolute/path/to/oauth-client-secrets.json"
export GOOGLE_OAUTH_TOKEN_PATH="/absolute/path/to/google_oauth_token.json"
export GOOGLE_DRIVE_PARENT_FOLDER_ID="optional_parent_folder_id"
```

Notes:
- `GOOGLE_OAUTH_TOKEN_PATH` is where your refresh token is saved after first login.
- `GOOGLE_DRIVE_PARENT_FOLDER_ID` is optional; if set, company folders are created under that parent folder.

## 3) First run behavior

On first run, your browser opens and asks you to sign in + consent. After approval:
- token is saved to `GOOGLE_OAUTH_TOKEN_PATH`
- later runs reuse/refresh token automatically

## 4) Verify

Run the 10-company demo in `/Users/murphy/PythonProjects/UpWork/sec_api_automation/docs/runbook.md`.
Confirm folders/files appear in your My Drive.
