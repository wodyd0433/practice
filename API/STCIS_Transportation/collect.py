
'''
STCIS를 API를 호출해서 4개의 목적지 (광화문, 여의도, 성수, 강남)로 가는 출근시간의 교통카드 기반 소요 시간 데이터를 수집해서 csv로 저장한다.
1. API key를 로드한다.
2. 세션을 만든다.
3. 법정행정구역코드를 수집한다.
4. OD 데이터를 수집한다.
5. 출발지를 구 단위로 그룹화한다.
6. csv로 저장한다.
'''

from dotenv import load_dotenv
import requests
import pandas as pd
import json
from time import sleep
import os

from session import *
from fetch import *

def run_collection(
        requested_date: str, # 수집을 요청하는 날짜,
        destination_emdCd: str, # 목적지의 읍면동 코드
        destination_emdNm: str, # 목적지의 이름 (광화문/여의도/성수/강남)
        hour_from: int, # 수집을 시작하는 시간,
        hour_to: int, # 수집을 종료하는 시간,
        date_from: str, # 수집을 하는 시작 날짜,
        date_to: str, # 수집을 하는 종료 날짜,
        pause_second: int, # API 호출 시 호출 간격 설정,
) -> None:
    # 1. .env 파일의 환경변수를 로드한다.
    load_dotenv()
    apikey = os.getenv("STCIS_API_KEY")

    # 2. Session을 만든다.
    session = make_session()

    # 3. area_codes를 dataframe으로 추출한 후 서울 대상으로만 필터링한다.
    area_codes = fetch_area_codes(session, apikey)
    area_codes = area_codes 중에서 시도가 서울인것만을 대상

    # 4. 모든 시도/군구/읍면동 에서 (광화문/여의도/성수/강남)로 걸리는 시간 API 호출한다. 
    collect_quater_od()

    # 5. 출발지를 군구 단위로 묶는다.
    build_gu_aggregate()

    # 6. csv로 저장한다.
    save_to_csv()

    # 7. session을 종료한다.
    session.close()
