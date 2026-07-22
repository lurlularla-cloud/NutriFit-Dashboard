"""
iHerb, 올리브영, 쿠팡의 제품 데이터를 각각 로드하고 표준화된 포맷으로 변환한 뒤,
통합된 단일 CSV 파일로 결합하여 지정된 대시보드 데이터 폴더에 저장하는 스크립트입니다.

주요 처리 단계:
1. 각 플랫폼의 데이터를 상대 경로를 통해 판다스 데이터프레임으로 로드합니다.
2. 브랜드, 제형, 가격, 리뷰수, 평점 등을 플랫폼별 특성에 맞게 추출 및 정제합니다.
3. 공통 컬럼 포맷으로 표준화하고 결합합니다.
4. 'NutriFit-Dashboard/data/integrated_products.csv' 경로로 저장합니다.
"""
import pandas as pd
import numpy as np
import re
import os

def clean_iherb_brand(brand_name):
    """
    iHerb 브랜드명에서 한글 브랜드명을 우선 추출하고 정제합니다.
    예: "California Gold Nutrition (캘리포니아 골드 뉴트리션)" -> "캘리포니아 골드 뉴트리션"
    """
    if not isinstance(brand_name, str):
        return '기타'
    match = re.search(r'\(([^)]+)\)', brand_name)
    if match:
        korean_brand = match.group(1).strip()
        if re.search(r'[가-힣]', korean_brand):
            return korean_brand
    cleaned = re.sub(r'\(.*?\)', '', brand_name).strip()
    return cleaned

def extract_coupang_brand(name):
    """
    쿠팡 제품명에서 브랜드를 추출합니다.
    대괄호로 된 수식어를 우선 제거한 후 알려진 브랜드 목록을 확인하고,
    없을 경우 첫 단어를 브랜드명으로 채택합니다.
    """
    if not isinstance(name, str):
        return '기타'
    cleaned = re.sub(r'\[.*?\]', '', name).strip()
    
    known_brands = [
        '종근당건강', '종근당', '고려은단', '나우푸드', '락토핏', '아임비타', '센트룸', 
        '뉴트리원', 'GNM자연의품격', 'GNM', '듀오락', '솔가', '에스더포뮬러', '여에스더',
        '세노비스', '정관장', '한미양행', '일양약품', '안국건강', '씨제이웰케어', 'CJ웰케어',
        '오쏘몰', 'WHOLELIFE', '센트휴', '비코드', '리본핏', '네이처드림', '황금이네', 
        '캘리포니아 골드 뉴트리션', 'California Gold Nutrition', '닥터스 베스트', "Doctor's Best"
    ]
    for brand in known_brands:
        if brand.lower() in cleaned.lower():
            return brand
            
    words = cleaned.split()
    if words:
        brand_candidate = words[0]
        prevent_words = ['유기농', '식물성', '국산', '프리미엄', '수입', '1일', '데일리', '특가', '정품', '캐나다', '미국']
        if brand_candidate in prevent_words and len(words) > 1:
            return words[1]
        return brand_candidate
    return '기타'

def extract_form(name):
    """
    제품명 분석을 통해 제형(캡슐, 타블렛, 분말, 젤리/구미, 액상, 환)을 정규식 기반으로 분류합니다.
    """
    if not isinstance(name, str):
        return '기타'
    name_lower = name.lower()
    if '캡슐' in name_lower:
        return '캡슐'
    elif '소프트젤' in name_lower:
        return '소프트젤'
    elif '타블렛' in name_lower:
        return '타블렛'
    
    # '정' 분류 시 오탐 방지 (예: 정품, 정량 제외 및 수량 단위 '정' 탐색)
    cleaned_for_tablet = re.sub(r'정품|정량|정상|정보|정리|정수|정직|정밀', '', name_lower)
    if re.search(r'\d+\s*정', cleaned_for_tablet) or ' 타블렛' in name_lower or re.search(r'\b정\b', cleaned_for_tablet):
        return '타블렛'
    elif '정' in cleaned_for_tablet and not any(w in cleaned_for_tablet for w in ['과정', '결정', '가정', '감정', '개정']):
        # 제품 정보 끝부분에 '120정', '60정' 등 형태로 기재되는 경우가 많으므로 정으로 판단
        return '타블렛'
        
    if '포' in name_lower or '분말' in name_lower or '가루' in name_lower or '파우더' in name_lower:
        return '분말'
    elif '젤리' in name_lower or '구미' in name_lower:
        return '젤리/구미'
    elif '액상' in name_lower or '앰플' in name_lower or '즙' in name_lower or '드링크' in name_lower or '액' in name_lower:
        return '액상'
    elif '환' in name_lower:
        cleaned_for_pill = re.sub(r'환경|환불|환영|변환|교환|소환', '', name_lower)
        if '환' in cleaned_for_pill:
            return '환'
    return '기타'

def parse_price(val):
    """
    문자열 또는 숫자 형태의 가격 정보를 정수형으로 변환합니다.
    """
    if pd.isna(val):
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    val_str = str(val).replace('₩', '').replace(',', '').strip()
    match = re.search(r'\d+', val_str)
    if match:
        return int(match.group())
    return 0

def parse_review_count(val):
    """
    문자열 또는 숫자 형태의 리뷰수 정보를 정수형으로 변환합니다.
    '999+' 등 특수 문자열을 처리합니다.
    """
    if pd.isna(val):
        return 0
    if isinstance(val, (int, float)):
        return int(val)
    val_str = str(val).replace('+', '').replace(',', '').strip()
    match = re.search(r'\d+', val_str)
    if match:
        return int(match.group())
    return 0

