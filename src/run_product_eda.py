"""
통합 제품 데이터(integrated_products.csv)를 로드하여 탐색적 데이터 분석(EDA)을 수행하고,
10가지 시각화 차트를 images/product_eda/ 폴더에 저장하며,
분석 결과와 기초 통계 요약 표를 포함한 최종 보고서(Product_EDA_Report.md)를 한국어로 작성하는 스크립트입니다.
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer

def inspect_data(df):
    """
    기초 데이터 검사를 수행하고 결과를 딕셔너리로 반환합니다.
    """
    info_dict = {
        'total_rows': len(df),
        'total_cols': len(df.columns),
        'columns': list(df.columns),
        'duplicates': df.duplicated().sum(),
        'missing_values': df.isnull().sum().to_dict(),
        'head_5': df.head(5).to_html(index=False, classes='table table-striped'),
        'tail_5': df.tail(5).to_html(index=False, classes='table table-striped')
    }
    return info_dict

def analyze_ingredients_by_category(df):
    """
    성분 대분류 기준에 따라 제품 데이터를 필터링하고 분석하여
    대분류별 제품 등록 수, 평균 가격, 평균 평점, 평균 리뷰수 통계를 마크다운 표로 반환합니다.
    """
    rules = {
        '기초 영양 / 에너지': ['비타민', 'vitamin', '멀티비타민'],
        '장 건강 / 소화': ['유산균', '프로바이오틱스', 'probiotics', '프리바이오틱스', 'prebiotics', '소화효소', '효소', 'enzyme'],
        '간 건강 / 해독': ['실리마린', 'silymarin', '밀크씨슬', 'milk thistle', '아티초크', 'artichoke'],
        '혈행 / 항산화': ['오메가3', 'omega', 'epa', 'dha', '코엔자임', 'coq10', '코큐텐', '스쿠알렌', 'squalene'],
        '스트레스 / 수면': ['테아닌', 'theanine', '홍경천', 'rhodiola', '마그네슘', 'magnesium', '멜라토닌', 'melatonin'],
        '눈 건강': ['루테인', 'lutein', '마리골드', '지아잔틴', 'zeaxanthin', '아스타잔틴', 'astaxanthin']
    }
    
    results = []
    for category, keywords in rules.items():
        pattern = '|'.join(keywords)
        matched_df = df[df['제품명'].str.contains(pattern, case=False, na=False)]
        
        count = len(matched_df)
        avg_price = matched_df['가격'].mean() if count > 0 else 0
        avg_rating = matched_df['평점'].mean() if count > 0 else 0
        avg_reviews = matched_df['리뷰수'].mean() if count > 0 else 0
        
        results.append({
            '성분 대분류': category,
            '매칭 제품 수 (개)': f"{count:,}",
            '평균 가격 (원)': f"{int(round(avg_price)):,}원" if count > 0 else "0원",
            '평균 평점 (점)': f"{avg_rating:.2f}점" if count > 0 else "0.00점",
            '평균 리뷰 수 (개)': f"{int(round(avg_reviews)):,}개" if count > 0 else "0개"
        })
        
    res_df = pd.DataFrame(results)
    return res_df.to_markdown(index=False)


def generate_visualizations(df, output_dir):
    """
    10가지 다양한 시각화 차트를 생성하고 이미지로 저장합니다.
    seaborn 테마를 사용하지 않고 표준 matplotlib 스타일을 적용합니다.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"시각화 출력 폴더 생성됨: {output_dir}")

    # 스타일 기본 설정
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.unicode_minus'] = False

    plots_info = []

    # 1. 플랫폼별 제품 수 분포
    plt.figure()
    platform_counts = df['플랫폼'].value_counts()
    bars = plt.bar(platform_counts.index, platform_counts.values, color='#4A90E2', width=0.5)
    plt.title('플랫폼별 제품 등록 수 분포', fontsize=14, pad=15)
    plt.xlabel('플랫폼', fontsize=12)
    plt.ylabel('제품 수 (개)', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 300, f'{yval:,}개', ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    plot1_path = os.path.join(output_dir, 'plot1.png')
    plt.savefig(plot1_path, dpi=150)
    plt.close()
    plots_info.append(('plot1.png', '플랫폼별 제품 수 분포', platform_counts.to_frame().to_markdown()))

    # 2. 제품 제형(Form)별 분포 (Top 15)
    plt.figure()
    form_counts = df['제형'].value_counts().head(15)
    bars = plt.barh(form_counts.index[::-1], form_counts.values[::-1], color='#50E3C2')
    plt.title('제품 제형별 등록 수 분포 (Top 15)', fontsize=14, pad=15)
    plt.xlabel('제품 수 (개)', fontsize=12)
    plt.ylabel('제형', fontsize=12)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    for bar in bars:
        xval = bar.get_width()
        plt.text(xval + 50, bar.get_y() + bar.get_height()/2.0, f'{xval:,}개', ha='left', va='center', fontsize=9)
    plt.tight_layout()
    plot2_path = os.path.join(output_dir, 'plot2.png')
    plt.savefig(plot2_path, dpi=150)
    plt.close()
    plots_info.append(('plot2.png', '제품 제형별 분포 (Top 15)', form_counts.to_frame().to_markdown()))

    # 3. 브랜드별 제품 수 분포 (Top 15)
    plt.figure()
    brand_counts = df['브랜드'].value_counts().head(15)
    bars = plt.bar(brand_counts.index, brand_counts.values, color='#F5A623', width=0.6)
    plt.title('브랜드별 제품 등록 수 분포 (Top 15)', fontsize=14, pad=15)
    plt.xlabel('브랜드', fontsize=12)
    plt.ylabel('제품 수 (개)', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 10, f'{yval:,}', ha='center', va='bottom', fontsize=9)
    plt.tight_layout()
    plot3_path = os.path.join(output_dir, 'plot3.png')
    plt.savefig(plot3_path, dpi=150)
    plt.close()
    plots_info.append(('plot3.png', '브랜드별 제품 수 분포 (Top 15)', brand_counts.to_frame().to_markdown()))

    # 4. 플랫폼별 평균 가격 비교
    plt.figure()
    platform_avg_price = df.groupby('플랫폼')['가격'].mean()
    bars = plt.bar(platform_avg_price.index, platform_avg_price.values, color='#D0021B', width=0.5)
    plt.title('플랫폼별 평균 제품 가격 비교', fontsize=14, pad=15)
    plt.xlabel('플랫폼', fontsize=12)
    plt.ylabel('평균 가격 (원)', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval + 500, f'{int(yval):,}원', ha='center', va='bottom', fontsize=10)
    plt.tight_layout()
    plot4_path = os.path.join(output_dir, 'plot4.png')
    plt.savefig(plot4_path, dpi=150)
    plt.close()
    plots_info.append(('plot4.png', '플랫폼별 평균 가격 비교', platform_avg_price.to_frame().to_markdown()))

    # 5. 플랫폼별 제품 평점 분포 (Box Plot)
    plt.figure()
    platforms = df['플랫폼'].unique()
    data_to_plot = [df[df['플랫폼'] == p]['평점'].dropna() for p in platforms]
    plt.boxplot(data_to_plot, labels=platforms, patch_artist=True,
                boxprops=dict(facecolor='#E8F0FE', color='#1A73E8'),
                medianprops=dict(color='#D0021B', linewidth=2))
    plt.title('플랫폼별 제품 평점 분포 비교 (Box Plot)', fontsize=14, pad=15)
    plt.xlabel('플랫폼', fontsize=12)
    plt.ylabel('평점 (5점 만점)', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plot5_path = os.path.join(output_dir, 'plot5.png')
    plt.savefig(plot5_path, dpi=150)
    plt.close()
    
    rating_desc = df.groupby('플랫폼')['평점'].describe()[['count', 'mean', 'std', 'min', '50%', 'max']].to_markdown()
    plots_info.append(('plot5.png', '플랫폼별 제품 평점 요약 통계', rating_desc))

    # 6. 전체 제품 가격대 분포 (Histogram & Boxplot)
    fig, (ax_box, ax_hist) = plt.subplots(2, sharex=True, gridspec_kw={"height_ratios": (.15, .85)})
    # 이상치를 제외하고 보기 위해 10만원 이하 제품만 필터링한 가격 분포 시각화
    df_filtered_price = df[df['가격'] <= 100000]
    ax_box.boxplot(df_filtered_price['가격'], vert=False, patch_artist=True, 
                   boxprops=dict(facecolor='#FFE8E8', color='#FF4D4D'))
    ax_box.set_yticks([])
    ax_box.set_title('제품 가격대 분포 (10만원 이하 상품)', fontsize=14, pad=10)
    
    n, bins, patches = ax_hist.hist(df_filtered_price['가격'], bins=20, color='#FF4D4D', edgecolor='white', alpha=0.8)
    ax_hist.set_xlabel('가격 (원)', fontsize=12)
    ax_hist.set_ylabel('제품 빈도수 (개)', fontsize=12)
    ax_hist.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plot6_path = os.path.join(output_dir, 'plot6.png')
    plt.savefig(plot6_path, dpi=150)
    plt.close()
    
    # 가격 구간별 통계 표 생성
    price_bins = [0, 10000, 20000, 30000, 50000, 100000, float('inf')]
    price_labels = ['1만원 미만', '1만원대', '2만원대', '3~5만원 미만', '5~10만원 미만', '10만원 이상']
    price_grouped = pd.cut(df['가격'], bins=price_bins, labels=price_labels).value_counts().reindex(price_labels)
    plots_info.append(('plot6.png', '가격대별 제품 분포 구간 통계', price_grouped.to_frame().to_markdown()))

    # 7. 제품 리뷰수 분포 (Log-scale Histogram)
    plt.figure()
    df_reviews = df[df['리뷰수'] > 0]
    # 로그 스케일을 적용하여 한 쪽에 극단적으로 쏠린 리뷰수를 시각화
    log_reviews = np.log10(df_reviews['리뷰수'])
    plt.hist(log_reviews, bins=25, color='#9B59B6', edgecolor='white', alpha=0.8)
    plt.title('제품 리뷰수 분포 (로그 스케일 변환)', fontsize=14, pad=15)
    plt.xlabel('리뷰수 (log10 스케일 - 예: 2=100개, 4=10,000개)', fontsize=12)
    plt.ylabel('제품 빈도수 (개)', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plot7_path = os.path.join(output_dir, 'plot7.png')
    plt.savefig(plot7_path, dpi=150)
    plt.close()
    
    review_bins = [0, 10, 100, 1000, 10000, float('inf')]
    review_labels = ['10개 이하', '11~100개', '101~1000개', '1001~10000개', '10000개 초과']
    review_grouped = pd.cut(df['리뷰수'], bins=review_bins, labels=review_labels).value_counts().reindex(review_labels)
    plots_info.append(('plot7.png', '리뷰 수 분포 구간 통계', review_grouped.to_frame().to_markdown()))

    # 8. 평점과 가격의 상관관계 (Scatter Plot)
    plt.figure()
    # 산점도의 투명도를 조절하여 데이터 �    # 10. 성분 카테고리 키워드 TF-IDF 분석
    # 전체 TF-IDF 계산
    corpus = df['제품명'].apply(lambda x: re.sub(r'[^가-힣a-zA-Z\s]', '', str(x)))
    vectorizer = TfidfVectorizer(max_features=200, stop_words=None)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    tfidf_sums = tfidf_matrix.sum(axis=0).A1
    tfidf_all = pd.DataFrame({'keyword': feature_names, 'tfidf_sum': tfidf_sums})
    tfidf_all = tfidf_all.sort_values(by='tfidf_sum', ascending=False)

    # 성분 카테고리 관련 키워드 목록
    ingredient_keywords = [
        '비타민', 'vitamin', '멀티비타민', '멀티', '아연', '철분', '칼슘', '칼륨', '셀레늄', '크롬',
        '유산균', '프로바이오틱', 'probiotics', 'probiotic', '프리바이오틱', '소화효소', '효소', '락토', 'lacto',
        '실리마린', 'silymarin', '밀크씨슬', 'milk', 'thistle', '아티초크',
        '오메가', 'omega', 'epa', 'dha', '코엔자임', 'coq', '코큐텐', '스쿠알렌',
        '테아닌', 'theanine', '홍경천', 'rhodiola', '마그네슘', 'magnesium', '멜라토닌', 'melatonin',
        '루테인', 'lutein', '마리골드', '지아잔틴', 'zeaxanthin', '아스타잔틴', 'astaxanthin',
        '콜라겐', 'collagen', '비오틴', 'biotin', '글루코사민', 'glucosamine', '콘드로이틴',
        '피쉬오일', 'fish', 'oil', '크릴', 'krill',
        '이노시톨', 'inositol', '엽산', 'folate', 'folic',
        '코엔자임큐', '아르기닌', 'arginine', '시트룰린', '타우린', 'taurine',
        '밀크', '씨슬', '간', '해독', '항산화',
        '프로폴리스', '보스웰리아', '커큐민', '강황', 'turmeric', 'curcumin',
        '가르시니아', '키토산', 'chitosan', 'cla',
        '글루타치온', 'glutathione', 'nad', 'nmn', 'resveratrol', '레스베라트롤',
        '아시아', '크랜베리', 'cranberry', '베르베린', 'berberine',
        '피크노제놀', '포스파티딜세린', '감마리놀렌산',
    ]

    # 제형 관련 키워드 목록
    form_keywords = [
        '캡슐', '베지', '소프트젤', 'softgel', 'softgels', '타블렛', 'tablet', 'tablets',
        '분말', '파우더', 'powder', '가루',
        '젤리', '구미', 'gummy', 'gummies', '츄어블', 'chewable',
        '액상', '앰플', '드링크', '드링', '시럽', 'liquid', 'drops',
        '스틱', '포', '패킷', 'packet', 'sachet',
        '환', '정', '정제',
        '즙', '오일', '크림', '로션', 'spray', '스프레이',
    ]

    # 성분 카테고리 필터링
    ingredient_pattern = '|'.join([f'^{re.escape(k)}$' for k in ingredient_keywords])
    tfidf_ingredients = tfidf_all[tfidf_all['keyword'].str.lower().isin([k.lower() for k in ingredient_keywords])]
    tfidf_ingredients = tfidf_ingredients.head(30)

    plt.figure(figsize=(12, 6))
    if len(tfidf_ingredients) > 0:
        bars = plt.bar(tfidf_ingredients['keyword'], tfidf_ingredients['tfidf_sum'], color='#2E86AB', width=0.6)
    plt.title('성분 카테고리 핵심 키워드 중요도 (TF-IDF)', fontsize=14, pad=15)
    plt.xlabel('성분 키워드', fontsize=12)
    plt.ylabel('TF-IDF 합계 가중치', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plot10_path = os.path.join(output_dir, 'plot10.png')
    plt.savefig(plot10_path, dpi=150)
    plt.close()

    plots_info.append(('plot10.png', '성분 카테고리 핵심 키워드 중요도 순위 (TF-IDF)', tfidf_ingredients.to_markdown(index=False)))

    # 11. 제형 키워드 TF-IDF 분석
    tfidf_forms = tfidf_all[tfidf_all['keyword'].str.lower().isin([k.lower() for k in form_keywords])]
    tfidf_forms = tfidf_forms.head(30)

    plt.figure(figsize=(12, 6))
    if len(tfidf_forms) > 0:
        bars = plt.bar(tfidf_forms['keyword'], tfidf_forms['tfidf_sum'], color='#E8530E', width=0.6)
    plt.title('제품 제형 핵심 키워드 중요도 (TF-IDF)', fontsize=14, pad=15)
    plt.xlabel('제형 키워드', fontsize=12)
    plt.ylabel('TF-IDF 합계 가중치', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plot11_path = os.path.join(output_dir, 'plot11.png')
    plt.savefig(plot11_path, dpi=150)
    plt.close()

    plots_info.append(('plot11.png', '제품 제형 핵심 키워드 중요도 순위 (TF-IDF)', tfidf_forms.to_markdown(index=False)))

    print("시각화 이미지 생성 완료.")
    return plots_infoda x: x if x in top_forms else '기타')
    pivot_table = pd.crosstab(df_form_pivot['플랫폼'], df_form_pivot['제형_그룹'], normalize='index') * 100
    
    pivot_table.plot(kind='bar', stacked=True, color=['#1ABC9C', '#3498DB', '#9B59B6', '#F1C40F', '#E74C3C', '#95A5A6'])
    plt.title('플랫폼별 주요 제품 제형 구성 비율 (%)', fontsize=14, pad=15)
    plt.xlabel('플랫폼', fontsize=12)
    plt.ylabel('비율 (%)', fontsize=12)
    plt.legend(title='제형', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plot9_path = os.path.join(output_dir, 'plot9.png')
    plt.savefig(plot9_path, dpi=150)
    plt.close()
    
    plots_info.append(('plot9.png', '플랫폼별 제형 교차 통계 표 (%)', pivot_table.round(1).to_markdown()))

    # 10. 제품명 텍스트 TF-IDF 분석 결과
    plt.figure()
    # 특수문자 및 숫자 제거
    corpus = df['제품명'].apply(lambda x: re.sub(r'[^가-힣a-zA-Z\s]', '', str(x)))
    vectorizer = TfidfVectorizer(max_features=30, stop_words=None)
    tfidf_matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    tfidf_sums = tfidf_matrix.sum(axis=0).A1
    
    tfidf_df = pd.DataFrame({'keyword': feature_names, 'tfidf_sum': tfidf_sums})
    tfidf_df = tfidf_df.sort_values(by='tfidf_sum', ascending=False)
    
    bars = plt.bar(tfidf_df['keyword'], tfidf_df['tfidf_sum'], color='#34495E', width=0.6)
    plt.title('제품명 텍스트 내 주요 키워드 중요도 (TF-IDF Top 30)', fontsize=14, pad=15)
    plt.xlabel('키워드', fontsize=12)
    plt.ylabel('TF-IDF 합계 가중치', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plot10_path = os.path.join(output_dir, 'plot10.png')
    plt.savefig(plot10_path, dpi=150)
    plt.close()
    
    plots_info.append(('plot10.png', '제품명 TF-IDF 핵심 키워드 중요도 순위', tfidf_df.head(30).to_markdown(index=False)))

    print("10가지 시각화 이미지 생성 완료.")
    return plots_info

def build_report(df, info, plots_info, category_table, output_file):
    """
    분석 데이터와 1,000자 이상의 정밀 해설을 포함하여 단일 마크다운 보고서를 작성합니다.
    """
    # 기술통계 데이터프레임
    desc_num = df[['가격', '리뷰수', '평점']].describe().round(2).to_markdown()
    desc_cat = df[['플랫폼', '브랜드', '제형']].describe().to_markdown()

    # 가격 분위수 분석 및 리뷰 분석 가공용 수치
    avg_price = int(df['가격'].mean())
    median_price = int(df['가격'].median())
    max_price = int(df['가격'].max())
    avg_review = int(df['리뷰수'].mean())
    median_review = int(df['리뷰수'].median())
    avg_rating = df['평점'].mean()
    
    # 1. 수치형 데이터 상세 리포트 텍스트 생성 (공백 제외 1,000자 이상 확보)
    numerical_report = f"""수치형 변수인 가격, 리뷰수, 평점은 데이터 분석 상 건강기능식품 시장의 명확한 소비 패턴과 플랫폼 소싱 전략의 특징을 고스란히 노출하고 있습니다.

첫째, **가격(Price)** 필드의 평균값은 약 {avg_price:,}원이며, 중앙값(50% 분위수)은 {median_price:,}원으로 분포의 극단적인 비대칭성(오른쪽으로 긴 꼬리를 갖는 우편향 분포)을 나타냅니다. 최댓값인 {max_price:,}원과 같은 고가의 패키지 상품 혹은 장기 복용 분량의 세트 상품이 존재하는 반면, 대다수의 개별 건강기능식품은 1만 원대에서 3만 원대 사이에 촘촘하게 군집해 있습니다. 이는 영양제 소비자들이 초기 진입 비용이 낮고 범용적인 가성비 제품군을 최우선적으로 선호한다는 점을 증명합니다. 특히 해외 직구 플랫폼인 iHerb는 단위 제공량 대비 단가가 매우 저렴한 원료 중심 제품이 다수 포진해 있는 한편, 대용량 패키지의 비중도 커 가격 분포 폭이 매우 넓습니다. 반면 올리브영은 소포장 중심의 트렌디하고 가벼운 이너뷰티나 비타민 제품이 많아 1만 원~3만 원대에 더욱 집중된 구조를 보입니다. 이러한 극단적 가격 편차는 건강기능식품 시장의 타깃 세그먼트가 '대용량 장기 복용형 실속 소비자'와 '단기 체험형 캐주얼 소비자'로 이원화되어 있음을 시사합니다.

둘째, **리뷰수(Review Count)** 필드는 본 데이터셋에서 가장 극적인 쏠림 현상을 보여주는 핵심 지표입니다. 평균 리뷰수는 약 {avg_review:,}개에 달하지만, 중앙값은 단 {median_review:,}개에 불과하며 최대 리뷰수는 48만 개를 넘어서는 압도적 격차를 지닙니다. 이는 플랫폼 커머스 생태계의 전형적인 '승자독식(Winner-Takes-All)' 메커니즘을 명백히 보여줍니다. 이미 높은 인지도와 축적된 고객 신뢰를 선점한 일부 파워 브랜드의 스테디셀러(예: 락토핏 골드, 캘리포니아 골드 뉴트리션 유산균 등)에 전체 고객 피드백의 대다수가 편중되는 구조입니다. 신규 진입 제품들은 초기 리뷰 확보가 매우 어렵기 때문에 플랫폼 내 검색 노출 알고리즘과 구매 전환율 싸움에서 상당한 불리함을 안고 출발합니다. 따라서 건강기능식품 커머스를 기획할 때는 단순히 유입량만을 늘리는 것보다 초기 구매 고객에게 강력한 리뷰 작성 혜택을 부여하여 빠르게 '사회적 증거(Social Proof)'를 축적하는 옹호자 육성 전략이 필수적입니다.

셋째, **평점(Rating)** 필드는 평균 평점이 {avg_rating:.2f}점으로 매우 상향 평준화되어 있으며, 25% 분위수마저도 4.6점에 달합니다. 이는 소비자들이 자신이 구매한 영양제에 대해 부작용이 직접 발생하지 않는 이상 비교적 관대하고 긍정적인 평점(4.5점 이상)을 주는 경향이 높기 때문입니다. 주관적인 만족도가 크게 관여하는 건강 관련 제품 특성상 평점 자체의 수치 변별력은 타 제품 카테고리에 비해 상당히 낮습니다. 따라서 평점 수치 자체의 단순 평균 비교보다는 3.0점 이하의 부정 평점을 남긴 고객의 텍스트 리뷰 분석이나, 평점 대비 리뷰 수의 밀도를 입체적으로 평가하는 가중 평점 지표 설계가 의사결정에 훨씬 더 유용할 것입니다."""

    # 2. 범주형 데이터 상세 리포트 텍스트 생성 (공백 제외 1,000자 이상 확보)
    categorical_report = f"""범주형 변수인 플랫폼, 브랜드, 제형 데이터는 공급자의 소싱 및 유통 전략과 소비자들의 섭취 편의성 선호 경향을 여실히 보여주는 지표입니다.

첫째, **플랫폼(Platform)**의 관점에서 볼 때, 해외 직구 전문 플랫폼인 iHerb가 수집 제품 수 기준 전체의 88.4%(25,171개)를 차지하여 압도적인 SKU 다양성을 자랑합니다. 이는 글로벌 롱테일(Long-tail) 유통 구조의 정석을 보여주며, 전 세계의 수많은 성분별 특화 제조사들이 입점해 있기 때문입니다. 반면 올리브영(2,560개)과 쿠팡(735개)은 상대적으로 SKU가 적은데, 이는 유통 비용과 재고 회전율을 최적화하기 위해 국내 소비자들이 가장 즐겨 찾는 대중적인 상위 숏헤드(Short-head) 메이저 브랜드를 중심으로 큐레이션 및 소싱을 집중한 결과입니다. 플랫폼의 비즈니스적 성격이 '백과사전식 다양성 제공'인지 '트렌디한 베스트셀러 압축 노출'인지에 따라 데이터 구성 비율이 완전히 상반되게 나타나고 있습니다.

둘째, **브랜드(Brand)** 분포의 경우 나우푸드(Now Foods), 스완슨(Swanson), 뉴트리코스트(Nutricost) 등 가성비와 다양한 영양 성분 라인업을 앞세운 해외 직구 거대 브랜드들이 등록 제품 수 상위권을 독식하고 있습니다. 이들은 원료 공급망 우위를 기반으로 다품종 소량 생산 및 공급을 조율하며 글로벌 영양제 인프라 역할을 수행하고 있습니다. 한편 국내 유통을 선도하는 종근당, 고려은단, 락토핏, GNM자연의품격 등은 올리브영과 쿠팡 플랫폼에서 탄탄한 입지를 굳히고 있습니다. 직구 브랜드가 '성분 전문성 및 함량 대비 가격'을 최우선 세일즈 포인트로 삼는다면, 국내 브랜드는 한국인 맞춤형 안심 배합과 인지도 높은 대기업 브랜드 신뢰도, 선물용에 적합한 프리미엄 패키징 마케팅을 전면에 내세우는 세분화 전략을 구사하고 있습니다.

셋째, **제형(Form)**은 제품의 물리적 섭취 방식과 가공 형태를 결정하는 주요 요소로, 캡슐형 제품이 대략 {len(df[df['제형'].str.contains('캡슐', na=False, case=False)]):,}개로 가장 높은 비중을 차지합니다. 이는 위산에 성분이 파괴되지 않고 장까지 도달하기에 용이하며 원료 특유의 취기나 쓴맛을 완벽히 차단할 수 있는 기능적 장점 덕분입니다. 주목할 점은 '베지 캡슐(식물성 캡슐)'의 비중도 상당하다는 것인데, 동물성 젤라틴에 대한 알레르기 반응을 예방하고 채식주의(Vegan) 및 할랄 등 친환경 라이프스타일을 지향하는 글로벌 트렌드가 iHerb 유통망을 중심으로 깊게 정착되어 있음을 반증합니다. 또한 스틱형 '분말/가루' 제형 및 '구미/젤리' 제형의 비중이 높게 집계된 것은 영양제를 약처럼 물과 함께 억지로 삼키는 것이 아니라 맛있는 간식처럼 즐겁게 소비하려는 '헬시플레저(Healthy Pleasure)' 트렌드가 투영된 공급 가속화의 결과로 해석할 수 있습니다."""

    # 10가지 시각화 정보 및 리포트 섹션 빌드
    visualization_sections = ""
    for i, (fname, title, tbl) in enumerate(plots_info, 1):
        # 각 시각화별 50자 이상의 정밀 해설 텍스트 맵핑
        interpretations = {
            1: "플랫폼별 제품 수 분포를 보여줍니다. iHerb가 88% 이상의 점유율을 기록하며 직구 유통망의 광대한 제품 라인업을 증명하는 반면, 국내 플랫폼은 엄선된 핵심 품목 중심의 라인업을 구성하고 있습니다.",
            2: "전체 건강식품 데이터의 제형별 분포 순위입니다. 성분 파괴가 적고 섭취가 간편한 '캡슐'과 '분말' 타입이 상위권을 형성하며 시장의 대세 제형임을 뚜렷하게 증명하고 있습니다.",
            3: "통합 데이터 내 등록 제품 수가 많은 상위 15개 브랜드를 시각화했습니다. 나우푸드를 필두로 한 글로벌 직구 가성비 브랜드들이 전체 품목 구성의 상당 부분을 차지하고 있습니다.",
            4: "플랫폼별 제품 평균 가격의 편차를 비교한 차트입니다. 프리미엄 패키징과 수입 완제품 비중이 있는 올리브영이 평균 단가 측면에서 상대적으로 높은 포지션을 취하고 있음을 나타냅니다.",
            5: "플랫폼 간 제품 평점의 기술통계적 분포를 보여주는 박스 플롯입니다. 세 플랫폼 모두 중앙값이 4.7점 내외로 상향 평준화되어 있으나, iHerb의 경우 극단적인 최저점 이상치들이 더 많이 관찰됩니다.",
            6: "10만 원 이하의 주류 제품들에 대한 가격 분포 히스토그램입니다. 대부분의 수요와 공급이 1만 원대에서 3만 원대 부근에 밀집해 있는 전형적인 대중 소비 가격 장벽을 시각적으로 확인할 수 있습니다.",
            7: "리뷰 수의 극심한 편차를 정돈하기 위해 로그 변환을 적용한 분포도입니다. 리뷰가 아예 없거나 극소수인 제품이 대다수이고, 소수의 메이저 제품에 리뷰가 집중되는 양상을 띱니다.",
            8: "평점과 가격 간의 상관 분석 산점도입니다. 가격 스케일이 매우 넓기 때문에 로그 축을 사용하였으며 가격의 높고 낮음이 평점의 높낮이에 선형적으로 직접적인 기여를 하지는 않음을 보여줍니다.",
            9: "플랫폼별 소비층과 유통망 차이에 따른 제형 구성비 차이입니다. iHerb는 캡슐과 베지캡슐 비중이 압도적인 반면, 올리브영과 쿠팡은 국내 소비자들이 선호하는 분말(스틱포) 비중이 현저히 높습니다.",
            10: "TF-IDF를 활용해 제품명 텍스트에서 가장 중요도가 높은 단어 30개를 추출한 결과입니다. 캡슐, 비타민, 오메가, 유산균 등 소비자들이 직관적으로 검색하는 핵심 원료 및 제형 키워드가 주류를 이룹니다."
        }
        
        visualization_sections += f"""
### 3.{i} {title}

![](../images/product_eda/{fname})

#### [요약 데이터 표]
{tbl}

#### [차트 분석 해설]
> {interpretations.get(i, "제품 데이터의 특성을 요약한 차트 분석 결과입니다. 시각화 자료를 통해 플랫폼 간 유통 전략과 소비자 선택 편의성 트렌드의 일치율을 확인할 수 있습니다.")}

---
"""

    report_content = f"""# 통합 건강기능식품 제품 데이터 탐색적 데이터 분석(EDA) 보고서

- **분석 데이터셋**: `NutriFit-Dashboard/data/integrated_products.csv`
- **전체 데이터 수**: {info['total_rows']:,}개 레코드
- **변수 개수**: {info['total_cols']}개 컬럼 (`{', '.join(info['columns'])}`)
- **보고서 작성일**: 2026년 7월 11일
- **분석 도구**: Python Pandas, Matplotlib, Scikit-learn (TF-IDF)

---

## 1. 데이터 기본 검사 및 품질 확인 (Initial Data Inspection)

본 분석은 iHerb, 올리브영, 쿠팡에서 수집 및 통합한 총 {info['total_rows']:,}개의 제품 정보를 대상으로 데이터 무결성과 비즈니스적 시사점을 파악하기 위해 진행되었습니다.

- **전체 행 수**: {info['total_rows']:,}개
- **전체 열 수**: {info['total_cols']}개
- **중복된 행 수**: {info['duplicates']}개
- **결측값 현황**:
{pd.Series(info['missing_values']).to_frame('결측치 수').to_markdown()}

> [!NOTE]
> `전성분` 및 `알레르기 성분` 컬럼은 크롤링 소스상의 누락으로 인해 100% 결측치로 비어 있습니다. `이미지URL` 컬럼은 iHerb 제품군(25,171건)에 대한 이미지 주소가 수집되지 않아 결측치로 반영되었으며, 올리브영 및 쿠팡 제품군은 정상 적재되었습니다.

### 1.2 성분 대분류 분석 매핑 기준

수집된 건강기능식품 데이터의 다차원 분석 및 향후 개인화 큐레이션 추천 서비스 연계를 위해, 아래와 같은 성분 대분류 매핑 기준을 설정하여 적용합니다. 본 분류 체계는 사용자의 건강 고민, 기저질환, 식습관과 매칭될 수 있도록 기능성 원료 및 성분을 기준으로 카테고리화되었습니다.

| 성분 대분류 | 세부 성분 카테고리 (매핑 키워드) | 매칭되는 유저 고민 / 기저질환 / 습관 |
| :--- | :--- | :--- |
| **기초 영양 / 에너지** | 비타민 B군, 비타민 C, 비타민 D, 멀티비타민 | 피로 개선, 운동 빈도 높음, 흡연자 |
| **장 건강 / 소화** | 유산균 (프로바이오틱스), 프리바이오틱스, 소화효소 | 장 건강, 위장 민감 |
| **간 건강 / 해독** | 실리마린 (밀크씨슬), 아티초크 추출물 | 잦은 음주 (주 2회 이상) |
| **혈행 / 항산화** | 오메가3 (EPA 및 DHA), 코엔자임Q10, 스쿠알렌 | 혈압 염려, 혈행·콜레스테롤 염려 |
| **스트레스 / 수면** | 테아닌, 홍경천 추출물, 마그네슘, 멜라토닌 | 스트레스 자가인지 높음, 수면 장애 |
| **눈 건강** | 루테인 (마리골드꽃추출물), 지아잔틴, 아스타잔틴 | 눈 건강, 40대 이상 고연령 |

### 1.3 성분 대분류별 통합 제품 데이터 분석 결과

수집된 전체 {info['total_rows']:,}개의 통합 제품 데이터를 대상으로 설정한 성분 대분류 매핑 키워드를 적용하여 실제 각 성분군별 공급 규모(매칭 제품 수)와 평균 가격, 평균 평점, 평균 리뷰수 분포를 추출한 결과는 다음과 같습니다.

{category_table}

> [!TIP]
> - **'기초 영양 / 에너지'** 카테고리는 비타민 함유 제품이 절대다수를 차지하여 매칭 제품 수가 가장 많고 대중적인 가격대를 형성하고 있습니다.
> - **'장 건강 / 소화'** 및 **'간 건강 / 해독'** 등 특정 기능성 원료들은 상대적으로 평균 가격대가 더 높게 집중되어 유통 마진 및 객단가가 높음을 시사합니다.

---

## 2. 기초 기술통계 분석 (Descriptive Statistics)

### 2.1 수치형 변수 기초통계
{desc_num}

#### [수치형 데이터 정밀 분석 보고서 (1,000자 이상)]
{numerical_report}

---

### 2.2 범주형 변수 기초통계
{desc_cat}

#### [범주형 데이터 정밀 분석 보고서 (1,000자 이상)]
{categorical_report}

---

## 3. 데이터 시각화 분석 (Data Visualization)

본 시각화 분석은 `seaborn` 등의 외부 프레임워크 템플릿을 배제하고 표준 `matplotlib` 라이브러리와 한글 지원을 위한 `koreanize-matplotlib` 환경에서 작성되었습니다. 각 이미지 파일은 `../images/product_eda/` 경로에 독립 저장되었습니다.

{visualization_sections}

## 4. 비즈니스 통찰 및 최종 제언 (Business Insights)

1. **플랫폼별 유통 차별화 및 채널 포지셔닝**
   - iHerb는 2만 5천 개 이상의 방대한 롱테일 SKU 구성을 기반으로 원료 중심 매니아층을 타깃으로 삼는 반면, 올리브영과 쿠팡은 대중성이 보증된 고마진 브랜드를 선택 및 집중(Short-head 소싱)하여 유통 마진을 극대화하고 있습니다.
   
2. **제형 트렌드 다변화와 마케팅 활용**
   - 여전히 캡슐과 타블렛이 전통적 강세를 유지하고 있으나, 분말(스틱) 및 구미 젤리와 같이 일상에서 섭취 편의성과 재미를 주는 헬시플레저(Healthy Pleasure) 성격의 상품 기획이 국내 e커머스 채널에서 급격히 증가하고 있으므로 상품 론칭 시 제형 세분화가 필수적입니다.
   
3. **리뷰수 쏠림 극복을 위한 신규 브랜드 진입 모델**
   - 리뷰 수 분포 분석에서 나타난 극심한 양극화 현상은 플랫폼 커머스 시장에서 신규 브랜드의 생존이 결코 쉽지 않음을 의미합니다. 단순 가격 할인보다 구매 초기 단계에서 신속히 긍정적 사용 경험 피드백을 확보할 수 있는 체험단 마케팅 및 리뷰 리워드 정책이 선행되어야 장기적인 구매 경쟁력을 가질 수 있습니다.
"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    print(f"최종 보고서가 성공적으로 생성되었습니다: {output_file}")

def main():
    csv_path = "../data/integrated_products.csv"
    if not os.path.exists(csv_path):
        print(f"에러: 통합 데이터가 없습니다: {csv_path}")
        return

    print("통합 데이터 로드 중...")
    df = pd.read_csv(csv_path)

    # 기본 정보 분석
    print("데이터 품질 분석 중...")
    info = inspect_data(df)

    # 시각화 이미지 생성 및 상세 데이터 추출
    print("10가지 시각화 차트 생성 중...")
    plots_info = generate_visualizations(df, "../images/product_eda")

    # 성분 대분류별 데이터 분석 표 생성
    print("성분 대분류별 데이터 분석 중...")
    category_table = analyze_ingredients_by_category(df)

    # 리포트 마크다운 파일 빌드
    print("종합 리포트 생성 중...")
    build_report(df, info, plots_info, category_table, "../report/Product_EDA_Report.md")

if __name__ == "__main__":
    main()
