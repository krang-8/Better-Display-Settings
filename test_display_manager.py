import unittest
from types import SimpleNamespace

from display_manager import (
    DisplayController,
    hotkey_issue_messages,
    monitor_code,
    normalize_config,
    parse_hotkey,
    parse_edid_monitor_name,
    profile_summary,
    short_identity,
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
