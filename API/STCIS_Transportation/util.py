import requests

ROOT_URL = "https://stcis.go.kr"

def call_api(session: requests.Session, end_point: str, params: dict[str, str], timeout: int = 30) -> dict:
    response = session.get(f"{ROOT_URL}/{end_point}", params = params, timeout = timeout)
    response.raise_for_status()
    return response.json()