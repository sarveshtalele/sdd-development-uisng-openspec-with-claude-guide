import unittest

from itinerary.cli import parse_args


class TestParseArgs(unittest.TestCase):
    def test_valid_args(self):
        args = parse_args(["Lisbon, Portugal", "3"])
        self.assertEqual(args.destination, "Lisbon, Portugal")
        self.assertEqual(args.days, 3)

    def test_missing_all_args_exits(self):
        with self.assertRaises(SystemExit):
            parse_args([])

    def test_missing_days_exits(self):
        with self.assertRaises(SystemExit):
            parse_args(["Lisbon"])

    def test_invalid_days_zero_exits(self):
        with self.assertRaises(SystemExit):
            parse_args(["Lisbon", "0"])

    def test_invalid_days_negative_exits(self):
        with self.assertRaises(SystemExit):
            parse_args(["Lisbon", "-2"])

    def test_invalid_days_not_integer_exits(self):
        with self.assertRaises(SystemExit):
            parse_args(["Lisbon", "three"])

    def test_optional_flags_parsed(self):
        args = parse_args(
            ["Kyoto", "5", "--pace", "relaxed", "--interests", "temples,food", "--budget", "moderate"]
        )
        self.assertEqual(args.pace, "relaxed")
        self.assertEqual(args.interests, "temples,food")
        self.assertEqual(args.budget, "moderate")


if __name__ == "__main__":
    unittest.main()
