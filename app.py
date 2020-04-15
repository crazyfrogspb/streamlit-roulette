import time
from typing import Dict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import nltk
import numpy as np
import streamlit as st
from PIL import Image
from streamlit import caching

from utils import fancy_cache, select_block_container_style, SessionState


# np.random.seed(24)


def display_case(case):
    sentences = nltk.sent_tokenize(case)
    question = f"**{sentences[-1]}**"
    case_md = "## " + " ".join(sentences[:-1]) + " " + question

    return case_md


@fancy_cache(unique_to_session=True, allow_output_mutation=True)
def get_static_store() -> Dict:
    """This dictionary is initialized once and can be used to store the files uploaded"""
    return {}


select_block_container_style()

nltk.download("punkt")

st.title("Рулетка кейсов")

state = SessionState.get(cases=[], played_inds=[], orig_case_num=0, file_value=None)

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


def read_cases(file_value, force=False):
    if not state.cases or force or file_value != state.file_value:
        cases = static_store[file_value].splitlines()
        state.cases = [case for case in cases if case]
        state.orig_case_num = len(state.cases)
        state.played_inds = []
        state.file_value = file_value


def get_colors(orig_case_num, current_ind):
    colors = ["lightgrey"] * orig_case_num
    if state.played_inds:
        for ind in state.played_inds:
            colors[ind] = "dimgray"
    if current_ind is not None:
        colors[current_ind] = "indianred"

    return colors


def plot_wheel(played_inds=None, current_ind=None):
    size = 360 / state.orig_case_num
    sizes = [size] * state.orig_case_num
    labels = [i for i in range(1, state.orig_case_num + 1)]
    colors = get_colors(state.orig_case_num, current_ind)
    fig1, ax1 = plt.subplots(figsize=(3, 3))
    ax1.axis("equal")
    wedges, texts = ax1.pie(sizes, labels=labels, rotatelabels=True, startangle=0, colors=colors, counterclock=False)
    centre_circle = plt.Circle((0, 0), 0.5, color="white", fc="white", linewidth=1)
    ax1.add_artist(centre_circle)
    img = Image.open("podlodka3.png")
    basewidth = 120
    wpercent = basewidth / float(img.size[0])
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    width, height = img.size[0], img.size[1]
    fig1.figimage(img, fig1.bbox.xmax - width // 2, fig1.bbox.ymax - height // 2)
    for w in wedges:
        w.set_linewidth(2)
        w.set_edgecolor("white")
    wheel.pyplot(fig1, clear_figure=False)
    plt.close(fig1)

    return wedges, fig1


if file_buffer is not None:
    read_cases(file_buffer.getvalue())
else:
    state.cases = None
    state.played_inds = []
    state.orig_case_num = 0
    st.info("Загрузите хотя бы один файл")

reload_button = st.empty()
selection_button = st.button("Выбрать кейс")
wheel = st.empty()
case_placeholder = st.empty()
if reload_button.button("Рестарт"):
    if file_buffer:
        read_cases(file_buffer.getvalue(), force=True)
        wedges, fig1 = plot_wheel(played_inds=state.played_inds)

if menu_state == "Скрыть":
    file_picker.empty()
    reload_button.empty()


if state.cases:
    wedges, fig1 = plot_wheel(played_inds=state.played_inds)
    if state.played_inds:
        case_placeholder.markdown(display_case(state.cases[state.played_inds[-1]]))

if selection_button:
    if len(state.played_inds) == state.orig_case_num:
        case_placeholder.markdown("## Кейсы закончились!")
    else:
        case_placeholder.empty()
        case_num = len(state.cases)
        rand_choice = np.random.randint(state.orig_case_num * 3, state.orig_case_num * 5)
        ind = 0
        for i in range(rand_choice):
            if ind >= state.orig_case_num:
                ind = 0
            while ind in state.played_inds:
                ind += 1
                if ind >= state.orig_case_num:
                    ind = 0
            colors = get_colors(state.orig_case_num, ind)
            for w_num, w in enumerate(wedges):
                w.set_color(colors[w_num])
                w.set_linewidth(2)
                w.set_edgecolor("white")
            wheel.pyplot(fig1, clear_figure=False)
            time.sleep(min(0.1, 0.005 + 0.0025 * i))
            ind += 1
            if len(state.played_inds) == state.orig_case_num - 1:
                break
        state.played_inds.append(ind - 1)
        case_placeholder.markdown(display_case(state.cases[ind - 1]))
        st.markdown(f"### Осталось кейсов: {state.orig_case_num - len(state.played_inds)}")
