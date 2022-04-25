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
    activity = st.selectbox('Select Activity',["Calories", "Steps", "Sleep"])
    # subset = subset[subset["Cancer"] == cancer]

    category = st.selectbox('Select Categories',["Steps", "Sleep Time", "Choice 3"])
    
    #daily_calories = pd.read_csv("https://raw.githubusercontent.com/qzhang21/BMI706_FinalProject/main/Data/dailyCalories_merged.csv")
    #daily_steps = pd.read_csv("https://raw.githubusercontent.com/qzhang21/BMI706_FinalProject/main/Data/dailySteps_merged.csv")
    daily_activity = pd.read_csv(data_root + data_dict[activity])
    category_var = pd.read_csv(data_root + data_dict[category])
    test_df = daily_activity.merge(category_var, on=["Id", "ActivityDay"]) # merge files

    # split the quantiles
    quantile_df = test_df.quantile(q=[0, .25, 0.50, 0.75, 1], axis = 0)
    q1 = float(quantile_df.iloc[1, [-1]])
    q2 = float(quantile_df.iloc[2, [-1]])
    q3 = float(quantile_df.iloc[3, [-1]])
    min_cat = float(quantile_df.iloc[0, [-1]])
    max_cat = float(quantile_df.iloc[4, [-1]])
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

    selection = alt.selection_single(fields=['Quantile'], bind='legend')
    base = alt.Chart(test_df).transform_filter(selection)

    chart = base.transform_density(
        activity,
        as_=[activity, 'density'],
        extent=[min(y_axis_val), max(y_axis_val)],
        groupby=['Quantile']
    ).mark_area(orient='horizontal').encode(
        y='Calories:Q',
        color=alt.condition(selection, 'Quantile:N', alt.value("lightgray")),
        tooltip = ['Calories'],
        x=alt.X(
            'density:Q',
            stack='center',
            impute=None,
            title=None,
            axis=alt.Axis(labels=False, values=[0],grid=False, title=" ")
        ),
        column=alt.Column(
            'Quantile:N',
            header=alt.Header(labels=False, title=None)
            )
        ).properties(
        width=125,
        height=300
    ).add_selection(selection)

    #st.write(selection)
    #subset = test_df[test_df["Quantile"] == selection]

    selection_id = alt.selection_multi(fields=['Id'],bind='legend')
    chart2 = base.mark_line(strokeWidth=1).encode(
        x = alt.X('ActivityDay'),
        y = alt.Y(activity),
        color = alt.condition(selection_id, 'Id:N', alt.value('lightgray')),
        opacity=alt.condition(selection_id, alt.value(1.0), alt.value(0.2)),
        tooltip = ['ActivityDay',activity]
    ).properties(
        #title=f"{cancer} mortality rates for {'males' if sex == 'M' else 'females'} in {year}",
        width = 500,
        height = 400
    ).add_selection(selection).add_selection(selection_id)

    #st.write(category + " selected!")

    chart3 = alt.vconcat(chart, chart2
    ).resolve_scale(
        color='independent'
    ).configure_facet(
        spacing=0
    ).configure_view(
        stroke=None
    )
    
    # #st.altair_chart(chart, use_container_width=True)
    st.write("Steps Quantile")
    st.write("min:",min_cat,"25%:",q1,"50%:",q2,"75%:",q3,"max:",max_cat)
    st.altair_chart(chart3, use_container_width=True)

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