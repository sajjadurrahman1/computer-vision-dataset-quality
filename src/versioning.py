from __future__ import annotations

import os
import shutil
from datetime import datetime


def create_release_copy(src_dir: str = "data/raw", releases_dir: str = "data/releases") -> str:
    os.makedirs(releases_dir, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    release_path = os.path.join(releases_dir, f"release_{stamp}")
    os.makedirs(release_path, exist_ok=True)

    for name in os.listdir(src_dir):
        src = os.path.join(src_dir, name)
        dst = os.path.join(release_path, name)

        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            shutil.copy2(src, dst)

    return release_path
