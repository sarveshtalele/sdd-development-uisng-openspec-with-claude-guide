import json
import unittest
from types import SimpleNamespace

import httpx
from openai import APIError

from itinerary.config import Config
from itinerary.generator import build_user_prompt, generate_itinerary
from itinerary.schema import ItineraryValidationError


class FakeChatCompletions:
    """Stands in for `client.chat.completions` without making a network call."""

    def __init__(self, content: str = "", error: Exception | None = None):
        self._content = content
        self._error = error

    def create(self, model, messages):
        if self._error is not None:
            raise self._error
        message = SimpleNamespace(content=self._content)
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


class FakeClient:
    """Stands in for `openai.OpenAI` — same shape, no network access."""

    def __init__(self, content: str = "", error: Exception | None = None):
        self.chat = SimpleNamespace(completions=FakeChatCompletions(content, error))


class TestBuildUserPrompt(unittest.TestCase):
    def test_includes_all_provided_fields(self):
        prompt = build_user_prompt("Lisbon", 3, pace="relaxed", interests="food", budget="moderate")
        self.assertIn("Lisbon", prompt)
        self.assertIn("3-day", prompt)
        self.assertIn("relaxed", prompt)
        self.assertIn("food", prompt)
        self.assertIn("moderate", prompt)

    def test_omits_unset_optional_fields(self):
        prompt = build_user_prompt("Lisbon", 3, pace=None, interests=None, budget=None)
        self.assertNotIn("Preferred pace", prompt)
        self.assertNotIn("Interests", prompt)
        self.assertNotIn("Budget level", prompt)


class TestGenerateItinerary(unittest.TestCase):
    """
    These tests exercise generate_itinerary end-to-end — prompt construction, the
    client call, JSON parsing, and shape validation — using a stand-in client instead
    of a live OpenAI-compatible endpoint. This is the concrete verification for the
    design decision in design.md to isolate the model call behind one function: every
    line up to and including the client call is proven correct here without a live key.
    Whether a *real* OpenAI-compatible endpoint returns a response that parses into
    this same shape was separately verified live against a real proxy (see
    BUILD-LOG.md); this test file's job is everything downstream of that call.
    """

    def setUp(self):
        self.config = Config(api_key="test-key", base_url="https://example.com/v1", model="test-model")

    def test_well_formed_response_is_validated_and_returned(self):
        content = json.dumps(
            {"days": [{"day": 1, "activities": [{"time": "9:00 AM", "description": "Visit museum"}]}]}
        )
        client = FakeClient(content)
        itinerary = generate_itinerary(self.config, "Lisbon", 1, client=client)
        self.assertEqual(itinerary.destination, "Lisbon")
        self.assertEqual(len(itinerary.days), 1)

    def test_non_json_response_raises_validation_error(self):
        client = FakeClient("not json at all")
        with self.assertRaises(ItineraryValidationError):
            generate_itinerary(self.config, "Lisbon", 1, client=client)

    def test_malformed_shape_raises_validation_error(self):
        content = json.dumps({"days": [{"day": 1, "activities": []}]})
        client = FakeClient(content)
        with self.assertRaises(ItineraryValidationError):
            generate_itinerary(self.config, "Lisbon", 1, client=client)

    def test_wrong_day_count_raises_validation_error(self):
        content = json.dumps(
            {"days": [{"day": 1, "activities": [{"time": "9:00 AM", "description": "x"}]}]}
        )
        client = FakeClient(content)
        with self.assertRaises(ItineraryValidationError):
            generate_itinerary(self.config, "Lisbon", 2, client=client)

    def test_api_error_raises_validation_error(self):
        request = httpx.Request("POST", "https://example.com/v1/chat/completions")
        api_error = APIError("Invalid API key.", request, body=None)
        client = FakeClient(error=api_error)
        with self.assertRaises(ItineraryValidationError):
            generate_itinerary(self.config, "Lisbon", 1, client=client)


if __name__ == "__main__":
    unittest.main()
