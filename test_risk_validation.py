
import math

from agents import risk_agent


def make_state(rainfall=0, precipitation=0, wind=10):
    return {
        "rainfall_mm": rainfall,
        "current_precipitation_mm": precipitation,
        "wind_speed_kmh": wind,
        "agent_logs": [],
    }


def expect_rejected(label, state):
    try:
        risk_agent(state)
    except (ValueError, TypeError):
        print(f"PASS: {label} was rejected")
    else:
        raise AssertionError(
            f"FAIL: {label} should have been rejected"
        )


# Valid inputs should still work.
result = risk_agent(make_state(0, 0, 10))
assert result["risk_level"] == "LOW"
print("PASS: Valid LOW input accepted")

# Invalid inputs should be rejected.
expect_rejected(
    "Negative rainfall",
    make_state(rainfall=-5),
)

expect_rejected(
    "Non-numeric rainfall",
    make_state(rainfall="unknown"),
)

expect_rejected(
    "NaN wind speed",
    make_state(wind=math.nan),
)

expect_rejected(
    "Missing rainfall",
    {
        "current_precipitation_mm": 0,
        "wind_speed_kmh": 10,
        "agent_logs": [],
    },
)

print("ALL RISK VALIDATION TESTS PASSED!")
