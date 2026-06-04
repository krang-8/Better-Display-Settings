# Better Display Settings

A small Windows display manager prototype.

## Features

- Detects connected display adapters and current resolution, refresh rate, position, and primary state.
- Saves the current monitor layout as named profiles.
- Applies saved profiles with Windows display APIs.
- Registers optional global hotkeys while the app is running, such as `Ctrl+Alt+1`.
- Shows or hides Windows taskbar windows per active display.

## Run

Double-click `run.bat`, or run:

```powershell
python .\display_manager.py
```

Profiles are stored beside the app in `display_profiles.json`.

## Notes

- Hotkeys only work while the app is open.
- Per-screen taskbar control works by hiding or showing Windows taskbar windows. Explorer may recreate those windows after display changes, sign-in, or restart, so reapply the setting from the app if needed.
- Display profile application uses the built-in `ChangeDisplaySettingsExW` API. Resolution, position, color depth, and refresh rate are covered in this first version; some GPU/display-driver combinations may require a later `SetDisplayConfig` implementation for perfect enable/disable behavior.
