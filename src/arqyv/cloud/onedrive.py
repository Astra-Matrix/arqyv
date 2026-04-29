"""Microsoft OneDrive cloud provider using MSAL + Microsoft Graph API."""

from __future__ import annotations

import logging
from pathlib import Path

import httpx

from arqyv.cloud.base import CloudFile, CloudProvider

log = logging.getLogger(__name__)

_AUTHORITY = "https://login.microsoftonline.com/consumers"
_SCOPES = ["Files.Read"]
_GRAPH_BASE = "https://graph.microsoft.com/v1.0"


class OneDriveProvider(CloudProvider):
    name = "Microsoft OneDrive"  # type: ignore[override]

    def __init__(self, client_id: str, token_dir: Path) -> None:
        self._client_id = client_id
        self._token_dir = token_dir
        self._access_token: str | None = None

    def authenticate(self) -> bool:
        try:
            import msal  # type: ignore[import]

            cache = msal.SerializableTokenCache()
            cache_path = self._token_dir / "onedrive_cache.bin"
            if cache_path.exists():
                cache.deserialize(cache_path.read_text())

            app = msal.PublicClientApplication(
                client_id=self._client_id,
                authority=_AUTHORITY,
                token_cache=cache,
            )
            accounts = app.get_accounts()
            result = None
            if accounts:
                result = app.acquire_token_silent(_SCOPES, account=accounts[0])

            if not result:
                flow = app.initiate_device_flow(scopes=_SCOPES)
                print(flow.get("message", ""))  # instructs user to visit URL
                result = app.acquire_token_by_device_flow(flow)

            if "access_token" in result:
                self._access_token = result["access_token"]
                cache_path.write_text(cache.serialize())
                log.info("OneDrive authenticated.")
                return True
            log.error("OneDrive auth failed: %s", result.get("error_description"))
            return False
        except Exception:
            log.exception("OneDrive authentication error.")
            return False

    def is_authenticated(self) -> bool:
        return self._access_token is not None

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self._access_token}"}

    def list_files(self, remote_path: str = "/", recursive: bool = False) -> list[CloudFile]:
        if not self._access_token:
            return []
        try:
            url = f"{_GRAPH_BASE}/me/drive/root/children"
            resp = httpx.get(url, headers=self._headers(), timeout=15)
            resp.raise_for_status()
            items = resp.json().get("value", [])
            return [
                CloudFile(
                    id=item["id"],
                    name=item["name"],
                    path=item.get("parentReference", {}).get("path", "") + "/" + item["name"],
                    size_bytes=item.get("size", 0),
                    mime_type=item.get("file", {}).get("mimeType"),
                    modified_at=item.get("lastModifiedDateTime"),
                    download_url=item.get("@microsoft.graph.downloadUrl"),
                )
                for item in items
                if "file" in item
            ]
        except Exception:
            log.exception("OneDrive list_files failed.")
            return []

    def download_file(self, cloud_file: CloudFile, local_dest: Path) -> bool:
        if not cloud_file.download_url:
            return False
        try:
            with httpx.stream("GET", cloud_file.download_url, timeout=120) as r:
                r.raise_for_status()
                with open(local_dest, "wb") as f:
                    for chunk in r.iter_bytes():
                        f.write(chunk)
            return True
        except Exception:
            log.exception("OneDrive download failed: %s", cloud_file.name)
            return False

    def upload_file(self, local_path: Path, remote_dest: str) -> CloudFile | None:
        log.warning("OneDrive upload not yet implemented.")
        return None

    def delete_file(self, cloud_file: CloudFile) -> bool:
        log.warning("OneDrive delete not yet implemented.")
        return False
