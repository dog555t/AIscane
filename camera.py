import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from PIL import Image


def capture_image(output_dir: str, filename: Optional[str] = None) -> str:
    os.makedirs(output_dir, exist_ok=True)
    name = filename or f"receipt_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.jpg"
    output_path = Path(output_dir) / name

    command = [
        "libcamera-still",
        "-n",
        "-o",
        str(output_path),
        "--width",
        "1280",
        "--height",
        "960",
        "--autofocus-mode",
        "continuous",
    ]

    try:
        subprocess.run(command, check=True, timeout=15)
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as exc:
        placeholder = Image.new("RGB", (1280, 960), color=(240, 240, 240))
        placeholder.save(output_path)
        print(f"[WARN] libcamera capture failed ({exc}); saved placeholder image instead: {output_path}")

    time.sleep(0.25)
    return str(output_path)
