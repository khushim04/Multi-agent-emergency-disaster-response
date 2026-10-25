
from langgraph.graph import StateGraph, START, END

from test_output_validation import validate_output




from state import DisasterState
from agents import (
    
    risk_agent,
    route_by_risk,
    monitor_agent,
    warning_agent,
    resource_agent,
    communication_agent,
    finalize_agent,
)



def simulated_weather_agent(state: DisasterState) -> dict:
    """Provide test weather values without calling the API."""

    print(
        f"\n[Simulated Weather Agent] "
        f"Testing {state['location']}"
    )

    return {
        "location": state["location"],
        "latitude": 0.0,
        "longitude": 0.0,
        "observation_time": "SIMULATED",
        "temperature_c": 25.0,
        "humidity_percent": 50.0,
        "current_precipitation_mm": (
            state["current_precipitation_mm"]
        ),
        "rainfall_mm": state["rainfall_mm"],
        "weather_code": 0,
        "wind_speed_kmh": state["wind_speed_kmh"],
        "weather_status": "Simulated test data",
    }


def build_test_workflow():
    builder = StateGraph(DisasterState)

    builder.add_node("weather", simulated_weather_agent)
    builder.add_node("risk", risk_agent)
    builder.add_node("monitor", monitor_agent)
    builder.add_node("warning", warning_agent)
    builder.add_node("resource", resource_agent)
    builder.add_node("finalize", finalize_agent)
    builder.add_node("communication", communication_agent)

    builder.add_edge(START, "weather")
    builder.add_edge("weather", "risk")

    builder.add_conditional_edges(
        "risk",
        route_by_risk,
        {
            "low": "monitor",
            "medium": "warning",
            "high": "resource",
        },
    )

    builder.add_edge("monitor", "communication")
    builder.add_edge("warning", "communication")
    builder.add_edge("resource", "communication")

    builder.add_edge("communication", "finalize")
    builder.add_edge("finalize", END)

    return builder.compile()


app = build_test_workflow()

test_cases = [
    {
        "name": "LOW",
        "rainfall_mm": 0,
        "current_precipitation_mm": 0,
        "wind_speed_kmh": 10,
        "expected_risk": "LOW",
        "expected_agent_log": "Monitoring recommendation prepared",
    },
    {
        "name": "MEDIUM",
        "rainfall_mm": 30,
        "current_precipitation_mm": 0,
        "wind_speed_kmh": 10,
        "expected_risk": "MEDIUM",
        "expected_agent_log": "Warning recommendation prepared",
    },
    {
        "name": "HIGH",
        "rainfall_mm": 100,
        "current_precipitation_mm": 0,
        "wind_speed_kmh": 10,
        "expected_risk": "HIGH",
        "expected_agent_log": "No matching shelter records found",
    },
]

for case in test_cases:
    initial_state = {
        "location": f"Test-{case['name']}",
        "rainfall_mm": case["rainfall_mm"],
        "current_precipitation_mm": (
            case["current_precipitation_mm"]
        ),
        "wind_speed_kmh": case["wind_speed_kmh"],
        "agent_logs": [],
        "shelter_options": [],
    }

    
    
    # Capture execution trace and final state in one run.
    
    executed_nodes = []
    result = {}

    for event_type, update in app.stream(
        initial_state,
        stream_mode=["updates", "values"],
    ):
        if event_type == "updates":
            for node_name in update:
                executed_nodes.append(node_name)

        elif event_type == "values":
            result = update

    if not result:
        raise AssertionError("Workflow returned no final state")

    print(f"Execution trace: {' -> '.join(executed_nodes)}")

    
    expected_path = {
        "LOW": [
            "weather", "risk", "monitor",
            "communication", "finalize",
        ],
        "MEDIUM": [
            "weather", "risk", "warning",
            "communication", "finalize",
        ],
        "HIGH": [
            "weather", "risk", "resource",
            "communication", "finalize",
        ],
    }

    assert executed_nodes == expected_path[case["name"]], (
        f"Incorrect execution path for {case['name']}: "
        f"{executed_nodes}"
    )

    print(f"PASS: {case['name']} execution trace verified")




    # Validate the complete workflow output.
    validate_output(result)
    print("PASS: Workflow output structure validated")

    assert result.get("communication_message"), (
        "Communication message is missing"
    )


    assert case["expected_risk"] in result["communication_message"], (
        "Communication message has the wrong risk level"
    )




    assert result["risk_level"] == case["expected_risk"], (
        f"Incorrect risk for {case['name']}"
    )

    assert case["expected_agent_log"] in result["agent_logs"], (
        f"Incorrect branch for {case['name']}"
    )

    assert result.get("summary"), "Final summary is missing"

    print(
        f"\nPASS: {case['name']} | "
        f"Risk: {result['risk_level']} | "
        f"Summary generated successfully"
    )

print("\nALL END-TO-END WORKFLOW TESTS PASSED!")

