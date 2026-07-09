import argparse
import sys

from .config import ConfigError, load_config
from .generator import generate_itinerary
from .renderer import render_itinerary
from .schema import ItineraryValidationError


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="itinerary",
        description="Generate a day-by-day travel itinerary using an OpenAI-compatible model.",
    )
    parser.add_argument("destination", help="Trip destination, e.g. 'Lisbon, Portugal'")
    parser.add_argument("days", type=int, help="Number of days for the trip (positive integer)")
    parser.add_argument("--pace", default=None, help="Preferred pace, e.g. 'relaxed' or 'packed'")
    parser.add_argument(
        "--interests", default=None, help="Comma-separated interests, e.g. 'museums,food'"
    )
    parser.add_argument(
        "--budget", default=None, help="Budget level, e.g. 'budget', 'moderate', 'luxury'"
    )

    args = parser.parse_args(argv)

    if args.days <= 0:
        parser.error("days must be a positive integer")

    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        config = load_config()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    try:
        itinerary = generate_itinerary(
            config,
            destination=args.destination,
            days=args.days,
            pace=args.pace,
            interests=args.interests,
            budget=args.budget,
        )
    except ItineraryValidationError as exc:
        print(f"Itinerary validation error: {exc}", file=sys.stderr)
        return 1

    print(render_itinerary(itinerary), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
