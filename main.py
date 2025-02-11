import streamlit as st

import json
import urllib.request
import pandas as pd

from typing import List
from datetime import timedelta

# 전체 폰트 설정
st.markdown(
    """
	<style>
		@import url(".../dist/web/static/pretendard.min.css");
		* {
			font-family: 'Pretendard' !important
		}
	</style>
	""",
    unsafe_allow_html=True,
)


def request(action, **params):
    return {"action": action, "params": params, "version": 6}


def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode("utf-8")
    response = json.load(
        urllib.request.urlopen(
            urllib.request.Request("http://127.0.0.1:8765", requestJson)
        )
    )
    if len(response) != 2:
        raise Exception("response has an unexpected number of fields")
    if "error" not in response:
        raise Exception("response is missing required error field")
    if "result" not in response:
        raise Exception("response is missing required result field")
    if response["error"] is not None:
        raise Exception(response["error"])
    return response["result"]


def get_new_card_count_list(selected_deck_names: List[str]):
    card_counts: List[int] = []
    for selected_deck_name in selected_deck_names:
        new_cards = invoke("findCards", query=f'is:new deck:"{selected_deck_name}"')
        card_counts.append(len(new_cards))

    return card_counts


def get_new_card_total(new_card_count_list: List[int]) -> int:
    total = 0
    for new_card_count in new_card_count_list:
        total += new_card_count

    return total


with st.sidebar:
    st.title("Anki Manager")

st.title("학습 시뮬레이터")
st.write(
    """목표 날짜까지 일일 학습량을 계산해주는 시뮬레이터입니다. 
    예를 들어, JLPT 시험일인 2025년 7월 6일의 전 날까지 1,170개의 새카드 학습을 완료하고 싶은 경우, 
    하루에 필요한 학습량을 자동으로 계산해 줍니다. 
    2025년 2월 11일부터 시험일까지 약 145일 동안 하루 평균 8개의 새카드를 학습하면 목표를 달성할 수 있습니다."""
)

deck_names = invoke("deckNames")

selected_deck_names = st.multiselect(
    "시뮬레이션을 위한 덱을 선택해 주세요.",
    deck_names[1::],
)

if selected_deck_names:
    new_card_count_list = get_new_card_count_list(selected_deck_names)
    new_card_total = get_new_card_total(new_card_count_list)
    data = {
        "덱 제목": selected_deck_names,
        "새카드": new_card_count_list,
    }

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        begin = st.date_input("학습 시작일")
    with col2:
        end = st.date_input("학습 종료일")

    diff_days = (end - begin).days
    if diff_days == 0:
        diff_days = 1
    else:
        diff_days += 1

    st.subheader("시뮬레이션 결과")

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    # 하루 평균 공부량
    avg_count = new_card_total / diff_days
    avg_count = round((avg_count - int(avg_count)) * diff_days)

    metric_col1.metric("새카드 총합", f"{new_card_total}개", border=True)
    metric_col2.metric("남은 일수", f"{diff_days}일", border=True)
    metric_col3.metric(
        "하루 평균 공부량", f"{(new_card_total / diff_days):.2f}개", border=True
    )

    # 학습 기간 계산
    learning_start_date = begin
    intensive_period_days = int(avg_count)  # 집중 학습 기간 일수
    intensive_end_date = learning_start_date + timedelta(days=intensive_period_days)

    regular_start_date = learning_start_date + timedelta(days=int(avg_count + 1))
    regular_end_date = (
        learning_start_date + timedelta(days=int(avg_count - 1))
    ) + timedelta(days=int(diff_days - avg_count))
    regular_period_days = diff_days - intensive_period_days

    # 일일 학습 카드 수 계산
    intensive_daily_cards = (
        new_card_total / diff_days + 1
    )  # 집중 학습 기간 일일 카드 수
    regular_daily_cards = new_card_total / diff_days  # 일반 학습 기간 일일 카드 수

    # 학습 기간 문자열 포맷팅
    intensive_period = f"{learning_start_date.strftime('%Y년 %m월 %d일')} ~ {intensive_end_date.strftime('%m월 %d일')}"
    regular_period = f"{regular_start_date.strftime('%Y년 %m월 %d일')} ~ {regular_end_date.strftime('%m월 %d일')}"

    # 최종 학습 계획 메시지
    learning_schedule = f"""##### 총 {diff_days}일의 학습 기간 중

- **{intensive_period} ({intensive_period_days}일)** → 하루 {int(intensive_daily_cards)}개
- **{regular_period} ({regular_period_days}일)** → 하루 {int(regular_daily_cards)}개의 학습을 권장드립니다.
    """

    st.markdown(learning_schedule)
