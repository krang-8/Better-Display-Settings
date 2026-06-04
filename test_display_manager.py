import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch

from display_manager import (
    app_summary,
    backup_config,
    display_layout_bounds,
    display_map_rectangles,
    display_state_label,
    display_state_tag,
    DisplayController,
    hotkey_status_tag,
    hotkey_issue_messages,
    monitor_code,
    normalize_config,
    parse_hotkey,
    parse_edid_monitor_name,
    profile_preview,
    profile_summary,
    repair_profile_for_current_monitors,
    should_retry_taskbar_apply,
    short_identity,
    status_message,
    taskbar_apply_status,
    taskbar_diagnostic_parts,
    taskbar_visibility_payload,
    unique_profile_name,
)


class DisplayManagerLogicTests(unittest.TestCase):
    def test_parse_hotkey_accepts_common_combinations(self):
        self.assertEqual(parse_hotkey("Ctrl+Alt+1"), (0x0002 | 0x0001, ord("1")))
        self.assertEqual(parse_hotkey("Ctrl+Shift+F9"), (0x0002 | 0x0004, 0x78))

    def test_monitor_code_extracts_hardware_code(self):
        self.assertEqual(
            monitor_code(r"MONITOR\DELA1C2\{4d36e96e-e325-11ce-bfc1-08002be10318}\0003"),
            "DELA1C2",
        )

    def test_parse_edid_monitor_name_reads_descriptor(self):
        edid = bytearray(128)
        edid[54:72] = b"\x00\x00\x00\xfc\x00DELL S2522HG\n"

        self.assertEqual(parse_edid_monitor_name(edid), "DELL S2522HG")

    def test_profile_summary_counts_applied_enabled_and_taskbar_displays(self):
        profile = {
            "taskbar_visible_displays": [],
            "taskbar_visible_monitors": ["MONITOR-1"],
            "displays": [
                {"device_name": "DISPLAY1", "monitor_id": "MONITOR-1", "apply": True, "enabled": True},
                {"device_name": "DISPLAY2", "apply": True, "enabled": False},
                {"device_name": "DISPLAY3", "apply": False, "enabled": True},
            ],
        }

        self.assertEqual(
            profile_summary(profile),
            {
                "enabled": "1 on",
                "disabled": "1 off",
                "taskbars": "1 taskbar",
            },
        )

    def test_profile_preview_summarizes_selected_profile(self):
        profile = {
            "name": "Triple",
            "hotkey": "Ctrl+Alt+3",
            "taskbar_visible_displays": ["DISPLAY1"],
            "displays": [
                {"device_name": "DISPLAY1", "apply": True, "enabled": True},
                {"device_name": "DISPLAY2", "apply": True, "enabled": False},
            ],
        }

        self.assertEqual(
            profile_preview(profile, "registered"),
            {
                "name": "Triple",
                "meta": "Ctrl+Alt+3 | hotkey registered",
                "details": "1 on | 1 off | 1 taskbar",
            },
        )

    def test_profile_preview_handles_empty_selection(self):
        self.assertEqual(profile_preview(None)["name"], "No profile selected")

    def test_normalize_config_adds_profile_defaults(self):
        config = normalize_config({"profiles": [{"displays": [{"active": False}]}]})

        display = config["profiles"][0]["displays"][0]
        self.assertEqual(config["profiles"][0]["hotkey"], "")
        self.assertEqual(config["profiles"][0]["taskbar_visible_displays"], [])
        self.assertEqual(config["profiles"][0]["taskbar_visible_monitors"], [])
        self.assertTrue(display["apply"])
        self.assertFalse(display["enabled"])
        self.assertEqual(display["monitor_id"], "")
        self.assertEqual(display["monitor_key"], "")

    def test_short_identity_uses_readable_tail(self):
        self.assertEqual(short_identity(""), "-")
        self.assertEqual(short_identity(r"MONITOR\\ACME123\\{long-device-instance}"), "{long-device-instance}")

    def test_taskbar_visibility_payload_stores_device_and_monitor_identity(self):
        payload = taskbar_visibility_payload(
            [
                SimpleNamespace(device_name="DISPLAY1", monitor_id="MONITOR-1", monitor_key="KEY-1"),
                SimpleNamespace(device_name="DISPLAY2", monitor_id="", monitor_key="KEY-2"),
            ]
        )

        self.assertEqual(payload["taskbar_visible_displays"], ["DISPLAY1", "DISPLAY2"])
        self.assertEqual(payload["taskbar_visible_monitors"], ["MONITOR-1", "KEY-2"])

    def test_taskbar_diagnostic_parts_show_actual_and_expected_state(self):
        taskbars = [
            {"device_name": "DISPLAY1", "visible": True},
            {"device_name": "DISPLAY2", "visible": True},
            {"device_name": None, "visible": False},
        ]

        self.assertEqual(
            taskbar_diagnostic_parts(taskbars, {"DISPLAY1"}),
            ["DISPLAY1: visible/show", "DISPLAY2: visible/hide", "unmapped: hidden/hide"],
        )

    def test_taskbar_apply_status_reports_setting_and_missing_windows(self):
        self.assertEqual(
            taskbar_apply_status(
                {"changed": 1, "enabled_windows_setting": True},
                ["DISPLAY2"],
            ),
            "Updated 1 taskbar window(s); enabled Windows multi-taskbar setting; missing taskbars for DISPLAY2",
        )

    def test_taskbar_apply_status_reports_clean_noop(self):
        self.assertEqual(
            taskbar_apply_status({"changed": 0}, []),
            "No taskbar window changes needed",
        )

    def test_should_retry_taskbar_apply_only_when_windows_needs_time(self):
        self.assertFalse(should_retry_taskbar_apply({"changed": 1}, []))
        self.assertTrue(should_retry_taskbar_apply({"changed": 0, "enabled_windows_setting": True}, []))
        self.assertTrue(should_retry_taskbar_apply({"changed": 0}, ["DISPLAY2"]))

    def test_status_message_adds_timestamp(self):
        self.assertEqual(
            status_message("Applied profile.", datetime(2026, 6, 3, 14, 5, 7)),
            "14:05:07  Applied profile.",
        )

    def test_app_summary_reports_current_state(self):
        displays = [
            SimpleNamespace(active=True),
            SimpleNamespace(active=True),
            SimpleNamespace(active=False),
        ]

        self.assertEqual(
            app_summary(displays, [{"name": "Dual"}], True, False),
            "2 monitor(s) | 1 profile(s) | Windows multi-taskbar on | enforcement off",
        )

    def test_display_state_helpers_prioritize_primary(self):
        display = SimpleNamespace(primary=True, active=True)

        self.assertEqual(display_state_label(display), "Primary")
        self.assertEqual(display_state_tag(display), "primary")

    def test_hotkey_status_tag_groups_visual_states(self):
        self.assertEqual(hotkey_status_tag("registered"), "status_registered")
        self.assertEqual(hotkey_status_tag("invalid"), "status_problem")
        self.assertEqual(hotkey_status_tag("unavailable"), "status_problem")
        self.assertEqual(hotkey_status_tag("not set"), "status_muted")

    def test_display_layout_bounds_uses_active_monitor_extents(self):
        displays = [
            SimpleNamespace(active=True, x=-1920, y=0, width=1920, height=1080),
            SimpleNamespace(active=True, x=0, y=0, width=2560, height=1440),
            SimpleNamespace(active=False, x=2560, y=0, width=3840, height=2160),
        ]

        self.assertEqual(display_layout_bounds(displays), (-1920, 0, 2560, 1440))

    def test_display_map_rectangles_center_scaled_layout(self):
        displays = [
            SimpleNamespace(active=True, x=0, y=0, width=100, height=100),
            SimpleNamespace(active=True, x=100, y=0, width=100, height=100),
        ]

        rectangles = display_map_rectangles(displays, 240, 140, padding=20)

        self.assertEqual(rectangles[0]["x1"], 20)
        self.assertEqual(rectangles[0]["x2"], 120)
        self.assertEqual(rectangles[1]["x1"], 120)
        self.assertEqual(rectangles[1]["x2"], 220)
        self.assertEqual(rectangles[0]["y1"], 20)

    def test_repair_profile_for_current_monitors_drops_stale_adapters_and_backfills_ids(self):
        profile = {
            "displays": [
                {"device_name": "DISPLAY1", "label": "Generic PnP Monitor", "enabled": True},
                {"device_name": "DISPLAY2", "label": "Generic PnP Monitor", "enabled": True},
                {"device_name": "DISPLAY4", "label": "AMD Radeon", "enabled": False, "width": 0, "height": 0},
            ],
            "taskbar_visible_displays": ["DISPLAY1"],
            "taskbar_visible_monitors": [],
        }
        current = [
            SimpleNamespace(
                device_name="DISPLAY1",
                label="DISPLAY1 - DELL S2522HG",
                monitor_id="MONITOR-1",
                monitor_key="KEY-1",
                active=True,
                primary=False,
                x=0,
                y=0,
                width=1920,
                height=1080,
                frequency=240,
                bits_per_pixel=32,
            ),
            SimpleNamespace(
                device_name="DISPLAY2",
                label="DISPLAY2 - MAG 275QF X30",
                monitor_id="MONITOR-2",
                monitor_key="KEY-2",
                active=True,
                primary=True,
                x=1920,
                y=0,
                width=2560,
                height=1440,
                frequency=300,
                bits_per_pixel=32,
            ),
        ]

        self.assertTrue(repair_profile_for_current_monitors(profile, current))
        self.assertEqual([display["device_name"] for display in profile["displays"]], ["DISPLAY1", "DISPLAY2"])
        self.assertEqual(profile["displays"][0]["label"], "DISPLAY1 - DELL S2522HG")
        self.assertEqual(profile["displays"][0]["monitor_id"], "MONITOR-1")
        self.assertEqual(profile["taskbar_visible_monitors"], ["MONITOR-1"])

    def test_backup_config_copies_existing_config(self):
        class FakePath:
            def __init__(self, exists, content=""):
                self._exists = exists
                self.content = content

            def exists(self):
                return self._exists

            def read_text(self, encoding=None):
                return self.content

            def write_text(self, content, encoding=None):
                self.content = content
                return len(content)

        source = FakePath(True, '{"profiles": []}')
        backup = FakePath(False)
        with patch("display_manager.CONFIG_PATH", source), patch("display_manager.CONFIG_BACKUP_PATH", backup):
            self.assertTrue(backup_config())

        self.assertEqual(backup.content, '{"profiles": []}')

    def test_backup_config_skips_missing_config(self):
        class MissingPath:
            def exists(self):
                return False

        with patch("display_manager.CONFIG_PATH", MissingPath()):
            self.assertFalse(backup_config())

    def test_unique_profile_name_adds_numeric_suffix(self):
        profiles = [{"name": "Triple Copy"}, {"name": "Triple Copy 2"}]

        self.assertEqual(unique_profile_name("Triple Copy", profiles), "Triple Copy 3")
        self.assertEqual(unique_profile_name("Dual Copy", profiles), "Dual Copy")

    def test_hotkey_issue_messages_reports_invalid_and_unavailable(self):
        profiles = [{"name": "Dual"}, {"name": "Triple"}, {"name": "TV"}]
        statuses = {"Dual": "registered", "Triple": "invalid", "TV": "unavailable"}

        self.assertEqual(
            hotkey_issue_messages(profiles, statuses),
            ["Triple: invalid", "TV: unavailable"],
        )

    def test_resolve_device_name_reports_identity_match(self):
        controller = DisplayController()
        device, matched = controller._resolve_device_name(
            {"device_name": "DISPLAY9", "monitor_id": "MONITOR-1", "monitor_key": ""},
            [SimpleNamespace(device_name="DISPLAY2", monitor_id="MONITOR-1", monitor_key="KEY-1")],
        )

        self.assertEqual(device, "DISPLAY2")
        self.assertTrue(matched)

    def test_resolve_device_name_falls_back_when_identity_is_missing(self):
        controller = DisplayController()
        device, matched = controller._resolve_device_name(
            {"device_name": "DISPLAY9", "monitor_id": "MONITOR-X", "monitor_key": ""},
            [SimpleNamespace(device_name="DISPLAY2", monitor_id="MONITOR-1", monitor_key="KEY-1")],
        )

        self.assertEqual(device, "DISPLAY9")
        self.assertFalse(matched)


if __name__ == "__main__":
    unittest.main()
