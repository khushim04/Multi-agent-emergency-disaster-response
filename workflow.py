
from langgraph.graph import StateGraph, START, END

from state import DisasterState
from agents import (
    weather_agent,
    risk_agent,
    route_by_risk,
    monitor_agent,
    warning_agent,
    resource_agent,
    communication_agent,
    finalize_agent,
)


def build_workflow(use_simulated_weather=False):
    builder = StateGraph(DisasterState)

    # Choose the weather source.
    if use_simulated_weather:
        from agents import simulated_weather_agent
        weather_node = simulated_weather_agent
    else:
        weather_node = weather_agent

    builder.add_node("weather", weather_node)
    builder.add_node("risk", risk_agent)
    builder.add_node("monitor", monitor_agent)
    builder.add_node("warning", warning_agent)
    builder.add_node("resource", resource_agent)
    builder.add_node("communication", communication_agent)
    builder.add_node("finalize", finalize_agent)

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
