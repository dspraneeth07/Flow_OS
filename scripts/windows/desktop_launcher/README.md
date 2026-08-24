# FlowOS.exe (Windows desktop launcher)

A small (~11MB) Windows launcher you can hand to users who don't have Python
installed. It is not a frozen copy of the whole FlowOS backend — the backend
and its ~3GB of AI/ML dependencies are far too large and fragile to freeze
reliably with PyInstaller. Instead, `FlowOS.exe` is a thin bootstrapper:

1. First run: shows a FlowOS-branded window, downloads a standalone
   ("embeddable") Python runtime into `%LOCALAPPDATA%\FlowOS\runtime`, bootstraps
   pip, then `pip install`s the `flowos` package into that runtime. Progress
   (download %, current step) is shown live in the window.
2. Every run: starts `flowos run` from that runtime, waits for the `/health`
   endpoint, opens the default browser to the running app, then shows a
   "FlowOS is running" status window with a Stop button.
3. Later runs skip straight to step 2 — no re-download.

Nothing under `%LOCALAPPDATA%\FlowOS` is touched by the exe itself once
installed; deleting that folder fully uninstalls FlowOS.

## Building

Requires this repo's `.venv` to already exist (`make init` from the repo root).

```powershell
cd scripts\windows\desktop_launcher
.\build.ps1
```

Output: `scripts\windows\desktop_launcher\dist\FlowOS.exe`. That single file is
what you send to users — no installer, no admin rights required.

## Assets

- `assets/icon.ico` — multi-resolution app icon, generated from
  `src/frontend/public/favicon.ico` (the FlowOS mark).
- `assets/splash.png` — the FlowOS logo + wordmark shown in the launcher
  window while it installs/starts.

Regenerate either if the FlowOS brand mark changes; both are plain
raster images, no build step needed beyond dropping in new files of the
same name.

## Known limitations

- **Unsigned.** Windows SmartScreen will warn on first launch ("Windows
  protected your PC") until this is signed with a code-signing certificate.
  Users click "More info" → "Run anyway".
- **Needs internet on first run.** It downloads Python (~10MB) and the
  `flowos` package (~3GB, since it bundles all supported integrations). There
  is no offline/bundled-dependencies mode — see the "heavy onedir bundle"
  alternative discussed with the team if that's ever needed instead.
- **Windows only.** The embeddable Python distribution and `.exe` packaging
  are Windows-specific; macOS/Linux would need a different launcher.
