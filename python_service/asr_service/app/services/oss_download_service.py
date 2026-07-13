from __future__ import annotations

import os
from pathlib import Path

import oss2

from app.config import settings


class OSSDownloadService:
    def __init__(self, download_dir: str = "./tmp_downloads") -> None:
        self.download_dir = download_dir
        os.makedirs(self.download_dir, exist_ok=True)

        auth = oss2.Auth(
            settings.oss_access_key_id,
            settings.oss_access_key_secret,
        )

        self.bucket = oss2.Bucket(
            auth,
            settings.oss_endpoint,
            settings.oss_bucket,
            region=settings.oss_region,
        )

    def download_to_local(
        self,
        task_id: int,
        original_name: str,
        object_key: str,
    ) -> str:
        suffix = Path(original_name).suffix or ".bin"

        task_dir = Path(self.download_dir) / f"task_{task_id}"
        task_dir.mkdir(parents=True, exist_ok=True)

        local_path = task_dir / f"source{suffix}"

        self.bucket.get_object_to_file(object_key, str(local_path))

        return str(local_path)