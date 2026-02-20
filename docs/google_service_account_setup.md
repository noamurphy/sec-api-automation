# Google Service Account Setup (Optional Alternative)

Use this only if you have Google Workspace and a suitable Shared Drive setup.

## Create service account

1. Open Google Cloud Console
2. Select/create a project
3. Enable **Google Drive API**
4. Go to **IAM & Admin > Service Accounts**
5. Create a service account (for example: `sec-drive-uploader`)
6. Create and download a JSON key

## Prepare target Drive

1. Create or choose a Shared Drive location where folders will be created
2. Add the service account email from the JSON file to the Shared Drive
3. Grant at least **Content manager** permission

## Configure local environment

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/absolute/path/to/service-account.json"
export SEC_USER_AGENT="First Last email@domain.com"
export GOOGLE_DRIVE_AUTH_MODE="service_account"
```

## Verify

Run the 10-company demo in `/Users/murphy/PythonProjects/UpWork/sec_api_automation/docs/runbook.md` and confirm:
- Folders are created
- Folder permission is "anyone with link can view"
- PDF files upload successfully
