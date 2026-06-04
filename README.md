# Better Display Settings

A small Windows display manager prototype.

## Features

- Detects connected display adapters and current resolution, refresh rate, position, and primary state.
- Shows attached monitors in the main display list instead of raw GPU/display-adapter entries.
- Uses EDID monitor names from Windows when available, such as `DELL S2522HG`, instead of generic PnP labels.
- Stores monitor hardware identity fields in profiles so saved layouts can be matched back to the same physical monitor when Windows display numbers move around.
- Repairs older saved profiles at startup by backfilling current monitor identities and removing stale zero-size adapter entries.
- Saves the current monitor layout as named profiles.
- Edits saved profiles, including display position, resolution, refresh rate, apply selection, enabled/disabled monitor state, hotkey, and taskbar choices.
- Duplicates saved profiles so variants like dual/triple monitor layouts are quicker to create.
- Applies saved profiles with Windows display APIs.
- Registers optional global hotkeys while the app is running, such as `Ctrl+Alt+1`.
- Shows whether each profile hotkey is registered, missing, invalid, or unavailable because Windows rejected it.
- Shows or hides Windows taskbar windows per active display.
- Shows current monitor/profile/taskbar state in a header summary so action results stay readable.
- Cancels pending taskbar retries when you apply a new taskbar selection or display profile, avoiding stacked delayed re-applies.
- Retries taskbar visibility only when Windows needs time to create a missing taskbar window or when the app just enabled Windows' multi-monitor taskbar setting.
- Only changes taskbar windows when Windows reports they are in the wrong visible/hidden state, reducing needless Explorer refreshes.
- Includes a taskbar diagnostics action that reports visible/hidden versus expected state per mapped display.
- Enables Windows' multi-monitor taskbar setting when a selected layout needs secondary taskbars, then reports if Explorer still has not created a desired taskbar window.
- Includes a manual profile repair action for saved profiles with stale monitor identities.
- Includes a reset action that shows taskbars everywhere and turns taskbar enforcement off.
- Persists the last manually applied taskbar visibility selection by display name and monitor identity.
- Keeps a `display_profiles.json.bak` backup before config writes and falls back to it if the main config cannot be read.
- Restores saved taskbar visibility shortly after app startup.
- Uses scrollable tables for monitors and profiles.
- Uses a modern dark dashboard layout with accent actions, status cards, and clearer profile/taskbar controls.

## Run

Double-click `run.bat`, or run:

```powershell
python .\display_manager.py
```

To launch without a console window, double-click `BetterDisplaySettings.pyw`.

Profiles are stored beside the app in `display_profiles.json`.

## Workflow

1. Open the app.
2. Click `Save Current As...` to capture the current Windows display layout.
3. Select a profile and click `Duplicate` if you want to start a variant from an existing layout.
4. Select a profile and click `Edit Profile` to customize display coordinates, resolution, refresh rate, enabled monitor state, taskbar visibility, or hotkey.
5. Click `Apply Selected`, or use the configured hotkey while the app is running.
6. Use the taskbar checkboxes when you only want to update which screens show a taskbar.
7. Use `Repair Profiles` if saved profiles still contain stale display entries after changing monitor hardware or ports.

In the profile editor:

- `Apply` controls whether the profile changes that display at all.
- `Enabled` controls whether the profile tries to attach or detach that display.
- `Taskbar` controls whether that display should show a taskbar after the profile is applied.
- The `Identity` column is a short hardware/device hint used for profile matching.

## Notes

- Hotkeys only work while the app is open.
- If a hotkey shows as `unavailable`, another app or Windows has already reserved it.
- Per-screen taskbar control works by hiding or showing Windows taskbar windows. Explorer may recreate those windows after display changes, sign-in, or restart, so the app can keep enforcing the selected layout while it stays open.
- Use `Diagnose` if taskbar state looks wrong; it reports what Windows currently exposes for each taskbar window.
- If `Diagnose` reports missing desired taskbars, Explorer has not exposed a taskbar window for that display yet. The app enables Windows' multi-monitor taskbar setting automatically when needed.
- Use `Reset` if taskbar state gets confusing; it shows all taskbars and disables enforcement so Windows returns to a safe baseline.
- If a saved profile references a physical monitor that cannot be matched, the app warns and falls back to the saved Windows display name.
- Display resolution is read from the active Windows display mode, not the DPI-scaled monitor rectangle.
- Display profile application uses the built-in `ChangeDisplaySettingsExW` API. Resolution, position, color depth, refresh rate, primary display, and attach/detach requests are covered in this first version; some GPU/display-driver combinations may require a later `SetDisplayConfig` implementation for perfect enable/disable behavior.

## Test

```powershell
python -m unittest
```
