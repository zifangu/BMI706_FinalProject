import os
os.system('pip install scipy altair numpy pandas')

# from turtle import color, width
from scipy import stats
# from pyparsing import oneOf
import streamlit as st
import altair as alt
import pandas as pd
import numpy as np


# https://github.com/streamlit/demo-self-driving


data_root = "https://raw.githubusercontent.com/qzhang21/BMI706_FinalProject/main/Data/"
data_dict = {"Activity": "dailyActivity_merged.csv",
            "Calories": "dailyCalories_merged.csv",
            "Steps": "dailySteps_merged.csv",
            "Sleep": "sleepDay_merged.csv",
            "Intensities": "dailyIntensities_merged.csv",
            "Weight": "weightLogInfo_merged.csv"}
# call example: data_root + data_dict["Activity"]


def instruction_call():
    st.write("# Welcome!")
    st.write("*Apr. 24th, 2022*")
    st.write("This product is made possible by April Yan, Ivan Gu, Marie Zhang, and Yuanchen Wang.")
    st.write("Select any visualization in the drop-down list on the sidebar to view content.")
    st.sidebar.success("Choose any visualization to view content.")
    return


def run_vis_1():
    # year = st.slider('Select Year', min(df['Year']), max(df['Year']), 2008)
    st.sidebar.success("This module is used to visualize temporal trend of selected activities (e.g., calories, sedentary time) of a chosen categories (e.g., steps, sleep time).")
    st.sidebar.success("The initial example shows four quantiles of daily steps of all participants. Click a single quantile, below shows the participants with steps falling in that quantile.")
    st.sidebar.success("Click legend of the plot below to select multiple participants. You can observe the total calories comsumption at the days when participants have steps within speficic quantile.")
    activity = st.selectbox('Select Activity',["Calories", "Intensities"])
    var = activity

    # read in the a file required for the plot
    daily_activity = pd.read_csv(data_root + data_dict[activity])
    daily_activity = date_lapse(daily_activity, date_names=['ActivityDay'])
    daily_activity = daily_activity.drop(columns=['lapse'])

    if activity == "Intensities":
        var = st.selectbox(f"Variables in {activity}", daily_activity.columns.to_list()[2:])
        daily_activity = daily_activity[['Id', 'ActivityDay', var]]


    # subset = subset[subset["Cancer"] == cancer]
    # TODO: Sleep time column is sleepDay, not ActivityDay. Need to conditional merge.
    category = st.selectbox('Select Categories',["Steps", "Sleep"])
    category_var = pd.read_csv(data_root + data_dict[category])


    if category == "Sleep":
        var_cat = st.selectbox(f"Variables in {category}", category_var.columns.to_list()[3:])
        category_var = date_lapse(category_var, date_names=['SleepDay'])
        category_var = category_var.rename(columns={'SleepDay': 'ActivityDay'})
        #category_var = category_var.drop(columns=['lapse', 'TotalSleepRecords'])
        category_var = category_var[['Id', 'ActivityDay', 'lapse', var_cat]]
    else:
        var_cat = "StepTotal"
        category_var = date_lapse(category_var, date_names=['ActivityDay'])
        #category_var = category_var.drop(columns=['lapse'])
        category_var = category_var[['Id', 'ActivityDay','lapse', var_cat]]
    
    # daily_calories = pd.read_csv("https://raw.githubusercontent.com/qzhang21/BMI706_FinalProject/main/Data/dailyCalories_merged.csv")
    # daily_steps = pd.read_csv("https://raw.githubusercontent.com/qzhang21/BMI706_FinalProject/main/Data/dailySteps_merged.csv")
 
    # merge files
    test_df = daily_activity.merge(
        category_var, on=["Id", "ActivityDay"])  # merge files


    # split the quantiles
    quantile_df = test_df.quantile(q=[0, .25, 0.50, 0.75, 1], axis = 0)
    q1 = float(quantile_df.iloc[1, [-1]])
    q2 = float(quantile_df.iloc[2, [-1]])
    q3 = float(quantile_df.iloc[3, [-1]])
    min_cat = float(quantile_df.iloc[0, [-1]])
    max_cat = float(quantile_df.iloc[4, [-1]])
    # second plot, also plot Q1,2,3,4. This is to show how many days do individuals are within the quantiles
    # gets the index of the df matching the condition. [0] to get the index
    index_q1 = np.where(test_df.iloc[:, [-1]] < q1)[0]
    index_q2 = np.where(
        (test_df.iloc[:, [-1]] >= q1) & (test_df.iloc[:, [-1]] < q2))[0]
    index_q3 = np.where(
        (test_df.iloc[:, [-1]] >= q2) & (test_df.iloc[:, [-1]] < q3))[0]
    index_q4 = np.where(test_df.iloc[:, [-1]] >= q3)[0]

    # assign quantiles
    test_df['Quantile'] = None
    test_df.loc[index_q1, 'Quantile'] = "Q1"
    test_df.loc[index_q2, 'Quantile'] = "Q2"
    test_df.loc[index_q3, 'Quantile'] = "Q3"
    test_df.loc[index_q4, 'Quantile'] = "Q4"

    # # special case for non-intensities
    # if activity != "Intensities": var = activity
    # axis_dictionary = dict()
    # axis_dictionary['activity'] = "Calories"
    y_axis_val = test_df[var]

    # selection = alt.selection_multi(fields=['Quantile'], bind='legend')
    # st.write(test_df)
    # y_axis_val = test_df[activity]

    selection = alt.selection_single(fields=['Quantile'])
    base = alt.Chart(test_df).transform_filter(selection)

    chart = alt.Chart(test_df).transform_density(
        var,
        as_=[var, 'density'],
        extent=[min(y_axis_val), max(y_axis_val)],
        groupby=['Quantile']
    ).mark_area(orient='horizontal').encode(
        y=alt.Y(var, type="quantitative"),
        color=alt.condition(selection, 'Quantile:N', alt.value("lightgray")),
        tooltip = [var],
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2)),
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
    chart2 = base.mark_point().encode(
        x = alt.X('lapse',axis=alt.Axis(title="Time (Day)")),
        y = alt.Y(var, type="quantitative", scale=alt.Scale(domain=[min(test_df[var]),max(test_df[var])])),
        color = alt.condition(selection_id, 'Id:N', alt.value('lightgray')),
        opacity=alt.condition(selection_id, alt.value(1.0), alt.value(0.2)),
        tooltip = ['ActivityDay',var,'Quantile']
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
    st.write(f"{var_cat} Quantile")
    st.write("min:",min_cat,"25%:",q1,"50%:",q2,"75%:",q3,"max:",max_cat)
    st.write("Click the quantile in the violin plot to select range/quantile of interest")
    st.altair_chart(chart3, use_container_width=True)
    st.write("Click the legend in the scatter plot to select participants of interest")

    return


def run_vis_2(): # wyc
    # time vs variables
    st.sidebar.success("Daily mean values over all participants of the variable selected.")

    # st.write("## Variables vs. Time (Day)")

    lapse_name = "lapse"
    date_names = ["ActivityDay", "SleepDay", "ActivityDate", "Date"]

    df_name = st.selectbox("Select Variable", [
                           "Calories", "Steps", "Sleep", "Weight"])
    # var = st.selectbox("Select Variable", list(data_dict.keys()))
    if df_name == "Calories":
        var = "Calories"
    elif df_name == "Steps":
        var = "StepTotal"
    elif df_name == "Sleep":
        var = st.selectbox(f"Variables in {df_name}", [
                           "TotalMinutesAsleep", "TotalTimeInBed"])
    elif df_name == "Weight":
        var = st.selectbox(f"Variables in {df_name}", [
                           "WeightKg", "WeightPounds", "BMI"])

    df = pd.read_csv(data_root + data_dict[df_name])
    df = date_lapse(df, date_names=date_names, lapse_name=lapse_name)

    df_sum = df.groupby(by=lapse_name).mean().reset_index()
    df_sum["sd"] = df.groupby(by=lapse_name).std().reset_index()[var]
    df_sum["lower"] = [row[var]-row["sd"] for _, row in df_sum.iterrows()]
    df_sum["upper"] = [row[var]+row["sd"] for _, row in df_sum.iterrows()]

    uniqueId = np.unique(df["Id"])
    participants = st.multiselect("Select Participants", uniqueId)
    df["selected"] = [True if row["Id"]
                      in participants else False for _, row in df.iterrows()]

    color = alt.Color('Id:N', legend=None,
                      scale=alt.Scale(scheme='category10'))

    indiv = alt.Chart(df).mark_line(strokeDash=[5, 4]).encode(
        x=alt.X(lapse_name, axis=alt.Axis(title="Time (Day)")),
        y=alt.Y(var, axis=alt.Axis(title=f"{var}")),
        color=color,
        # tooltip=[lapse_name, var],
        opacity=alt.condition(alt.datum.selected,
                              alt.value(0.8), alt.value(0.2)),
        # tooltip=alt.condition(alt.datum.selected, ["Id:N", f"{var}:N"], [])
        # not supported by altair
    ).properties(
        title=f"{var} by Time",
        width=500
    )

    avg = alt.Chart(df_sum).mark_line().encode(
        x=alt.X(lapse_name),
        y=alt.Y(var),
        color=alt.value('gray'),
        tooltip=[alt.Tooltip(f"{lapse_name}:O", title="Time (Day)"), 
        alt.Tooltip(f"{var}:Q", title="Average Calories", format=",.2f"),
        alt.Tooltip("sd:Q", title="Standard Deviation", format=",.2f"),
        alt.Tooltip("lower:Q", title="Lower Bound", format=",.2f"),
        alt.Tooltip("upper:Q", title="Upper Bound", format=",.2f")]
    ).properties(
        width=500
    )

    band = alt.Chart(df_sum).mark_area().encode(
        x=alt.X(lapse_name),
        y='lower',
        y2='upper',
        color=alt.value('lightgray'),
        opacity=alt.value(0.2)
    ).properties(
        width=500
    )


    legend = alt.Chart(df[df["selected"] == True]).mark_point(filled=True, size=200).encode(
        y=alt.Y('Id:N', axis=alt.Axis(
            orient='right', title="Selected Participant(s)")),
        color=color
    ).properties(
        title="",
        width=20
    )
    plot = (indiv + band + avg) 

    if len(participants) != 0:
        selected = alt.Chart(df[df["selected"] == True]).mark_line(point=True).encode(
            x=alt.X(lapse_name, axis=alt.Axis(title="Time (Day)")),
            y=alt.Y(var, axis=alt.Axis(title=f"{var}")),
            color=color,
            opacity=alt.value(0.8),
            tooltip=[alt.Tooltip("Id:N", title="Participant ID"),
                alt.Tooltip(f"{lapse_name}:O", title="Time (Day)"), 
                alt.Tooltip(f"{var}:Q", title="Calories")]
        ).properties(
        title=f"{var} by Time: Selected Participant(s) only",
        width=500
        )
        plot = ((indiv + band + avg) | legend) & selected
    
    plot

    st.write(f"Total number of participants with current variable `{var}`: {len(uniqueId)}")
    st.write(f"Number of participant(s) selected: {len(participants)}")
    st.write(" ")
    st.write("**Note:**")
    st.write("*Gray solid line:* total average of all participants;")
    st.write("*Light gray area:* one standard deviation of the average.")
    return


def run_vis_3():
    processed_data_dir = "ProcessedData"
    #data_dir = "Data"
    df = pd.read_csv(os.path.join(processed_data_dir,"dailyActivity_weight_merged.csv"),index_col=0)
    df_btwn = pd.read_csv(os.path.join(processed_data_dir,"indiv_dailyActivity_weight_merged.csv"),index_col=0)

    distance_vars = ["TotalSteps",
        "TotalDistance",
        "TrackerDistance",
        "LoggedActivitiesDistance",
        "VeryActiveDistance",
        "ModeratelyActiveDistance",
        "LightActiveDistance",
        "SedentaryActiveDistance"]
    
    time_vars = ["VeryActiveMinutes",
        "FairlyActiveMinutes",
        "LightlyActiveMinutes",
        "SedentaryMinutes"]

    y_vars_between = ["Calories",
        "BMI",
        "WeightKg"]
    y_var_within = "Calories"

    individuals = st.multiselect(label="Select individuals",
        options=df['Id'].unique())
    df_within = df[df['Id'].isin(individuals)]
    
    distance_var = st.selectbox(label="Select distance variable",
        options=distance_vars,
        index=0)
    y_var_between = st.selectbox(label="Select Y variable for comparison between individuals",
        options=y_vars_between,
        index=0)
    
    st.write("Note:")
    st.write("There is only one option (calories) for the y-variable for selected individuals since each individual only has one BMI or weight value.")
    st.write("")
    w = 300
    # plots for distance
    # if len(individuals) > 0:
    #     st.write(list(df_btwn.index) in list(set(individuals).intersection(set(df_btwn.index))))
    # determine y axis limits
    y_min_btwn = min(df_btwn[y_var_between])
    y_max_btwn = max(df_btwn[y_var_between])
    if len(individuals) > 0:
        y_min_wthn = min(df_within[y_var_within])
        y_max_wthn = max(df_within[y_var_within])
        #coloration = alt.condition("df_btwn.index in individuals",alt.ColorValue("green"),alt.ColorValue("blue"))
    else:
        y_min_wthn = min(df_btwn[y_var_within])
        y_max_wthn = max(df_btwn[y_var_within])
    
    coloration="green"

    if y_var_between == y_var_within:
        y_min_btwn = min(y_min_btwn,y_min_wthn)
        y_min_wthn = y_min_btwn
        y_max_btwn = max(y_max_btwn,y_max_wthn)
        y_max_wthn = y_max_btwn
    scatter_btwn_dist = alt.Chart(df_btwn).mark_point(
        color=coloration#"green"#alt.condition("df_btwn.Id in individuals",alt.ColorValue("green"),alt.ColorValue("blue"))
    ).encode(
        x=alt.X(distance_var),
        y=alt.Y(y_var_between,scale=alt.Scale(domain=(y_min_btwn,y_max_btwn)))
    ).properties(
        title=f"{y_var_between} vs. {distance_var} (Between Individuals)",
        width=w
    )
    reg_btwn_dist = scatter_btwn_dist.transform_regression(distance_var,y_var_between).mark_line(
        color="red"#,scale=alt.Scale(domain=(y_min_btwn,y_max_btwn))
    )

    scatter_wthn_dist = alt.Chart(df_within).mark_point().encode(
        x=alt.X(distance_var),
        y=alt.Y(y_var_within,scale=alt.Scale(domain=(y_min_wthn,y_max_wthn)))
    ).properties(
        title=f"{y_var_within} vs. {distance_var} (Selected Individual(s))",
        width=w
    )
    reg_wthn_dist = scatter_wthn_dist.transform_regression(distance_var,y_var_within).mark_line(
        color="red"#,scale=alt.Scale(domain=(y_min_wthn,y_max_wthn))
    )
    disp_plot_dist = scatter_btwn_dist + reg_btwn_dist | scatter_wthn_dist + reg_wthn_dist

    disp_plot_dist

    s1,i1,r1,p1,se1 = stats.linregress(x=df_btwn[distance_var],y=df_btwn[y_var_between])
    st.write(f"**{y_var_between} vs. {distance_var} (Between Individuals)**")
    st.write(f"slope={s1:.2E}, intercept={i1:.2E}, R-squared={r1**2:.2f}, p-val={p1:.2E}, SE={se1:.2E}")
    if len(individuals) > 0:
        st.write(f"**{y_var_within} vs. {distance_var} (Selected Individual(s))**")
        s2,i2,r2,p2,se2 = stats.linregress(x=df_within[distance_var],y=df_within[y_var_within])
        st.write(f"slope={s2:.2E}, intercept={i2:.2E}, R-squared={r2**2:.2f}, p-val={p2:.2E}, SE={se1:.2E}")

    st.write("="*100)
    time_var = st.selectbox(label="Select time variable",
        options=time_vars,
        index=0)

    # plots for time

    scatter_btwn_time = alt.Chart(df_btwn).mark_point(
        color=coloration#"green"
    ).encode(
        x=alt.X(time_var),
        y=alt.Y(y_var_between,scale=alt.Scale(domain=(y_min_btwn,y_max_btwn)))
    ).properties(
        title=f"{y_var_between} vs. {time_var} (Between Individuals)",
        width=w
    )
    reg_btwn_time = scatter_btwn_time.transform_regression(time_var,y_var_between).mark_line(
        color="red"#,scale=alt.Scale(domain=(y_min_btwn,y_max_btwn))
    )
    scatter_wthn_time = alt.Chart(df_within).mark_point().encode(
        x=alt.X(time_var),
        y=alt.Y(y_var_within,scale=alt.Scale(domain=(y_min_wthn,y_max_wthn)))
    ).properties(
        title=f"{y_var_within} vs. {time_var} (Selected Individual(s))",
        width=w
    )
    reg_wthn_time = scatter_wthn_time.transform_regression(time_var,y_var_within).mark_line(
        color="red"#,scale=alt.Scale(domain=(y_min_wthn,y_max_wthn))
    )
    disp_plot_time = scatter_btwn_time + reg_btwn_time | scatter_wthn_time + reg_wthn_time

    disp_plot_time
    s3,i3,r3,p3,se3 = stats.linregress(x=df_btwn[time_var],y=df_btwn[y_var_between])
    st.write(f"**{y_var_between} vs. {time_var} (Between Individuals)**")
    st.write(f"slope={s3:.2E}, intercept={i3:.2E}, R-squared={r3**2:.2f}, p-val={p3:.2E}, SE={se3:.2E}")
    if len(individuals) > 0:
        st.write(f"**{y_var_within} vs. {time_var} (Selected Individual(s))**")
        s4,i4,r4,p4,se4 = stats.linregress(x=df_within[time_var],y=df_within[y_var_within])
        st.write(f"slope={s4:.2E}, intercept={i4:.2E}, R-squared={r4**2:.2f}, p-val={p4:.2E}, SE={se4:.2E}")
    # final_plot = alt.vconcat(disp_plot_dist, disp_plot_time)
    # final_plot

    st.markdown("""
    <style>
    .big-font {
        font-size:30px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    st.markdown('<p class="big-font">MORE NOTES:</p>', unsafe_allow_html=True)
    st.write("In the between individuals plots, each individual is a data point." + 
    "\n\n"+"In the selected individual(s) plot, each time point for each individual is a data point.")
    return


def date_lapse(df, date_names=["ActivityDay", "SleepDay", "ActivityDate", "Date"], lapse_name="lapse"):
    # return a df with a new column called "lapse" (or as specified)
    name = np.array(df.columns)[[i in date_names for i in df.columns]][0]
    df[name] = pd.to_datetime(df[name])
    start_dates = {}
    for id, frame in df.sort_values(by=name).groupby("Id"):
        start_dates[id] = frame.iloc[0][name]
    df[lapse_name] = [(row[name] - start_dates[row["Id"]]
                       ).days for _, row in df.iterrows()]
    return df


def main():
    st.sidebar.title("BMI 706 Final Project")
    vis_mode = st.sidebar.selectbox("Choose mode and visualization",
                                    ["Show Instructions",
                                     "Activities vs. Category",
                                     "Variables vs. Time",
                                     "Correlations"])

    # initialize data
    # data_init()

    if vis_mode == "Show Instructions":
        instruction_call()
    elif vis_mode == "Activities vs. Category":
        run_vis_1()
    elif vis_mode == "Variables vs. Time":
        run_vis_2()
    elif vis_mode == "Correlations":
        run_vis_3()


if __name__ == "__main__":
    main()
