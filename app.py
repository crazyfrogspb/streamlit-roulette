import hashlib
import io
import os
import random
import time
from typing import Dict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nltk
import numpy as np
import streamlit as st
from streamlit import caching

from utils import get_session_id, select_block_container_style


# np.random.seed(24)
user_session_id = get_session_id()


def display_case(case):
    sentences = nltk.sent_tokenize(case)
    question = f"**{sentences[-1]}**"
    case_md = "## " + " ".join(sentences[:-1]) + " " + question

    return case_md


@st.cache(allow_output_mutation=True)
def get_static_store(user_session_id) -> Dict:
    """This dictionary is initialized once and can be used to store the files uploaded"""
    return {}


select_block_container_style()

nltk.download("punkt")

st.title("Рулетка кейсов")

menu_state = st.radio("Показать меню", ["Показать", "Скрыть"], 0)
static_store = get_static_store(user_session_id)

file_picker = st.empty()
file_buffer = file_picker.file_uploader("Загрузите файл с кейсами", type="txt")

if file_buffer:
    value = file_buffer.getvalue()
    if value not in static_store.values():
        static_store[file_buffer.getvalue()] = value
else:
    static_store.clear()


@st.cache(allow_output_mutation=True)
def read_cases(file_value, user_session_id):
    cases = static_store[file_value].splitlines()
    cases = [case for case in cases if case]
    orig_case_num = len(cases)
    return cases, orig_case_num, []


if file_buffer is not None:
    cases, orig_case_num, played_inds = read_cases(file_buffer.getvalue(), user_session_id)
else:
    cases = None
    played_inds = []
    orig_case_num = 0
    st.info("Загрузите хотя бы один файл")

reload_button = st.empty()
selection_button = st.button("Выбрать кейс")
wheel = st.pyplot(label=user_session_id)
case_placeholder = st.empty()
if reload_button.button("Перезагрузить файлы"):
    caching.clear_cache()
    static_store.clear()
    played_inds = []
    wheel.empty()

if menu_state == "Скрыть":
    file_picker.empty()
    reload_button.empty()


def get_colors(orig_case_num, current_ind):
    colors = ["lightgrey"] * orig_case_num
    if current_ind is not None:
        colors[current_ind] = "indianred"
    if played_inds:
        for ind in played_inds:
            colors[ind] = "dimgray"

    return colors


def plot_wheel(played_inds=None, current_ind=None):
    size = 360 / orig_case_num
    sizes = [size] * orig_case_num
    labels = [i for i in range(1, orig_case_num + 1)]
    colors = get_colors(orig_case_num, current_ind)
    fig1, ax1 = plt.subplots()
    wedges, texts = ax1.pie(sizes, labels=labels, rotatelabels=True, startangle=0, colors=colors, counterclock=False)
    for w in wedges:
        w.set_linewidth(2)
        w.set_edgecolor("white")
    while True:
        try:
            wheel.pyplot(fig1)
            break
        except IndexError:
            pass

    plt.close(fig1)

    return wedges


if cases:
    wedges = plot_wheel(played_inds=played_inds)
    if played_inds:
        case_placeholder.markdown(display_case(cases[played_inds[-1]]))

if selection_button:
    if len(played_inds) == orig_case_num:
        case_placeholder.markdown("## Кейсы закончились!")
    else:
        case_num = len(cases)
        rand_choice = np.random.randint(orig_case_num * 3, orig_case_num * 5)
        ind = 0
        for i in range(rand_choice):
            while ind in played_inds:
                ind += 1
                if ind >= orig_case_num:
                    ind = 0
            if ind >= orig_case_num:
                ind = 0
            plot_wheel(orig_case_num, ind)
            time.sleep(i * 0.002)
            ind += 1
            if len(played_inds) == orig_case_num - 1:
                break
        played_inds.append(ind - 1)
        case_placeholder.markdown(display_case(cases[ind - 1]))
        st.markdown(f"### Осталось кейсов: {orig_case_num - len(played_inds)}")
