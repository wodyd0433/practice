from collect import *
from aggregate import *
import argparse

destinations = [
    {"emd_cd": "1120011500", "name": "성수동2가", "date": "20260224"},
    {"emd_cd": "1120011400", "name": "성수동1가", "date": "20260224"},
    ]

def main() -> None:
    for destination in destinations:

        frame = run_collection(
            requested_date = destination["date"],
            destination_emdCd = destination["emd_cd"],
            destination_emdNm = destination["name"],
            pause_second = 0.05,
        )

        aggregate_gu(
            frame,
            requested_date = destination["date"],
            destination_emdCd = destination["emd_cd"],
            destination_emdNm = destination["name"]
            )

if __name__ == "__main__":
    main()