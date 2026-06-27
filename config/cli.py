import argparse

from config.settings import settings


def parse_args():
    parser = argparse.ArgumentParser(
        prog="RecruiterOS",
        description="RecruiterOS AI Recruiting Platform",
    )

    parser.add_argument(
        "--profile",
        type=str,
        default=settings.default_profile,
        help="Profile name (hunter, client001, companyABC, etc.)",
    )

    parser.add_argument(
        "--search-only",
        action="store_true",
        help="Run discovery pipeline only.",
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging.",
    )

    return parser.parse_args()