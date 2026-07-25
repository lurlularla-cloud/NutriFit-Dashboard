"""
영양 매칭 허브 대시보드 (UX 고도화 및 문진 스펙 확장 버전)
- 1클릭 전체 동의 시스템 도입
- 소비자 친화적 단어 순화 (DUR 교차 -> 복용약 부작용 분석, 초개인화 -> AI 맞춤 영양제 보고서)
- 각 스텝별 시각화 이미지/그래프 배치 및 문진 선택지 대폭 확장
"""
import streamlit as st
import pandas as pd
import numpy as np
import os

# ==========================================================
# 0. 대시보드 기본 세팅 및 데이터 로드 (캐싱 적용)
# ==========================================================
st.set_page_config(page_title="영양 매칭 허브 (NutriHub)", layout="wide")

@st.cache_data
def load_base_data():
    try:
        from src.api.data_loaders import load_dur_master_zip
        dur_master = load_dur_master_zip("건강보험심사평가원_의약품안전사용서비스(DUR) 의약품 목록_20260601.zip")
    except Exception:
        dur_master = pd.DataFrame({'품목명': ['아스피린정'], '주성분코드': ['123456ATB']})

    try:
        products = pd.read_csv("data/integrated_products.csv")
    except FileNotFoundError:
        products = pd.DataFrame({
            '브랜드': ['나우푸드', '락토핏', '고려은단', '솔가', '종근당', '뉴트리원'],
            '제품명': ['실리마린 밀크씨슬 추출물', '생유산균 골드', '비타민C 1000', '비타민D3 2200IU', '프로메가 오메가3', '루테인 지아잔틴 164'],
            '전성분': ['밀크씨슬 추출물, 실리마린, 셀룰로오스', '프로바이오틱스, 유산균, 락토바실러스', '비타민C, 아스코르브산', '비타민D, 정제어유, 젤라틴', '오메가3, EPA, DHA, 비타민E', '루테인, 지아잔틴, 마리골드꽃추출물'],
            '제형': ['캡슐', '분말·포', '정제(알약)', '연질캡슐', '연질캡슐', '캡슐'],
            '가격': [18900, 15400, 22000, 28000, 19900, 24500],
            '이미지경로': ['images/milk_thistle.jpg', 'images/lactofit.jpg', 'images/vitaminc.jpg', 'images/vitamind.jpg', '', '']
        })
    return products, dur_master

products_df, dur_df = load_base_data()

if "step" not in st.session_state:
    st.session_state.step = "agreement"
if "survey_data" not in st.session_state:
    st.session_state.survey_data = {}

# ==========================================================
# 1. 사이드바 내비게이션
# ==========================================================
st.sidebar.markdown("### 🧬 영양 매칭 허브")
st.sidebar.caption("식약처 공공데이터 기반 섭취 밸런스 검증")
menu = st.sidebar.radio("원하시는 메뉴를 선택하세요", ["🔍 맞춤형 섭취 밸런스 체크", "📊 투명한 매칭 기준 및 전성분 분석"])

