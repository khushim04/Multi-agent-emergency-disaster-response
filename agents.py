
from state import DisasterState
from weather_service import get_weather_data
import math

import logging
logger = logging.getLogger(__name__)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)



def weather_agent(state: DisasterState) -> dict:
    """Retrieve real weather data and update the shared state."""

    
    try:
        weather = get_weather_data(state["location"])
    except Exception:
        logger.exception(
            "Weather Agent failed for location: %s",
            state.get("location", "Unknown"),
        )
        raise


    logger.info(
    "Weather data retrieved successfully for location: %s",
    weather["location"],
)

    status = (
        f"Weather data retrieved for {weather['location']}"
    )

    print(f"\n[Weather Agent] {status}")
    print(
        f"[Weather Agent] Recent 3-point rainfall: "
        f"{weather['rainfall_3h_mm']} mm"
    )

    return {
        "location": weather["location"],
        "latitude": weather["latitude"],
        "longitude": weather["longitude"],
        "observation_time": weather["observation_time"],
        "temperature_c": weather["temperature_c"],
        "humidity_percent": weather["humidity_percent"],
        "current_precipitation_mm": (
            weather["current_precipitation_mm"]
        ),
        "rainfall_mm": weather["rainfall_3h_mm"],
        "weather_code": weather["weather_code"],
        "wind_speed_kmh": weather["wind_speed_kmh"],
        "weather_status": status,
        "agent_logs": state["agent_logs"] + [
            "Weather API retrieved data successfully"
        ],
    }


def simulated_weather_agent(state: DisasterState) -> dict:
    """Load simulated weather without calling the weather API."""

    status = "Simulated demonstration data — not live weather"

    return {
        "location": state.get(
            "location", "DEMO CITY (SIMULATED)"
        ),
        "latitude": state.get("latitude", 0.0),
        "longitude": state.get("longitude", 0.0),
        "observation_time": "SIMULATED TEST DATA",
        "temperature_c": state.get("temperature_c", 25.0),
        "humidity_percent": state.get("humidity_percent", 50.0),
        "current_precipitation_mm": state.get(
            "current_precipitation_mm", 0.0
        ),
        "rainfall_mm": state.get("rainfall_mm", 0.0),
        "weather_code": state.get("weather_code", 0),
        "wind_speed_kmh": state.get("wind_speed_kmh", 0.0),
        "weather_status": status,
        "agent_logs": state.get("agent_logs", []) + [
            "Simulated weather loaded; no weather API call made"
        ],
    }



def risk_agent(state: DisasterState) -> dict:
    """Classify prototype risk after validating weather measurements."""

    required_fields = [
        "rainfall_mm",
        "current_precipitation_mm",
        "wind_speed_kmh",
        "agent_logs",
    ]

    missing_fields = [
        field for field in required_fields
        if field not in state or state[field] is None
    ]

    if missing_fields:
        raise ValueError(
            f"Risk Agent cannot run. Missing fields: "
            f"{', '.join(missing_fields)}"
        )

    try:
        rainfall = float(state["rainfall_mm"])
        current_precipitation = float(
            state["current_precipitation_mm"]
        )
        wind_speed = float(state["wind_speed_kmh"])
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Weather measurements must be numeric."
        ) from exc

    measurements = {
        "rainfall_mm": rainfall,
        "current_precipitation_mm": current_precipitation,
        "wind_speed_kmh": wind_speed,
    }

    for field, value in measurements.items():
        if not math.isfinite(value):
            raise ValueError(
                f"{field} must be a finite number."
            )

        if value < 0:
            raise ValueError(
                f"{field} cannot be negative."
            )

    score = 0
    factors = []

    # Factor 1: Recent rainfall
    if rainfall >= 100:
        score += 4
        factors.append("very high recent rainfall")
    elif rainfall >= 50:
        score += 3
        factors.append("high recent rainfall")
    elif rainfall >= 25:
        score += 2
        factors.append("moderate recent rainfall")

    # Factor 2: Current precipitation
    if current_precipitation >= 10:
        score += 2
        factors.append("high current precipitation")
    elif current_precipitation >= 2:
        score += 1
        factors.append("current precipitation detected")

    # Factor 3: Wind speed
    if wind_speed >= 75:
        score += 2
        factors.append("high wind speed")
    elif wind_speed >= 40:
        score += 1
        factors.append("elevated wind speed")

    # Illustrative prototype thresholds only.
    if score >= 4:
        risk = "HIGH"
    elif score >= 2:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    if not factors:
        factors.append(
            "no prototype scoring thresholds triggered"
        )

    factor_summary = ", ".join(factors)

    log_message = (
        f"Prototype risk: {risk}; score: {score}; "
        f"factors: {factor_summary}"
    )

    print(f"[Risk Agent] {log_message}")

    logger.info(
    "Risk assessment completed: risk=%s, score=%s",
    risk,
    score,
)

    return {
        "risk_level": risk,
        "agent_logs": state["agent_logs"] + [log_message],
    }



