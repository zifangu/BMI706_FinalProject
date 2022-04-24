from turtle import width
import streamlit as st
import altair as alt
import pandas as pd
import numpy as np
import os

# https://github.com/streamlit/demo-self-driving


data_root = "https://raw.githubusercontent.com/qzhang21/BMI706_FinalProject/main/Data/"
data_dict = {"Activity": "dailyActivity_merged.csv",
            "Calories": "dailyCalories_merged.csv",
            "Steps": "dailySteps_merged.csv",
            "Sleep": "sleepDay_merged.csv",
            "Intensities": "dailyIntensities_merged.csv"}
# call example: data_root + data_dict["Activity"]

def instruction_call():
    st.write("Welcome. This product is made possible by April Yan, Ivan Gu, Marie Zhang, and Yuanchen Wang.")

    st.sidebar.success("Choose any visualization to view content.")
    return

def run_vis_1():
    # year = st.slider('Select Year', min(df['Year']), max(df['Year']), 2008)
    activity = st.selectbox('Select Activity',["Calories", "Intensities", "Choice 3"])



    # subset = subset[subset["Cancer"] == cancer]
    # TODO: Sleep time column is sleepDay, not ActivityDay. Need to conditional merge.
    category = st.selectbox('Select Categories',["Steps", "Sleep", "Choice 3"])
    
    # daily_calories = pd.read_csv("https://raw.githubusercontent.com/qzhang21/BMI706_FinalProject/main/Data/dailyCalories_merged.csv")
    # daily_steps = pd.read_csv("https://raw.githubusercontent.com/qzhang21/BMI706_FinalProject/main/Data/dailySteps_merged.csv")

    # read in the two files required for the plot
    daily_activity = pd.read_csv(data_root + data_dict[activity])
    category_var = pd.read_csv(data_root + data_dict[category])

    if activity == "Intensities":
        var = st.selectbox(f"Variables in {activity}", ["TotalMinutesAsleep", "TotalTimeInBed"])
        
    # merge files
    test_df = daily_activity.merge(category_var, on=["Id", "ActivityDay"]) # merge files

    # split the quantiles
    quantile_df = test_df.quantile(q=[.25, 0.50, 0.75], axis = 0)
    q1 = float(quantile_df.iloc[0, [-1]])
    q2 = float(quantile_df.iloc[1, [-1]])
    q3 = float(quantile_df.iloc[2, [-1]])
    # second plot, also plot Q1,2,3,4. This is to show how many days do individuals are within the quantiles
    index_q1 = np.where(test_df.iloc[:, [-1]] < q1)[0] # gets the index of the df matching the condition. [0] to get the index
    index_q2 = np.where((test_df.iloc[:, [-1]] >= q1) & (test_df.iloc[:, [-1]] < q2))[0]
    index_q3 = np.where((test_df.iloc[:, [-1]] >= q2) & (test_df.iloc[:, [-1]] < q3))[0]
    index_q4 = np.where(test_df.iloc[:, [-1]] >= q3)[0]

    # assign quantiles
    test_df['Quantile'] = None
    test_df.loc[index_q1, 'Quantile'] = "Q1"
    test_df.loc[index_q2, 'Quantile'] = "Q2"
    test_df.loc[index_q3, 'Quantile'] = "Q3"
    test_df.loc[index_q4, 'Quantile'] = "Q4"

    # axis_dictionary = dict()
    # axis_dictionary['activity'] = "Calories"
    y_axis_val = test_df[activity]


    selection = alt.selection_multi(fields=['Quantile'], bind='legend')


    chart = alt.Chart(test_df).transform_density(
        activity,
        as_=[activity, 'density'],
        extent=[min(y_axis_val), max(y_axis_val)],
        groupby=['Quantile']
    ).mark_area(orient='horizontal').encode(
        y=alt.Y(activity, type="quantitative"),
        color='Quantile:N',
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
        x=alt.X(
            'density:Q',
            stack='center',
            impute=None,
            title=None,
            axis=alt.Axis(labels=False, values=[0],grid=False, ticks=True),
        ),
        tooltip=['density:Q'],
        column=alt.Column(
            'Quantile:N',
            header=alt.Header(
                titleOrient='bottom',
                labelOrient='bottom',
                labelPadding=0,
            ),
        )
    ).add_selection(
        selection
    ).properties(
        width=100
    ).configure_facet(
        spacing=0
    ).configure_view(
        stroke=None
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

    participant = st.multiselect("Select Participants", np.array(np.unique(df["Id"]), dtype='str'))

    scatter = alt.Chart(df).mark_line().encode(
        x=alt.X(lapse_name),
        y=alt.Y(var),
        color=alt.Color("Id", type="nominal", legend=alt.Legend(columns=4)),
        tooltip=[lapse_name, var],
        opacity = alt.value(0.2)
    ).properties(
        title=f"{var} by Time",
        width=800
    )

    avg = alt.Chart(df).mark_line(color="gray").encode(
        x=alt.X(lapse_name),
        y=alt.Y(f"mean({var})")
    ).properties(
        width=800
    )

    scatter + avg

    return

def run_vis_3():
    processed_data_dir = "ProcessedData"
    data_dir = "Data"
    df = pd.read_csv(os.path.join(processed_data_dir,"dailyActivity_weight_merged.csv"),index_col=0)
    df = date_lapse(df)

    data_level = st.selectbox("Select Level of Data",["Within Individual","Between Individuals"])
    if data_level == "Within Individual":
        x_vars = list(df.columns).remove('Id')
    elif data_level == "Between Individuals":
        x_vars = list(df.columns).remove('Id')
    
    x_var = st.selectbox("Select X variable",x_vars)

    y_vars = df.columns.remove(x_var)

    y_var = st.selectbox("Select Y variable",y_vars)
    
    st.write(type(df.columns))

    
    return

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