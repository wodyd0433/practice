from pathlib import Path
import requests
from time import sleep

import pandas as pd

API_ROOT = "http://stcis.go.kr/openapi" 
ROOT_DIR = Path(__file__).resolve().parents[0]
RAW_DIR = ROOT_DIR / "datasets"
ENV_DIR = ROOT_DIR / ".env"


'''
class
RequestStat               | 요청 상태값을 남기는 클래스

def
- run_collection
--- make_session          | return requests.Session
--- fetch_area_codes      | return pd.Dataframe
----- call_api            | return dict
--- collect_quarter_od    | return tuple[pd.Datafram, dict[str, object]]
----- call_api            | return dict
'''

# API 호출 결과를 유형별로 집계해 메타 정보에 남긴다.
# 나중에 어떻게 쓰이는지 확인이 필요함
class RequestStat:
    ok: int = 0
    not_found: int = 0
    error: int = 0
    exception: int = 0

# 공통 GET 호출 래퍼로 HTTP 오류를 즉시 노출하고 JSON만 반환한다.
def call_api(session: requests.Session, endpoint: str, params: dict[str,str], timeout: int =30) -> dict:
    response = session.get(f"{API_ROOT}/{endpoint}", params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()

# 재사용 가능한 세션을 만들고 서비스 식별용 User-Agent를 설정한다.
def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent":"API-practice--stcis/1.0"})
    return session

# 시도 -> 시군구 -> 읍면동 순서로 전체 행정구역 코드를 펼처서 테이블로 만든다.
def fetch_area_codes(session: requests.Session, apikey: str) -> pd.DataFrame:
    province_data = call_api(session, "areacode.json", {"apikey":apikey})
    print("="*20 + "\n시/도 정보를 호출합니다.\n" + "="*20)
    provinces = province_data.get("result", []) or []
    rows: list[dict[str,str | None]] = []
    '''
    privinces
    "result":[{"sdCd":"11","sdNm":"서울특별시","sggCd":null,"sggNm":null,"emdCd":null,"emdNm":null},
    {"sdCd":"26","sdNm":"부산광역시","sggCd":null,"sggNm":null,"emdCd":null,"emdNm":null},
    ]
    '''
    # 시 호출 --> 군/구 호출 --> 읍/면/동 호출 --> append
    for province in provinces:
        sd_cd = str(province.get("sdCd") or "")
        if not sd_cd:
            continue
        sgg_data = call_api(session, "areacode.json", {"apikey":apikey, "sdCd":sd_cd})
        print("="*20 + "\n군/구 정보를 호출합니다.\n" + "="*20)
        for sgg in sgg_data.get("result",[]) or []:
            sgg_cd = str(sgg.get("sggCd") or "")
            if not sgg_cd:
                continue
            emd_data = call_api(session, "areacode.json", {"apikey":apikey, "sdCd":sd_cd, "sggCd":sgg_cd})
            print("="*20 + "\n읍/면/동 정보를 호출합니다.\n" + "="*20)
            for emd in emd_data.get("result", []) or []:
                emd_cd = str(emd.get("emdCd") or "")
                if not emd_cd:
                    continue
                rows.append(
                    {
                        "sdCd": str(emd.get("sdCd") or ""),
                        "sdNm": emd.get("sdNm"),
                        "sggCd": str(emd.get("sggCd") or ""),
                        "sggNm": emd.get("sggNm"),
                        "emdCd": str(emd.get("emdCd") or ""),
                        "emdNm": emd.get("emdNm"),
                    }
                )
            sleep(0.5)
        sleep(0.5)
    print("="*20 + "\n모든 법정행정코드가 호출이 완료되었습니다." + "="*20)
    frame = pd.DataFrame(rows)
    return frame.drop_duplicates(subset=["emdCd"]).sort_values(["sdCd", "sggCd", "emdCd"]).reset_index(drop=True)