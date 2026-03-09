import requests
import json

API_ROOT = "https://stcis.go.kr/openapi"

def call_api(session: requests.Session, end_point: str, params: dict[str, str], timeout: int = 30) -> dict:
    response = session.get(f"{API_ROOT}/{end_point}", params = params, timeout = timeout)
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "")

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError as exc:
        preview = response.text[:300].strip()
        raise ValueError(
            f"Expected JSON but received non-JSON response. "
            f"url={response.url!r}, status={response.status_code}, "
            f"content_type={content_type!r}, body_preview={preview!r}"
        ) from exc
