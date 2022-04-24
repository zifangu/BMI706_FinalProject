import streamlit as st
import altair as alt
import pandas as pd
import numpy as np

# https://github.com/streamlit/demo-self-driving

# def data_init():
#     # read in csv
#     daily_calories = pd.read_csv("https://raw.githubusercontent.com/qzhang21/BMI706_FinalProject/main/dailyCalories_merged.csv")
#     daily_steps = pd.read_csv("https://raw.githubusercontent.com/qzhang21/BMI706_FinalProject/main/dailySteps_merged.csv")

data_root = "https://raw.githubusercontent.com/qzhang21/BMI706_FinalProject/main/Data/"
data_dict = {"Activity": "dailyActivity_merged.csv",
            "Calories": "dailyCalories_merged.csv",
            "Steps": "dailySteps_merged.csv",
            "Sleep": "sleepDay_merged.csv"}
# call example: data_root + data_dict["Activity"]

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
    lapse_name="lapse"
    date_names=["ActivityDay", "SleepDay", "ActivityDate", "Date"]

    df_name = st.selectbox("Select Variable",["Calories", "Steps", "Sleep"])
    # var = st.selectbox("Select Variable", list(data_dict.keys()))
    if df_name == "Calories":
        var = "Calories"
    elif df_name == "Steps":
        var = "StepTotal"
    elif df_name == "Sleep":
        var = st.selectbox(f"Variables in {df_name}", ["TotalMinutesAsleep", "TotalTimeInBed"])

    df = pd.read_csv(data_root + data_dict[df_name])
    df = date_lapse(df, date_names=date_names, lapse_name=lapse_name)

    chart = alt.Chart(df).mark_line().encode(
        x=alt.X(lapse_name),
        y=alt.Y(var),
        color=alt.Color("Id", type="nominal"),
        tooltip=[lapse_name, var],
    ).properties(
        title="hi",
    )

    chart

    return

def run_vis_3():


def date_lapse(df, date_names=["ActivityDay", "SleepDay", "ActivityDate", "Date"], lapse_name="lapse"):
    # return a df with a new column called "lapse" (or as specified)
    name = np.array(df.columns)[[i in date_names for i in df.columns]][0]
    df[name] = pd.to_datetime(df[name])
    start_dates = {}
    for id, frame in df.sort_values(by=name).groupby("Id"):
        start_dates[id] = frame.iloc[0][name]
    df[lapse_name] = [(row[name] - start_dates[row["Id"]]).days  for _, row in df.iterrows()]
    return df

def main():
    st.sidebar.title("BMI 706 Final Project")
    vis_mode = st.sidebar.selectbox("Choose mode and visualization",
        ["Show Instructions",
        "Activities vs. Category",
        "Activities vs. Time",
        "Correlations",
        "Show the source code"])

    # initialize data
    # data_init()

    if vis_mode == "Show Instructions":
        instruction_call()
    elif vis_mode == "Activities vs. Category":
        run_vis_1()
    elif vis_mode == "Activities vs. Time":
        run_vis_2()
    elif vis_mode == "Correlations":
        run_vis_3()


if __name__ == "__main__":
    main()