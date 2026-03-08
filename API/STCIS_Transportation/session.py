import requests

def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent":"STCIS API Request/1.0"})
    return session