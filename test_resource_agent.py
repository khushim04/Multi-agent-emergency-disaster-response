
from agents import resource_agent
from shelter_db import get_connection


def main():
    # This record is fictional and used only for testing.
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE shelters
            SET verified = 1
            WHERE name = ? AND city = ?
            """,
            ("TEST Shelter A", "Bhopal"),
        )

    state = {
        "location": "Bhopal",
        "agent_logs": [],
        "shelter_options": [],
    }

    result = resource_agent(state)

    print("\n--- RESOURCE AGENT TEST ---")
    print("Recommendation:", result["recommendation"])
    print("Shelter options:", result["shelter_options"])
    print("Agent logs:", result["agent_logs"])

    assert result["shelter_options"], (
        "Expected a matching test shelter."
    )

    assert any(
        "TEST Shelter A" in shelter
        for shelter in result["shelter_options"]
    ), "Expected TEST Shelter A in the results."

    print("\nResource Agent test passed!")


if __name__ == "__main__":
    main()
