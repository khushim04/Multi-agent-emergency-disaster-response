
import logging
from unittest.mock import patch

from agents import resource_agent


def test_resource_lookup_failure():
    state = {
        "location": "Test-City",
        "agent_logs": [],
        "shelter_options": [],
    }

    with patch(
        "agents.find_shelters",
        side_effect=RuntimeError("Simulated database failure"),
    ):
        with patch("agents.logger") as mock_logger:
            result = resource_agent(state)

    mock_logger.exception.assert_called_once()

    assert result["shelter_options"] == []
    assert "official emergency services" in (
        result["recommendation"]
    ).lower()

    assert "Shelter database lookup failed" in (
        result["agent_logs"]
    )

    print("PASS: Shelter lookup failure was logged")
    print("PASS: Safe fallback recommendation returned")
    print("PASS: Workflow state preserved safely")


if __name__ == "__main__":
    test_resource_lookup_failure()
    print("ALL RESOURCE LOGGING TESTS PASSED!")
