from services.discovery_service import DiscoveryService


def main():
    run = DiscoveryService().run_discovery()

    if run.errors:
        raise RuntimeError("; ".join(run.errors))


if __name__ == "__main__":
    main()