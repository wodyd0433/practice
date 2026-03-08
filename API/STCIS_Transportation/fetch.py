from time import sleep
import pandas as pd
import requests
from util import *

def fetch_area_codes(session: requests.Session, apikey: str) -> pd.DataFrame:
    # api call하여 시도 코드를 받는다. -> 
    # api call하여 군구 코드를 받는다. -> 
    # api call하여 읍면동 코드를 받는다.
    rows: list[dict[str,str] | None] = []

    sd_data = call_api(session, end_point="areacode.json", params = {"apikey":apikey})
    for sd_result in sd_data.get("result", []):
        sd_cd = str(sd_result.get("sdCd"))
        sgg_data = call_api(session, end_point="areacode.json", params = {"apikey":apikey, "sdCd":sd_cd})

        for sgg_result in sgg_data.get("result", []):
            sgg_cd = str(sgg_result.get("sggCd"))
            emd_data = call_api(session, end_point="areacode.json", params = {"apikey":apikey, "sdCd":sd_cd, "sggCd":sgg_cd})

            for emd_result in emd_data.get("result", []):
                rows.append(
                    {
                        "sdCd": str(emd_result.get("sdCd")),
                        "sdNm": emd_result.get("sdNm"),
                        "sggCd": str(emd_result.get("sggCd")),
                        "sggNm": emd_result.get("sggNm"),
                        "emdCd": str(emd_result.get("emdCd")),
                        "emdNm": emd_result.get("emdNm"),
                    }
                )
        sleep(0.05)
    sleep(0.05)

    area_code_frame = pd.DataFrame(rows)
    return area_code_frame.drop_duplicates(subset=["emdCd"]).sort_values(["sdCd","sggCd","emdCd"]).reset_index(drop=True)