def route_by_risk(state: DisasterState) -> str:
    risk = state["risk_level"]

    if risk == "HIGH":
        return "high"
    elif risk == "MEDIUM":
        return "medium"
    return "low"


def monitor_agent(state: DisasterState) -> dict:
    message = (
        "Continue monitoring weather and official alerts."
    )

    print("[Monitor Agent]", message)

    return {
        "recommendation": message,
        "agent_logs": state["agent_logs"] + [
            "Monitoring recommendation prepared"
        ],
    }


def warning_agent(state: DisasterState) -> dict:
    message = (
        "Review official weather alerts and prepare for "
        "possible evacuation if instructed by authorities."
    )

    print("[Warning Agent]", message)

    return {
        "recommendation": message,
        "agent_logs": state["agent_logs"] + [
            "Warning recommendation prepared"
        ],
    }


from shelter_db import find_shelters


def resource_agent(state: DisasterState) -> dict:
    """Search the database for matching shelter records."""

    city = state["location"]

    try:
        shelters = find_shelters(city, minimum_places=1)

        logger.info(
    "Shelter lookup completed for location: %s; matches=%d",
    city,
    len(shelters),
)
    except (ValueError, Exception) as exc:


        logger.exception(
    "Shelter lookup failed for location: %s",
    city,
)
        # Keep the workflow running if the lookup fails.
        message = (
            "Shelter lookup failed. Contact official emergency "
            "services for current, verified shelter information."
        )

        print(f"[Resource Agent] {message}")
        print(f"[Resource Agent] Lookup error: {exc}")

        return {
            "shelter_options": [],
            "recommendation": message,
            "agent_logs": state["agent_logs"] + [
                "Shelter database lookup failed"
            ],
        }

    # The database currently contains development/test records.
    if shelters:
        shelter_lines = [
            (
                f"{item['name']} — {item['address']} "
                f"({item['available_places']} reported places)"
            )
            for item in shelters
        ]

        message = (
            "Database matches found, but their real-world status "
            "must be independently verified before use:\n"
            + "\n".join(shelter_lines)
        )

        print("[Resource Agent]", message)

        return {
            "shelter_options": shelter_lines,
            "recommendation": message,
            "agent_logs": state["agent_logs"] + [
                f"Shelter database returned {len(shelters)} match(es)"
            ],
        }

    message = (
        f"No matching shelter records found for {city}. "
        "Contact official emergency services for current shelter "
        "locations and capacity."
    )

    print("[Resource Agent]", message)

    return {
        "shelter_options": [],
        "recommendation": message,
        "agent_logs": state["agent_logs"] + [
            "No matching shelter records found"
        ],
    }



def finalize_agent(state: DisasterState) -> dict:
    summary = (
        f"Location: {state['location']} | "
        f"Recent hourly rainfall total: "
        f"{state['rainfall_mm']} mm | "
        f"Prototype risk: {state['risk_level']}"
    )

    print("[Finalizer] Workflow completed.")

    logger.info(
    "Emergency response workflow finalized for location: %s",
    state["location"],
)

    return {
        "summary": summary,
        "agent_logs": state["agent_logs"] + [
            "Final summary generated"
        ],
    }

def communication_agent(state: DisasterState) -> dict:
    """Generate a structured, risk-specific user message."""

    location = state["location"]
    risk = state["risk_level"]
    rainfall = state["rainfall_mm"]
    wind_speed = state["wind_speed_kmh"]
    recommendation = state.get(
        "recommendation",
        "Follow official weather updates.",
    )

    if risk == "HIGH":
        title = "HIGH PROTOTYPE RISK"
        guidance = (
            "Check official weather and emergency alerts immediately. "
            "Follow instructions from local authorities. If you need "
            "shelter, contact official emergency services for current, "
            "verified locations and availability."
        )

    elif risk == "MEDIUM":
        title = "MEDIUM PROTOTYPE RISK"
        guidance = (
            "Monitor official weather alerts, review local safety "
            "guidance, and prepare for changing conditions. Follow "
            "any instructions issued by local authorities."
        )

    else:
        title = "LOW PROTOTYPE RISK"
        guidance = (
            "Continue monitoring weather conditions and official "
            "alerts. A low prototype score does not guarantee safety."
        )

    message = (
        f"{title}\n"
        f"Location: {location}\n"
        f"Recent hourly rainfall total: {rainfall} mm\n"
        f"Wind speed: {wind_speed} km/h\n"
        f"Prototype risk level: {risk}\n\n"
        f"Recommended action:\n{guidance}\n\n"
        f"Agent recommendation: {recommendation}"
    )

    print("\n[Communication Agent] Message generated:")
    print(message)
    
    logger.info(
        "Communication message generated for risk level: %s",
        risk,
    )


    return {
        "communication_message": message,
        "agent_logs": state["agent_logs"] + [
            f"Communication message generated for {risk} risk"
        ],
    }


