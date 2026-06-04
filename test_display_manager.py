import unittest

from display_manager import normalize_config, parse_hotkey, profile_summary, short_identity


class DisplayManagerLogicTests(unittest.TestCase):
    def test_parse_hotkey_accepts_common_combinations(self):
        self.assertEqual(parse_hotkey("Ctrl+Alt+1"), (0x0002 | 0x0001, ord("1")))
        self.assertEqual(parse_hotkey("Ctrl+Shift+F9"), (0x0002 | 0x0004, 0x78))

    def test_profile_summary_counts_applied_enabled_and_taskbar_displays(self):
        profile = {
            "taskbar_visible_displays": ["DISPLAY1"],
            "displays": [
                {"device_name": "DISPLAY1", "apply": True, "enabled": True},
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
        self.assertTrue(display["apply"])
        self.assertFalse(display["enabled"])
        self.assertEqual(display["monitor_id"], "")
        self.assertEqual(display["monitor_key"], "")

    def test_short_identity_uses_readable_tail(self):
        self.assertEqual(short_identity(""), "-")
        self.assertEqual(short_identity(r"MONITOR\\ACME123\\{long-device-instance}"), "{long-device-instance}")


if __name__ == "__main__":
    unittest.main()