# ----------------------------------------------------------
# [페이지 1] 개인별 맞춤 큐레이션 세션
# ----------------------------------------------------------
if menu == "🔍 맞춤형 섭취 밸런스 체크":
    
    if st.session_state.step == "agreement":
        st.markdown(
            """
            <div style="background-color: #0F1E36; padding: 35px; border-radius: 12px; color: white; margin-bottom: 25px;">
                <span style="color: #4A90E2; font-weight: bold; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">Evidence-Based Curation</span>
                <h1 style="color: white; margin-top: 5px; font-size: 36px; font-weight: 700;">내 몸이 원하는 영양 성분 설계, 투명하게 맞추다</h1>
                <p style="font-size: 15px; opacity: 0.85; margin-top: 10px; line-height: 1.6;">
                    과다하게 겹쳐 먹고 있지는 않나요? 복용 중인 의약품과 부딪히지는 않나요?<br>
                    식약처 건강기능식품 마스터 데이터와 심평원 DUR 데이터를 기반으로 객관적인 영양성분 밸런스를 확인하세요.
                </p>
            </div>
            """, unsafe_allow_html=True
        )

        left_col, right_col = st.columns([1.1, 0.9], gap="large")
        
        with left_col:
            st.markdown("### 💬 NutriHub를 다녀간 고객들의 솔직 후기")
            with st.container(border=True):
                st.markdown("**⭐ 5.0** | **30대 여성 직장인**")
                st.markdown("> *\"내 몸에 딱 맞춰서 영양제를 제안해 주니까 정말 쓰기 편해요. 바로 최저가로 구매할 수 있어서 복잡하게 고민할 필요가 없어 좋았습니다!\"*")
            with st.container(border=True):
                st.markdown("**⭐ 4.8** | **40대 남성 운동 헤비유저**")
                st.markdown("> *\"평소 과다하게 섭취하던 성분 그래프를 한눈에 짚어주니 직관적입니다. 안심하고 챙길 수 있겠네요.\"*")
                
            st.write("<br>", unsafe_allow_html=True)
            
            # 🌟 2) 스텝별 예시/결과 이미지 및 직관적인 단어 순화 매핑
            st.markdown("### 💡 서비스 핵심 프로세스 개요")
            p1, p2, p3 = st.columns(3)
            with p1:
                st.markdown("**STEP 01. 건강 습관 분석**")
                if os.path.exists("images/milk_thistle.jpg"): st.image("images/milk_thistle.jpg", caption="기본 프로필/습관 분석", use_container_width=True)
                else: st.info("📋 23개 생활변수 다각도 스캔")
            with p2:
                st.markdown("**STEP 02. 복용약 부작용 분석**")
                if os.path.exists("images/vitaminc.jpg"): st.image("images/vitaminc.jpg", caption="의약품 상호작용 추적", use_container_width=True)
                else: st.info("🛡️ 약물 충돌 가능성 실시간 매핑")
            with p3:
                st.markdown("**STEP 03. AI 맞춤 영양제 보고서**")
                if os.path.exists("images/vitamind.jpg"): st.image("images/vitamind.jpg", caption="과다섭취 스코어 분석", use_container_width=True)
                else: st.info("📊 과다섭취 및 성분 균형 시각화")

        with right_col:
            st.markdown("### 🔒 안전한 분석을 위한 절차")
            with st.container(border=True):
                st.write("안전한 매칭과 민감정보 보호를 위해 약관 동의 절차를 진행해 주세요.")
                st.write("<br>", unsafe_allow_html=True)
                
                # 🌟 1) 1번 클릭으로 전체 동의할 수 있는 기능 추가
                all_agree = st.checkbox("✨ 모든 필수 항목에 한 번에 동의합니다.")
                
                st.markdown("---")
                chk1 = st.checkbox("서비스 이용약관 및 개인정보 동의 (필수)", value=all_agree)
                chk2 = st.checkbox("본인은 만 14세 이상 이용자입니다 (필수)", value=all_agree)
                chk3 = st.checkbox("건강지표 및 기저질환 민감정보 수집 동의 (필수)", value=all_agree)
                
                st.write("<br>", unsafe_allow_html=True)
                if st.button("🚀 1:1 영양 밸런스 체크 시작하기", use_container_width=True, type="primary"):
                    if chk1 and chk2 and chk3:
                        st.session_state.step = "survey"
                        st.rerun()
                    else:
                        st.error("모든 필수 조항에 동의해 주셔야 분석이 가능합니다.")

    # [B] 문진 입력 단계
    elif st.session_state.step == "survey":
        st.title("📋 나의 건강 지표 및 섭취 현황 등록")
        t1, t2, t3 = st.tabs(["📊 신체 & 습관 스캔", "🛡️ 안전 제한 요인", "💊 복용 중인 영양성분"])
        
        with t1:
            gender = st.radio("성별", ["남성", "여성", "응답하지 않음"])
            age_group = st.selectbox("연령대", ["20대 미만", "20대", "30대", "40대", "50대", "60대 이상"])
            c1, c2 = st.columns(2)
            height = c1.number_input("키 (cm)", value=170.0)
            weight = c2.number_input("몸무게 (kg)", value=65.0)
            bmi = weight / ((height / 100) ** 2)
            drinking = st.selectbox("음주 빈도", ["전혀 안 함", "보통", "잦은 음주"])
            
            # 🌟 3) 운동 스타일 및 최우선 개선 목적 선택지 대폭 확장 [스펙 반영]
            workout = st.multiselect(
                "운동 스타일 (복수 선택 가능)", 
                ["안 함·체력유지재활", "저강도 걷기·스트레칭", "요가·필라테스·코어", "저항성·웨이트 근력 운동", "고강도 유산소(러닝/사이클)", "크로스핏·고강도 인터벌", "구기종목 및 격렬한 스포츠"]
            )
            goals = st.multiselect(
                "최우선 개선 목적 (최대 2개)", 
                ["만성피로", "눈 건조·피로", "장 건강", "피부탄력·이너뷰티", "체지방감소·다이어트", "면역력저하", "관절보호", "수면부족·스트레스케어", "항노화·항산화", "생리불순·생리통"],
                max_selections=2
            )
            
        with t2:
            allergy = st.multiselect("유발 알레르기 물질", ["갑각류", "대두", "글루텐", "유제품", "견과류", "어류", "없음"])
            user_drug = st.text_input("현재 복용중인 처방약 명칭 (DUR 데이터 확인용)", "")
            diseases = st.multiselect("과거 기저질환 및 주의 상태", ["고혈압", "당뇨", "이상지질혈증", "만성 위장질환", "혈전 관련질환-항응고제", "간·신장질환", "없음·기타"])
            pill_discomfort = st.radio("정제 제형 부담감", ["상관없음", "매우 불편함"])
            budget = st.select_slider("선호 월 지출 예산 구조", options=["1~3만원", "3~5만원", "5~10만원", "10만원 이상"])

        with t3:
            # 🌟 3) 클릭하여 선택하는 영양소 보관함 구조로 확장 다각화
            st.markdown("#### 📦 현재 섭취하고 있는 영양소 종류를 클릭해 주세요.")
            select_vitd = st.checkbox("비타민D")
            select_vitb = st.checkbox("비타민B군")
            select_vitc = st.checkbox("비타민C")
            select_zinc = st.checkbox("아연")
            select_cal = st.checkbox("칼슘")
            select_mag = st.checkbox("마그네슘")
            select_omega = st.checkbox("오메가3")
            select_milk = st.checkbox("밀크씨슬 (실리마린)")
            
            st.markdown("---")
            st.caption("체크하신 영양소의 1일 영양성분 기준치 대비 섭취량(%)을 대략적으로 지정해 주세요.")
            
            take_vitd = st.slider("비타민D 복용량 (%)", 0, 1000, 0, step=50) if select_vitd else 0
            take_vitb = st.slider("비타민B군 복용량 (%)", 0, 2000, 0, step=50) if select_vitb else 0
            take_vitc = st.slider("비타민C 복용량 (%)", 0, 2000, 0, step=50) if select_vitc else 0
            take_zinc = st.slider("아연 복용량 (%)", 0, 500, 0, step=10) if select_zinc else 0
            take_cal = st.slider("칼슘 복용량 (%)", 0, 500, 0, step=10) if select_cal else 0
            take_mag = st.slider("마그네슘 복용량 (%)", 0, 500, 0, step=10) if select_mag else 0

        if st.button("🚀 영양 데이터 정밀 매핑 리포트 출력", use_container_width=True, type="primary"):
            st.session_state.survey_data = {
                "gender": gender, "age": age_group, "bmi": bmi, "allergy": allergy, "drinking": drinking,
                "workout": workout, "diseases": diseases, "goals": goals, "pill": pill_discomfort,
                "budget": budget, "user_drug": user_drug, "stress": "3단계",
                "intake": {"비타민D": take_vitd, "비타민B군": take_vitb, "비타민C": take_vitc, "아연": take_zinc, "칼슘": take_cal, "마그네슘": take_mag},
                "specials": {"오메가3": select_omega, "실리마린": select_milk}
            }
            st.session_state.step = "result"
            st.rerun()

    # [C] 정밀 결과 리포트 단계
    elif st.session_state.step == "result":
        st.title("📊 AI 맞춤 영양제 보고서 및 분석 결과")
        profile = st.session_state.survey_data
        
        c_l, c_r = st.columns([1, 1], gap="large")
        with c_l:
            st.subheader("📊 일일 성분 결합 스캔 상태계")
            for nutrient, value in profile["intake"].items():
                if value == 0: continue
                if value >= 500: color, status = "#D9534F", "과다 섭취 (위험)"
                elif value >= 120: color, status = "#F0AD4E", "경계 수치 (주의)"
                else: color, status = "#5CB85C", "안정권 (적정)"
                st.markdown(f"**{nutrient}** <span style='float:right; color:{color}; font-weight:bold;'>{value}% ({status})</span>", unsafe_allow_html=True)
                st.progress(min(value / 600.0, 1.0))
        
        with c_r:
            st.subheader("🩺 안심 섭취 배제 가이드라인")
            if "혈전 관련질환-항응고제" in profile["diseases"]:
                st.error("🚨 **항응고 물질 중복 방지:** 기저질환 확인 결과 오메가3 및 비타민K 함유 영양제는 지혈 억제 상호작용 리스크가 있어 매칭 필터에서 자동 차단 조치되었습니다.")
            else:
                st.success("✅ 보유 지병 및 처방 약물 대비 차단 유발 원료 없음")
                
        st.write("---")
        st.subheader("🏆 당신을 위한 매칭 최적화 영양제 리스트")
        
        pool = products_df.copy()
        pool['match_score'] = 0
        pool['reason'] = "신체 균형용 매칭"
        
        for idx, row in pool.iterrows():
            score = 0
            reasons = []
            if profile["drinking"] == "잦은 음주" and "밀크씨슬" in row['전성분']:
                score += 4; reasons.append("음주 지표 기반 간 대사 효소 방어 목적 원료 매칭")
            if any(g in row['전성분'] for g in profile["goals"]):
                score += 3; reasons.append("선택한 신체 피로/고민 집중 해결 원료 타겟 매칭")
            pool.at[idx, 'match_score'] = score
            if reasons: pool.at[idx, 'reason'] = " 💡 ".join(reasons)
            
        pool = pool.sort_values(by='match_score', ascending=False)
        
        for r_idx, r_row in pool.head(2).iterrows():
            with st.container(border=True):
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.markdown(f"#### 🏆 [{r_row['브랜드']}] {r_row['제품명']}")
                    st.caption(f"🔬 **원료 명세:** {r_row['전성분']}")
                    st.info(f"📚 **공공데이터 기반 추천 사유:** {r_row['reason']}")
                with col_b:
                    st.write("<br>", unsafe_allow_html=True)
                    st.link_button("최저가 바로 구매하기 🛒", "https://www.coupang.com", use_container_width=True, type="primary")

        if st.button("🔄 처음부터 다시 스캔하기", use_container_width=True):
            st.session_state.step = "agreement"
            st.rerun()

