"""One-off build step (run by the developer, not shipped): download an
embeddable Python runtime and install the full ``flowos`` package into it.
The result is later packaged alongside the launcher into a single
self-extracting installer exe. See build_installer.ps1.
"""

from __future__ import annotations

import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

BUILD_DIR = Path(r"C:\FlowOSBuild")
RUNTIME_DIR = BUILD_DIR / "runtime"
PYTHON_VERSION = "3.11.9"
PYTHON_EMBED_URL = f"https://www.python.org/ftp/python/{PYTHON_VERSION}/python-{PYTHON_VERSION}-embed-amd64.zip"
UV_URL = "https://github.com/astral-sh/uv/releases/latest/download/uv-x86_64-pc-windows-msvc.zip"
PYTHON_EXE = RUNTIME_DIR / "python.exe"
UV_EXE = BUILD_DIR / "uv.exe"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def download(url: str, dest: Path) -> None:
    log(f"Downloading {url} -> {dest}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(url, dest)  # noqa: S310


def enable_site_packages(runtime_dir: Path) -> None:
    for pth in runtime_dir.glob("python*._pth"):
        text = pth.read_text(encoding="utf-8")
        if "#import site" in text:
            pth.write_text(text.replace("#import site", "import site"), encoding="utf-8")


def run(args: list[str]) -> None:
    log(f"Running: {args}")
    result = subprocess.run(args, check=False)  # noqa: S603
    if result.returncode != 0:
        msg = f"Command failed (exit {result.returncode}): {args}"
        raise RuntimeError(msg)


def main() -> None:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)

    if not PYTHON_EXE.exists():
        zip_path = BUILD_DIR / "python-embed.zip"
        download(PYTHON_EMBED_URL, zip_path)
        log("Extracting Python runtime...")
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(RUNTIME_DIR)
        zip_path.unlink(missing_ok=True)
        enable_site_packages(RUNTIME_DIR)
    else:
        log("Python runtime already present, skipping.")

    if not UV_EXE.exists():
        uv_zip = BUILD_DIR / "uv.zip"
        download(UV_URL, uv_zip)
        log("Extracting uv...")
        with zipfile.ZipFile(uv_zip) as zf:
            zf.extractall(BUILD_DIR)
        uv_zip.unlink(missing_ok=True)
    else:
        log("uv already present, skipping.")

    log("Installing flowos (this pulls ~3GB of dependencies)...")
    run([str(UV_EXE), "pip", "install", "--python", str(PYTHON_EXE), "-U", "flowos"])

    log("Verifying flowos is runnable...")
    run([str(PYTHON_EXE), "-c", "import flowos; print('flowos import OK')"])

    log("Runtime build complete.")


if __name__ == "__main__":
    sys.exit(main() or 0)
