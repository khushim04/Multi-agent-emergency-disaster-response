import math
import time
import requests


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
)



def _get_json(url: str, params: dict, timeout: int) -> dict:
    """Request JSON with retries for temporary API failures."""

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(
                url,
                params=params,
                timeout=timeout,
            )

            # Retry temporary server errors.
            if response.status_code in (500, 502, 503, 504):
                if attempt < max_attempts:
                    
                    time.sleep(attempt)
                    continue

            response.raise_for_status()

            try:
                data = response.json()
            except ValueError as exc:
                raise ValueError(
                    "The API returned an invalid JSON response."
                ) from exc

            if not isinstance(data, dict):
                raise ValueError(
                    "The API returned an unexpected response format."
                )

            if data.get("error"):
                raise ValueError(
                    f"Weather API error: "
                    f"{data.get('reason', 'Unknown error')}"
                )

            return data

        
        except requests.RequestException:
            if attempt == max_attempts:
                raise
            time.sleep(attempt)


            

    raise requests.RequestException(
        "Weather API request failed after multiple attempts."
    )


def _require_number(
    data: dict,
    key: str,
    section: str,
    minimum: float | None = None,
    maximum: float | None = None,
) -> float:
    """Validate a numeric field received from the API."""

    value = data.get(key)

    # bool is a subclass of int in Python, so reject it explicitly.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(
            f"Missing or invalid field: {section}.{key}"
        )

    value = float(value)

    if not math.isfinite(value):
        raise ValueError(
            f"Non-finite value received: {section}.{key}"
        )

    if minimum is not None and value < minimum:
        raise ValueError(
            f"{section}.{key} cannot be below {minimum}."
        )

    if maximum is not None and value > maximum:
        raise ValueError(
            f"{section}.{key} cannot exceed {maximum}."
        )

    return value


def get_coordinates(location: str) -> dict:
    """Convert an Indian city name into coordinates."""

    if not isinstance(location, str) or not location.strip():
        raise ValueError(
            "Please enter a valid city name."
        )

    data = _get_json(
        GEOCODING_URL,
        params={
            "name": location.strip(),
            "count": 1,
            "language": "en",
            "format": "json",
            "countryCode": "IN",
        },
        timeout=15,
    )

    results = data.get("results", [])

    if not isinstance(results, list) or not results:
        raise ValueError(
            f"Location not found in India: {location}"
        )

    place = results[0]

    if not isinstance(place, dict):
        raise ValueError(
            "The geocoding API returned invalid location data."
        )

    name = place.get("name")
    latitude = _require_number(
        place, "latitude", "location", -90, 90
    )
    longitude = _require_number(
        place, "longitude", "location", -180, 180
    )

    if not isinstance(name, str) or not name.strip():
        raise ValueError(
            "The geocoding API did not return a valid city name."
        )

    return {
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "country": place.get("country", ""),
    }


def get_weather_data(location: str) -> dict:
    """Fetch current weather and recent hourly precipitation."""

    place = get_coordinates(location)

    data = _get_json(
        WEATHER_URL,
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "precipitation,"
                "weather_code,"
                "wind_speed_10m"
            ),
            "hourly": (
                "precipitation,"
                "temperature_2m,"
                "relative_humidity_2m"
            ),
            "past_hours": 6,
            "forecast_days": 1,
            "timezone": "auto",
        },
        timeout=20,
    )

    current = data.get("current")
    hourly = data.get("hourly")

    if not isinstance(current, dict):
        raise ValueError(
            "The weather API did not return current conditions."
        )

    if not isinstance(hourly, dict):
        raise ValueError(
            "The weather API did not return hourly data."
        )

    current_time = current.get("time")

    if not isinstance(current_time, str) or not current_time:
        raise ValueError(
            "The API returned an invalid observation timestamp."
        )

    # Validate the current weather measurements.
    temperature = _require_number(
        current, "temperature_2m", "current"
    )
    humidity = _require_number(
        current, "relative_humidity_2m", "current", 0, 100
    )
    current_precipitation = _require_number(
        current, "precipitation", "current", 0
    )
    weather_code = _require_number(
        current, "weather_code", "current", 0
    )
    wind_speed = _require_number(
        current, "wind_speed_10m", "current", 0
    )

    if not weather_code.is_integer():
        raise ValueError(
            "The API returned an invalid weather code."
        )

    # Validate hourly timestamps and precipitation values.
    times = hourly.get("time")
    precipitation = hourly.get("precipitation")

    if not isinstance(times, list) or not isinstance(
        precipitation, list
    ):
        raise ValueError(
            "Hourly timestamps or precipitation data are missing."
        )

    if len(times) != len(precipitation):
        raise ValueError(
            "Hourly timestamps and precipitation arrays do not match."
        )

    past_values = []

    for timestamp, rainfall in zip(times, precipitation):
        if not isinstance(timestamp, str):
            raise ValueError(
                "An invalid timestamp was returned in hourly data."
            )

        # Ignore future forecast records.
        if timestamp > current_time:
            continue

        # Skip missing readings but reject invalid numeric readings.
        if rainfall is None:
            continue

        if (
            isinstance(rainfall, bool)
            or not isinstance(rainfall, (int, float))
            or not math.isfinite(float(rainfall))
            or rainfall < 0
        ):
            raise ValueError(
                "Invalid hourly precipitation value received."
            )

        past_values.append((timestamp, float(rainfall)))

    # Sort records chronologically before selecting the latest three.
    past_values.sort(key=lambda item: item[0])

    if not past_values:
        raise ValueError(
            "No usable recent hourly precipitation data is available."
        )

    latest_three = past_values[-3:]
    recent_rainfall = sum(value for _, value in latest_three)

    return {
        "location": place["name"],
        "latitude": place["latitude"],
        "longitude": place["longitude"],
        "observation_time": current_time,
        "temperature_c": temperature,
        "humidity_percent": humidity,
        "current_precipitation_mm": current_precipitation,
        "rainfall_3h_mm": round(recent_rainfall, 2),
        "weather_code": int(weather_code),
        "wind_speed_kmh": wind_speed,
    }


if __name__ == "__main__":
    try:
        weather = get_weather_data("Indore")

        print("\n--- WEATHER API TEST ---")
        for key, value in weather.items():
            print(f"{key}: {value}")

    except (requests.RequestException, ValueError) as exc:
        print("Weather retrieval failed:", exc)