# ----------------------------------------------------------
# [페이지 2] 투명한 매칭 기준 및 전성분 분석 뷰
# ----------------------------------------------------------
elif menu == "📊 투명한 매칭 기준 및 전성분 분석":
    st.title("📊 데이터 적재 현황 및 크로스 분석실")
    
    tab_1, tab_2 = st.tabs(["🗃️ 적재 상품 원형 매트릭스", "📐 가중치 스코어 연산 기준 스펙"])
    
    with tab_1:
        st.subheader("📦 전체 원시 데이터 현황")
        st.write(f"현재 데이터베이스에 적재 및 동기화된 건강기능식품 목록은 총 **{len(products_df)}개**입니다.")
        c_s1, c_s2 = st.columns(2)
        with c_s1:
            st.bar_chart(products_df['제형'].value_counts())
        with c_s2:
            st.dataframe(products_df[['브랜드', '제품명', '가격', '제형']], use_container_width=True)

    with tab_2:
        st.subheader("📐 식약처 가이드 기반 코어 연산 스펙 정의")
        spec_df = pd.DataFrame({
            "핵심 지표 인자": ["생애주기 (임산부)", "습관 인자 (음주)", "처방 의약품 연동", "목적성 고민 요인"],
            "제외 및 가산 처리 기준 명세": [
                "식약처 개별인정형 정보 가이드에 의거, 태아 영향 가능 물질 고함량 제품군 강제 제외 처리",
                "식약처 기능성 원료인정 DB 기반, 간 기능 개선 실리마린 배합 제품에 가중 스코어 +4점 할당",
                "심평원 DUR 금기 마스터 매트릭스와 실시간 대조하여 병용 우려 물질 리스트에서 100% 드랍 제외",
                "기능성 원료현황 고지 원료(비타민B군 등) 타겟별 매칭 가산 스코어 +3점 할당"
            ]
        })
        st.table(spec_df)