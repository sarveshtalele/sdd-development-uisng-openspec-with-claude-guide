from dataclasses import dataclass


class ItineraryValidationError(Exception):
    """Raised when a model response does not match the expected itinerary shape."""


@dataclass(frozen=True)
class Activity:
    time: str
    description: str


@dataclass(frozen=True)
class Day:
    day: int
    activities: list[Activity]


@dataclass(frozen=True)
class Itinerary:
    destination: str
    days: list[Day]


def validate_itinerary(raw: object, destination: str, expected_days: int) -> Itinerary:
    """Validates a raw, model-provided object against the expected itinerary shape.

    Raises ItineraryValidationError with a description of exactly what was wrong,
    rather than letting a malformed response reach the renderer.
    """
    if not isinstance(raw, dict):
        raise ItineraryValidationError("Model response is not a JSON object.")

    raw_days = raw.get("days")
    if not isinstance(raw_days, list):
        raise ItineraryValidationError("Model response is missing a 'days' list.")

    if len(raw_days) != expected_days:
        raise ItineraryValidationError(
            f"Expected {expected_days} day(s), got {len(raw_days)}."
        )

    days: list[Day] = []
    for index, entry in enumerate(raw_days, start=1):
        if not isinstance(entry, dict):
            raise ItineraryValidationError(f"Day {index} entry is not a JSON object.")

        day_number = entry.get("day")
        if day_number != index:
            raise ItineraryValidationError(
                f"Day {index} entry has 'day' = {day_number!r}, expected {index}."
            )

        raw_activities = entry.get("activities")
        if not isinstance(raw_activities, list) or not raw_activities:
            raise ItineraryValidationError(
                f"Day {index} is missing a non-empty 'activities' list."
            )

        activities: list[Activity] = []
        for activity_index, activity in enumerate(raw_activities, start=1):
            if not isinstance(activity, dict):
                raise ItineraryValidationError(
                    f"Day {index}, activity {activity_index} is not a JSON object."
                )

            time = activity.get("time")
            description = activity.get("description")

            if not isinstance(time, str) or not time:
                raise ItineraryValidationError(
                    f"Day {index}, activity {activity_index} is missing a 'time' string."
                )
            if not isinstance(description, str) or not description:
                raise ItineraryValidationError(
                    f"Day {index}, activity {activity_index} is missing a "
                    "'description' string."
                )

            activities.append(Activity(time=time, description=description))

        days.append(Day(day=day_number, activities=activities))

    return Itinerary(destination=destination, days=days)
