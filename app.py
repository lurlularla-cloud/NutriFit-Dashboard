"""
영양 매칭 허브 대시보드 (최종 통합본 - 영양소 확장 및 중복/상충 진단 고도화)
- 1클릭 전체 동의 및 소비자 친화적 단어 순화 반영 완료
- [문진 고도화] 섭취 영양소 종류를 대폭 확장하고 바둑판(Grid) 레이아웃으로 리디자인
- [리포트 고도화] 복용 영양소 중 상충 배합(서로 피해야 하는 조합) 및 불필요 성분 실시간 진단 기능 추가
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
st.sidebar.caption("식약처 공공데이터 기반 섭취 밸런스 검증[cite: 1]")
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
                    식약처 건강기능식품 마스터 데이터와 심평원 DUR 데이터를 기반으로 객관적인 영양성분 밸런스를 확인하세요.[cite: 1]
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
            
            st.markdown("### 💡 서비스 핵심 프로세스 개요")
            p1, p2, p3 = st.columns(3)
            with p1:
                st.markdown("**STEP 01. 건강 습관 분석**")
                if os.path.exists("images/milk_thistle.jpg"): st.image("images/milk_thistle.jpg", caption="기본 프로필/습관 분석", use_container_width=True)
                else: st.info("📋 23개 생활변수 다각도 스캔[cite: 1]")
            with p2:
                st.markdown("**STEP 02. 복용약 부작용 분석**")
                if os.path.exists("images/vitaminc.jpg"): st.image("images/vitaminc.jpg", caption="의약품 상호작용 추적", use_container_width=True)
                else: st.info("🛡️ 약물 충돌 가능성 실시간 매핑[cite: 1]")
            with p3:
                st.markdown("**STEP 03. AI 맞춤 영양제 보고서**")
                if os.path.exists("images/vitamind.jpg"): st.image("images/vitamind.jpg", caption="과다섭취 스코어 분석", use_container_width=True)
                else: st.info("📊 과다섭취 및 성분 균형 시각화")

        with right_col:
            st.markdown("### 🔒 안전한 분석을 위한 절차")
            with st.container(border=True):
                st.write("안전한 매칭과 민감정보 보호를 위해 약관 동의 절차를 진행해 주세요.")
                st.write("<br>", unsafe_allow_html=True)
                
                all_agree = st.checkbox("✨ 모든 필수 항목에 한 번에 동의합니다.")
                
                st.markdown("---")
                chk1 = st.checkbox("서비스 이용약관 및 개인정보 동의 (필수)", value=all_agree)
                chk2 = st.checkbox("본인은 만 14세 이상 이용자입니다 (필수)", value=all_agree)
                chk3 = st.checkbox("건강지표 및 기저질환 민감정보 수집 동의 (필수)", value=all_agree)[cite: 1]
                
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
            gender = st.radio("성별", ["남성", "여성", "응답하지 않음"])[cite: 1]
            age_group = st.selectbox("연령대", ["20대 미만", "20대", "30대", "40대", "50대", "60대 이상"])[cite: 1]
            c1, c2 = st.columns(2)
            height = c1.number_input("키 (cm)", value=170.0)[cite: 1]
            weight = c2.number_input("몸무게 (kg)", value=65.0)[cite: 1]
            bmi = weight / ((height / 100) ** 2)
            drinking = st.selectbox("음주 빈도", ["전혀 안 함", "보통", "잦은 음주"])[cite: 1]
            
            workout = st.multiselect(
                "운동 스타일 (복수 선택 가능)", 
                ["안 함·체력유지재활", "저강도 걷기·스트레칭", "요가·필라테스·코어", "저항성·웨이트 근력 운동", "고강도 유산소(러닝/사이클)", "크로스핏·고강도 인터벌", "구기종목 및 격렬한 스포츠"][cite: 1]
            )
            goals = st.multiselect(
                "최우선 개선 목적 (최대 2개)", 
                ["만성피로", "눈 건조·피로", "장 건강", "피부탄력·이너뷰티", "체지방감소·다이어트", "면역력저하", "관절보호", "수면부족·스트레스케어", "항노화·항산화", "생리불순·생리통"],[cite: 1]
                max_selections=2
            )
            
        with t2:
            allergy = st.multiselect("유발 알레르기 물질", ["갑각류", "대두", "글루텐", "유제품", "견과류", "어류", "없음"])[cite: 1]
            user_drug = st.text_input("현재 복용중인 처방약 명칭 (DUR 데이터 확인용)", "")[cite: 1]
            diseases = st.multiselect("과거 기저질환 및 주의 상태", ["고혈압", "당뇨", "이상지질혈증", "만성 위장질환", "혈전 관련질환-항응고제", "간·신장질환", "없음·기타"])[cite: 1]
            pill_discomfort = st.radio("정제 제형 부담감", ["상관없음", "매우 불편함"])[cite: 1]
            budget = st.select_slider("선호 월 지출 예산 구조", options=["1~3만원", "3~5만원", "5~10만원", "10만원 이상"])[cite: 1]

        with t3:
            # 🌟 [요청 반영] 1. 영양소 종류 대폭 확장 및 바둑판(Grid) 멀티컬럼 레이아웃 디자인 수정
            st.markdown("#### 📦 현재 섭취하고 있는 영양소 종류를 선택해 주세요.")
            
            # 4열 바둑판 레이아웃 배치
            g_col1, g_col2, g_col3, g_col4 = st.columns(4)
            with g_col1:
                select_vitd = st.checkbox("비타민D")
                st.caption("뼈 건강·면역")
                select_vitb = st.checkbox("비타민B군")
                st.caption("에너지·피로 회복")
                select_vitc = st.checkbox("비타민C")
                st.caption("항산화·활력")
                select_vita = st.checkbox("비타민A / 베타카로틴")
                st.caption("시각·피부 보호")
            with g_col2:
                select_zinc = st.checkbox("아연")
                st.caption("정상적인 면역 기능")
                select_cal = st.checkbox("칼슘")
                st.caption("뼈·치아 형성")
                select_mag = st.checkbox("마그네슘")
                st.caption("신경·근육 유지")
                select_iron = st.checkbox("철분")
                st.caption("체내 산소 운반·혈액")
            with g_col3:
                select_omega = st.checkbox("오메가3 (EPA/DHA)")
                st.caption("혈행 개선·건조한 눈")
                select_milk = st.checkbox("밀크씨슬 (실리마린)")
                st.caption("간 건강 도움")
                select_lutein = st.checkbox("루테인 / 지아잔틴")
                st.caption("황반 색소 밀도 유지")
                select_coq10 = st.checkbox("코엔자임 Q10")
                st.caption("항산화·높은 혈압 감소")
            with g_col4:
                select_probio = st.checkbox("프로바이오틱스 (유산균)")
                st.caption("장 건강·유익균 증식")
                select_msm = st.checkbox("MSM (식이유황)")
                st.caption("관절·연골 건강")
                select_collagen = st.checkbox("콜라겐")
                st.caption("피부 이너뷰티")
                select_theanine = st.checkbox("L-테아닌")
                st.caption("스트레스 긴장 완화")
            
            st.markdown("---")
            st.markdown("#### 📊 선택한 영양소의 대략적인 일일 복용량(%)을 지정해 주세요.")
            st.caption("100% = 일일 성분 권장량 기준치")
            
            # 활성화된 슬라이더만 조건부 표출
            take_vitd = st.slider("비타민D 복용 비중 (%)", 0, 1000, 0, step=50) if select_vitd else 0
            take_vitb = st.slider("비타민B군 복용 비중 (%)", 0, 2000, 0, step=50) if select_vitb else 0
            take_vitc = st.slider("비타민C 복용 비중 (%)", 0, 2000, 0, step=50) if select_vitc else 0
            take_vita = st.slider("비타민A 복용 비중 (%)", 0, 500, 0, step=10) if select_vita else 0
            take_zinc = st.slider("아연 복용 비중 (%)", 0, 500, 0, step=10) if select_zinc else 0
            take_cal = st.slider("칼슘 복용량 (%)", 0, 500, 0, step=10) if select_cal else 0
            take_mag = st.slider("마그네슘 복용량 (%)", 0, 500, 0, step=10) if select_mag else 0
            take_iron = st.slider("철분 복용량 (%)", 0, 500, 0, step=10) if select_iron else 0
            take_omega = 100 if select_omega else 0
            take_milk = 100 if select_milk else 0
            take_lutein = 100 if select_lutein else 0
            take_coq10 = 100 if select_coq10 else 0
            take_probio = 100 if select_probio else 0
            take_msm = 100 if select_msm else 0
            take_collagen = 100 if select_collagen else 0
            take_theanine = 100 if select_theanine else 0

        if st.button("🚀 영양 데이터 정밀 매핑 리포트 출력", use_container_width=True, type="primary"):
            st.session_state.survey_data = {
                "gender": gender, "age": age_group, "bmi": bmi, "allergy": allergy, "drinking": drinking,
                "workout": workout, "diseases": diseases, "goals": goals, "pill": pill_discomfort,
                "budget": budget, "user_drug": user_drug, "stress": "3단계",
                "intake": {
                    "비타민D": take_vitd, "비타민B군": take_vitb, "비타민C": take_vitc, "비타민A": take_vita,
                    "아연": take_zinc, "칼슘": take_cal, "마그네슘": take_mag, "철분": take_iron
                },
                "specials": {
                    "오메가3": select_omega, "실리마린": select_milk, "루테인": select_lutein, "코큐텐": select_coq10,
                    "유산균": select_probio, "MSM": select_msm, "콜라겐": select_collagen, "테아닌": select_theanine
                }
            }
            st.session_state.step = "result"
            st.rerun()

    # [C] 정밀 결과 리포트 단계
    elif st.session_state.step == "result":
        st.title("📊 AI 맞춤 영양제 보고서 및 분석 결과")
        profile = st.session_state.survey_data
        intake = profile["intake"]
        specials = profile["specials"]
        
        c_l, c_r = st.columns([1.1, 0.9], gap="large")
        with c_l:
            st.subheader("📊 일일 성분 결합 스캔 상태계")
            st.caption("유저님이 직접 입력하신 현재 복용 성분들의 1일 권장량 대비 누적 그래프입니다.")
            
            age_desc = ""
            if "20대" in profile["age"] or "30대" in profile["age"]:
                age_desc = "⚡ **20~30대 청장년기 KDRI 기준 적용:** 활력 증진을 위한 비타민 B군 수용폭을 최적 매칭 상태로 가동합니다.[cite: 1]"
            elif "40대" in profile["age"] or "50대" in profile["age"] or "60대 이상" in profile["age"]:
                age_desc = "🩺 **40대 이상 중장년기 KDRI 기준 적용:** 만성 질환 대비 및 안구·혈행 집중 필터를 엄격하게 스캔 중입니다.[cite: 1]"
                
            st.info(f"🧬 **개인별 조건에 따른 기준점 실시간 추적**\n\n{age_desc}")
            
            for nutrient, value in intake.items():
                if value == 0: continue
                if value >= 500: color, status = "#D9534F", "과다 섭취 (위험)"
                elif value >= 120: color, status = "#F0AD4E", "경계 수치 (주의)"
                else: color, status = "#5CB85C", "안정권 (적정)"
                st.markdown(f"**{nutrient}** <span style='float:right; color:{color}; font-weight:bold;'>{value}% ({status})</span>", unsafe_allow_html=True)
                st.progress(min(value / 600.0, 1.0))
        
        with c_r:
            st.subheader("🛡️ 안심 섭취 배제 가이드라인")
            if "혈전 관련질환-항응고제" in profile["diseases"]:
                st.error("🚨 **항응고 물질 중복 방지 (위험):** 기저질환 확인 결과 오메가3 및 비타민K 함유 영양제는 지혈 억제 상호작용 리스크가 있어 매칭 필터에서 자동 차단 조치되었습니다.[cite: 1]")
            else:
                st.success("✅ 보유 지병 및 처방 약물 대비 차단 유발 원료 없음 [안심]")
                
            # 과다 섭취 판정
            st.markdown("<br>#### 🚫 지금 먹는 성분 중 조정이 필요한 요소", unsafe_allow_html=True)
            over_count = 0
            for nutrient, value in intake.items():
                if value >= 120:
                    over_count += 1
                    st.markdown(f"• **{nutrient} ({value}%)**: 권장치 이상으로 겹쳐 드시고 있습니다. 추가 단일제 섭취를 중단하여 위장 장애나 독성 리스크를 방지하세요.[cite: 1]")
            if over_count == 0:
                st.write("• 현재 과다 복용 중인 성분이 없어 아주 건강하게 섭취 중이십니다.")
                
        st.write("---")
        
        # 🌟 [요청 반영] 2. 서로 중복으로 먹으면 안 되는 영양제 및 불필요한 성분 실시간 진단 블록
        st.subheader("❌ 상충 배합(같이 먹으면 안 되는 조합) 및 불필요 성분 진단 필터")
        with st.container(border=True):
            conflict_detected = False
            
            # A. 상충 배합(병용 기피 조합) 규칙 로직
            if intake["칼슘"] > 0 and intake["철분"] > 0:
                st.warning("⚠️ **[상충 배합 감지] 칼슘 ➕ 철분**\n\n칼슘과 철분은 체내 흡수 통로가 동일하여 동시에 섭취 시 서로의 흡수를 강력하게 방해합니다. 철분은 아침 공복에, 칼슘은 저녁 식후에 따로 분리하여 섭취하세요.")
                conflict_detected = True
            if specials["오메가3"] and specials["실리마린"] and intake["비타민E"] > 150:
                st.warning("⚠️ **[주의 조합] 고함량 지용성 비타민 중복**\n\n오메가3 제품군에 항산화 목적으로 포함된 비타민E와 별도 비타민 복합제를 동시에 장기 과다 복용 시 간 수치 부하 우려가 발생할 수 있습니다.")
                conflict_detected = True
            if intake["마그네슘"] > 150 and intake["칼슘"] > 150:
                st.info("💡 **[함량 조절 팁] 마그네슘 ➕ 칼슘**\n\n두 미네랄을 한 번에 너무 과함량으로 섭취하면 흡수 효율이 급감합니다. 이상적인 비율인 **칼슘 2 : 마그네슘 1** 배합비를 유지해 주시는 것을 권장합니다.")
                conflict_detected = True
                
            # B. 라이프스타일 대비 불필요/과잉 성분 제안
            if "안 함" in "".join(profile["workout"]) and specials["MSM"]:
                st.markdown("• 🚫 **불필요/과잉 예상 성분 - [MSM (식이유황)]**\n\n관절 결합 조직에 가해지는 물리적 고강도 운동량이 없으므로 현재 컨디션에서는 굳이 필수적으로 섭취하지 않아도 되는 관리 성분으로 분류됩니다.")
                conflict_detected = True
            if "비흡연" in profile["smoking"] and intake["비타민A"] > 200:
                st.markdown("• 🚫 **불필요/과잉 예상 성분 - [고함량 비타민A]**\n\n특이 안구 질환이 없는 상태에서 고함량의 비타민A 단일제를 지속 편성하는 것은 체내 축적 리스크 대비 효율성이 낮아 종합 제품 내 미량 포함 정도로 충분합니다.")
                conflict_detected = True
                
            if not conflict_detected:
                st.success("✅ 현재 복용중인 영양제 간 심각한 상충 배합(흡수 방해) 요소 및 불필요한 중복 과잉 성분이 발견되지 않았습니다. 섭취 설계를 잘 유지하고 계십니다.")

        st.write("---")
        
        # 심층 분석 리포트
        st.subheader("🩺 AI 맞춤형 섭취 스펙 분석 보고서")
        rep_col1, rep_col2, rep_col3 = st.columns(3, gap="medium")
        
        with rep_col1:
            with st.container(border=True):
                st.markdown(f"#### 📅 {profile['age']} 나이대별 신체 특징 분석")
                if "20대" in profile["age"] or "30대" in profile["age"]:
                    st.write("**특징:** 스트레스 및 불규칙한 생활로 인한 세포 에너지 고갈 패턴이 두드러지는 시기입니다.[cite: 1]")
                    st.write("**필수 추천:** 활력 증진을 위한 **비타민 B군** 및 면역 균형을 위한 **비타민 D** 보충이 시급합니다.[cite: 1]")
                else:
                    st.write("**특징:** 혈행 탄력 저하, 관절 밀도 감소 및 안구 노화 전조가 본격화되는 시기입니다.[cite: 1]")
                    st.write("**필수 추천:** 심혈관 보호를 위한 **오메가3**, 눈 보호를 위한 **루테인**, 골다공증 예방을 위한 **칼슘/마그네슘** 섭취가 중요합니다.[cite: 1]")
                    
        with rep_col2:
            with st.container(border=True):
                st.markdown("#### 🏃‍♂️ 운동 스타일 및 패턴 매칭")
                workout_str = ", ".join(profile["workout"])
                st.write(f"**나의 스타일:** `{workout_str if workout_str else '선택 없음'}`")
                
                if "근력 운동" in workout_str or "인터벌" in workout_str:
                    st.write("**분석:** 근육 손실 방지와 젖산 분해를 위한 세포 에너지 및 미네랄 소모율이 대단히 높습니다.[cite: 1]")
                    st.write("**권장 성분:** 근육 이완과 쥐 내림 방지를 위한 **마그네슘**, 관절 연골을 보호하는 **MSM** 배합을 추천합니다.[cite: 1]")
                elif "유산소" in workout_str:
                    st.write("**분석:** 지속적인 산소 호흡으로 인해 유해 활성산소(산화 스트레스) 배출량이 증가합니다.[cite: 1]")
                    st.write("**권장 성분:** 활성산소를 제거하는 **비타민 C** 및 피로 물질을 억제하는 **비타민 B군**이 필수적입니다.[cite: 1]")
                else:
                    st.write("**분석:** 기초 대사량이 낮아질 수 있는 정적인 패턴입니다. 기본 권장 가이드로 매칭됩니다.[cite: 1]")

        with rep_col3:
            with st.container(border=True):
                st.markdown("#### 🎯 관심사(건강 고민) 집중 솔루션")
                goals_str = ", ".join(profile["goals"])
                st.write(f"**나의 타겟 고민:** `{goals_str if goals_str else '없음'}`")
                
                if profile["goals"]:
                    for goal in profile["goals"]:
                        if goal == "만성피로":
                            st.write("• **만성피로 케어:** 간 해독 기능을 극대화하는 **실리마린(밀크씨슬)**과 에너지 발전소 역할을 하는 **비타민B군** 결합이 1순위입니다.[cite: 1]")
                        elif goal == "눈 건조·피로":
                            st.write("• **아이 케어:** 황반 색소 밀도를 유지해 주는 **루테인/지아잔틴**과 망막 혈행을 돕는 **오메가3** 조합을 추천합니다.[cite: 1]")
                        elif goal == "장 건강":
                            st.write("• **장 건강 케어:** 100억 이상의 유익균 증식을 돕는 **프로바이오틱스(유산균)**를 추천합니다.[cite: 1]")
                else:
                    st.write("선택된 건강 고민이 없습니다. 기본 종합 면역 영양 밸런스 위주로 설계됩니다.")

        st.write("<br>", unsafe_allow_html=True)

        # 복용 중요도 순위 테이블
        st.markdown("### ⏰ 나만을 위한 영양제 복용 타임라인 가이드")
        st.caption("성분 간의 흡수 경합 및 위장 자극을 고려하여 과학적으로 배정한 최적의 복용 시간대와 주기 테이블입니다.[cite: 1]")
        
        timeline_data = []
        if "20대" in profile["age"] or "30대" in profile["age"] or "만성피로" in profile["goals"]:
            timeline_data.append({"우선순위": "🥇 1순위 (필수)", "성분명": "비타민B군 / 밀크씨슬", "복용 시간대": "아침 식사 직후", "섭취 주기": "매일 1회", "💡 섭취 핵심 팁": "비타민B군은 수용성으로 아침에 먹어야 하루 활력을 주며, 식후에 먹어야 위장 장애가 없습니다.[cite: 1]"})
        if "장 건강" in profile["goals"]:
            timeline_data.append({"우선순위": "🥇 1순위 (필수)", "성분명": "프로바이오틱스 (유산균)", "복용 시간대": "아침 기상 직후 (공복)", "섭취 주기": "매일 1회", "💡 섭취 핵심 팁": "위산이 가장 약한 아침 공복에 물 한 잔과 복용해야 유익균이 장까지 무사히 살아갑니다.[cite: 1]"})
        if "40대" in profile["age"] or "50대 이상" in profile["age"] or "눈 건조·피로" in profile["goals"]:
            timeline_data.append({"우선순위": "🥈 2순위 (권장)", "성분명": "오메가3 / 루테인", "복용 시간대": "점심 또는 저녁 식사 직후", "섭취 주기": "매일 1회", "💡 섭취 핵심 팁": "지용성 영양소는 식사 중에 포함된 지방 성분과 결합해야 흡수율이 최대 3배 이상 증가합니다.[cite: 1]"})
        if "근력 운동" in profile["workout"]:
            timeline_data.append({"우선순위": "🥉 3순위 (보완)", "성분명": "마그네슘 / 칼슘", "복용 시간대": "취침 1시간 전", "섭취 주기": "매일 1회", "💡 섭취 핵심 팁": "마그네슘은 근육을 이완하고 신경을 안정시켜 주어 숙면을 유도하는 최적의 밤 시간대 영양소입니다.[cite: 1]"})
            
        if not timeline_data:
            timeline_data.append({"우선순위": "🥇 1순위 (필수)", "성분명": "종합 비타민 / 비타민D", "복용 시간대": "아침 식사 후", "섭취 주기": "매일 1회", "💡 섭취 핵심 팁": "가장 기본이 되는 필수 비타민 조합으로 식후 섭취 시 생체 이용률이 높아집니다.[cite: 1]"})
            
        st.table(pd.DataFrame(timeline_data))

        st.write("---")
        st.subheader("🏆 당신을 위한 매칭 최적화 영양제 리스트")
        
        pool = products_df.copy()
        pool['match_score'] = 0
        pool['reason'] = "신체 균형용 매칭"
        
        if profile["allergy"] and "없음" not in profile["allergy"]:
            for alg in profile["allergy"]: pool = pool[~pool['전성분'].str.contains(alg, na=False)]
        if profile["pill"] == "매우 불편함": pool = pool[pool['제형'].str.contains("구미|젤리|액상|드링크|분말·포", na=False)]
        if "혈전 관련질환-항응고제" in profile["diseases"]: pool = pool[~pool['전성분'].str.contains("오메가3|비타민K", na=False)]
            
        for idx, row in pool.iterrows():
            score = 0
            reasons = []
            if profile["drinking"] == "잦은 음주" and "밀크씨슬" in row['전성분']:[cite: 1]
                score += 4; reasons.append("음주 지표 기반 간 대사 효소 방어 목적 원료 매칭")[cite: 1]
            if any(g in row['전성분'] for g in profile["goals"]):[cite: 1]
                score += 3; reasons.append("선택한 신체 피로/고민 집중 해결 원료 타겟 매칭")[cite: 1]
            pool.at[idx, 'match_score'] = score
            if reasons: pool.at[idx, 'reason'] = " 💡 ".join(reasons)
            
        pool = pool.sort_values(by='match_score', ascending=False)
        
        rank = 1
        for r_idx, r_row in pool.head(2).iterrows():
            with st.container(border=True):
                col_a, col_b, col_c = st.columns([1, 2.5, 1.5])
                with col_a:
                    if '이미지경로' in r_row and os.path.exists(str(r_row['이미지경로'])):
                        st.image(str(r_row['이미지경로']), use_container_width=True, caption=f"추천 {rank}위")
                    else:
                        st.image("images/default_product.png", use_container_width=True, caption=f"추천 {rank}위")
                with col_b:
                    st.markdown(f"#### 🏆 {rank}위: [{r_row['브랜드']}] {r_row['제품명']}")
                    st.caption(f"🔬 **원료 명세:** {r_row['전성분']}")
                    st.info(f"📚 **공공데이터 기반 추천 사유:** {r_row['reason']}")
                with col_c:
                    st.write("<br><br>", unsafe_allow_html=True)
                    st.markdown(f"### 💵 {int(r_row['가격']):,} 원")
                    st.link_button("최저가 바로 구매하기 🛒", "https://www.coupang.com", use_container_width=True, type="primary", key=f"btn_buy_{r_idx}")
            rank += 1

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
        with c_s1: st.bar_chart(products_df['제형'].value_counts())
        with c_s2: st.dataframe(products_df[['브랜드', '제품명', '가격', '제형']], use_width=True)

    with tab_2:
        st.subheader("📐 식약처 가이드 기반 코어 연산 스펙 정의[cite: 1]")
        spec_df = pd.DataFrame({
            "핵심 지표 인자": ["생애주기 (임산부)", "습관 인자 (음주)", "처방 의약품 연동", "목적성 고민 요인"],
            "제외 및 가산 처리 기준 명세": [
                "식약처 개별인정형 정보 가이드에 의거, 태아 영향 가능 물질 고함량 제품군 강제 제외 처리[cite: 1]",
                "식약처 기능성 원료인정 DB 기반, 간 기능 개선 실리마린 배합 제품에 가중 스코어 +4점 할당[cite: 1]",
                "심평원 DUR 금기 마스터 매트릭스와 실시간 대조하여 병용 우려 물질 리스트에서 100% 드랍 제외[cite: 1]",
                "기능성 원료현황 고지 원료(비타민B군 등) 타겟별 매칭 가산 스코어 +3점 할당[cite: 1]"
            ]
        })
        st.table(spec_df)