
from unittest.mock import patch
import requests

from weather_service import get_coordinates


def test_invalid_city():
    """An unknown city should produce a clear error."""
    mock_response = {
        "results": []
    }

    with patch(
        "weather_service.requests.get"
    ) as mock_get:
        response = mock_get.return_value
        response.status_code = 200
        response.json.return_value = mock_response

        try:
            get_coordinates("InvalidCityXYZ")
        except (ValueError, LookupError) as exc:
            print("PASS: Invalid city handled safely")
            print(f"Message: {exc}")
        else:
            raise AssertionError(
                "Expected an error for an invalid city"
            )


def test_api_failure():
    """Repeated API failures should not crash silently."""
    with patch(
        "weather_service.requests.get",
        side_effect=requests.exceptions.Timeout(
            "Connection timed out"
        ),
    ):
        try:
            get_coordinates("Indore")
        except requests.exceptions.RequestException:
            print("PASS: API timeout propagated safely")
        else:
            raise AssertionError(
                "Expected a request exception after retries"
            )


if __name__ == "__main__":
    test_invalid_city()
    test_api_failure()
    print("ALL WEATHER ERROR TESTS PASSED!")
