# -*- coding: utf-8 -*-
"""
NutriFit Dashboard API 및 데이터 로더 모듈.

식품안전나라, 공공데이터포털(식품/건기식, 의약품)의 인증키 및 엔드포인트를 관리하고,
심평원 DUR ZIP 압축 파일 내부의 엑셀 또는 CSV 데이터를 실시간으로 로드하는 기능을 제공합니다.
"""

import os
import requests
import zipfile  
import pandas as pd
from dotenv import load_dotenv

# 1. .env 파일에서 세분화된 3개의 인증키를 로드합니다.
load_dotenv()
FOOD_SAFETY_API_KEY = os.getenv("FOOD_SAFETY_API_KEY")  # 식품안전나라
PUBLIC_FOOD_API_KEY = os.getenv("PUBLIC_FOOD_API_KEY")  # 공공데이터(식품/건기식)
PUBLIC_DRUG_API_KEY = os.getenv("PUBLIC_DRUG_API_KEY")  # 공공데이터(e약은요)


# ==========================================================
# [그룹 1] 식품안전나라 API (인증키: FOOD_SAFETY_API_KEY)
# ==========================================================
FOOD_SAFETY_SERVICES = {
    "개별인정형_정보": "I-0050",
    "건강기능식품_영양DB": "I0760",
    "기능성_원료인정_현황": "I-0040"
}


# ==========================================================
# [그룹 2] 공공데이터포털 - 식품/건기식 (인증키: PUBLIC_FOOD_API_KEY)
# ==========================================================
FOOD_ENDPOINTS = {
    "건강기능식품정보": "https://apis.data.go.kr/1471000/HtfsInfoService03/getHtfsInfoList",
    "식품영양성분DB정보": "https://apis.data.go.kr/1471000/FoodNtrCpntDbInfo02/getFoodNtrCpntDbList"
}


# ==========================================================
# [그룹 3] 공공데이터포털 - 의약품 (인증키: PUBLIC_DRUG_API_KEY)
# ==========================================================
DRUG_ENDPOINTS = {
    "e약은요": "https://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
}


# ==========================================================
# [그룹 4] ★ 심평원 DUR ZIP 압축 파일 실시간 로더 (실제 파일명 매핑)
# ==========================================================
def load_dur_master_zip(zip_file_name):
    """data/ 폴더 내의 지정된 ZIP 파일을 열어 내부 엑셀 또는 CSV 데이터를 로드합니다."""
    zip_path = os.path.join("data", zip_file_name)
    
    if not os.path.exists(zip_path):
        print(f"[경고] [{zip_path}] 파일이 존재하지 않습니다. data/ 폴더 안의 파일명을 다시 확인해 주세요.")
        return None
        
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            file_list = z.namelist()
            # 압축 내부에서 엑셀 및 CSV 파일 필터링
            data_files = [f for f in file_list if f.endswith(('.xlsx', '.xls', '.csv'))]
            
            if not data_files:
                print(f"[오류] {zip_file_name} 내부에 데이터 파일(xlsx, xls, csv)이 존재하지 않습니다.")
                return None
                
            target_file = data_files[0]
            
            with z.open(target_file) as f:
                if target_file.endswith('.csv'):
                    try:
                        # cp949 인코딩으로 CSV 로드 시도
                        df = pd.read_csv(f, encoding='cp949')
                    except Exception:
                        # 실패 시 utf-8 인코딩으로 다시 로드 시도
                        with z.open(target_file) as f_retry:
                            df = pd.read_csv(f_retry, encoding='utf-8')
                    print(f"[완료] 심평원 DUR 마스터 로드 완료! (CSV)")
                else:
                    # openpyxl 엔진으로 압축 내부 엑셀을 실시간 데이터프레임으로 변환
                    df = pd.read_excel(f, engine='openpyxl')
                    print(f"[완료] 심평원 DUR 마스터 로드 완료! (Excel)")
                    
                print(f"[정보] 파일명: {zip_file_name} -> 내부 문서: [{target_file}] (총 {len(df)}행 데이터 확보)")
                return df
                
    except Exception as e:
        print(f"[오류] ZIP 파일 읽기 중 오류 발생 ({zip_file_name}): {e}")
        return None

# ==========================================================
# 🚀 [자동 실행 및 데이터 할당 테스트]
# ==========================================================
if __name__ == "__main__":
    # 요청하신 실제 파일명 그대로 지정
    DUR_FILE_NAME = "건강보험심사평가원_의약품안전사용서비스(DUR) 의약품 목록_20260601.zip"
    
    # 함수를 실행하여 dur_df 변수에 전체 의약품 마스터 테이블을 담습니다.
    dur_df = load_dur_master_zip(DUR_FILE_NAME)
    
    # 로드가 정상적으로 됐다면 상위 5개 데이터 미리보기 출력
    if dur_df is not None:
        print("\n[DUR 마스터 데이터 샘플 보기]")
        print(dur_df.head())
