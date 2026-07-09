import os
from dataclasses import dataclass

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"


class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    api_key: str
    base_url: str
    model: str


def load_config(env: dict | None = None) -> Config:
    """Reads configuration from environment variables.

    `env` defaults to `os.environ` and is accepted as a parameter so tests can supply
    a stand-in mapping instead of mutating real process environment variables.
    """
    env = os.environ if env is None else env

    api_key = env.get("OPENAI_API_KEY")
    if not api_key:
        raise ConfigError(
            "OPENAI_API_KEY is not set. Set it to your OpenAI-compatible API key "
            "before running this tool."
        )

    base_url = env.get("OPENAI_BASE_URL", DEFAULT_BASE_URL)
    model = env.get("ITINERARY_MODEL", DEFAULT_MODEL)

    return Config(api_key=api_key, base_url=base_url, model=model)
