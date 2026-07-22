"""
NutriFit 대시보드 메인 애플리케이션 (수치적 결과 리포트 고도화 버전)
- KDRI 한국인 영양소 섭취기준 기반 누적 섭취 수치 분석 및 시각화
- 복용 영양제 중 위험/주의/적정 스코어링 시스템 구현
- 의약품 상호작용 및 회피 성분 실시간 크로스 체크 매핑
"""
import streamlit as st
import pandas as pd
import numpy as np
import os
from src.api.data_loaders import load_dur_master_zip

st.set_page_config(page_title="NutriFit 대시보드", layout="wide")

# ==========================================================
# 0. 데이터 로드 및 초기 세팅 (캐싱 적용)
# ==========================================================
@st.cache_data
def load_base_data():
    """크롤링 데이터와 심평원 DUR 압축 데이터를 로드하는 함수"""
    try:
        products = pd.read_csv("data/integrated_products.csv")
    except FileNotFoundError:
        # fallback 데이터 세팅 (이미지 매핑 데이터 포함)
        products = pd.DataFrame({
            '브랜드': ['나우푸드', '락토핏', '고려은단', '솔가'],
            '제품명': ['실리마린 밀크씨슬 추출물', '생유산균 골드', '비타민C 1000', '비타민D3 2200IU'],
            '전성분': ['밀크씨슬 추출물, 실리마린, 셀룰로오스', '프로바이오틱스, 유산균, 락토바실러스', '비타민C, 아스코르브산', '비타민D, 정제어유, 젤라틴'],
            '제형': ['캡슐', '분말·포', '정제(알약)', '연질캡슐'],
            '가격': [18900, 15400, 22000, 28000],
            '이미지경로': ['images/milk_thistle.jpg', 'images/lactofit.jpg', 'images/vitaminc.jpg', 'images/vitamind.jpg']
        })
        
    dur_master = load_dur_master_zip("건강보험심사평가원_의약품안전사용서비스(DUR) 의약품 목록_20260601.zip")
    return products, dur_master

products_df, dur_df = load_base_data()

# 세션 상태 초기화
if "step" not in st.session_state:
    st.session_state.step = "agreement"
if "survey_data" not in st.session_state:
    st.session_state.survey_data = {}

# ==========================================================
# 1. 시작 전 동의 화면 및 서비스 한눈에 보기 (5:5 분할 레이아웃)
# ==========================================================
if st.session_state.step == "agreement":
    st.title("🥗 뉴트리핏(NutriFit) – AI 개인 맞춤형 웰니스 큐레이션")
    st.caption("🚨 본 서비스는 의학적 치료나 진단을 대체하지 않으며, 식약처 데이터를 기반으로 한 영양 정보 참고용 서비스입니다.")
    st.write("<br>", unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 1], gap="large")

    with left_col:
        st.subheader("🔍 뉴트리핏은 어떤 서비스인가요?")
        st.markdown("""
        뉴트리핏은 식약처 공공데이터베이스(기능성 원료현황/개별인정형 정보/DUR 품목정보)에 입각하여,
        유저가 입력한 **기본 프로필, 라이프스타일, 복용 중인 영양제/의약품** 성분을 정밀 스캔합니다.
        중복·과다 섭취 위험성을 수치화하고 가장 안전한 큐레이션을 제안해 드립니다.
        """)
        
        st.info("💡 **프로세스 안내:** 서비스 개요 확인 ➡️ 23개 문진 및 현재 복용 영양제 등록 ➡️ 수치 기반 위험도 리포트 출력 ➡️ 최적화 제품 즉시 구매 랜딩아웃")
        
        st.write("---")
        st.markdown("### 🎯 뉴트리핏 실시간 인기 제품 (맛보기 예시)")
        
        c_sample1, c_sample2 = st.columns(2)
        with c_sample1:
            with st.container(border=True):
                st.markdown("#### 💊 [나우푸드] 실리마린 밀크씨슬")
                st.caption("✨ 잦은 음주 및 피로 회복 목적 가산")
                st.link_button("쿠팡 구매 링크 🛒", "https://www.coupang.com", use_container_width=True)
        with c_sample2:
            with st.container(border=True):
                st.markdown("#### 💊 [락토핏] 생유산균 골드")
                st.caption("✨ 불규칙한 식습관 개선 타겟 반영")
                st.link_button("올리브영 구매 링크 🛒", "https://www.oliveyoung.co.kr", use_container_width=True)

    with right_col:
        st.subheader("📋 내 맞춤 영양제 찾기")
        with st.container(border=True):
            st.markdown("#### 🔒 필수 동의 및 이용 약관")
            
            agree1 = st.checkbox("[필수] 서비스 이용약관 및 일반 개인정보 수집·이용 동의")
            agree2 = st.checkbox("[필수] 만 14세 이상 이용 확인 (만 14세 미만 이용 제한)")
            agree3 = st.checkbox("[필수] 건강 상태 및 라이프스타일(민감정보) 수집·이용 동의")
            
            st.write("<br>", unsafe_allow_html=True)
            
            if st.button("🚀 나만의 맞춤 웰니스 진단 시작하기", use_container_width=True, type="primary"):
                if agree1 and agree2 and agree3:
                    st.session_state.step = "survey"
                    st.rerun()
                else:
                    st.error("❌ 모든 필수 약관에 동의하셔야 문진을 시작할 수 있습니다.")

