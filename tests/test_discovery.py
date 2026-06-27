from pipelines.discovery_pipeline import DiscoveryPipeline


def main():
    pipeline = DiscoveryPipeline()
    pipeline.run()

    print("Discovery pipeline test completed.")


if __name__ == "__main__":
    main()