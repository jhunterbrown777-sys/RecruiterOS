import argparse

from config.settings import settings


def parse_args():
    parser = argparse.ArgumentParser(description="RecruiterOS")

    parser.add_argument(
        "--profile",
        type=str,
        default=settings.default_profile,
        help="Active profile name, e.g. hunter, client001, companyABC",
    )

    return parser.parse_args()