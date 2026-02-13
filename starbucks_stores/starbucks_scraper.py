
import requests
import pandas as pd
from loguru import logger
import os

# 로거 설정
log_path = "starbucks_stores/starbucks_scraper.log"
logger.add(log_path, rotation="500 MB", encoding="utf-8")

def get_starbucks_stores(sido_code):
    """
    특정 시도 코드를 사용하여 스타벅스 매장 정보를 가져옵니다.
    """
    url = "https://www.starbucks.co.kr/store/getStore.do"
    headers = {
        "Host": "www.starbucks.co.kr",
        "Origin": "https://www.starbucks.co.kr",
        "Referer": "https://www.starbucks.co.kr/store/store_map.do",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
    }
    payload = {
        "in_biz_cds": "0",
        "in_scodes": "0",
        "search_text": "",
        "p_sido_cd": f"{sido_code:02}",
        "p_gugun_cd": "",
        "isError": "true",
        "in_biz_cd": "",
        "iend": "2000", # 충분히 큰 값으로 설정하여 모든 매장을 가져오도록 함
        "searchType": "A",
        "set_date": "",
        "rndCod": "WAN3GHYX0D",
        "todayPop": "0",
        "all_store": "0",
        "T03": "0", "T01": "0", "T27": "0", "T12": "0", "T09": "0",
        "T30": "0", "T05": "0", "T22": "0", "T21": "0", "T36": "0",
        "T43": "0", "Z9999": "0", "T64": "0", "T66": "0", "P02": "0",
        "P10": "0", "P50": "0", "P20": "0", "P60": "0", "P30": "0",
        "P70": "0", "P40": "0", "P80": "0", "whcroad_yn": "0",
        "P90": "0", "P01": "0", "new_bool": "0"
    }

    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # HTTP 오류가 발생하면 예외를 발생시킴
        logger.info(f"Sido Code '{sido_code:02}'_매장 정보 수집 성공. 찾은 매장 수: {len(response.json()['list'])}")
        return response.json()["list"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Sido Code '{sido_code:02}'_매장 정보 수집 중 오류 발생: {e}")
        return []

@logger.catch
def main():
    """
    전국 스타벅스 매장 정보를 수집하여 CSV 파일로 저장합니다.
    """
    all_stores = []
    # p_sido_cd=01 부터 17까지
    for sido_code in range(1, 18):
        stores = get_starbucks_stores(sido_code)
        all_stores.extend(stores)

    if not all_stores:
        logger.warning("수집된 매장 정보가 없습니다.")
        return

    df = pd.DataFrame(all_stores)
    
    # 데이터 폴더가 없으면 생성
    data_dir = "starbucks_stores/data"
    os.makedirs(data_dir, exist_ok=True)
    
    # CSV 파일로 저장
    output_path = os.path.join(data_dir, "starbucks_ai.csv")
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    
    logger.success(f"전체 {len(df)}개 매장 정보를 '{output_path}' 파일에 성공적으로 저장했습니다.")

if __name__ == "__main__":
    main()
