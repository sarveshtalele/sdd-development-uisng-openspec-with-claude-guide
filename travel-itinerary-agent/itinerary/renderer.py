from .schema import Itinerary


def render_itinerary(itinerary: Itinerary) -> str:
    lines = [f"Itinerary for {itinerary.destination}", ""]
    for day in itinerary.days:
        lines.append(f"Day {day.day}:")
        for activity in day.activities:
            lines.append(f"  {activity.time} - {activity.description}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
