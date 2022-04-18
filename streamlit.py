import streamlit as st
import altair as alt
import pandas as pd
import numpy as np

# https://github.com/streamlit/demo-self-driving


def instruction_call():
    st.write("Welcome. This product is made possible by April Yan, Ivan Gu, Marie Zhang, and Yuanchen Wang.")

    st.sidebar.success("Choose any visualization to view content.")
    return

def run_vis_1():
    # year = st.slider('Select Year', min(df['Year']), max(df['Year']), 2008)
    activity = st.selectbox('Select Activity',["Calorie", "Choice 2", "Choice 3"])
    # subset = subset[subset["Cancer"] == cancer]

    category = st.selectbox('Select Categories',["Steps", "Sleep Time", "Choice 3"])

    st.write(category + " selected!")
    return

def main():
    st.sidebar.title("BMI 706 Final Project")
    vis_mode = st.sidebar.selectbox("Choose mode and visualization",
        ["Show Instructions", "Activities vs. Category", "Show the source code"])
    if vis_mode == "Show Instructions":
        instruction_call()
    elif vis_mode == "Activities vs. Category":
        run_vis_1()


if __name__ == "__main__":
    main()