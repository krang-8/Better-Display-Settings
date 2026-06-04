import ctypes
import json
import queue
import threading
import tkinter as tk
from ctypes import wintypes
from dataclasses import dataclass, asdict
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk


APP_TITLE = "Better Display Settings"
CONFIG_PATH = Path(__file__).with_name("display_profiles.json")

CCHDEVICENAME = 32
CCHFORMNAME = 32

DISPLAY_DEVICE_ACTIVE = 0x00000001
DISPLAY_DEVICE_PRIMARY_DEVICE = 0x00000004

ENUM_CURRENT_SETTINGS = -1
ENUM_REGISTRY_SETTINGS = -2

DM_BITSPERPEL = 0x00040000
DM_PELSWIDTH = 0x00080000
DM_PELSHEIGHT = 0x00100000
DM_DISPLAYFLAGS = 0x00200000
DM_DISPLAYFREQUENCY = 0x00400000
DM_POSITION = 0x00000020

CDS_UPDATEREGISTRY = 0x00000001
CDS_SET_PRIMARY = 0x00000010
CDS_NORESET = 0x10000000
DISP_CHANGE_SUCCESSFUL = 0
MONITORINFOF_PRIMARY = 0x00000001

SW_HIDE = 0
SW_SHOW = 5

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
WM_HOTKEY = 0x0312
WM_QUIT = 0x0012


user32 = ctypes.WinDLL("user32", use_last_error=True)


class POINTL(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wintypes.WCHAR * CCHDEVICENAME),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        ("dmPosition", POINTL),
        ("dmDisplayOrientation", wintypes.DWORD),
        ("dmDisplayFixedOutput", wintypes.DWORD),
        ("dmColor", wintypes.SHORT),
        ("dmDuplex", wintypes.SHORT),
        ("dmYResolution", wintypes.SHORT),
        ("dmTTOption", wintypes.SHORT),
        ("dmCollate", wintypes.SHORT),
        ("dmFormName", wintypes.WCHAR * CCHFORMNAME),
        ("dmLogPixels", wintypes.WORD),
        ("dmBitsPerPel", wintypes.DWORD),
        ("dmPelsWidth", wintypes.DWORD),
        ("dmPelsHeight", wintypes.DWORD),
        ("dmDisplayFlags", wintypes.DWORD),
        ("dmDisplayFrequency", wintypes.DWORD),
        ("dmICMMethod", wintypes.DWORD),
        ("dmICMIntent", wintypes.DWORD),
        ("dmMediaType", wintypes.DWORD),
        ("dmDitherType", wintypes.DWORD),
        ("dmReserved1", wintypes.DWORD),
        ("dmReserved2", wintypes.DWORD),
        ("dmPanningWidth", wintypes.DWORD),
        ("dmPanningHeight", wintypes.DWORD),
    ]


class DISPLAY_DEVICEW(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("DeviceName", wintypes.WCHAR * 32),
        ("DeviceString", wintypes.WCHAR * 128),
        ("StateFlags", wintypes.DWORD),
        ("DeviceID", wintypes.WCHAR * 128),
        ("DeviceKey", wintypes.WCHAR * 128),
    ]


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]


class MONITORINFOEXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", RECT),
        ("rcWork", RECT),
        ("dwFlags", wintypes.DWORD),
        ("szDevice", wintypes.WCHAR * CCHDEVICENAME),
    ]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", POINTL),
    ]


EnumDisplayDevicesW = user32.EnumDisplayDevicesW
EnumDisplayDevicesW.argtypes = [
    wintypes.LPCWSTR,
    wintypes.DWORD,
    ctypes.POINTER(DISPLAY_DEVICEW),
    wintypes.DWORD,
]
EnumDisplayDevicesW.restype = wintypes.BOOL

EnumDisplaySettingsW = user32.EnumDisplaySettingsW
EnumDisplaySettingsW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD, ctypes.POINTER(DEVMODEW)]
EnumDisplaySettingsW.restype = wintypes.BOOL

ChangeDisplaySettingsExW = user32.ChangeDisplaySettingsExW
ChangeDisplaySettingsExW.argtypes = [
    wintypes.LPCWSTR,
    ctypes.POINTER(DEVMODEW),
    wintypes.HWND,
    wintypes.DWORD,
    wintypes.LPVOID,
]
ChangeDisplaySettingsExW.restype = wintypes.LONG

MonitorEnumProc = ctypes.WINFUNCTYPE(
    wintypes.BOOL,
    wintypes.HANDLE,
    wintypes.HDC,
    ctypes.POINTER(RECT),
    wintypes.LPARAM,
)
EnumDisplayMonitors = user32.EnumDisplayMonitors
EnumDisplayMonitors.argtypes = [wintypes.HDC, ctypes.POINTER(RECT), MonitorEnumProc, wintypes.LPARAM]
EnumDisplayMonitors.restype = wintypes.BOOL
GetMonitorInfoW = user32.GetMonitorInfoW
GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MONITORINFOEXW)]
GetMonitorInfoW.restype = wintypes.BOOL

