from collect import *
import argparse

DESTINATION_EMD_CD = "1120011400"
DESTINATION_NAME = "성수동1가"

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default="20260224")
    parser.add_argument("--pause-seconds", type=float, default=0.05)
    args = parser.parse_args()

    run_collection(
        requested_date = args.date,
        destination_emdCd = DESTINATION_EMD_CD,
        destination_emdNm = DESTINATION_NAME,
        pause_second = args.pause_seconds,
    )

if __name__ == "__main__":
    main()