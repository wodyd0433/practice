
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
from pathlib import Path

from session import *
from fetch import *

ROOT_DIR = Path(__file__).resolve().parents[0]
RAW_DIR = ROOT_DIR/"datasets"/"raw"

def run_collection(
        requested_date: str, # 수집하는 날짜
        destination_emdCd: str, # 목적지의 읍면동 코드
        destination_emdNm: str, # 목적지의 이름 (광화문/여의도/성수/강남)
        pause_second: int, # API 호출 시 호출 간격 설정,
) -> None:
    # 1. .env 파일의 환경변수를 로드한다.
    load_dotenv()
    apikey = os.getenv("STCIS_API_KEY")
    if not apikey:
        raise ValueError("STCIS_API_KEY is not set.")

    # 2. Session을 만든다.
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    session = make_session()
    try:
        # 3. area_codes가 이미 있는경우 csv 파일을 호출한다.
        AREA_DIR = "stcis_areacodes.csv"
        if Path(RAW_DIR/AREA_DIR).exists():
            area_codes = pd.read_csv(RAW_DIR/AREA_DIR)

        else:
            # 4. area_codes가 없는 경우 API 호출하고 csv로 저장한다.
            area_codes = fetch_area_codes(session, apikey)
            area_codes.to_csv(RAW_DIR/AREA_DIR, index=False, encoding="utf-8-sig")

        # 5. area_code를 서울 대상으로만 필터링한다.
        area_codes = area_codes.loc[area_codes["sdCd"].eq("11")].copy()

        # 6. 모든 시도/군구/읍면동 에서 목적지로 걸리는 시간 API를 호출한다.
        frame = fetch_od(
            session=session,
            apikey=apikey,
            opratDate=requested_date,
            origins=area_codes,
            destination_emd_cd=destination_emdCd,
            pause_second=pause_second,
        )
        frame = frame.sort_values(
            ["opratDate", "stgSggCd", "stgEmdCd", "tzon", "quater"]
        ).reset_index(drop=True)
        frame.to_csv(
            RAW_DIR / f"{destination_emdNm} 교통카드_{requested_date}.csv",
            index=False,
            encoding="utf-8-sig",
        )
    finally:
        session.close()
