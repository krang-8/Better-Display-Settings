# Better Display Settings

A small Windows display manager prototype.

## Features

- Detects connected display adapters and current resolution, refresh rate, position, and primary state.
- Saves the current monitor layout as named profiles.
- Edits saved profiles, including display position, resolution, refresh rate, active/apply selection, hotkey, and taskbar choices.
- Applies saved profiles with Windows display APIs.
- Registers optional global hotkeys while the app is running, such as `Ctrl+Alt+1`.
- Shows or hides Windows taskbar windows per active display.
- Persists the last manually applied taskbar visibility selection.

## Run

Double-click `run.bat`, or run:

```powershell
python .\display_manager.py
```

Profiles are stored beside the app in `display_profiles.json`.

## Workflow

1. Open the app.
2. Click `Save Current As...` to capture the current Windows display layout.
3. Select a profile and click `Edit Profile` to customize display coordinates, resolution, refresh rate, taskbar visibility, or hotkey.
4. Click `Apply Selected`, or use the configured hotkey while the app is running.
5. Use the taskbar checkboxes when you only want to update which screens show a taskbar.

## Notes

- Hotkeys only work while the app is open.
- Per-screen taskbar control works by hiding or showing Windows taskbar windows. Explorer may recreate those windows after display changes, sign-in, or restart, so reapply the setting from the app if needed.
- Display profile application uses the built-in `ChangeDisplaySettingsExW` API. Resolution, position, color depth, and refresh rate are covered in this first version; some GPU/display-driver combinations may require a later `SetDisplayConfig` implementation for perfect enable/disable behavior.
- This repo is ready to push once an `origin` remote is configured.
