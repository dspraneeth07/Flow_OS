"""Assembles the single-file Linux installer (FlowOS-Linux.run) from:
  - C:\\FlowOSBuildLinux\\python-linux.tar.gz      (untouched, official CPython build)
  - C:\\FlowOSBuildLinux\\site-packages-payload\\   (flowos + deps, installed via uv --target)
  - launcher.sh                                    (runs the server once installed)
  - sfx_stub.sh                                    (self-extracting shell wrapper)

Not run automatically - invoked once the uv cross-install finishes.
"""

from __future__ import annotations

import tarfile
from pathlib import Path

BUILD_DIR = Path(r"C:\FlowOSBuildLinux")
PYTHON_TAR = BUILD_DIR / "python-linux.tar.gz"
PAYLOAD_DIR = BUILD_DIR / "site-packages-payload"
PAYLOAD_TAR = BUILD_DIR / "flowos-payload.tar.gz"
SCRIPT_DIR = Path(__file__).parent
FRONTEND_SRC = Path(r"c:\Users\Techm\Atlantic AI Labs\FlowOS\src\backend\base\flowos\frontend")
OUT_FILE = BUILD_DIR / "FlowOS-Linux.run"


def main() -> None:
    frontend_dst = PAYLOAD_DIR / "flowos" / "frontend"
    if frontend_dst.exists():
        import shutil

        shutil.rmtree(frontend_dst)
    import shutil

    shutil.copytree(FRONTEND_SRC, frontend_dst)
    print(f"Copied frontend build into {frontend_dst}")

    print("Archiving flowos + dependencies (this is a large tree, may take a while)...")
    with tarfile.open(PAYLOAD_TAR, "w:gz", compresslevel=1) as tf:
        tf.add(PAYLOAD_DIR, arcname=".")
    print(f"Wrote {PAYLOAD_TAR} ({PAYLOAD_TAR.stat().st_size / 1e6:.1f} MB)")

    python_tar_size = PYTHON_TAR.stat().st_size
    payload_tar_size = PAYLOAD_TAR.stat().st_size

    stub_text = (SCRIPT_DIR / "sfx_stub.sh").read_text(encoding="utf-8")
    stub_text = stub_text.replace("__PYTHON_TAR_SIZE__", str(python_tar_size))
    stub_text = stub_text.replace("__PAYLOAD_TAR_SIZE__", str(payload_tar_size))

    launcher_bytes = (SCRIPT_DIR / "launcher.sh").read_bytes()

    with OUT_FILE.open("wb") as out:
        out.write(stub_text.encode("utf-8"))
        out.write(PYTHON_TAR.read_bytes())
        out.write(PAYLOAD_TAR.read_bytes())
        out.write(launcher_bytes)

    print(f"Wrote {OUT_FILE} ({OUT_FILE.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
