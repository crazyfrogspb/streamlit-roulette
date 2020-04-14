import nltk
import os
import io
import numpy as np
import streamlit as st
import time
import random
import hashlib
from typing import Dict
from streamlit import caching
import matplotlib.pyplot as plt

COLOR = "black"
BACKGROUND_COLOR = "#fff"


def select_block_container_style():
    """Add selection section for setting setting the max-width and padding
    of the main block container"""
    st.sidebar.header("Block Container Style")
    max_width_100_percent = st.sidebar.checkbox("Max-width: 100%?", False)
    if not max_width_100_percent:
        max_width = st.sidebar.slider("Select max-width in px", 100, 2000, 1200, 100)
    else:
        max_width = 1200
    padding_top = st.sidebar.number_input("Select padding top in rem", 0, 200, 5, 1)
    padding_right = st.sidebar.number_input("Select padding right in rem", 0, 200, 1, 1)
    padding_left = st.sidebar.number_input("Select padding left in rem", 0, 200, 1, 1)
    padding_bottom = st.sidebar.number_input("Select padding bottom in rem", 0, 200, 10, 1)

    _set_block_container_style(
        max_width, max_width_100_percent, padding_top, padding_right, padding_left, padding_bottom,
    )


def _set_block_container_style(
    max_width: int = 1200,
    max_width_100_percent: bool = False,
    padding_top: int = 5,
    padding_right: int = 1,
    padding_left: int = 1,
    padding_bottom: int = 10,
):
    if max_width_100_percent:
        max_width_str = f"max-width: 100%;"
    else:
        max_width_str = f"max-width: {max_width}px;"
    st.markdown(
        f"""
<style>
    .reportview-container .main .block-container{{
        {max_width_str}
        padding-top: {padding_top}rem;
        padding-right: {padding_right}rem;
        padding-left: {padding_left}rem;
        padding-bottom: {padding_bottom}rem;
    }}
    .reportview-container .main {{
        color: {COLOR};
        background-color: {BACKGROUND_COLOR};
    }}
</style>
""",
        unsafe_allow_html=True,
    )


select_block_container_style()


def display_case(case):
    sentences = nltk.sent_tokenize(case)
    question = f"**{sentences[-1]}**"
    case_md = "## " + " ".join(sentences[:-1]) + " " + question

    return case_md


nltk.download("punkt")

st.title("Рулетка кейсов")


@st.cache(allow_output_mutation=True)
def get_static_store() -> Dict:
    """This dictionary is initialized once and can be used to store the files uploaded"""
    return {}


menu_state = st.radio("Показать меню", ["Показать", "Скрыть"], 0)
static_store = get_static_store()

file_picker = st.empty()
file_buffer = file_picker.file_uploader("Загрузите файл с кейсами", type="txt")

if file_buffer:
    value = file_buffer.getvalue()
    if value not in static_store.values():
        static_store[file_buffer.getvalue()] = value
else:
    static_store.clear()


@st.cache(allow_output_mutation=True)
def read_cases(file_value):
    cases = static_store[file_value].splitlines()
    cases = [case for case in cases if case]
    return cases


if file_buffer is not None:
    cases = read_cases(file_buffer.getvalue())
    orig_case_num = len(cases)
else:
    cases = None
    st.info("Загрузите хотя бы один файл")

reload_button = st.empty()
if reload_button.button("Перезагрузить файлы"):
    caching.clear_cache()
    static_store.clear()

if menu_state == "Скрыть":
    file_picker.empty()
    reload_button.empty()

wheel = st.empty()
if cases:
    size = 360 / orig_case_num
    sizes = [size] * orig_case_num
    labels = [i for i in range(1, orig_case_num + 1)]
    colors = ["gray"] * orig_case_num
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, labels=labels, rotatelabels=True, startangle=0, colors=colors)
    wheel.pyplot(fig1)

if st.button("Выбрать кейс"):
    case_placeholder = st.empty()
    if not cases:
        case_placeholder.markdown("## Кейсы закончились!")
    else:
        case_num = len(cases)
        for i in range(50):
            ind = random.choice(range(case_num))
            case_placeholder.markdown(display_case(cases[ind]))
            if case_num > 1:
                time.sleep(i * 0.001)
        st.markdown(f"### Осталось кейсов: {case_num - 1}")
        cases.pop(ind)
