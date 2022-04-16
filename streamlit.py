import streamlit as st
import altair as alt
import pandas as pd
import numpy as np

def main():
    st.sidebar.title("What to do")
    app_mode = st.sidebar.selectbox("Choose the app mode",
        ["Instructions", "Run the app", "Show the source code"])




if __name__ == "__main__":
    main()