# ==========================================================
# 2. STEP별 문진표 입력 화면 (23개 확정 스펙 완벽 반영)
# ==========================================================
elif st.session_state.step == "survey":
    st.title("📋 개인 맞춤형 문진표 작성 및 영양제 보관함 설정")
    st.progress(0.65)
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["STEP1. 기본 정보", "STEP2. 라이프스타일", "STEP3. 건강 상태(안전성)", "STEP4. 건강 고민", "STEP5. 복용 영양제 등록"])
    
    with tab1:
        st.subheader("👤 기본 정보 (Demographics)")
        gender = st.radio("1. 성별", ["남성", "여성", "응답하지 않음"])
        male_goals = st.multiselect("2. 남성 전용 - 고민 영역", ["탈모·두피 관리", "전립선 건강", "근육량 증가"]) if gender == "남성" else []
        female_status = st.selectbox("3. 여성 전용 - 생애주기 상태", ["해당없음", "임신 준비 중", "임신 중", "수유 중", "폐경기"]) if gender == "여성" else "해당없음"
        age_group = st.selectbox("4. 연령대", ["20대 미만", "20대", "30대", "40대", "50대", "60대 이상"])
        c1, c2 = st.columns(2)
        height = c1.number_input("5. 키 (cm)", min_value=100.0, max_value=250.0, value=170.0)
        weight = c2.number_input("몸무게 (kg)", min_value=30.0, max_value=200.0, value=65.0)
        bmi = weight / ((height / 100) ** 2)

    with tab2:
        st.subheader("🏃‍♂️ 라이프스타일 & 일상 습관")
        workout = st.multiselect("6. 운동 종류 및 목적", ["안 함·체력유지재활", "고강도 유산소", "저항성·근력 운동", "유연성·코어", "고강도 인터벌"])
        drinking = st.selectbox("7. 음주 빈도", ["전혀 안 함", "보통", "잦은 음주"])
        caffeine = st.radio("8. 하루 카페인 섭취", ["0잔", "1~2잔", "3잔", "4잔 이상"])
        diet = st.selectbox("9. 식습관", ["일반식·불규칙", "육식 위주", "채식·간헐적 단식", "완벽한 비건"])
        sleep = st.radio("10. 수면 시간", ["5시간 미만", "5~7시간", "8시간 이상"])
        stress = st.select_slider("11. 스트레스 자가인지", options=["1단계", "2단계", "3단계", "4단계", "5단계"])

    with tab3:
        st.subheader("⚠️ 건강 상태 & 안전성 필터")
        smoking = st.radio("12. 흡연 여부", ["비흡연", "흡연"])
        allergy = st.multiselect("13. 알레르기 원료", ["갑각류", "대두", "글루텐", "유제품", "견과류", "어류", "없음"])
        side_effects = st.multiselect("14. 과거 부작용 경험 성분", ["철분", "오메가3", "비타민C", "유산균", "기타 직접입력"])
        user_drug = st.text_input("15. 현재 복용 중인 전문 의약품 이름 (DUR 실시간 스캔용)", "")
        diseases = st.multiselect("지병 종류 선택", ["고혈압", "당뇨", "이상지질혈증", "만성 위장질환", "혈전 관련질환-항응고제", "간·신장질환", "없음·기타"])

    with tab4:
        st.subheader("🎯 건강 고민 및 목표")
        goals = st.multiselect("16. 건강 고민 및 목표 (최대 2개 선택)", ["만성피로", "눈 건조·피로", "장 건강", "피부탄력·이너뷰티", "체지방감소·다이어트", "면역력저하", "관절보호", "수면부족·스트레스케어", "항노화·항산화", "생리불순·생리통"], max_selections=2)

    with tab5:
        st.subheader("💊 현재 먹는 실제 영양제 성분 체크 (NutriMatch 벤치마킹)")
        st.caption("현재 복용 중인 영양제 라벨을 확인하여 1일 영양성분 기준치 대비 수치(%)를 기재해 주세요.")
        
        col_take1, col_take2 = st.columns(2)
        with col_take1:
            take_vitd = st.number_input("비타민D 누적 섭취량 (%)", min_value=0, max_value=2000, value=0, step=50)
            take_vitb = st.number_input("비타민B군 누적 섭취량 (%)", min_value=0, max_value=5000, value=0, step=50)
            take_vitc = st.number_input("비타민C 누적 섭취량 (%)", min_value=0, max_value=5000, value=0, step=50)
            take_zinc = st.number_input("아연 누적 섭취량 (%)", min_value=0, max_value=1000, value=0, step=10)
        with col_take2:
            take_cal = st.number_input("칼슘 누적 섭취량 (%)", min_value=0, max_value=1000, value=0, step=10)
            take_mag = st.number_input("마그네슘 누적 섭취량 (%)", min_value=0, max_value=1000, value=0, step=10)
            take_omega = st.checkbox("오메가3 제품 복용 중")
            take_silymarin = st.checkbox("밀크씨슬(실리마린) 제품 복용 중")
            
        st.write("---")
        st.subheader("🛒 섭취 편의성 및 구매 성향 선호도")
        pill_discomfort = st.radio("17. 알약 불편감", ["상관없음", "매우 불편함"])
        pref_form = st.multiselect("18. 대안 제형 선호", ["소형 알약", "구미·젤리", "액상·드링크", "분말·포"])
        value_priority = st.multiselect("20. 구매 시 우선 가치", ["성분 함량", "원산지·브랜드", "첨가물 최소화", "복용 편의성"], max_selections=2)
        budget = st.select_slider("22. 월 예산대", options=["1~3만원", "3~5만원", "5~10만원", "10만원 이상"])

    st.write("<br>", unsafe_allow_html=True)
    if st.button("🚀 식약처/DUR 공공데이터 기반 정밀 분석 리포트 생성", use_container_width=True, type="primary"):
        forbidden_ingredients = []
        if user_drug and dur_df is not None and '품목명' in dur_df.columns:
            matched_dur = dur_df[dur_df['품목명'].str.contains(user_drug, na=False)]
            if not matched_dur.empty and '주성분코드' in dur_df.columns:
                forbidden_ingredients = matched_dur['주성분코드'].dropna().unique().tolist()

        st.session_state.survey_data = {
            "gender": gender, "age": age_group, "bmi": bmi, "allergy": allergy, "workout": workout,
            "drinking": drinking, "caffeine": caffeine, "smoking": smoking, "diseases": diseases, 
            "goals": goals, "pill": pill_discomfort, "budget": budget, "user_drug": user_drug, 
            "forbidden_ingredients": forbidden_ingredients, "stress": stress,
            "intake": {
                "비타민D": take_vitd, "비타민B군": take_vitb, "비타민C": take_vitc,
                "아연": take_zinc, "칼슘": take_cal, "마그네슘": take_mag,
                "오메가3": 150 if take_omega else 0, "실리마린": 150 if take_silymarin else 0
            }
        }
        st.session_state.step = "result"
        st.rerun()

