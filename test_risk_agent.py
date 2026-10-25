
from agents import (
    risk_agent,
    route_by_risk,
    monitor_agent,
    warning_agent,
    resource_agent,
)


test_cases = [
    {
        "name": "LOW",
        "rainfall_mm": 0,
        "current_precipitation_mm": 0,
        "wind_speed_kmh": 10,
        "expected": "LOW",
    },
    {
        "name": "MEDIUM",
        "rainfall_mm": 30,
        "current_precipitation_mm": 0,
        "wind_speed_kmh": 10,
        "expected": "MEDIUM",
    },
    {
        "name": "HIGH",
        "rainfall_mm": 100,
        "current_precipitation_mm": 0,
        "wind_speed_kmh": 10,
        "expected": "HIGH",
    },
]

branch_agents = {
    "low": monitor_agent,
    "medium": warning_agent,
    "high": resource_agent,
}

for case in test_cases:
    state = {
        "location": "Test City",
        "rainfall_mm": case["rainfall_mm"],
        "current_precipitation_mm": (
            case["current_precipitation_mm"]
        ),
        "wind_speed_kmh": case["wind_speed_kmh"],
        "agent_logs": [],
        "shelter_options": [],
    }

    result = risk_agent(state)
    state.update(result)

    route = route_by_risk(state)

    assert state["risk_level"] == case["expected"], (
        f"Risk mismatch for {case['name']}"
    )

    assert route == case["expected"].lower(), (
        f"Routing mismatch for {case['name']}"
    )

    branch_result = branch_agents[route](state)

    print(
        f"PASS: {case['name']} risk -> "
        f"{route.upper()} route -> "
        f"{branch_result['recommendation']}"
    )

print("\nAll three simulated risk tests passed!")
