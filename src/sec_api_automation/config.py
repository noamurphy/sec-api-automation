from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


@dataclass(frozen=True)
class AppConfig:
    sec_user_agent: str
    drive_auth_mode: str
    drive_credentials_path: Path | None
    drive_oauth_client_secrets_path: Path | None
    drive_oauth_token_path: Path
    drive_parent_folder_id: str | None
    output_dir: Path
    work_dir: Path
    request_timeout_seconds: int = 20
    min_request_interval_seconds: float = 0.2

    @staticmethod
    def from_env(output_dir: Path, work_dir: Path) -> "AppConfig":
        sec_user_agent = os.getenv("SEC_USER_AGENT", "")
        drive_auth_mode = os.getenv("GOOGLE_DRIVE_AUTH_MODE", "oauth").strip().lower()
        drive_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
        oauth_client_secrets = os.getenv("GOOGLE_OAUTH_CLIENT_SECRETS", "")
        oauth_token_path = os.getenv("GOOGLE_OAUTH_TOKEN_PATH", "").strip()
        drive_parent_folder_id = os.getenv("GOOGLE_DRIVE_PARENT_FOLDER_ID", "").strip()
        if not sec_user_agent:
            raise ValueError(
                "SEC_USER_AGENT is required. Example: 'First Last email@domain.com'"
            )
        if drive_auth_mode not in {"oauth", "service_account"}:
            raise ValueError("GOOGLE_DRIVE_AUTH_MODE must be 'oauth' or 'service_account'")
        if drive_auth_mode == "service_account" and not drive_credentials:
            raise ValueError(
                "GOOGLE_APPLICATION_CREDENTIALS is required when GOOGLE_DRIVE_AUTH_MODE=service_account"
            )
        if drive_auth_mode == "oauth" and not oauth_client_secrets:
            raise ValueError(
                "GOOGLE_OAUTH_CLIENT_SECRETS is required when GOOGLE_DRIVE_AUTH_MODE=oauth"
            )
        resolved_oauth_token_path = (
            Path(oauth_token_path) if oauth_token_path else (work_dir / "google_oauth_token.json")
        )
        return AppConfig(
            sec_user_agent=sec_user_agent,
            drive_auth_mode=drive_auth_mode,
            drive_credentials_path=Path(drive_credentials) if drive_credentials else None,
            drive_oauth_client_secrets_path=(
                Path(oauth_client_secrets) if oauth_client_secrets else None
            ),
            drive_oauth_token_path=resolved_oauth_token_path,
            drive_parent_folder_id=drive_parent_folder_id or None,
            output_dir=output_dir,
            work_dir=work_dir,
        )
