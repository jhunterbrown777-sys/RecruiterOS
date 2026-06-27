from config.logger import setup_logger
from orchestrator.state import WorkflowState
from orchestrator.workflow import WorkflowRun


class ChiefRecruiter:
    def __init__(self, profile_name: str = "hunter"):
        self.profile_name = profile_name
        self.logger = setup_logger("ChiefRecruiter")

    def run_discovery_workflow(self) -> WorkflowRun:
        run = WorkflowRun(profile_name=self.profile_name)

        try:
            self.logger.info(f"Starting discovery workflow for profile: {self.profile_name}")

            run.set_state(WorkflowState.DISCOVERING, "Starting job discovery")

            from pipelines.discovery_pipeline import DiscoveryPipeline

            pipeline = DiscoveryPipeline()
            pipeline.run()

            run.set_state(WorkflowState.COMPLETE, "Discovery complete")
            run.add_result("workflow", "discovery")
            run.add_result("status", "complete")

            self.logger.info("Discovery workflow complete")

        except Exception as e:
            run.add_error(str(e))
            self.logger.error(f"Discovery workflow failed: {e}")

        return run

    def run_application_workflow(self) -> WorkflowRun:
        run = WorkflowRun(profile_name=self.profile_name)

        try:
            self.logger.info(f"Starting application workflow for profile: {self.profile_name}")

            run.set_state(WorkflowState.ANALYZING, "Running application pipeline")

            import app

            app.main()

            run.set_state(WorkflowState.COMPLETE, "Application workflow complete")
            run.add_result("workflow", "application")
            run.add_result("status", "complete")

            self.logger.info("Application workflow complete")

        except Exception as e:
            run.add_error(str(e))
            self.logger.error(f"Application workflow failed: {e}")

        return run