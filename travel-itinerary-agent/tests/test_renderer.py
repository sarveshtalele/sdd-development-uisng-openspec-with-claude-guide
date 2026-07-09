import unittest

from itinerary.renderer import render_itinerary
from itinerary.schema import Activity, Day, Itinerary


class TestRenderItinerary(unittest.TestCase):
    def test_render_basic(self):
        itinerary = Itinerary(
            destination="Lisbon",
            days=[
                Day(day=1, activities=[Activity(time="9:00 AM", description="Visit museum")]),
            ],
        )
        output = render_itinerary(itinerary)
        self.assertIn("Itinerary for Lisbon", output)
        self.assertIn("Day 1:", output)
        self.assertIn("9:00 AM - Visit museum", output)

    def test_render_multiple_days_in_order(self):
        itinerary = Itinerary(
            destination="Tokyo",
            days=[
                Day(day=1, activities=[Activity(time="9:00 AM", description="Shrine visit")]),
                Day(day=2, activities=[Activity(time="11:00 AM", description="Market tour")]),
            ],
        )
        output = render_itinerary(itinerary)
        self.assertLess(output.index("Day 1:"), output.index("Day 2:"))


if __name__ == "__main__":
    unittest.main()
