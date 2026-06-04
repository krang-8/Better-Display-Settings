# Better Display Settings

A small Windows display manager prototype.

## Features

- Detects connected display adapters and current resolution, refresh rate, position, and primary state.
- Shows attached monitors in the main display list instead of raw GPU/display-adapter entries.
- Uses EDID monitor names from Windows when available, such as `DELL S2522HG`, instead of generic PnP labels.
- Stores monitor hardware identity fields in profiles so saved layouts can be matched back to the same physical monitor when Windows display numbers move around.
- Saves the current monitor layout as named profiles.
- Edits saved profiles, including display position, resolution, refresh rate, apply selection, enabled/disabled monitor state, hotkey, and taskbar choices.
- Applies saved profiles with Windows display APIs.
- Registers optional global hotkeys while the app is running, such as `Ctrl+Alt+1`.
- Shows or hides Windows taskbar windows per active display.
- Retries and optionally keeps enforcing taskbar visibility while the app is open, which helps when Explorer recreates taskbar windows.
- Persists the last manually applied taskbar visibility selection by display name and monitor identity.
- Restores saved taskbar visibility shortly after app startup.
- Uses scrollable tables for monitors and profiles.

## Run

Double-click `run.bat`, or run:

```powershell
python .\display_manager.py
```

Profiles are stored beside the app in `display_profiles.json`.

## Workflow

1. Open the app.
2. Click `Save Current As...` to capture the current Windows display layout.
3. Select a profile and click `Edit Profile` to customize display coordinates, resolution, refresh rate, enabled monitor state, taskbar visibility, or hotkey.
4. Click `Apply Selected`, or use the configured hotkey while the app is running.
5. Use the taskbar checkboxes when you only want to update which screens show a taskbar.

In the profile editor:

- `Apply` controls whether the profile changes that display at all.
- `Enabled` controls whether the profile tries to attach or detach that display.
- `Taskbar` controls whether that display should show a taskbar after the profile is applied.
- The `Identity` column is a short hardware/device hint used for profile matching.

## Notes

- Hotkeys only work while the app is open.
- Per-screen taskbar control works by hiding or showing Windows taskbar windows. Explorer may recreate those windows after display changes, sign-in, or restart, so the app retries after each taskbar update and can keep enforcing the selected layout while it stays open.
- If a saved profile references a physical monitor that cannot be matched, the app warns and falls back to the saved Windows display name.
- Display resolution is read from the active Windows display mode, not the DPI-scaled monitor rectangle.
- Display profile application uses the built-in `ChangeDisplaySettingsExW` API. Resolution, position, color depth, refresh rate, primary display, and attach/detach requests are covered in this first version; some GPU/display-driver combinations may require a later `SetDisplayConfig` implementation for perfect enable/disable behavior.
- This repo is ready to push once an `origin` remote is configured. The current environment can push to a provided remote URL, but does not expose a GitHub repository creation tool.

## Test

```powershell
python -m unittest
```
