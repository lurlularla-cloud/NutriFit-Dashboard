# -*- coding: utf-8 -*-
"""
TF-IDF 성분 카테고리 및 제품 제형 시각화 차트 생성 스크립트.
plot10.png(성분 카테고리 키워드 TF-IDF)와 plot11.png(제품 제형 키워드 TF-IDF) 이미지를 생성합니다.
"""
import os
import re
import sys
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
from sklearn.feature_extraction.text import TfidfVectorizer

sys.stdout.reconfigure(encoding='utf-8')

def main():
    csv_path = "NutriFit-Dashboard/data/integrated_products.csv"
    output_dir = "NutriFit-Dashboard/images/product_eda"
    os.makedirs(output_dir, exist_ok=True)

    df = pd.read_csv(csv_path)

    corpus = df['제품명'].apply(lambda x: re.sub(r'[^가-힣a-zA-Z\s]', '', str(x)))
    vectorizer = TfidfVectorizer(max_features=2000, stop_words=None)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    tfidf_sums = tfidf_matrix.sum(axis=0).A1
    tfidf_all = pd.DataFrame({'keyword': feature_names, 'tfidf_sum': tfidf_sums})
    tfidf_all = tfidf_all.sort_values(by='tfidf_sum', ascending=False)

    ingredient_keywords = [
        '비타민', 'vitamin', '멀티비타민', '유산균', '프로바이오틱스', 'probiotics', 'probiotic', '소화효소', '효소', '실리마린', 'silymarin', '밀크씨슬', 'milk', 'thistle', '아티초크',
        '오메가', 'omega', 'epa', 'dha', '코엔자임', 'coq', '코큐텐', '스쿠알렌',
        '테아닌', 'theanine', '홍경천', 'rhodiola', '마그네슘', 'magnesium', '멜라토닌', 'melatonin',
        '루테인', 'lutein', '지아잔틴', 'zeaxanthin', '아스타잔틴', 'astaxanthin',
        '콜라겐', 'collagen', '비오틴', 'biotin', '글루코사민', 'glucosamine',
        '피쉬오일', 'fish', 'oil', '크릴', 'krill', '이노시톨', 'inositol', '엽산', 'folate', 'folic',
        '아르기닌', 'arginine', '시트룰린', '타우린', 'taurine',
        '밀크씨슬', '아연', '칼슘', '철분', '항산화', '단백질', '프로틴', '유기농', '강황', '커큐민'
    ]

    form_keywords = [
        '캡슐', '베지캡슐', '베지', '소프트젤', 'softgel', 'softgels', '타블렛', 'tablet', 'tablets',
        '분말', '파우더', 'powder', '가루',
        '구미', '젤리', 'gummy', 'gummies', '츄어블', 'chewable',
        '액상', '드링크', '액체', 'liquid', 'drops',
        '패킷', '스틱', '포', 'packet', 'sachet',
        '환', '정', '정제', '스프레이', 'spray'
    ]

    # 1. 성분 카테고리 plot10.png
    tfidf_ingredients = tfidf_all[tfidf_all['keyword'].str.lower().isin([k.lower() for k in ingredient_keywords])].copy()
    tfidf_ingredients = tfidf_ingredients.sort_values(by='tfidf_sum', ascending=False).head(15)

    plt.figure(figsize=(10, 5))
    bars = plt.bar(tfidf_ingredients['keyword'], tfidf_ingredients['tfidf_sum'], color='#2E86AB', width=0.6)
    plt.title('성분 카테고리 핵심 키워드 중요도 순위 (TF-IDF)', fontsize=14, pad=15)
    plt.xlabel('성분 키워드', fontsize=12)
    plt.ylabel('TF-IDF 합계 가중치', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'plot10.png'), dpi=150)
    plt.close()

    # 2. 제품 제형 plot11.png
    tfidf_forms = tfidf_all[tfidf_all['keyword'].str.lower().isin([k.lower() for k in form_keywords])].copy()
    tfidf_forms = tfidf_forms.sort_values(by='tfidf_sum', ascending=False).head(15)

    plt.figure(figsize=(10, 5))
    bars = plt.bar(tfidf_forms['keyword'], tfidf_forms['tfidf_sum'], color='#E8530E', width=0.6)
    plt.title('제품 제형 핵심 키워드 중요도 순위 (TF-IDF)', fontsize=14, pad=15)
    plt.xlabel('제형 키워드', fontsize=12)
    plt.ylabel('TF-IDF 합계 가중치', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'plot11.png'), dpi=150)
    plt.close()

    print("plot10.png 및 plot11.png 생성 완료")

if __name__ == "__main__":
    main()
