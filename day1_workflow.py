
from typing import TypedDict
from langgraph.graph import StateGraph, START, END


# 1. Shared state
class DisasterState(TypedDict):
    rainfall_mm: float
    risk_level: str
    recommendation: str
    history: list[str]


# 2. Weather Agent
def weather_agent(state: DisasterState):
    rainfall = state["rainfall_mm"]

    if rainfall >= 100:
        message = "Abnormally heavy rainfall detected."
    else:
        message = "Rainfall checked."

    print(f"\n[Weather Agent] {message}")

    return {
        "history": state["history"] + [message]
    }


# 3. Risk Agent
def risk_agent(state: DisasterState):
    rainfall = state["rainfall_mm"]

    # Illustrative thresholds for this exercise only
    if rainfall >= 100:
        risk = "HIGH"
    elif rainfall >= 50:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    print(f"[Risk Agent] Risk level: {risk}")

    return {
        "risk_level": risk,
        "history": state["history"] + [
            f"Risk calculated: {risk}"
        ]
    }


# 4. Routing function
def route_by_risk(state: DisasterState):
    risk = state["risk_level"]

    print(f"[Router] Selecting route for {risk} risk.")

    if risk == "HIGH":
        return "high"
    elif risk == "MEDIUM":
        return "medium"
    else:
        return "low"


# 5. LOW-risk node
def monitor_agent(state: DisasterState):
    message = "Continue monitoring weather conditions."
    print(f"[Monitor Agent] {message}")

    return {
        "recommendation": message,
        "history": state["history"] + [message]
    }


# 6. MEDIUM-risk node
def warning_agent(state: DisasterState):
    message = (
        "Monitor official alerts and prepare "
        "for possible evacuation."
    )
    print(f"[Warning Agent] {message}")

    return {
        "recommendation": message,
        "history": state["history"] + [message]
    }


# 7. HIGH-risk resource node
def resource_agent(state: DisasterState):
    # Placeholder: real shelter lookup comes later.
    message = (
        "Check verified nearby shelters and follow "
        "official emergency-service instructions."
    )
    print(f"[Resource Agent] {message}")

    return {
        "recommendation": message,
        "history": state["history"] + [message]
    }


# 8. Build the graph
builder = StateGraph(DisasterState)

builder.add_node("weather", weather_agent)
builder.add_node("risk", risk_agent)
builder.add_node("monitor", monitor_agent)
builder.add_node("warning", warning_agent)
builder.add_node("resource", resource_agent)

builder.add_edge(START, "weather")
builder.add_edge("weather", "risk")

# Conditional routing
builder.add_conditional_edges(
    "risk",
    route_by_risk,
    {
        "low": "monitor",
        "medium": "warning",
        "high": "resource"
    }
)

# Every branch ends after its task
builder.add_edge("monitor", END)
builder.add_edge("warning", END)
builder.add_edge("resource", END)

app = builder.compile()


# 9. Run a test scenario
if __name__ == "__main__":
    rainfall = 20.0

    initial_state = {
        "rainfall_mm": rainfall,
        "risk_level": "UNKNOWN",
        "recommendation": "",
        "history": []
    }

    result = app.invoke(initial_state)

    print("\n--- FINAL RESULT ---")
    print("Rainfall:", result["rainfall_mm"], "mm")
    print("Risk:", result["risk_level"])
    print("Recommendation:", result["recommendation"])
    print("History:", result["history"])
