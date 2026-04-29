"""Dropbox cloud provider."""

from __future__ import annotations

import logging
from pathlib import Path

from arqyv.cloud.base import CloudFile, CloudProvider

log = logging.getLogger(__name__)


class DropboxProvider(CloudProvider):
    name = "Dropbox"  # type: ignore[override]

    def __init__(self, app_key: str, app_secret: str, token_dir: Path) -> None:
        self._app_key = app_key
        self._app_secret = app_secret
        self._token_path = token_dir / "dropbox_token.txt"
        self._dbx: object | None = None

    def authenticate(self) -> bool:
        try:
            import dropbox  # type: ignore[import]
            from dropbox import DropboxOAuth2FlowNoRedirect

            if self._token_path.exists():
                token = self._token_path.read_text().strip()
                self._dbx = dropbox.Dropbox(token)
                log.info("Dropbox loaded cached token.")
                return True

            auth_flow = DropboxOAuth2FlowNoRedirect(
                self._app_key, self._app_secret, token_access_type="offline"
            )
            authorize_url = auth_flow.start()
            print(f"1. Go to: {authorize_url}")
            print("2. Click 'Allow'.")
            auth_code = input("3. Enter the authorization code: ").strip()
            oauth_result = auth_flow.finish(auth_code)
            self._token_path.write_text(oauth_result.access_token)
            self._dbx = dropbox.Dropbox(oauth_result.access_token)
            log.info("Dropbox authenticated.")
            return True
        except Exception:
            log.exception("Dropbox authentication failed.")
            return False

    def is_authenticated(self) -> bool:
        return self._dbx is not None

    def list_files(self, remote_path: str = "", recursive: bool = False) -> list[CloudFile]:
        if not self._dbx:
            return []
        try:
            import dropbox  # type: ignore[import]
            result = self._dbx.files_list_folder(remote_path or "", recursive=recursive)  # type: ignore[attr-defined]
            files = []
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    files.append(CloudFile(
                        id=entry.id,
                        name=entry.name,
                        path=entry.path_display,
                        size_bytes=entry.size,
                        mime_type=None,
                        modified_at=str(entry.client_modified),
                    ))
            return files
        except Exception:
            log.exception("Dropbox list_files failed.")
            return []

    def download_file(self, cloud_file: CloudFile, local_dest: Path) -> bool:
        if not self._dbx:
            return False
        try:
            self._dbx.files_download_to_file(str(local_dest), cloud_file.path)  # type: ignore[attr-defined]
            return True
        except Exception:
            log.exception("Dropbox download failed: %s", cloud_file.name)
            return False

    def upload_file(self, local_path: Path, remote_dest: str) -> CloudFile | None:
        if not self._dbx:
            return None
        try:
            with open(local_path, "rb") as f:
                meta = self._dbx.files_upload(f.read(), remote_dest, mute=True)  # type: ignore[attr-defined]
            return CloudFile(
                id=meta.id,
                name=meta.name,
                path=meta.path_display,
                size_bytes=meta.size,
                mime_type=None,
                modified_at=str(meta.client_modified),
            )
        except Exception:
            log.exception("Dropbox upload failed: %s", local_path)
            return None

    def delete_file(self, cloud_file: CloudFile) -> bool:
        if not self._dbx:
            return False
        try:
            self._dbx.files_delete_v2(cloud_file.path)  # type: ignore[attr-defined]
            return True
        except Exception:
            log.exception("Dropbox delete failed: %s", cloud_file.name)
            return False
