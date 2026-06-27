from orchestrator.chief_recruiter import ChiefRecruiter
from orchestrator.state import WorkflowState


def main():
    chief = ChiefRecruiter(profile_name="hunter")
    run = chief.run_discovery_workflow()

    print(f"Profile: {run.profile_name}")
    print(f"State: {run.state}")
    print(f"Step: {run.current_step}")
    print(f"Results: {run.result}")
    print(f"Errors: {run.errors}")

    assert run.state in [WorkflowState.COMPLETE, WorkflowState.FAILED]


if __name__ == "__main__":
    main()