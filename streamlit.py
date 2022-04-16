import streamlit as st
import altair as alt
import pandas as pd
import numpy as np

def main():
    st.sidebar.title("BMI 706 Final Project")
    vis_mode = st.sidebar.selectbox("Choose mode and visualization",
        ["Instructions", "Visualization 1", "Show the source code"])
    if vis_mode == "Show instructions":
        st.sidebar.success("Choose any visualization to view content.")
    elif vis_mode == "Visualization 1":
        run_vis_1()

def run_vis_1():

    return


if __name__ == "__main__":
    main()