# -*- coding: utf-8 -*-
"""
공공데이터포털 및 식품안전나라 API 설정 모듈.

.env 파일에서 인증키를 로드하고 식품안전나라 서비스 ID 및
공공데이터포털 API 엔드포인트 URL을 관리합니다.
"""

import os
import requests
from dotenv import load_dotenv

# 1. .env 파일에 숨겨둔 인증키를 안전하게 불러옵니다.
load_dotenv()
API_KEY = os.getenv("DATA_GO_KR_API_KEY")

# 2. 식품안전나라 API 그룹 (인증키가 주소 중간에 들어가는 유형)
# Key: 데이터 이름 / Value: 서비스 ID
FOOD_SAFETY_SERVICES = {
    "기능성_원료인정_현황": "I-0040",
    "건강기능식품_영양DB": "I0760",
    "개별인정형_정보": "I-0050",
    "건강기능식품정보": "I2710"
}

# 3. 공공데이터포털 API 그룹 (일반적인 End Point 주소 유형)
# Key: 데이터 이름 / Value: 기본 엔드포인트 URL
PUBLIC_DATA_ENDPOINTS = {
    "식품영양성분_DB": "http://apis.data.go.kr/1471000/FoodNtrIrdntInfoService1/getFoodNtrItmList",
    "DUR_품목정보": "http://apis.data.go.kr/1471000/DurgPrfmdInfoService04/getUsjntTabooInfoList",
    "e약은요": "http://apis.data.go.kr/1471000/DrbEasyDrugInfoService/getDrbEasyDrugList"
}
