
import requests
from workflow import build_workflow


def main():
    location = input(
        "Enter a city name (e.g., Indore): "
    ).strip()

    if not location:
        print("Please enter a location.")
        return

    app = build_workflow()

    # The Weather Agent will populate the remaining fields.
    initial_state = {
        "location": location,
        "agent_logs": [],
        "shelter_options": [],
}

    

    try:
        result = app.invoke(initial_state)

    except (
        requests.RequestException,
        ValueError,
        KeyError,
    ) as exc:
        print("\nCould not complete the workflow.")
        print("Reason:", exc)
        print("Check your internet connection and location.")
        return

    print("\n========== WEATHER REPORT ==========")
    print("Location:", result["location"])
    print("Observation time:", result["observation_time"])
    print("Temperature:", result["temperature_c"], "°C")
    print("Humidity:", result["humidity_percent"], "%")
    print(
        "Current precipitation:",
        result["current_precipitation_mm"], "mm"
    )
    print(
        "Recent hourly rainfall total:",
        result["rainfall_mm"], "mm"
    )
    print("Wind speed:", result["wind_speed_kmh"], "km/h")

    print("\n========== RISK ASSESSMENT ==========")
    print("Risk level:", result["risk_level"])
    print("Recommendation:", result["recommendation"])
    print("Shelter options:", result["shelter_options"])

    print("\n========== AGENT LOG ==========")
    for step in result["agent_logs"]:
        print("-", step)

    print("\n========== FINAL SUMMARY ==========")
    print(result["summary"])


if __name__ == "__main__":
    main()
