
from unittest.mock import Mock, patch

from weather_service import _get_json


def make_response(status_code, json_data=None):
    response = Mock()
    response.status_code = status_code
    response.json.return_value = json_data or {"ok": True}

    if status_code >= 400:
        from requests import HTTPError
        response.raise_for_status.side_effect = HTTPError(
            f"HTTP {status_code}"
        )

    return response


@patch("weather_service.time.sleep")
@patch("weather_service.requests.get")
def test_retry_after_503(mock_get, mock_sleep):
    mock_get.side_effect = [
        make_response(503),
        make_response(200, {"ok": True}),
    ]

    result = _get_json(
        "https://example.test/weather",
        params={},
        timeout=5,
    )

    assert result == {"ok": True}
    assert mock_get.call_count == 2
    assert mock_sleep.call_count == 1

    print("PASS: Temporary 503 error retried")
    print("PASS: Successful response returned")
    print("ALL WEATHER RETRY TESTS PASSED!")




@patch("weather_service.time.sleep")
@patch("weather_service.requests.get")
def test_all_retries_fail(mock_get, mock_sleep):
    from requests import HTTPError

    response = make_response(503)
    mock_get.return_value = response

    try:
        _get_json(
            "https://example.test/weather",
            params={},
            timeout=5,
        )
    except HTTPError:
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2
        print("PASS: All three attempts were made")
        print("PASS: Final HTTP error propagated")
    else:
        raise AssertionError(
            "Expected an HTTPError after repeated 503 responses"
        )

@patch("weather_service.time.sleep")
@patch("weather_service.requests.get")
def test_retry_after_timeout(mock_get, mock_sleep):
    from requests.exceptions import Timeout

    mock_get.side_effect = [
        Timeout("Connection timed out"),
        make_response(200, {"ok": True}),
    ]

    result = _get_json(
        "https://example.test/weather",
        params={},
        timeout=5,
    )

    assert result == {"ok": True}
    assert mock_get.call_count == 2
    assert mock_sleep.call_count == 1

    print("PASS: Network timeout retried")
    print("PASS: Successful response returned after timeout")


if __name__ == "__main__":
    test_retry_after_503()
    test_all_retries_fail()
    test_retry_after_timeout()
    print("ALL WEATHER RETRY TESTS PASSED!")