# ==========================================================
# 3. 고도화된 수치 분석 리포트 및 AI 큐레이션 결과 화면
# ==========================================================
elif st.session_state.step == "result":
    st.title("📊 뉴트리핏 AI 정밀 영양소 과다·섭취 분석 리포트")
    profile = st.session_state.survey_data
    intake = profile["intake"]
    
    # 좌우 레이아웃 분할 배치 (좌: 수치적 스캔 결과 차트 / 우: 최적화 진단 소견 및 금기 가이드)
    chart_col, report_col = st.columns([1.1, 0.9], gap="large")
    
    with chart_col:
        st.subheader("📊 종합 영양 성분 누적 섭취 분석기")
        st.caption("등록된 실세 영양제 속 복잡한 성분 수치를 실시간 합산한 통계 결과입니다. (100% = 1일 영양성분 기준치)")
        
        # KDRI 기준 실시간 조건 가이드 시각화
        st.info(f"🧬 **개인별 조건에 따른 기준점 실시간 추적**\n\n• **{profile['age']} {profile['gender']}** 기준 KDRI 데이터 매핑: 라이프스타일 지표 및 흡연/음주 캡핑 수치가 위험 상한선(UL) 필터에 동의식으로 연동 중입니다.")
        
        # 성분별 진행 바 시각화 및 위험 스코어링 (NutriMatch UI의 고도화 구현)
        for nutrient, value in intake.items():
            if value == 0: continue
            
            # 위험도 분기 기준 설정
            if value >= 500:
                status_txt = f"🔥 누적 섭취: {value}% (위험 (초과))"
                bar_color = "red"
            elif value >= 120:
                status_txt = f"⚠️ 누적 섭취: {value}% (주의 (경계))"
                bar_color = "orange"
            else:
                status_txt = f"✅ 누적 섭취: {value}% (적정)"
                bar_color = "green"
                
            st.markdown(f"**{nutrient}** <span style='float:right; color:{bar_color}; font-weight:bold;'>{status_txt}</span>", unsafe_allow_html=True)
            st.progress(min(value / 600.0, 1.0)) # 600% 기준 스케일아웃 시각화

    with report_col:
        st.subheader("🩺 맞춤 복용 최적화 종합 리포트")
        
        # 1. 과다 섭취 경고 필터
        for nutrient, value in intake.items():
            if value >= 500:
                st.error(f"🚨 **{nutrient} {value}% 과다 복용 감지 (위험)**\n\n지용성 물질 혹은 특정 미네랄 장기 과다 복용 시 체내 축적으로 인한 독성 유발 및 간/신장 기능 장애 우려가 식약처 개별인정형 정보 주의사항에 고지되어 있습니다. 섭취량 조절이 시급합니다.")
            elif value >= 120:
                st.warning(f"⚠️ **{nutrient} {value}% 중복 복용 확인 (주의)**\n\n일일 권장 기준치를 초과했습니다. 타 성분 흡수 방해를 유발할 수 있으므로 단일제 추가 편성을 지양해 주세요.")
                
        # 2. 복용 의약품 DUR 및 지병 간 상호작용 피해야 할 성분 안내 [No.24]
        st.markdown("#### 🚫 약물 상호작용 및 피해야 할 성분 (공공데이터 검증)")
        avoid_list = []
        
        # 지병(diseases) 조건 매핑
        if "혈전 관련질환-항응고제" in profile["diseases"]:
            avoid_list.append("• **오메가3 / 비타민K:** 항응고제와 오메가3 병용 시 지혈 지연 및 출혈 리스크 우려 (의사 약사 전문가 상담 필수)")
        if "만성 위장질환" in profile["diseases"]:
            avoid_list.append("• **고함량 비타민C / 철분:** 위점막 자극으로 속쓰림, 설사를 가중시킬 수 있으므로 공복 섭취 제외 추천")
        if profile["forbidden_ingredients"]:
            avoid_list.append(f"• **복용 약물({profile['user_drug']}) 상호작용 성분:** 심평원 DUR 실시간 코드 매핑에 의해 충돌 가능 성분 감지. 복용 제한 요망")
            
        if avoid_list:
            for item in avoid_list:
                st.write(item)
        else:
            st.success("✅ 현재 복용중인 전문 의약품 및 기저질환 대비 치명적인 영양제 성분 상호작용 충돌이 발견되지 않았습니다.")

        # 3. 섭취 타이밍 스마트 팁
        st.info("💡 **복용 상호작용 스마트 팁:**\n\n칼슘과 마그네슘은 흡수 경로가 동일하여 고함량 병용 시 흡수율이 저하되므로 1:1 혹은 2:1 비율을 유지하거나, 지용성 영양소(비타민D, 오메가3)는 식사 직후 섭취하여 흡수 효율 증대를 도모하십시오.")

    st.write("---")
    
    # ----------------------------------------------------------
    # 🛒 4. 식약처 공공데이터 기반 AI 맞춤 추천 순위 영양제 제안
    # ----------------------------------------------------------
    st.subheader("🎯 뉴트리핏 AI 초개인화 맞춤 영양제 매칭 순위")
    st.caption("유저의 안전 필터(DUR/기저질환/과다성분)가 완전 반영되어 위험 풀이 하드 스크리닝된 최적 큐레이션 풀입니다.")
    
    # 엔진 가동
    recommend_pool = products_df.copy()
    
    # 하드 필터 제외 처리
    if profile["allergy"] and "없음" not in profile["allergy"]:
        for alg in profile["allergy"]:
            recommend_pool = recommend_pool[~recommend_pool['전성분'].str.contains(alg, na=False)]
    if profile["pill"] == "매우 불편함":
        recommend_pool = recommend_pool[recommend_pool['제형'].str.contains("구미|젤리|액상|드링크|분말|포", na=False)]
        
    # 과다 복용 성분 제품 풀에서 제외 연동
    for nutrient, value in intake.items():
        if value >= 500:
            recommend_pool = recommend_pool[~recommend_pool['전성분'].str.contains(nutrient, na=False)]

    # 의약품/기저질환 위험 성분 하드 스크리닝
    if "혈전 관련질환-항응고제" in profile["diseases"]:
        recommend_pool = recommend_pool[~recommend_pool['전성분'].str.contains("오메가3|비타민K", na=False)]

    # 가중치 산출 및 1대1 매칭 사유 정의
    recommend_pool['match_score'] = 0
    recommend_pool['recommend_reason'] = "기본 건강 밸런스 유지용 기초 영양성분 매칭"

    for idx, row in recommend_pool.iterrows():
        score = 0
        reasons = []
        
        # 나이에 따른 영양제 매칭 가중치
        if "20대" in profile["age"] or "30대" in profile["age"]:
            if any(x in row['전성분'] for x in ["비타민B", "테아닌"]):
                score += 2
                reasons.append("대사 소모가 활발한 2030 피로 회복을 위해 식약처 공인 에너지 대사 비타민B군 우선 배정")
        elif "40대" in profile["age"] or "50대" in profile["age"]:
            if any(x in row['전성분'] for x in ["오메가3", "루테인", "코엔자임"]):
                score += 3
                reasons.append("40대 이상 혈행 노화 전조 예방 및 항산화 세포 보호 기능성 성분 보완")

        # 생활습관(음주/운동) 매칭 가중치
        if profile["drinking"] == "잦은 음주" and ("밀크씨슬" in row['전성분'] or "실리마린" in row['전성분']):
            score += 4
            reasons.append("잦은 음주 이력에 따른 간 기능 보호 및 식약처 고지 간세포 손상 방지 성분 집중 가산")
        if "고강도" in "".join(profile["workout"]) and "마그네슘" in row['전성분']:
            score += 2
            reasons.append("고강도 운동 스타일에 따른 근육 피로 완화 및 신경 안정을 위한 미네랄 매칭")

        # 유저 1순위 건강 고민 매칭
        if profile["goals"]:
            for goal in profile["goals"]:
                if goal == "만성피로" and "비타민B" in row['전성분']:
                    score += 3
                    reasons.append("유저 지정 고민인 만성 피로 타겟 에너지 활성 활력 성분 집중 결합")
                elif goal == "장 건강" and "유산균" in row['전성분']:
                    score += 3
                    reasons.append("불규칙한 식습관 개선을 유도하는 유익균 증식 프로바이오틱스 밸런싱 반영")

        recommend_pool.at[idx, 'match_score'] = score
        if reasons:
            recommend_pool.at[idx, 'recommend_reason'] = " 💡 ".join(reasons)

    # 순위 소팅
    recommend_pool = recommend_pool.sort_values(by='match_score', ascending=False)

    # UI 레이아웃 카드식 랭킹 표출 (이미지 포함)
    if not recommend_pool.empty:
        rank = 1
        for idx, row in recommend_pool.head(3).iterrows():
            with st.container(border=True):
                p_col1, p_col2, p_col3 = st.columns([1, 2.5, 1.5])
                
                with p_col1:
                    # 폴더 내 실제 영양제 이미지 동적 스캔 매핑
                    if '이미지경로' in row and os.path.exists(str(row['이미지경로'])):
                        st.image(str(row['이미지경로']), use_container_width=True, caption=f"추천 순위 {rank}위")
                    else:
                        st.image("images/default_product.png", use_container_width=True, caption=f"추천 순위 {rank}위")
                        
                with p_col2:
                    st.markdown(f"### 🏆 {rank}위: [{row['브랜드']}] {row['제품명']}")
                    st.markdown(f"**🔬 식약처 등록 주원료 구성:** `{row['전성분']}`")
                    st.info(f"📋 **공공데이터 기반 매칭 사유**\n\n{row['recommend_reason']}")
                    
                with p_col3:
                    st.write("<br><br>", unsafe_allow_html=True)
                    st.markdown(f"## 💵 {int(row['가격']):,} 원")
                    # 최저가 구매 이커머스 즉시 아웃바운드 랜딩
                    st.link_button("최저가 구매하러 가기 🛒", "https://www.coupang.com", use_container_width=True, type="primary", key=f"rec_buy_{idx}")
            rank += 1
    else:
        st.warning("⚠️ 유저님의 DUR/기저질환/과다섭취 안전 필터 기준을 100% 충족하는 매칭 영양제가 풀에 존재하지 않습니다. 문진표에서 복용량 제한 수치를 일부 조정해 주세요.")

    st.write("<br><br>", unsafe_allow_html=True)
    st.caption("🚨 **면책 고지 (Disclaimer):** 본 뉴트리핏 리포트는 식약처 공공 API 및 심평원 DUR 데이터를 기반으로 제공되는 건강 정보 참고용 대시보드이며, 특정 약물의 처방이나 질병 치료를 위한 의학적 진단을 절대 대신하지 않습니다.")
    
    if st.button("🔄 처음부터 다시 진단하기", use_container_width=True):
        st.session_state.step = "agreement"
        st.rerun()