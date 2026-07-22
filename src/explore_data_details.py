"""
각 플랫폼(iHerb, 올리브영, 쿠팡) 데이터 파일의 컬럼 타입, 결측치,
그리고 가격 및 리뷰수 파싱 시 발생할 수 있는 데이터 패턴들을 상세히 분석하는 스크립트입니다.
"""
import pandas as pd
import re

def analyze_iherb():
    print("\n--- iHerb Data Analysis ---")
    path = "iherb/data/서동임_Herb_supplements (1).csv"
    df = pd.read_csv(path)
    print(df.info())
    print("\n[Sample data]")
    print(df[['displayName', 'brandName', 'discountPrice', 'rating', 'ratingCount', 'productForm']].head(3))
    
    # discountPrice 패턴 분석
    print("\n[discountPrice Sample values]")
    print(df['discountPrice'].dropna().head(10).tolist())
    
    # productForm 패턴 분석
    print("\n[productForm Value Counts]")
    print(df['productForm'].value_counts(dropna=False).head(10))

def analyze_oliveyoung():
    print("\n--- Olive Young Data Analysis ---")
    path = "oliveyoung/data/서동임_올리브영_건강식품_수집데이터.csv"
    df = pd.read_csv(path)
    print(df.info())
    print("\n[Sample data]")
    print(df[['brand', 'name', 'price_cur', 'score', 'review_count']].head(3))
    
    # review_count 패턴 분석
    print("\n[review_count Value Counts]")
    print(df['review_count'].value_counts(dropna=False).head(10))

def analyze_coupang():
    print("\n--- Coupang Data Analysis ---")
    path = "coupang/data/coupang_all_products.csv"
    df = pd.read_csv(path)
    print(df.info())
    print("\n[Sample data]")
    print(df[['product_name', 'price', 'rating', 'review_count']].head(3))
    
    # unit_price 패턴이나 product_name 브랜드 추출 가능성 체크
    print("\n[product_name Sample values for Brand Extraction]")
    for val in df['product_name'].head(10):
        print(f"Name: {val}")

if __name__ == "__main__":
    analyze_iherb()
    analyze_oliveyoung()
    analyze_coupang()
