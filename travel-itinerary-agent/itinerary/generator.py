import json

from openai import APIError, OpenAI

from .config import Config
from .schema import Itinerary, ItineraryValidationError, validate_itinerary

SYSTEM_PROMPT = (
    "You are a travel planning assistant. Respond with a single JSON object only, "
    "no prose, no markdown fences. The JSON object must have this exact shape: "
    '{"days": [{"day": <int starting at 1>, "activities": '
    '[{"time": "<free-form time like \'9:00 AM\'>", "description": "<activity>"}]}]}. '
    "Produce exactly the number of day entries requested, numbered sequentially "
    "starting from 1."
)


def build_user_prompt(
    destination: str,
    days: int,
    pace: str | None,
    interests: str | None,
    budget: str | None,
) -> str:
    parts = [f"Plan a {days}-day itinerary for {destination}."]
    if pace:
        parts.append(f"Preferred pace: {pace}.")
    if interests:
        parts.append(f"Interests: {interests}.")
    if budget:
        parts.append(f"Budget level: {budget}.")
    parts.append("Respond with only the JSON object described in the system prompt.")
    return " ".join(parts)


def generate_itinerary(
    config: Config,
    destination: str,
    days: int,
    pace: str | None = None,
    interests: str | None = None,
    budget: str | None = None,
    client: object | None = None,
) -> Itinerary:
    """Calls the configured OpenAI-compatible model and returns a validated Itinerary.

    `client` is accepted as a parameter, defaulting to a real `openai.OpenAI` client
    built from `config`, specifically so tests can pass in a stand-in object and
    exercise every line of this function except the actual network call.
    """
    if client is None:
        client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    try:
        response = client.chat.completions.create(
            model=config.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_user_prompt(
                        destination, days, pace, interests, budget
                    ),
                },
            ],
        )
    except APIError as exc:
        raise ItineraryValidationError(f"Itinerary request failed: {exc}") from exc

    raw_content = response.choices[0].message.content

    try:
        raw = json.loads(raw_content)
    except (json.JSONDecodeError, TypeError) as exc:
        raise ItineraryValidationError(f"Model response was not valid JSON: {exc}") from exc

    return validate_itinerary(raw, destination=destination, expected_days=days)
