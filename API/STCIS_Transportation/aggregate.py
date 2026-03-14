'''
서울의 모든 읍면동 출발지 --> 강남/성수/여의도/광화문의 교통카드 데이터를
1. 읍면동 단위의 지역으로 도착하는 시간대(tzon) 단위로 sum((교통량 * 걸린시간(초))/교통량
2. 시군구 단위의 지역으로 출발하는 시간대(tzon) 단위로 sum((교통량 * 걸린시간(초))/교통량
3. input은 run collection에서 frame으로 받고
4. output은 csv로 저장한다.
5. 함수 호출은 main에서 한다.
'''

import pandas as pd
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[0]
RAW_DIR = ROOT_DIR/"datasets"/"raw"

def aggregate_gu(
        frame:pd.DataFrame,
        requested_date:str,
        destination_emdCd:str,
        destination_emdNm:str,
        ) -> None:
    working = frame.copy()
    keys = [
        "opratDate",
        "stgSdCd",
        "stgSdNm",
        "stgSggCd",
        "stgSggNm",
        "arrSdCd",
        "arrSdNm",
        "arrSggCd",
        "arrSggNm",
        "arrEmdCd",
        "arrEmdNm",
        "tzon",
        "quater",
    ]

    '''
    grouped = (
        working.groupby(keys, dropna=False).apply(
            lambda group: pd.Series(
                {
                    "orgin_emd_count":group["stgEmdCd"].nunique(),
                    "useStf":group["useStf"].sum(min_count=1),
                    "useTm":(group["useStf"]*group["useTm"]).sum() / group["useStf"].sum(),
                }
            ),
            include_groups=False
        )
        .reset_index()
    )
    '''
    working["weighted_useTm"] = working["useStf"]*working["useTm"]
    grouped = (
        working.groupby(keys, dropna=False)
        .agg(
            origin_emd_count=("stgEmdCd", lambda s: int(s.nunique())),
            useStf=("useStf", lambda s: int(s.sum())),
            weighted_useTm=("weighted_useTm", "sum"),
        )
        .reset_index()
    )
    grouped["useTm"]=(grouped["weighted_useTm"] / grouped["useStf"]).round(2)
    grouped=grouped.drop(columns=["weighted_useTm"])

    grouped.to_csv(RAW_DIR/f"구단위 {destination_emdNm} 평균 소요시간_{requested_date}.csv",
                   index=False,
                   encoding="utf-8-sig",)

# aggregate 대상:
# 1. stgEmdCd --> unique 값으로 처리
# 2. stgEmdNm --> unique 값으로 처리
# 3. avg_time --> (useStf * useTm).sum() / useStf.sum()