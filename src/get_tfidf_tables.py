# -*- coding: utf-8 -*-
"""
제품명 TF-IDF 키워드 분석 스크립트.
성분 카테고리 키워드와 제품 제형 키워드를 각각 분리하여 TF-IDF 중요도 순위 상위 항목을 추출합니다.
"""
import sys
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer

sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_csv('NutriFit-Dashboard/data/integrated_products.csv')

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

# 성분 카테고리 키워드
tfidf_ingr = tfidf_all[tfidf_all['keyword'].str.lower().isin([k.lower() for k in ingredient_keywords])].copy()
tfidf_ingr = tfidf_ingr.sort_values(by='tfidf_sum', ascending=False).head(15)

# 제품 제형 키워드
tfidf_form = tfidf_all[tfidf_all['keyword'].str.lower().isin([k.lower() for k in form_keywords])].copy()
tfidf_form = tfidf_form.sort_values(by='tfidf_sum', ascending=False).head(15)

print("=== 성분 카테고리 핵심 키워드 중요도 순위 (TF-IDF) ===")
print(tfidf_ingr.to_markdown(index=False))

print("\n=== 제품 제형 핵심 키워드 중요도 순위 (TF-IDF) ===")
print(tfidf_form.to_markdown(index=False))
