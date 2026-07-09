import unittest

from itinerary.config import DEFAULT_BASE_URL, DEFAULT_MODEL, ConfigError, load_config


class TestLoadConfig(unittest.TestCase):
    def test_missing_api_key_raises(self):
        with self.assertRaises(ConfigError):
            load_config(env={})

    def test_api_key_present_uses_defaults(self):
        config = load_config(env={"OPENAI_API_KEY": "test-key"})
        self.assertEqual(config.api_key, "test-key")
        self.assertEqual(config.base_url, DEFAULT_BASE_URL)
        self.assertEqual(config.model, DEFAULT_MODEL)

    def test_overrides_applied(self):
        config = load_config(
            env={
                "OPENAI_API_KEY": "test-key",
                "OPENAI_BASE_URL": "https://example.com/v1",
                "ITINERARY_MODEL": "some-model",
            }
        )
        self.assertEqual(config.base_url, "https://example.com/v1")
        self.assertEqual(config.model, "some-model")


if __name__ == "__main__":
    unittest.main()
