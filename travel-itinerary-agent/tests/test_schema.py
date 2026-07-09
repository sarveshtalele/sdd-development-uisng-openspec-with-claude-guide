import unittest

from itinerary.schema import ItineraryValidationError, validate_itinerary


class TestValidateItinerary(unittest.TestCase):
    def test_valid_itinerary(self):
        raw = {
            "days": [
                {"day": 1, "activities": [{"time": "9:00 AM", "description": "Visit museum"}]},
                {"day": 2, "activities": [{"time": "10:00 AM", "description": "Walking tour"}]},
            ]
        }
        itinerary = validate_itinerary(raw, destination="Lisbon", expected_days=2)
        self.assertEqual(itinerary.destination, "Lisbon")
        self.assertEqual(len(itinerary.days), 2)
        self.assertEqual(itinerary.days[0].activities[0].description, "Visit museum")

    def test_wrong_day_count(self):
        raw = {"days": [{"day": 1, "activities": [{"time": "9:00 AM", "description": "x"}]}]}
        with self.assertRaises(ItineraryValidationError):
            validate_itinerary(raw, destination="Lisbon", expected_days=2)

    def test_not_a_dict(self):
        with self.assertRaises(ItineraryValidationError):
            validate_itinerary(["not", "a", "dict"], destination="Lisbon", expected_days=1)

    def test_missing_days_key(self):
        with self.assertRaises(ItineraryValidationError):
            validate_itinerary({}, destination="Lisbon", expected_days=1)

    def test_day_number_mismatch(self):
        raw = {"days": [{"day": 2, "activities": [{"time": "9:00 AM", "description": "x"}]}]}
        with self.assertRaises(ItineraryValidationError):
            validate_itinerary(raw, destination="Lisbon", expected_days=1)

    def test_empty_activities(self):
        raw = {"days": [{"day": 1, "activities": []}]}
        with self.assertRaises(ItineraryValidationError):
            validate_itinerary(raw, destination="Lisbon", expected_days=1)

    def test_activity_missing_field(self):
        raw = {"days": [{"day": 1, "activities": [{"time": "9:00 AM"}]}]}
        with self.assertRaises(ItineraryValidationError):
            validate_itinerary(raw, destination="Lisbon", expected_days=1)


if __name__ == "__main__":
    unittest.main()
