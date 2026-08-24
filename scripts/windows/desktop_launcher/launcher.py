"""FlowOS Desktop launcher.

Runs the ``flowos`` server that ships in the ``runtime\\`` folder next to this
executable, waits for it to become healthy, and opens it in the browser.
All the heavy lifting (installing Python + flowos + ~3GB of dependencies)
already happened at *build* time (see build_runtime.py) - this script does
not download or install anything. That keeps it simple and means there is
nothing here that can fail because the user has no internet connection.

Kept to the standard library on purpose: this script is itself frozen by
PyInstaller into a small exe, and everything it needs to actually run FlowOS
lives in the adjacent runtime folder instead.
"""

from __future__ import annotations

import os
import queue
import socket
import subprocess
import sys
import threading
import time
import tkinter as tk
import traceback
import urllib.request
import webbrowser
from pathlib import Path
from tkinter import messagebox, ttk

APP_NAME = "FlowOS"
DEFAULT_PORT = 7860
HEALTH_TIMEOUT_SECONDS = 300


def _exe_dir() -> Path:
    """Directory the running exe (or this script, when unfrozen) lives in."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


EXE_DIR = _exe_dir()
RUNTIME_DIR = EXE_DIR / "runtime"
DATA_DIR = EXE_DIR / "data"
LOG_PATH = EXE_DIR / "launcher.log"
PYTHON_EXE = RUNTIME_DIR / "python.exe"
FLOWOS_EXE = RUNTIME_DIR / "Scripts" / "flowos.exe"


def _assets_dir() -> Path:
    """Directory PyInstaller bundled our icon/splash into."""
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / "assets"  # noqa: SLF001
    return Path(__file__).parent / "assets"


def log(message: str) -> None:
    try:
        EXE_DIR.mkdir(parents=True, exist_ok=True)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
    except OSError:
        pass  # logging is best-effort; never let it be the thing that crashes us


def fatal_error(message: str) -> None:
    """Last-resort error reporting that works even if our Tk UI never came up."""
    log(f"FATAL: {message}")
    try:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(APP_NAME, f"{message}\n\nSee {LOG_PATH} for details.")
        root.destroy()
    except Exception:  # noqa: BLE001
        pass  # if even Tk is broken, the log file is all we have left


def is_port_free(port: int, host: str = "127.0.0.1") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex((host, port)) != 0


def find_free_port(port: int) -> int:
    while not is_port_free(port):
        port += 1
    return port


class ProgressUI:
    """A single window: shows startup progress, then the running server's status."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("640x460")
        self.root.resizable(False, False)
        self.root.configure(bg="#0B1220")
        try:
            self.root.iconbitmap(str(_assets_dir() / "icon.ico"))
        except tk.TclError:
            pass

        self.banner_image = tk.PhotoImage(file=str(_assets_dir() / "splash.png"))
        tk.Label(self.root, image=self.banner_image, bd=0).pack()

        self.status_var = tk.StringVar(value="Preparing...")
        tk.Label(
            self.root,
            textvariable=self.status_var,
            bg="#0B1220",
            fg="#94A3B8",
            font=("Segoe UI", 10),
        ).pack(pady=(6, 4))

        self.progress = ttk.Progressbar(self.root, mode="indeterminate", length=480)
        self.progress.pack(pady=4)
        self.progress.start(12)

        self.action_button = tk.Button(
            self.root,
            text="Quit",
            command=self._on_close,
            bg="#1E293B",
            fg="#F8FAFC",
            activebackground="#334155",
            activeforeground="#F8FAFC",
            relief="flat",
            padx=16,
            pady=6,
        )
        self.action_button.pack(pady=10)
        self.action_button.pack_forget()  # hidden until the server is up

        self.on_quit = None
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._queue: queue.Queue = queue.Queue()
        self.root.after(100, self._poll_queue)

    def _on_close(self):
        if self.on_quit:
            self.on_quit()
        self.root.destroy()

    def set_status(self, text: str) -> None:
        self._queue.put(("status", text))

    def show_running(self, url: str) -> None:
        self._queue.put(("running", url))

    def show_error(self, text: str) -> None:
        self._queue.put(("error", text))

    def _poll_queue(self) -> None:
        try:
            while True:
                kind, payload = self._queue.get_nowait()
                if kind == "status":
                    self.status_var.set(payload)
                elif kind == "running":
                    self.progress.stop()
                    self.progress.pack_forget()
                    self.status_var.set(f"FlowOS is running at {payload}")
                    self.action_button.config(text="Stop FlowOS")
                    self.action_button.pack(pady=10)
                elif kind == "error":
                    self.progress.stop()
                    messagebox.showerror(APP_NAME, payload)
                    self.root.destroy()
        except queue.Empty:
            pass
        if self.root.winfo_exists():
            self.root.after(100, self._poll_queue)

    def run(self) -> None:
        self.root.mainloop()


def wait_for_health(port: int, ui: ProgressUI, process: subprocess.Popen) -> None:
    ui.set_status("Starting FlowOS server (first launch can take a minute)...")
    deadline = time.time() + HEALTH_TIMEOUT_SECONDS
    url = f"http://127.0.0.1:{port}/health"
    while time.time() < deadline:
        if process.poll() is not None:
            msg = f"FlowOS server exited unexpectedly (code {process.returncode}). See {LOG_PATH} for details."
            raise RuntimeError(msg)
        try:
            with urllib.request.urlopen(url, timeout=2) as resp:  # noqa: S310
                if resp.status == 200:
                    return
        except Exception:  # noqa: BLE001
            pass
        time.sleep(1)
    msg = f"FlowOS did not become ready within {HEALTH_TIMEOUT_SECONDS} seconds."
    raise TimeoutError(msg)


def main() -> None:
    if not FLOWOS_EXE.exists():
        fatal_error(f"FlowOS runtime not found at {FLOWOS_EXE}. Reinstall FlowOS.")
        return

    ui = ProgressUI()
    server_process: subprocess.Popen | None = None

    def stop_server() -> None:
        if server_process and server_process.poll() is None:
            server_process.terminate()

    ui.on_quit = stop_server

    def worker() -> None:
        nonlocal server_process
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            port = find_free_port(DEFAULT_PORT)
            ui.set_status("Starting FlowOS server...")
            with LOG_PATH.open("a", encoding="utf-8") as log_file:
                server_process = subprocess.Popen(  # noqa: S603
                    [str(FLOWOS_EXE), "run", "--host", "127.0.0.1", "--port", str(port)],
                    cwd=str(DATA_DIR),
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
                )

            wait_for_health(port, ui, server_process)

            url = f"http://127.0.0.1:{port}"
            webbrowser.open(url)
            ui.show_running(url)
        except Exception as exc:  # noqa: BLE001
            log(f"ERROR: {exc}\n{traceback.format_exc()}")
            ui.show_error(str(exc))

    threading.Thread(target=worker, daemon=True).start()
    ui.run()
    stop_server()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        # Belt-and-suspenders: if anything above main()'s own handling still
        # escapes (e.g. Tk itself fails to initialize), this is the last
        # chance to leave a trace instead of vanishing with no error at all.
        fatal_error(f"{exc}\n{traceback.format_exc()}")
