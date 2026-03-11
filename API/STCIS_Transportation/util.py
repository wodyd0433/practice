import requests
import json

API_ROOT = "https://stcis.go.kr/openapi"

def call_api(session: requests.Session, end_point: str, params: dict[str, str], timeout: int = 30) -> dict:
    response = session.get(f"{API_ROOT}/{end_point}", params = params, timeout = timeout)
    response.raise_for_status()
    content_type = response.headers.get("Content-Type", "")
    return response.json()