import json
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8000"


def make_request(path: str, method: str = "GET", body: dict | None = None):
    data = None
    headers = {}

    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=data,
        headers=headers,
        method=method,
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            content = response.read().decode("utf-8")

            return (
                response.status,
                json.loads(content) if content else None,
            )

    except urllib.error.HTTPError as error:
        content = error.read().decode("utf-8")

        try:
            payload = json.loads(content)
        except json.JSONDecodeError:
            payload = content

        return error.code, payload


def test_health_endpoint():
    status, body = make_request("/api/v1/health")

    assert status == 200
    assert isinstance(body, dict)


def test_openapi_available():
    status, body = make_request("/openapi.json")

    assert status == 200
    assert isinstance(body, dict)
    assert "paths" in body


def test_required_api_routes_exist():
    status, body = make_request("/openapi.json")

    assert status == 200

    paths = body["paths"]

    assert "/api/v1/sessions" in paths
    assert "/api/v1/chat/messages" in paths
    assert "/api/v1/lead-capture" in paths


def test_session_creation():
    status, body = make_request(
        "/api/v1/sessions",
        method="POST",
        body={
            "source_page": "http://localhost:5173/test"
        },
    )

    assert status == 200
    assert isinstance(body, dict)
    assert "session_token" in body
    assert body["session_token"]