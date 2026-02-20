from __future__ import annotations

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


SCOPES = ["https://www.googleapis.com/auth/drive"]


class DriveClient:
    def __init__(self, credentials: Credentials | service_account.Credentials) -> None:
        self.service = build("drive", "v3", credentials=credentials, cache_discovery=False)

    @classmethod
    def from_service_account(cls, credentials_path: Path) -> "DriveClient":
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path), scopes=SCOPES
        )
        return cls(credentials=credentials)

    @classmethod
    def from_oauth(
        cls,
        client_secrets_path: Path,
        token_path: Path,
    ) -> "DriveClient":
        creds: Credentials | None = None
        if token_path.exists():
            creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        elif not creds or not creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(str(client_secrets_path), SCOPES)
            creds = flow.run_local_server(port=0)

        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json(), encoding="utf-8")
        return cls(credentials=creds)

    def create_company_folder(
        self,
        folder_name: str,
        parent_folder_id: str | None = None,
    ) -> tuple[str, str]:
        metadata: dict[str, str | list[str]] = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }
        if parent_folder_id:
            metadata["parents"] = [parent_folder_id]
        folder = (
            self.service.files()
            .create(body=metadata, fields="id,webViewLink", supportsAllDrives=True)
            .execute()
        )
        folder_id = folder["id"]

        self.service.permissions().create(
            fileId=folder_id,
            body={"type": "anyone", "role": "reader"},
            supportsAllDrives=True,
        ).execute()

        folder_link = folder.get("webViewLink") or f"https://drive.google.com/drive/folders/{folder_id}"
        return folder_id, folder_link

    def upload_file(self, folder_id: str, file_path: Path) -> str:
        metadata = {
            "name": file_path.name,
            "parents": [folder_id],
        }
        media = MediaFileUpload(str(file_path), mimetype="application/pdf", resumable=True)
        upload = (
            self.service.files()
            .create(
                body=metadata,
                media_body=media,
                fields="id,webViewLink",
                supportsAllDrives=True,
            )
            .execute()
        )
        return upload.get("webViewLink", "")