def main():
    print("=== 데이터 통합 프로세스 시작 ===")
    
    # 1. iHerb 데이터 처리
    iherb_path = "../../iherb/data/서동임_Herb_supplements (1).csv"
    if os.path.exists(iherb_path):
        print(f"iHerb 데이터 로드 중: {iherb_path}")
        df_iherb = pd.read_csv(iherb_path)
        
        # 필드 변환 및 정제
        df_iherb_clean = pd.DataFrame()
        df_iherb_clean['플랫폼'] = ['iHerb'] * len(df_iherb)
        df_iherb_clean['브랜드'] = df_iherb['brandName'].apply(clean_iherb_brand)
        df_iherb_clean['제품명'] = df_iherb['displayName']
        df_iherb_clean['전성분'] = [np.nan] * len(df_iherb)
        df_iherb_clean['제형'] = df_iherb['productForm'].fillna('기타')
        df_iherb_clean['알레르기 성분'] = [np.nan] * len(df_iherb)
        df_iherb_clean['가격'] = df_iherb['discountPrice'].apply(parse_price)
        df_iherb_clean['리뷰수'] = df_iherb['ratingCount'].apply(parse_review_count)
        df_iherb_clean['평점'] = df_iherb['rating'].fillna(0.0).astype(float)
        df_iherb_clean['상품URL'] = df_iherb['url']
        df_iherb_clean['이미지URL'] = [np.nan] * len(df_iherb)
        print(f"iHerb 변환 완료: {len(df_iherb_clean)}행")
    else:
        print(f"경고: iHerb 데이터 파일 없음: {iherb_path}")
        df_iherb_clean = pd.DataFrame()

    # 2. 올리브영 데이터 처리
    oy_path = "../../oliveyoung/data/서동임_올리브영_건강식품_수집데이터.csv"
    if os.path.exists(oy_path):
        print(f"올리브영 데이터 로드 중: {oy_path}")
        df_oy = pd.read_csv(oy_path)
        
        # 필드 변환 및 정제
        df_oy_clean = pd.DataFrame()
        df_oy_clean['플랫폼'] = ['올리브영'] * len(df_oy)
        df_oy_clean['브랜드'] = df_oy['brand'].apply(lambda x: str(x).strip() if pd.notna(x) else '기타')
        df_oy_clean['제품명'] = df_oy['name']
        df_oy_clean['전성분'] = [np.nan] * len(df_oy)
        df_oy_clean['제형'] = df_oy['name'].apply(extract_form)
        df_oy_clean['알레르기 성분'] = [np.nan] * len(df_oy)
        df_oy_clean['가격'] = df_oy['price_cur'].apply(parse_price)
        df_oy_clean['리뷰수'] = df_oy['review_count'].apply(parse_review_count)
        df_oy_clean['평점'] = df_oy['score'].fillna(0.0).astype(float)
        df_oy_clean['상품URL'] = df_oy['link']
        df_oy_clean['이미지URL'] = df_oy['img_url']
        print(f"올리브영 변환 완료: {len(df_oy_clean)}행")
    else:
        print(f"경고: 올리브영 데이터 파일 없음: {oy_path}")
        df_oy_clean = pd.DataFrame()

    # 3. 쿠팡 데이터 처리
    cp_path = "../../coupang/data/coupang_all_products.csv"
    if os.path.exists(cp_path):
        print(f"쿠팡 데이터 로드 중: {cp_path}")
        df_cp = pd.read_csv(cp_path)
        
        # 필드 변환 및 정제
        df_cp_clean = pd.DataFrame()
        df_cp_clean['플랫폼'] = ['쿠팡'] * len(df_cp)
        df_cp_clean['브랜드'] = df_cp['product_name'].apply(extract_coupang_brand)
        df_cp_clean['제품명'] = df_cp['product_name']
        df_cp_clean['전성분'] = [np.nan] * len(df_cp)
        df_cp_clean['제형'] = df_cp['product_name'].apply(extract_form)
        df_cp_clean['알레르기 성분'] = [np.nan] * len(df_cp)
        df_cp_clean['가격'] = df_cp['price'].apply(parse_price)
        df_cp_clean['리뷰수'] = df_cp['review_count'].apply(parse_review_count)
        df_cp_clean['평점'] = df_cp['rating'].fillna(0.0).astype(float)
        df_cp_clean['상품URL'] = df_cp['detail_url']
        df_cp_clean['이미지URL'] = df_cp['image_url']
        print(f"쿠팡 변환 완료: {len(df_cp_clean)}행")
    else:
        print(f"경고: 쿠팡 데이터 파일 없음: {cp_path}")
        df_cp_clean = pd.DataFrame()

    # 4. 데이터 통합 및 결합
    dfs_to_concat = [df for df in [df_iherb_clean, df_oy_clean, df_cp_clean] if not df.empty]
    if dfs_to_concat:
        df_integrated = pd.concat(dfs_to_concat, ignore_index=True)
        print(f"\n데이터 결합 완료! 총 {len(df_integrated)}개 제품 정보 통합됨.")
        
        # 저장 폴더가 존재하지 않으면 생성
        output_dir = "../data"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"출력 폴더 생성됨: {output_dir}")
            
        output_path = os.path.join(output_dir, "integrated_products.csv")
        df_integrated.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"통합 데이터 CSV 저장 완료: {output_path}")
    else:
        print("에러: 통합할 데이터셋이 존재하지 않습니다.")

if __name__ == "__main__":
    main()
