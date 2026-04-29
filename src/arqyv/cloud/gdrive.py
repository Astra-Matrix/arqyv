"""Google Drive cloud provider."""

from __future__ import annotations

import logging
import os
from pathlib import Path

from arqyv.cloud.base import CloudFile, CloudProvider

log = logging.getLogger(__name__)

_SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]
_TOKEN_FILE = "gdrive_token.json"


class GoogleDriveProvider(CloudProvider):
    name = "Google Drive"  # type: ignore[override]

    def __init__(self, client_id: str, client_secret: str, token_dir: Path) -> None:
        self._client_id = client_id
        self._client_secret = client_secret
        self._token_path = token_dir / _TOKEN_FILE
        self._service: object | None = None

    def authenticate(self) -> bool:
        try:
            from google.oauth2.credentials import Credentials  # type: ignore[import]
            from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore[import]
            from google.auth.transport.requests import Request  # type: ignore[import]
            from googleapiclient.discovery import build  # type: ignore[import]

            creds: Credentials | None = None
            if self._token_path.exists():
                creds = Credentials.from_authorized_user_file(str(self._token_path), _SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    client_config = {
                        "installed": {
                            "client_id": self._client_id,
                            "client_secret": self._client_secret,
                            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob"],
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://accounts.google.com/o/oauth2/token",
                        }
                    }
                    flow = InstalledAppFlow.from_client_config(client_config, _SCOPES)
                    creds = flow.run_local_server(port=0)

                self._token_path.write_text(creds.to_json())

            self._service = build("drive", "v3", credentials=creds)
            log.info("Google Drive authenticated.")
            return True
        except Exception:
            log.exception("Google Drive authentication failed.")
            return False

    def is_authenticated(self) -> bool:
        return self._service is not None

    def list_files(self, remote_path: str = "/", recursive: bool = False) -> list[CloudFile]:
        if not self._service:
            return []
        try:
            results = (
                self._service.files()  # type: ignore[attr-defined]
                .list(
                    pageSize=100,
                    fields="files(id, name, size, mimeType, modifiedTime, webContentLink)",
                )
                .execute()
            )
            return [
                CloudFile(
                    id=f["id"],
                    name=f["name"],
                    path=f["name"],
                    size_bytes=int(f.get("size", 0)),
                    mime_type=f.get("mimeType"),
                    modified_at=f.get("modifiedTime"),
                    download_url=f.get("webContentLink"),
                )
                for f in results.get("files", [])
            ]
        except Exception:
            log.exception("Google Drive list_files failed.")
            return []

    def download_file(self, cloud_file: CloudFile, local_dest: Path) -> bool:
        if not self._service:
            return False
        try:
            from googleapiclient.http import MediaIoBaseDownload  # type: ignore[import]
            import io

            request = self._service.files().get_media(fileId=cloud_file.id)  # type: ignore[attr-defined]
            fh = io.FileIO(str(local_dest), "wb")
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()
            return True
        except Exception:
            log.exception("Google Drive download failed: %s", cloud_file.name)
            return False

    def upload_file(self, local_path: Path, remote_dest: str) -> CloudFile | None:
        log.warning("Google Drive upload not yet implemented.")
        return None

    def delete_file(self, cloud_file: CloudFile) -> bool:
        log.warning("Google Drive delete not yet implemented.")
        return False
