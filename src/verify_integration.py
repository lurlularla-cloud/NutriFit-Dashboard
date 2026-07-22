"""
통합된 CSV 제품 데이터(integrated_products.csv)의 정합성, 스키마,
각 필드의 데이터 타입 및 파싱 결과(브랜드, 제형 등)를 검증하는 스크립트입니다.
"""
import pandas as pd
import os

def main():
    print("=== 통합 데이터 검증 시작 ===")
    
    file_path = "../data/integrated_products.csv"
    
    # 1. 파일 존재 여부 확인
    if not os.path.exists(file_path):
        print(f"오류: 통합 데이터 파일이 없습니다. ({file_path})")
        return
        
    print(f"통합 파일 확인됨: {file_path}")
    print(f"파일 크기: {os.path.getsize(file_path):,} bytes")
    
    # 2. CSV 데이터 로드
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"오류: CSV 로드 중 예외 발생: {e}")
        return
        
    print(f"통합 데이터 로드 성공. 행 수: {len(df):,}개 | 열 수: {len(df.columns)}")
    
    # 3. 컬럼 구조 검증
    expected_cols = ['플랫폼', '브랜드', '제품명', '전성분', '제형', '알레르기 성분', '가격', '리뷰수', '평점', '상품URL', '이미지URL']
    missing_cols = [col for col in expected_cols if col not in df.columns]
    if missing_cols:
        print(f"오류: 일부 컬럼이 누락되었습니다: {missing_cols}")
    else:
        print("컬럼 스키마 검증 완료 (모든 필수 컬럼 포함됨)")
        
    # 4. 플랫폼별 데이터 수 검증
    print("\n[플랫폼별 제품 수 분포]")
    platform_counts = df['플랫폼'].value_counts()
    print(platform_counts.to_string())
    
    # 예상 행 수와 비교
    expected_total = 25171 + 2560 + 735 # 28,466
    if len(df) == expected_total:
        print(f"행 수 검증 통과: 총 {len(df):,}개 제품 (예상치 {expected_total:,}개와 일치)")
    else:
        print(f"경고: 총 행 수({len(df)})가 예상 수({expected_total})와 다릅니다.")

    # 5. 가격, 리뷰수, 평점 타입 및 결측치 검증
    print("\n[수치형 데이터 기초 통계]")
    print(df[['가격', '리뷰수', '평점']].describe().to_string())
    
    # 가격/리뷰수에 0 미만 혹은 잘못된 값이 있는지 검증
    invalid_price = df[df['가격'] < 0]
    invalid_reviews = df[df['리뷰수'] < 0]
    
    if len(invalid_price) > 0:
        print(f"경고: 가격이 음수인 데이터가 {len(invalid_price)}개 존재합니다.")
    else:
        print("가격 유효성 검증 완료 (음수 없음)")
        
    if len(invalid_reviews) > 0:
        print(f"경고: 리뷰수가 음수인 데이터가 {len(invalid_reviews)}개 존재합니다.")
    else:
        print("리뷰수 유효성 검증 완료 (음수 없음)")

    # 6. 제형 추출 결과 검증
    print("\n[제형 필드 분포 (상위 10개)]")
    print(df['제형'].value_counts(dropna=False).head(10).to_string())
    
    # 7. 브랜드 추출 결과 검증
    print("\n[브랜드 필드 분포 (상위 15개)]")
    print(df['브랜드'].value_counts(dropna=False).head(15).to_string())
    
    # 8. 한글 및 특수 기호 인코딩 상태 샘플 체크
    print("\n[플랫폼별 무작위 샘플 1개씩]")
    for platform in df['플랫폼'].unique():
        sample = df[df['플랫폼'] == platform].sample(1).iloc[0]
        print(f"\n[{platform} 샘플]")
        print(f" - 브랜드: {sample['브랜드']}")
        print(f" - 제품명: {sample['제품명']}")
        print(f" - 제형: {sample['제형']}")
        print(f" - 가격: {sample['가격']:,}원")
        print(f" - 리뷰수: {sample['리뷰수']:,}개")
        print(f" - 평점: {sample['평점']}점")
        print(f" - URL: {sample['상품URL']}")
        
    print("\n=== 통합 데이터 검증 종료 ===")

if __name__ == "__main__":
    main()