EnumWindows = user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
GetClassNameW = user32.GetClassNameW
GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
GetClassNameW.restype = ctypes.c_int
GetWindowRect = user32.GetWindowRect
GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
GetWindowRect.restype = wintypes.BOOL
ShowWindow = user32.ShowWindow
ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
ShowWindow.restype = wintypes.BOOL
RegisterHotKey = user32.RegisterHotKey
RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
RegisterHotKey.restype = wintypes.BOOL
UnregisterHotKey = user32.UnregisterHotKey
UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
UnregisterHotKey.restype = wintypes.BOOL
GetMessageW = user32.GetMessageW
GetMessageW.argtypes = [ctypes.POINTER(MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
GetMessageW.restype = wintypes.BOOL
PostThreadMessageW = user32.PostThreadMessageW
PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
PostThreadMessageW.restype = wintypes.BOOL
GetCurrentThreadId = ctypes.WinDLL("kernel32", use_last_error=True).GetCurrentThreadId
GetCurrentThreadId.restype = wintypes.DWORD
VkKeyScanW = user32.VkKeyScanW
VkKeyScanW.argtypes = [wintypes.WCHAR]
VkKeyScanW.restype = wintypes.SHORT


@dataclass
class DisplayInfo:
    device_name: str
    label: str
    monitor_id: str
    monitor_key: str
    active: bool
    primary: bool
    x: int
    y: int
    width: int
    height: int
    frequency: int
    bits_per_pixel: int


class DisplayController:
    def list_displays(self):
        displays = []
        seen_devices = set()

        def callback(hmonitor, _hdc, _rect, _data):
            info = MONITORINFOEXW()
            info.cbSize = ctypes.sizeof(info)
            if not GetMonitorInfoW(hmonitor, ctypes.byref(info)):
                return True

            device_name = info.szDevice
            if not device_name or device_name in seen_devices:
                return True
            seen_devices.add(device_name)

            mode = DEVMODEW()
            mode.dmSize = ctypes.sizeof(mode)
            has_mode = EnumDisplaySettingsW(device_name, ENUM_CURRENT_SETTINGS, ctypes.byref(mode))
            monitor_name, monitor_id, monitor_key = self._monitor_metadata(device_name)

            displays.append(
                DisplayInfo(
                    device_name=device_name,
                    label=f"{device_name} - {monitor_name}",
                    monitor_id=monitor_id,
                    monitor_key=monitor_key,
                    active=True,
                    primary=bool(info.dwFlags & MONITORINFOF_PRIMARY),
                    x=int(info.rcMonitor.left),
                    y=int(info.rcMonitor.top),
                    width=int(info.rcMonitor.right - info.rcMonitor.left),
                    height=int(info.rcMonitor.bottom - info.rcMonitor.top),
                    frequency=int(mode.dmDisplayFrequency) if has_mode else 0,
                    bits_per_pixel=int(mode.dmBitsPerPel) if has_mode else 32,
                )
            )
            return True

        EnumDisplayMonitors(None, None, MonitorEnumProc(callback), 0)
        return displays

    def _monitor_metadata(self, device_name):
        adapter = DISPLAY_DEVICEW()
        adapter.cb = ctypes.sizeof(adapter)
        if EnumDisplayDevicesW(device_name, 0, ctypes.byref(adapter), 0):
            return adapter.DeviceString or device_name, adapter.DeviceID, adapter.DeviceKey
        return device_name, "", ""

    def apply_profile(self, profile):
        errors = []
        current_displays = self.list_displays()
        for display in profile.get("displays", []):
            if not display.get("apply", True):
                continue
            device, matched = self._resolve_device_name(display, current_displays)
            if not matched and (display.get("monitor_id") or display.get("monitor_key")):
                errors.append(f"{display.get('label', device)}: physical monitor not currently matched")
            mode = DEVMODEW()
            mode.dmSize = ctypes.sizeof(mode)
            if not self._load_mode(device, mode):
                errors.append(f"{device}: unable to read current or registry settings")
                continue

            mode.dmFields = DM_POSITION | DM_PELSWIDTH | DM_PELSHEIGHT | DM_BITSPERPEL
            enabled = display.get("enabled", display.get("active", True))
            mode.dmPosition.x = int(display.get("x", 0)) if enabled else 0
            mode.dmPosition.y = int(display.get("y", 0)) if enabled else 0
            mode.dmPelsWidth = int(display.get("width", 0)) if enabled else 0
            mode.dmPelsHeight = int(display.get("height", 0)) if enabled else 0
            mode.dmBitsPerPel = int(display.get("bits_per_pixel", 32))
            frequency = int(display.get("frequency", 0))
            if enabled and frequency:
                mode.dmFields |= DM_DISPLAYFREQUENCY
                mode.dmDisplayFrequency = frequency

            flags = CDS_UPDATEREGISTRY | CDS_NORESET
            if enabled and display.get("primary", False):
                flags |= CDS_SET_PRIMARY

            result = ChangeDisplaySettingsExW(
                device,
                ctypes.byref(mode),
                None,
                flags,
                None,
            )
            if result != DISP_CHANGE_SUCCESSFUL:
                errors.append(f"{device}: ChangeDisplaySettingsEx returned {result}")

        final_result = ChangeDisplaySettingsExW(None, None, None, 0, None)
        if final_result != DISP_CHANGE_SUCCESSFUL:
            errors.append(f"final apply returned {final_result}")
        return errors

    def _resolve_device_name(self, display, current_displays):
        monitor_id = display.get("monitor_id", "")
        monitor_key = display.get("monitor_key", "")
        for current in current_displays:
            if monitor_id and current.monitor_id == monitor_id:
                return current.device_name, True
            if monitor_key and current.monitor_key == monitor_key:
                return current.device_name, True
        return display["device_name"], False

    def _load_mode(self, device, mode):
        if EnumDisplaySettingsW(device, ENUM_CURRENT_SETTINGS, ctypes.byref(mode)):
            return True
        return bool(EnumDisplaySettingsW(device, ENUM_REGISTRY_SETTINGS, ctypes.byref(mode)))


class TaskbarController:
    TASKBAR_CLASSES = {"Shell_TrayWnd", "Shell_SecondaryTrayWnd"}

    def list_taskbars(self, displays):
        taskbars = []

        def callback(hwnd, _):
            buffer = ctypes.create_unicode_buffer(256)
            GetClassNameW(hwnd, buffer, len(buffer))
            class_name = buffer.value
            if class_name not in self.TASKBAR_CLASSES:
                return True

            rect = RECT()
            if not GetWindowRect(hwnd, ctypes.byref(rect)):
                return True

            display = self._match_display(rect, displays)
            taskbars.append(
                {
                    "hwnd": hwnd,
                    "class_name": class_name,
                    "rect": (rect.left, rect.top, rect.right, rect.bottom),
                    "device_name": display.device_name if display else None,
                }
            )
            return True

        EnumWindows(EnumWindowsProc(callback), 0)
        return taskbars

    def apply_visibility(self, visible_device_names, displays):
        visible = set(visible_device_names)
        changed = 0
        for taskbar in self.list_taskbars(displays):
            device_name = taskbar["device_name"]
            if device_name is None:
                continue
            ShowWindow(taskbar["hwnd"], SW_SHOW if device_name in visible else SW_HIDE)
            changed += 1
        return changed

    def _match_display(self, rect, displays):
        best_display = None
        best_overlap = 0
        for display in displays:
            if not display.active:
                continue
            left = max(rect.left, display.x)
            top = max(rect.top, display.y)
            right = min(rect.right, display.x + display.width)
            bottom = min(rect.bottom, display.y + display.height)
            overlap = max(0, right - left) * max(0, bottom - top)
            if overlap > best_overlap:
                best_overlap = overlap
                best_display = display
        return best_display


class HotkeyManager:
    def __init__(self, event_queue):
        self.event_queue = event_queue
        self.thread = None
        self.thread_id = None
        self.hotkeys = {}
        self.ready = threading.Event()

    def start(self, profiles):
        self.stop()
        self.ready.clear()
        self.thread = threading.Thread(target=self._run, args=(profiles,), daemon=True)
        self.thread.start()
        self.ready.wait(timeout=2)

    def stop(self):
        if self.thread and self.thread.is_alive() and self.thread_id:
            PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)
            self.thread.join(timeout=2)
        self.thread = None
        self.thread_id = None
        self.hotkeys = {}

    def _run(self, profiles):
        self.thread_id = GetCurrentThreadId()
        registered = []
        hotkey_id = 100
        for profile in profiles:
            hotkey = profile.get("hotkey", "").strip()
            parsed = parse_hotkey(hotkey)
            if not parsed:
                continue
            modifiers, vk = parsed
            if RegisterHotKey(None, hotkey_id, modifiers, vk):
                self.hotkeys[hotkey_id] = profile["name"]
                registered.append(hotkey_id)
                hotkey_id += 1

        self.ready.set()
        msg = MSG()
        while GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            if msg.message == WM_HOTKEY:
                profile_name = self.hotkeys.get(int(msg.wParam))
                if profile_name:
                    self.event_queue.put(profile_name)

        for registered_id in registered:
            UnregisterHotKey(None, registered_id)


def parse_hotkey(text):
    if not text:
        return None
    parts = [part.strip().upper() for part in text.replace(" ", "").split("+") if part.strip()]
    if not parts:
        return None

    modifiers = 0
    key = None
    for part in parts:
        if part in {"CTRL", "CONTROL"}:
            modifiers |= MOD_CONTROL
        elif part == "ALT":
            modifiers |= MOD_ALT
        elif part == "SHIFT":
            modifiers |= MOD_SHIFT
        elif part in {"WIN", "WINDOWS"}:
            modifiers |= MOD_WIN
        else:
            key = part

    if not key:
        return None
    if key.startswith("F") and key[1:].isdigit():
        number = int(key[1:])
        if 1 <= number <= 24:
            return modifiers, 0x6F + number
    if len(key) == 1:
        vk = VkKeyScanW(key)
        if vk != -1:
            return modifiers, vk & 0xFF
    if key.isdigit() and len(key) == 1:
        return modifiers, ord(key)
    return None


def load_config():
    if not CONFIG_PATH.exists():
        return {"profiles": []}
    try:
        return normalize_config(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return {"profiles": []}


def normalize_config(config):
    config.setdefault("profiles", [])
    for profile in config["profiles"]:
        profile.setdefault("hotkey", "")
        profile.setdefault("taskbar_visible_displays", [])
        profile.setdefault("taskbar_visible_monitors", [])
        for display in profile.get("displays", []):
            display.setdefault("apply", True)
            display.setdefault("enabled", display.get("active", True))
            display.setdefault("monitor_id", "")
            display.setdefault("monitor_key", "")
    return config


def save_config(config):
    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")


def display_to_profile_entry(display):
    entry = asdict(display)
    entry["apply"] = True
    entry["enabled"] = display.active
    return entry


def profile_summary(profile):
    displays = profile.get("displays", [])
    applied = [display for display in displays if display.get("apply", True)]
    enabled = [display for display in applied if display.get("enabled", display.get("active", True))]
    disabled = [display for display in applied if not display.get("enabled", display.get("active", True))]
    taskbar_count = len(taskbar_visible_entries(profile, enabled))
    return {
        "enabled": f"{len(enabled)} on",
        "disabled": f"{len(disabled)} off",
        "taskbars": f"{taskbar_count} taskbar",
    }


def taskbar_visible_entries(source, displays):
    visible_devices = set(source.get("taskbar_visible_displays", []))
    visible_monitors = set(source.get("taskbar_visible_monitors", []))
    return [
        display
        for display in displays
        if display_value(display, "device_name") in visible_devices
        or display_value(display, "monitor_id") in visible_monitors
        or display_value(display, "monitor_key") in visible_monitors
    ]


def taskbar_visibility_payload(displays):
    return {
        "taskbar_visible_displays": [display_value(display, "device_name") for display in displays],
        "taskbar_visible_monitors": [
            display_value(display, "monitor_id") or display_value(display, "monitor_key")
            for display in displays
            if display_value(display, "monitor_id") or display_value(display, "monitor_key")
        ],
    }


def display_value(display, key, default=""):
    if isinstance(display, dict):
        return display.get(key, default)
    return getattr(display, key, default)


def short_identity(identity):
    if not identity:
        return "-"
    tail = identity.replace("\\", "/").split("/")[-1]
    return tail[-28:] if len(tail) > 28 else tail


class ProfileEditorDialog(tk.Toplevel):
    def __init__(self, parent, profile):
        super().__init__(parent)
        self.title("Edit Display Profile")
        self.transient(parent)
        self.grab_set()
        self.resizable(True, True)
        self.result = None
        self.profile = json.loads(json.dumps(profile))
        self.rows = []

        self._build_ui()
        self.wait_window(self)

    def _build_ui(self):
        root = ttk.Frame(self, padding=12)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(2, weight=1)

        ttk.Label(root, text="Name").grid(row=0, column=0, sticky="w", padx=(0, 8), pady=(0, 8))
        self.name_var = tk.StringVar(value=self.profile.get("name", ""))
        ttk.Entry(root, textvariable=self.name_var).grid(row=0, column=1, sticky="ew", pady=(0, 8))

        ttk.Label(root, text="Hotkey").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=(0, 10))
        self.hotkey_var = tk.StringVar(value=self.profile.get("hotkey", ""))
        ttk.Entry(root, textvariable=self.hotkey_var).grid(row=1, column=1, sticky="ew", pady=(0, 10))

        table_frame = ttk.Frame(root)
        table_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        for index in range(9):
            table_frame.columnconfigure(index, weight=1 if index == 1 else 0)

        headers = ("Apply", "Enabled", "Display", "X", "Y", "Width", "Height", "Hz", "Taskbar")
        for column, text in enumerate(headers):
            ttk.Label(table_frame, text=text, font=("Segoe UI", 9, "bold")).grid(
                row=0, column=column, sticky="w", padx=4, pady=(0, 4)
            )

        visible_taskbars = set(self.profile.get("taskbar_visible_displays", []))
        visible_monitors = set(self.profile.get("taskbar_visible_monitors", []))
        for row_index, display in enumerate(self.profile.get("displays", []), start=1):
            apply_var = tk.BooleanVar(value=bool(display.get("apply", True)))
            enabled_var = tk.BooleanVar(value=bool(display.get("enabled", display.get("active", True))))
            taskbar_var = tk.BooleanVar(
                value=display.get("device_name") in visible_taskbars
                or display.get("monitor_id") in visible_monitors
                or display.get("monitor_key") in visible_monitors
            )
            values = {
                "x": tk.StringVar(value=str(display.get("x", 0))),
                "y": tk.StringVar(value=str(display.get("y", 0))),
                "width": tk.StringVar(value=str(display.get("width", 0))),
                "height": tk.StringVar(value=str(display.get("height", 0))),
                "frequency": tk.StringVar(value=str(display.get("frequency", 0))),
            }

            ttk.Checkbutton(table_frame, variable=apply_var).grid(row=row_index, column=0, padx=4, pady=2)
            ttk.Checkbutton(table_frame, variable=enabled_var).grid(row=row_index, column=1, padx=4, pady=2)
            identity = short_identity(display.get("monitor_id", ""))
            label = display.get("label", display.get("device_name", ""))
            if identity != "-":
                label = f"{label} [{identity}]"
            ttk.Label(table_frame, text=label).grid(
                row=row_index, column=2, sticky="w", padx=4, pady=2
            )
            ttk.Entry(table_frame, textvariable=values["x"], width=7).grid(row=row_index, column=3, padx=4, pady=2)
            ttk.Entry(table_frame, textvariable=values["y"], width=7).grid(row=row_index, column=4, padx=4, pady=2)
            ttk.Entry(table_frame, textvariable=values["width"], width=8).grid(
                row=row_index, column=5, padx=4, pady=2
            )
            ttk.Entry(table_frame, textvariable=values["height"], width=8).grid(
                row=row_index, column=6, padx=4, pady=2
            )
            ttk.Entry(table_frame, textvariable=values["frequency"], width=7).grid(
                row=row_index, column=7, padx=4, pady=2
            )
            ttk.Checkbutton(table_frame, variable=taskbar_var).grid(row=row_index, column=8, padx=4, pady=2)
            self.rows.append(
                {
                    "display": display,
                    "apply": apply_var,
                    "enabled": enabled_var,
                    "taskbar": taskbar_var,
                    "values": values,
                }
            )

        buttons = ttk.Frame(root)
        buttons.grid(row=3, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(buttons, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)
        ttk.Button(buttons, text="Save", command=self._save).pack(side=tk.RIGHT, padx=(0, 8))

    def _save(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Profile Name Required", "Enter a profile name.", parent=self)
            return

        hotkey = self.hotkey_var.get().strip()
        if hotkey and not parse_hotkey(hotkey):
            messagebox.showwarning(
                "Unsupported Hotkey",
                "Use combinations like Ctrl+Alt+1, Ctrl+Shift+F9, or Win+Alt+2.",
                parent=self,
            )
            return

        updated_displays = []
        visible_taskbars = []
        visible_taskbar_entries = []
        for row in self.rows:
            display = dict(row["display"])
            display["apply"] = row["apply"].get()
            display["enabled"] = row["enabled"].get()
            try:
                for key, variable in row["values"].items():
                    display[key] = int(variable.get())
            except ValueError:
                messagebox.showwarning("Invalid Display Value", "Display values must be whole numbers.", parent=self)
                return
            if display["apply"] and display["enabled"] and (display["width"] <= 0 or display["height"] <= 0):
                messagebox.showwarning(
                    "Invalid Resolution",
                    "Enabled displays need a width and height greater than zero.",
                    parent=self,
                )
                return
            if display["apply"] and display["enabled"] and row["taskbar"].get():
                visible_taskbars.append(display["device_name"])
                visible_taskbar_entries.append(display)
            updated_displays.append(display)

        visibility = taskbar_visibility_payload(visible_taskbar_entries)
        self.result = {
            "name": name,
            "hotkey": hotkey,
            "displays": updated_displays,
            "taskbar_visible_displays": visible_taskbars,
            "taskbar_visible_monitors": visibility["taskbar_visible_monitors"],
        }
        self.destroy()


class DisplayManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1080x700")
        self.minsize(980, 600)

        self.display_controller = DisplayController()
        self.taskbar_controller = TaskbarController()
        self.hotkey_events = queue.Queue()
        self.hotkeys = HotkeyManager(self.hotkey_events)
        self.config = load_config()
        self.displays = []
        self.taskbar_vars = {}
        self.enforce_taskbars_var = tk.BooleanVar(
            value=bool(self.config.get("enforce_taskbar_visibility", True))
        )

        self._build_ui()
        self.refresh_displays()
        self.refresh_profiles()
        self.after(200, self._poll_hotkeys)
        self.after(750, self._reapply_saved_taskbar_visibility)
        self.after(2500, self._taskbar_enforcement_loop)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        root = ttk.Frame(self, padding=14)
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(0, weight=1)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(1, weight=1)

        heading = ttk.Label(root, text=APP_TITLE, font=("Segoe UI", 18, "bold"))
        heading.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 12))

        display_frame = ttk.LabelFrame(root, text="Displays", padding=10)
        display_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        display_frame.rowconfigure(0, weight=1)
        display_frame.columnconfigure(0, weight=1)

        columns = ("monitor", "state", "position", "resolution", "refresh", "identity")
        self.display_tree = ttk.Treeview(display_frame, columns=columns, show="headings", height=10)
        for column, width in {
            "monitor": 260,
            "state": 90,
            "position": 110,
            "resolution": 110,
            "refresh": 80,
            "identity": 160,
        }.items():
            self.display_tree.heading(column, text=column.title())
            self.display_tree.column(column, width=width, anchor="w")
        self.display_tree.grid(row=0, column=0, sticky="nsew")
        display_scroll_y = ttk.Scrollbar(display_frame, orient=tk.VERTICAL, command=self.display_tree.yview)
        display_scroll_y.grid(row=0, column=1, sticky="ns")
        display_scroll_x = ttk.Scrollbar(display_frame, orient=tk.HORIZONTAL, command=self.display_tree.xview)
        display_scroll_x.grid(row=1, column=0, sticky="ew")
        self.display_tree.configure(yscrollcommand=display_scroll_y.set, xscrollcommand=display_scroll_x.set)

        display_buttons = ttk.Frame(display_frame)
        display_buttons.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(display_buttons, text="Refresh", command=self.refresh_displays).pack(side=tk.LEFT)

        profile_frame = ttk.LabelFrame(root, text="Display Profiles", padding=10)
        profile_frame.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        profile_frame.rowconfigure(0, weight=1)
        profile_frame.columnconfigure(0, weight=1)

        profile_columns = ("name", "hotkey", "enabled", "disabled", "taskbars")
        self.profile_tree = ttk.Treeview(profile_frame, columns=profile_columns, show="headings", height=10)
        for column, width in {
            "name": 170,
            "hotkey": 110,
            "enabled": 70,
            "disabled": 70,
            "taskbars": 90,
        }.items():
            self.profile_tree.heading(column, text=column.title())
            self.profile_tree.column(column, width=width, anchor="w")
        self.profile_tree.grid(row=0, column=0, sticky="nsew")
        profile_scroll_y = ttk.Scrollbar(profile_frame, orient=tk.VERTICAL, command=self.profile_tree.yview)
        profile_scroll_y.grid(row=0, column=1, sticky="ns")
        profile_scroll_x = ttk.Scrollbar(profile_frame, orient=tk.HORIZONTAL, command=self.profile_tree.xview)
        profile_scroll_x.grid(row=1, column=0, sticky="ew")
        self.profile_tree.configure(yscrollcommand=profile_scroll_y.set, xscrollcommand=profile_scroll_x.set)

        profile_buttons = ttk.Frame(profile_frame)
        profile_buttons.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(profile_buttons, text="Save Current As...", command=self.save_current_profile).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(profile_buttons, text="Apply Selected", command=self.apply_selected_profile).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(profile_buttons, text="Edit Profile", command=self.edit_selected_profile).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(profile_buttons, text="Delete", command=self.delete_selected_profile).pack(side=tk.LEFT)

        taskbar_frame = ttk.LabelFrame(root, text="Taskbar Visibility Per Display", padding=10)
        taskbar_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(14, 0))
        taskbar_frame.columnconfigure(0, weight=1)

        self.taskbar_checks = ttk.Frame(taskbar_frame)
        self.taskbar_checks.grid(row=0, column=0, sticky="ew")

        taskbar_buttons = ttk.Frame(taskbar_frame)
        taskbar_buttons.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        ttk.Button(taskbar_buttons, text="Apply Taskbar Visibility", command=self.apply_taskbar_visibility).pack(
            side=tk.LEFT, padx=(0, 6)
        )
        ttk.Button(taskbar_buttons, text="Show Taskbar Everywhere", command=self.show_taskbar_everywhere).pack(
            side=tk.LEFT
        )
        ttk.Button(taskbar_buttons, text="Refresh Taskbars", command=self.refresh_taskbar_status).pack(
            side=tk.LEFT, padx=(6, 0)
        )
        ttk.Checkbutton(
            taskbar_buttons,
            text="Keep enforced",
            variable=self.enforce_taskbars_var,
            command=self._save_taskbar_enforcement_setting,
        ).pack(side=tk.LEFT, padx=(12, 0))

        self.status = ttk.Label(root, text="", anchor="w")
        self.status.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def refresh_displays(self):
        self.displays = self.display_controller.list_displays()
        self.display_tree.delete(*self.display_tree.get_children())
        for display in self.displays:
            state = "Primary" if display.primary else "Active" if display.active else "Inactive"
            self.display_tree.insert(
                "",
                tk.END,
                values=(
                    display.label,
                    state,
                    f"{display.x}, {display.y}",
                    f"{display.width} x {display.height}" if display.active else "-",
                    f"{display.frequency} Hz" if display.frequency else "-",
                    short_identity(display.monitor_id),
                ),
            )
        self._rebuild_taskbar_checks()
        self.refresh_taskbar_status()

    def refresh_profiles(self):
        self.profile_tree.delete(*self.profile_tree.get_children())
        for index, profile in enumerate(self.config.get("profiles", [])):
            hotkey = profile.get("hotkey") or "no hotkey"
            summary = profile_summary(profile)
            self.profile_tree.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    profile["name"],
                    hotkey,
                    summary["enabled"],
                    summary["disabled"],
                    summary["taskbars"],
                ),
            )
        self.hotkeys.start(self.config.get("profiles", []))

    def save_current_profile(self):
        name = simpledialog.askstring("Save Profile", "Profile name:", parent=self)
        if not name:
            return
        hotkey = simpledialog.askstring(
            "Profile Hotkey",
            "Optional hotkey, for example Ctrl+Alt+1:",
            parent=self,
        )
        if hotkey and not parse_hotkey(hotkey):
            messagebox.showwarning(
                "Unsupported Hotkey",
                "Use combinations like Ctrl+Alt+1, Ctrl+Shift+F9, or Win+Alt+2.",
                parent=self,
            )
            return
        profile = {
            "name": name.strip(),
            "hotkey": (hotkey or "").strip(),
            "displays": [display_to_profile_entry(display) for display in self.displays],
        }
        profile.update(taskbar_visibility_payload(self._current_taskbar_visible_selection()))
        profiles = [item for item in self.config.get("profiles", []) if item["name"] != profile["name"]]
        profiles.append(profile)
        self.config["profiles"] = profiles
        save_config(self.config)
        self.refresh_profiles()
        self._set_status(f"Saved profile '{profile['name']}'.")

    def edit_selected_profile(self):
        profile = self._selected_profile()
        if not profile:
            return
        dialog = ProfileEditorDialog(self, profile)
        if not dialog.result:
            return
        profiles = [
            item for item in self.config.get("profiles", []) if item["name"] != profile["name"]
        ]
        profiles.append(dialog.result)
        self.config["profiles"] = profiles
        save_config(self.config)
        self.refresh_profiles()
        self._set_status(f"Updated profile '{dialog.result['name']}'.")

    def apply_selected_profile(self):
        profile = self._selected_profile()
        if not profile:
            return
        self.apply_profile(profile)

    def apply_profile(self, profile):
        errors = self.display_controller.apply_profile(profile)
        self.refresh_displays()
        if "taskbar_visible_displays" in profile or "taskbar_visible_monitors" in profile:
            visible = self._resolve_taskbar_visible_devices(profile)
            self.config["taskbar_visible_displays"] = visible
            self.config["taskbar_visible_monitors"] = profile.get("taskbar_visible_monitors", [])
            save_config(self.config)
            self._rebuild_taskbar_checks()
            changed = self._apply_taskbar_visibility(visible, update_status=False)
            self._schedule_taskbar_reapply(visible)
        else:
            changed = 0
        if errors:
            messagebox.showwarning("Profile Applied With Warnings", "\n".join(errors), parent=self)
        self._set_status(f"Applied profile '{profile['name']}'. Updated {changed} taskbar window(s).")

    def delete_selected_profile(self):
        profile = self._selected_profile()
        if not profile:
            return
        if not messagebox.askyesno("Delete Profile", f"Delete '{profile['name']}'?", parent=self):
            return
        self.config["profiles"] = [
            item for item in self.config.get("profiles", []) if item["name"] != profile["name"]
        ]
        save_config(self.config)
        self.refresh_profiles()
        self._set_status(f"Deleted profile '{profile['name']}'.")

    def apply_taskbar_visibility(self):
        visible_entries = self._current_taskbar_visible_selection()
        visibility = taskbar_visibility_payload(visible_entries)
        visible = visibility["taskbar_visible_displays"]
        self.config.update(visibility)
        save_config(self.config)
        changed = self._apply_taskbar_visibility(visible, update_status=False)
        self._schedule_taskbar_reapply(visible)
        self._set_status(f"Updated {changed} taskbar window(s).")

    def show_taskbar_everywhere(self):
        for var in self.taskbar_vars.values():
            var.set(True)
        self.apply_taskbar_visibility()

    def _rebuild_taskbar_checks(self):
        for child in self.taskbar_checks.winfo_children():
            child.destroy()
        self.taskbar_vars = {}
        saved_visible = set(self.config.get("taskbar_visible_displays", []))
        saved_monitors = set(self.config.get("taskbar_visible_monitors", []))
        has_saved_visible = "taskbar_visible_displays" in self.config or "taskbar_visible_monitors" in self.config
        for display in self.displays:
            if not display.active:
                continue
            visible = (
                display.device_name in saved_visible
                or display.monitor_id in saved_monitors
                or display.monitor_key in saved_monitors
            )
            var = tk.BooleanVar(value=visible if has_saved_visible else True)
            self.taskbar_vars[display.device_name] = var
            label = (
                f"{display.device_name} ({display.width} x {display.height} at {display.x}, {display.y})"
                f" [{short_identity(display.monitor_id)}]"
            )
            ttk.Checkbutton(self.taskbar_checks, text=label, variable=var).pack(anchor="w", pady=2)

    def refresh_taskbar_status(self):
        taskbars = self.taskbar_controller.list_taskbars(self.displays)
        mapped = sum(1 for taskbar in taskbars if taskbar["device_name"])
        self._set_status(
            f"Found {len(self.displays)} monitor(s), {len(taskbars)} taskbar window(s), {mapped} mapped."
        )

    def _current_taskbar_visible_selection(self):
        return [
            display
            for display in self.displays
            if display.active and self.taskbar_vars.get(display.device_name, tk.BooleanVar(value=True)).get()
        ]

    def _resolve_taskbar_visible_devices(self, source):
        return [display.device_name for display in taskbar_visible_entries(source, self.displays)]

    def _apply_taskbar_visibility(self, visible, update_status=True):
        changed = self.taskbar_controller.apply_visibility(visible, self.displays)
        if update_status:
            self._set_status(f"Updated {changed} taskbar window(s).")
        return changed

    def _schedule_taskbar_reapply(self, visible):
        for delay_ms in (350, 1200, 2500, 5000):
            self.after(delay_ms, lambda selected=list(visible): self._apply_taskbar_visibility(selected, False))

    def _taskbar_enforcement_loop(self):
        if self.enforce_taskbars_var.get() and self._has_saved_taskbar_visibility():
            self._apply_taskbar_visibility(self._resolve_taskbar_visible_devices(self.config), False)
        self.after(2500, self._taskbar_enforcement_loop)

    def _reapply_saved_taskbar_visibility(self):
        if not self._has_saved_taskbar_visibility():
            return
        visible = self._resolve_taskbar_visible_devices(self.config)
        changed = self._apply_taskbar_visibility(visible, update_status=False)
        self._schedule_taskbar_reapply(visible)
        self._set_status(f"Restored saved taskbar visibility. Updated {changed} taskbar window(s).")

    def _has_saved_taskbar_visibility(self):
        return "taskbar_visible_displays" in self.config or "taskbar_visible_monitors" in self.config

    def _save_taskbar_enforcement_setting(self):
        self.config["enforce_taskbar_visibility"] = self.enforce_taskbars_var.get()
        save_config(self.config)

    def _selected_profile(self):
        selection = self.profile_tree.selection()
        if not selection:
            messagebox.showinfo("Select Profile", "Choose a profile first.", parent=self)
            return None
        return self.config.get("profiles", [])[int(selection[0])]

    def _poll_hotkeys(self):
        try:
            while True:
                profile_name = self.hotkey_events.get_nowait()
                profile = next(
                    (item for item in self.config.get("profiles", []) if item["name"] == profile_name),
                    None,
                )
                if profile:
                    self.apply_profile(profile)
        except queue.Empty:
            pass
        self.after(200, self._poll_hotkeys)

    def _set_status(self, text):
        self.status.configure(text=text)

    def _on_close(self):
        self.hotkeys.stop()
        self.destroy()


if __name__ == "__main__":
    app = DisplayManagerApp()
    app.mainloop()
