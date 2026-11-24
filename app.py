# ===== 라이브러리 불러오기 =====
import streamlit as st
import pandas as pd
import plotly.express as px

# ===== 페이지 설정 =====
st.set_page_config(page_title="Titanic 대시보드", layout="wide")

# ===== 데이터 불러오기 =====
@st.cache_data
def load_data():
    # titanic.csv 파일을 한 번만 읽어 캐시에 저장
    return pd.read_csv("titanic.csv")

# ===== 분석 및 시각화 함수 =====
# 조건에 맞는 승객만 필터링하는 함수
def filter_data(df, sexes, classes, age_range):
    # 나이 범위(튜플)에서 최소 나이와 최대 나이 꺼내기
    min_age, max_age = age_range
    
    # ① 성별 조건: sex 열의 값이 sexes 목록에 포함되는지 확인
    cond_sex = df["sex"].isin(sexes)
    
    # ② 객실 등급 조건: pclass 열의 값이 classes 목록에 포함되는지 확인
    cond_class = df["pclass"].isin(classes)
    
    # ③ 나이 범위 조건: 전체 범위(0~80)이면 나이 결측(NaN) 승객도 포함 # [수정]
    if age_range == (0, 80): # [수정]
        cond_age = ((df["age"] >= min_age) & (df["age"] <= max_age)) | df["age"].isna() # [수정]
    else: # [수정]
        cond_age = (df["age"] >= min_age) & (df["age"] <= max_age) # [수정]
    
    # ④ 세 조건을 모두(&) 만족하는 행만 골라내어 반환
    return df[cond_sex & cond_class & cond_age]

# 대시보드 상단 KPI(승객 수, 생존율, 평균 나이)를 계산하는 함수
def kpi(df):
    # 데이터프레임이 비어 있으면 (0, 0, 0) 반환
    if df.empty:
        return 0, 0, 0
    
    # ① 승객 수 계산
    count = len(df)
    
    # ② 생존율(%) 계산 후 소수 첫째 자리로 반올림
    survival_rate = round(df["survived"].mean() * 100, 1)
    
    # ③ 평균 나이 계산 후 소수 첫째 자리로 반올림
    avg_age = round(df["age"].mean(), 1)
    
    # 3개의 값 반환
    return count, survival_rate, avg_age

# 객실 등급별 생존율(%) 막대그래프 함수
def class_rate_bar(df):
    # 객실 등급(pclass)별 평균 생존율을 백분율(%)로 계산하고 소수 첫째 자리까지 반올림
    rate_df = df.groupby("pclass", as_index=False)["survived"].mean()
    rate_df["survived"] = (rate_df["survived"] * 100).round(1)
    # x축이 숫자(1.5 등)로 표시되지 않도록 문자열로 변환
    rate_df["pclass"] = rate_df["pclass"].astype(str) + "등급"
    
    # 막대그래프 생성 (text로 막대 위 표시할 값 지정)
    fig = px.bar(
        rate_df,
        x="pclass",
        y="survived",
        text="survived",
        title="객실 등급별 생존율 (%)",
        labels={"pclass": "객실 등급", "survived": "생존율 (%)"}
    )
    
    # 막대 바깥쪽 위에 '%' 기호를 붙여 값 표시
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    return fig

# 생존 여부별 나이 히스토그램 함수
def age_hist(df):
    # 생존 여부(survived)로 색을 구분하고 겹쳐서(overlay) 그리는 히스토그램 생성
    fig = px.histogram(
        df,
        x="age",
        color="survived",
        barmode="overlay",
        opacity=0.6,
        title="생존 여부별 승객 나이 분포",
        labels={"age": "나이", "survived": "생존 여부"}
    )
    return fig

# ===== 제목 및 데이터 로드 =====
st.title("타이타닉, 누가 살아남았나?")

# 데이터 로드
df = load_data()

# ===== 사이드바 필터 =====
st.sidebar.header("검색 조건")

# 성별 선택 (기본값: 전체 선택)
sex_options = ["male", "female"]
selected_sexes = st.sidebar.multiselect("성별", sex_options, default=sex_options)

# 객실 등급 선택 (기본값: 전체 선택)
class_options = [1, 2, 3]
selected_classes = st.sidebar.multiselect("객실 등급", class_options, default=class_options)

# 나이 범위 슬라이더 (0~80세)
selected_age = st.sidebar.slider("나이 범위", min_value=0, max_value=80, value=(0, 80))

# ===== 예외 처리 1: 미선택 확인 ===== # [수정]
if not selected_sexes or not selected_classes: # [수정]
    st.warning("성별과 객실 등급을 최소 1개 이상 선택해 주세요.") # [수정]
    st.stop() # [수정]

# ===== 데이터 필터링 =====
filtered_df = filter_data(df, selected_sexes, selected_classes, selected_age)

# ===== 예외 처리 2: 결과 0명 확인 ===== # [수정]
if filtered_df.empty: # [수정]
    st.warning("조건에 맞는 승객이 없습니다") # [수정]
    st.stop() # [수정]

# ===== 상단 KPI 카드 =====
count, survival_rate, avg_age = kpi(filtered_df)

col1, col2, col3 = st.columns(3)
col1.metric("승객 수", f"{count}명")
col2.metric("생존율", f"{survival_rate}%")
col3.metric("평균 나이", f"{avg_age}세")

# ===== 본문 차트 =====
chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.plotly_chart(class_rate_bar(filtered_df), use_container_width=True)
with chart_col2:
    st.plotly_chart(age_hist(filtered_df), use_container_width=True)

# ===== 하단 데이터 표 =====
with st.expander("데이터 보기"):
    st.dataframe(filtered_df)
