
from workflow import build_workflow


def validate_output(result):
    required_fields = [
        "location",
        "risk_level",
        "recommendation",
        "communication_message",
        "summary",
        "agent_logs",
        "shelter_options",
    ]

    missing = [
        field for field in required_fields
        if field not in result or result[field] is None
    ]

    if missing:
        raise AssertionError(
            f"Missing required output fields: {missing}"
        )

    assert result["risk_level"] in {
        "LOW", "MEDIUM", "HIGH"
    }, "Invalid risk level"

    assert isinstance(
        result["recommendation"], str
    ), "Recommendation must be text"

    assert isinstance(
        result["communication_message"], str
    ), "Communication message must be text"

    assert isinstance(
        result["summary"], str
    ), "Summary must be text"

    assert isinstance(
        result["agent_logs"], list
    ), "Agent logs must be a list"

    assert isinstance(
        result["shelter_options"], list
    ), "Shelter options must be a list"



