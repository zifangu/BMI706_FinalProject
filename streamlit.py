import streamlit as st
import altair as alt
import pandas as pd
import numpy as np

# https://github.com/streamlit/demo-self-driving

# def data_init():
#     # read in csv
#     daily_calories = pd.read_csv("https://raw.githubusercontent.com/qzhang21/BMI706_FinalProject/main/dailyCalories_merged.csv")
#     daily_steps = pd.read_csv("https://raw.githubusercontent.com/qzhang21/BMI706_FinalProject/main/dailySteps_merged.csv")


def instruction_call():
    st.write("Welcome. This product is made possible by April Yan, Ivan Gu, Marie Zhang, and Yuanchen Wang.")

    st.sidebar.success("Choose any visualization to view content.")
    return

def run_vis_1():
    # year = st.slider('Select Year', min(df['Year']), max(df['Year']), 2008)
    activity = st.selectbox('Select Activity',["Calories", "Choice 2", "Choice 3"])
    # subset = subset[subset["Cancer"] == cancer]

    category = st.selectbox('Select Categories',["Steps", "Sleep Time", "Choice 3"])
    
    daily_calories = pd.read_csv("https://raw.githubusercontent.com/qzhang21/BMI706_FinalProject/main/Data/dailyCalories_merged.csv")
    daily_steps = pd.read_csv("https://raw.githubusercontent.com/qzhang21/BMI706_FinalProject/main/Data/dailySteps_merged.csv")

    test_df = daily_calories.merge(daily_steps, on=["Id", "ActivityDay"]) # merge files



    chart = alt.Chart(test_df).mark_circle().encode(
        x=alt.X("StepTotal"),
        y=alt.Y('Calories'),
        color=alt.Color("Id", type="nominal"),
        tooltip=["StepTotal", "Calories" ],
    ).properties(
        title="hi",
    )

    chart

    st.write(category + " selected!")
    return

def run_vis_2():
    # time vs variables
    return

def main():
    st.sidebar.title("BMI 706 Final Project")
    vis_mode = st.sidebar.selectbox("Choose mode and visualization",
        ["Show Instructions", "Activities vs. Category", "Show the source code"])

    # initialize data
    # data_init()

    if vis_mode == "Show Instructions":
        instruction_call()
    elif vis_mode == "Activities vs. Category":
        run_vis_1()
    elif vis_mode == "Activities vs. Time":
        run_vis_2()


if __name__ == "__main__":
    main()