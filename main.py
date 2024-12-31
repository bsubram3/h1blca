import streamlit as st
import pandas as pd
import numpy as np


@st.cache_resource
def load_data():
    lca_df = pd.read_csv("LCA_Disclosure_Data_FY2024.csv")
    return lca_df


lca_filtered_df = load_data()


# Conversion function
def convert_to_yearly(row):
    if row['WAGE_UNIT_OF_PAY'] != 'Year' and row['WAGE_RATE_OF_PAY_FROM'] > 15000:
        return row['WAGE_RATE_OF_PAY_FROM']
    elif row['PW_UNIT_OF_PAY'] == 'Year' and row['WAGE_RATE_OF_PAY_FROM'] > 200000:
        return row['WAGE_RATE_OF_PAY_FROM']
    elif row['WAGE_UNIT_OF_PAY'] == 'Week' and row['WAGE_RATE_OF_PAY_FROM'] < 10000:
        return row['WAGE_RATE_OF_PAY_FROM'] * 52  # 52 weeks in a year
    elif row['WAGE_UNIT_OF_PAY'] == 'Week' and row['WAGE_RATE_OF_PAY_FROM'] > 10000:
        if row['PW_UNIT_OF_PAY'] == 'Week':
            return row['WAGE_RATE_OF_PAY_FROM'] * 52  # 52 weeks in a year
        elif row['PW_UNIT_OF_PAY'] == 'Month':
            return row['WAGE_RATE_OF_PAY_FROM'] * 12  # 52 weeks in a year
    elif row['WAGE_UNIT_OF_PAY'] == 'Bi-Weekly':
        return row['WAGE_RATE_OF_PAY_FROM'] * 26  # 52 weeks in a year
    elif row['WAGE_UNIT_OF_PAY'] == 'Hour' and row['WAGE_RATE_OF_PAY_FROM'] < 1000:
        return row['WAGE_RATE_OF_PAY_FROM'] * 40 * 52  # assuming 40 hours/week
    elif row['WAGE_UNIT_OF_PAY'] == 'Hour' and row['WAGE_RATE_OF_PAY_FROM'] > 1000:
        if row['PW_UNIT_OF_PAY'] == 'Week':
            return row['WAGE_RATE_OF_PAY_FROM'] * 52  # 52 weeks in a year
        elif row['PW_UNIT_OF_PAY'] == 'Month':
            return row['WAGE_RATE_OF_PAY_FROM'] * 12  # 52 weeks in a year
    elif row['WAGE_UNIT_OF_PAY'] == 'Month':
        return row['WAGE_RATE_OF_PAY_FROM'] * 12
    elif row['WAGE_UNIT_OF_PAY'] == 'Year':
        return row['WAGE_RATE_OF_PAY_FROM']
    else:
        return None  # or some default value if unit is unknown


lca_filtered_df['WAGE'] = lca_filtered_df.apply(convert_to_yearly, axis=1)

lca_filtered_df['DATE'] = pd.to_datetime(lca_filtered_df['RECEIVED_DATE'])
lca_filtered_df['YEAR'] = lca_filtered_df['DATE'].dt.year
year_options = np.sort(lca_filtered_df['YEAR'].unique())[::-1]
state_options = lca_filtered_df['WORKSITE_STATE'].unique()
employer_options = lca_filtered_df['EMPLOYER_NAME'].unique()
city_options = lca_filtered_df['WORKSITE_CITY'].unique()

st.title("H1B Salary Data")

job_titles = None
visa_class = None
min_salary = None
max_salary = None
do_search = False

with st.form("my_form", border=False):
    col1, col2, col3, col4 = st.columns([4, 3, 2, 2])
    with col1:
        employer_name = st.selectbox("Employer Name", employer_options, placeholder='Select', index=None)
    with col2:
        city = st.selectbox("City", city_options, placeholder='Select', index=None)
    with col3:
        state = st.selectbox('State', state_options, placeholder='Select', index=None)
    with col4:
        year = st.selectbox('Year', year_options, placeholder='Select', index=1)

    min_val, max_val = lca_filtered_df['WAGE'].min(), lca_filtered_df['WAGE'].max()

    job_title_options = lca_filtered_df['SOC_TITLE'].unique()
    visa_class_options = lca_filtered_df['VISA_CLASS'].unique()
    col1, col2, col3, col4, col5 = st.columns((3, 1, 3, 5, 7), vertical_alignment='center')
    with col1:
        min_salary = float(st.text_input("Min Salary", min_val))
    with col2:
        st.text('-')
    with col3:
        max_salary = float(st.text_input("Max Salary", max_val))
    with col4:
        visa_class = st.multiselect('Visa Class', visa_class_options, placeholder='Select')
    with col5:
        job_titles = st.multiselect('Job Title', job_title_options, placeholder='Select')

    if st.form_submit_button('Search', type="primary"):
        do_search = True

if do_search:
    if year:
        lca_filtered_df = lca_filtered_df[lca_filtered_df['YEAR'] == year]
    if state:
        lca_filtered_df = lca_filtered_df[lca_filtered_df['WORKSITE_STATE'] == state]
    if employer_name:
        lca_filtered_df = lca_filtered_df[lca_filtered_df['EMPLOYER_NAME'].fillna(False).str.contains(employer_name, case=False)]
    if city:
        city_mask = (lca_filtered_df['WORKSITE_CITY'].str.contains(city, case=False)) & lca_filtered_df['WORKSITE_CITY'].notna()
        lca_filtered_df = lca_filtered_df[city_mask]
    if job_titles:
        lca_filtered_df = lca_filtered_df[lca_filtered_df['SOC_TITLE'].isin(job_titles)]
    if visa_class:
        lca_filtered_df = lca_filtered_df[lca_filtered_df['VISA_CLASS'].isin(visa_class)]
    if min_salary:
        lca_filtered_df = lca_filtered_df[lca_filtered_df['WAGE'] >= min_salary]
    if max_salary:
        lca_filtered_df = lca_filtered_df[lca_filtered_df['WAGE'] <= max_salary]

    lca_filtered_display_df = lca_filtered_df[['CASE_NUMBER', 'EMPLOYER_NAME', 'JOB_TITLE',
                                               'WORKSITE_CITY', 'WORKSITE_STATE', 'WAGE', 'RECEIVED_DATE',
                                               'SOC_TITLE', 'VISA_CLASS', 'CASE_STATUS']]

    result_size = len(lca_filtered_display_df)
    if result_size > 0:
        st.write(f"Showing {result_size} results:")
        df_without_index = lca_filtered_display_df.reset_index(drop=True)
        st.dataframe(df_without_index)
    else:
        st.write("No result found")
