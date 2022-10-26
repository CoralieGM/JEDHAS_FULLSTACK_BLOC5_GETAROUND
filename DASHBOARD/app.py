import streamlit as st
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import openpyxl
import io

# CONFIG
st.set_page_config(
    page_title="GetAround Dashboard",
    page_icon=" 🕚 🚗 🕦",
    layout="wide"
)

### TITLE AND TEXT
st.title("GetAround Dashboard")
st.markdown("👋 Hello there! Welcome to this simple GetAround dashboard app. GetAround is the Airbnb for cars. You can rent cars from any person for a few hours to a few days! Founded in 2009, this company has known rapid growth. In 2019, they count over 5 million users and about 20K available cars worldwide.")



# Use `st.cache` when loading data is extremly useful
# because it will cache your data so that your app 
# won't have to reload it each time you refresh your app
@st.cache(allow_output_mutation=True)
def load_data():
    df = pd.read_excel("./get_around_delay_analysis.xlsx")
    return df

# Load the data
data_loading_status = st.text('Loading data...')
data = load_data()
data_loading_status.text('data_loaded ✔️')


# Data exploration with some informations about the dataset
st.subheader("Data discovery")

# Look the data
nrows_data = st.slider('Select number of rows you want to see', min_value=1, max_value=200) # Getting the input.
data_rows = data.head(nrows_data) # Filtering the dataframe.
st.dataframe(data_rows) # Displaying the dataframe.


# Present the dataset
columns=" "
for column in data.columns:
    columns=columns+" "+str(column)+", "
st.markdown(f"""
    The dataset represent {len(data)} rental records.\n
    The columns are: {columns}""")

# infos
st.subheader("Data Types and missing values")
buffer = io.StringIO()
data.info(buf=buffer)
s = buffer.getvalue()
st.text(s)

# add a column checkout status
data['checkout_status']=["Late" if x>0 else "in_time" for x in data.delay_at_checkout_in_minutes]

# delete rows with NaN in delay_at_checkout_in_minutes for state 'ended'
data2 = data[(data['state'] == 'canceled') | data['delay_at_checkout_in_minutes'].notna()]

# delete outliers in delay_at_checkout_in_minutes
MINUTES_MAX = 1440 # maximum one day of late, rest are outliers
data2 = data2.drop(data2[data2.delay_at_checkout_in_minutes>MINUTES_MAX].index)

# Late checkouts proportions
st.subheader('Proportion of late checkouts')
fig = px.pie(data2, names='checkout_status',hole=0.33)
st.plotly_chart(fig)


# Delay at checkout repartition visualization
st.subheader('Repartition of late')
data2_with_late=data2[data2.delay_at_checkout_in_minutes>0]
fig = px.box(data2_with_late, x="delay_at_checkout_in_minutes")
fig.update_layout()
st.plotly_chart(fig, use_container_width=True)
    

# Delay at checkout repartition visualization
st.subheader('Repartition of time delta with previous rental')
fig = px.box(data, x="time_delta_with_previous_rental_in_minutes")
fig.update_layout()
st.plotly_chart(fig, use_container_width=True)


#### Create two columns
col1, col2 = st.columns(2)

with col1 : 
    #Distribution of state in dataset 
    st.subheader("Proportion of state's rentals")
    fig = px.pie(data,names='state',hole=0.33)
    st.plotly_chart(fig)

with col2 :
    #Distribution of checking type in dataset 
    st.subheader("Proportion of chekin type's rentals")
    fig = px.pie(data,names='checkin_type',hole=0.33)
    st.plotly_chart(fig)

col3, col4 = st.columns(2)
with col3 :
    mask3 = data2["state"] =="ended"
    st.subheader("Proportion of checkout status where state is ended")
    fig = px.pie(data2[mask3],names="checkout_status",hole=0.33)
    st.plotly_chart(fig)

with col4 :
    mask = data["checkout_status"] =="Late"
    st.subheader("Proportion of checkin_type's where checkout status is late")
    fig = px.pie(data[mask], names="checkin_type",hole=0.33)
    st.plotly_chart(fig)



# Consecutive rentals
st.subheader("CONSECUTIVE RENTALS")
st.markdown("Now let's look at the impact of the delay on the following rentals and how to avoid it")

# Get one dataset with 
consecutive_rental_data = pd.merge(data2, data2, how='inner', left_on = 'previous_ended_rental_id', right_on = 'rental_id')

# Remove unless columns and rows with missing previous rental delay values
consecutive_rental_data.drop(
    [
        "rental_id_y", 
        "car_id_y", 
        "state_y",
        "time_delta_with_previous_rental_in_minutes_y",
        "previous_ended_rental_id_y",
    ], 
    axis=1,
    inplace=True
)



# Look the data
nrows_data2 = st.slider('Select number of rows you want to see for this new dataset', min_value=1, max_value=200) # Getting the input.
data_rows2 = consecutive_rental_data.head(nrows_data2) # Filtering the dataframe.
st.dataframe(data_rows2) # Displaying the dataframe.


# Count the number of consecutive rentals cases
st.markdown(f"""
    Let's have a look to the consecutive rentals to understand the impact of delays on next users.
 
    The total number of usable cases is: **{len(consecutive_rental_data)}**
""")


# Impacted users with previous delay
col5, col6 = st.columns(2)

with col5:
    # The late for x when y is late
    st.subheader('Proportion of checkout in late for previous rentals with lated checkout')
    mask2 = consecutive_rental_data["checkout_status_x"]=="Late"
    consecutive_rental_data_with_late_x = consecutive_rental_data[mask2]
    fig = px.pie(consecutive_rental_data_with_late_x, names='checkout_status_y',hole=0.33)
    st.plotly_chart(fig)


with col6 :
    # Delayed Checkin
    consecutive_rental_data['delayed_checkin_in_minutes']=[
    consecutive_rental_data.time_delta_with_previous_rental_in_minutes_x[i]- consecutive_rental_data.delay_at_checkout_in_minutes_y[i] for i in range(len(consecutive_rental_data))
    ]
    mask4 = consecutive_rental_data["delayed_checkin_in_minutes"]<0
    st.subheader('Proportion of canceled rentals for delayed checkin')
    fig = px.pie(consecutive_rental_data[mask4] ,names='state_x',hole=0.33)
    st.plotly_chart(fig)


cancellation_df=consecutive_rental_data[(consecutive_rental_data["delayed_checkin_in_minutes"]<0) & (consecutive_rental_data["state_x"]=="canceled")]
impacted_df= consecutive_rental_data[consecutive_rental_data.delayed_checkin_in_minutes<0]

st.markdown(f"""
    The number of checkins impacted by previous delays is:  **{len(impacted_df)}** and {round((len(impacted_df)/len(consecutive_rental_data))*100,2)} % of consecutives rentals\n
    The number of potential cancellations due to delays is:  **{len(cancellation_df)}** and {round((len(cancellation_df)/len(impacted_df))*100,2)}% of impacted checkins\n
    """)


st.subheader('Proportion of delayed checkin by state')
fig = px.histogram(impacted_df,x="delayed_checkin_in_minutes", histnorm='probability density', nbins= 60, color="state_x",title='DELAYED CHECKIN')
st.plotly_chart(fig)


impacted_df_ended = impacted_df[impacted_df.state_x=='ended']
impacted_df_canceled = impacted_df[impacted_df.state_x=='canceled']

st.subheader('Distribition of delayed checkin in minute when the rental is ended')
fig = px.box(impacted_df_ended, x="delayed_checkin_in_minutes")
fig.update_layout()
st.plotly_chart(fig, use_container_width=True)

st.subheader('Distribition of delayed checkin in minute when the rental is canceled')
fig = px.box(impacted_df_canceled, x="delayed_checkin_in_minutes")
fig.update_layout()
st.plotly_chart(fig, use_container_width=True)

st.markdown(f"""
    Median of delayed checkin when the rental is ended :  **21 minutes** \n
    Median of delayed checkin when the rental is canceled :  **61.5 minutes** \n
    Median of checkout late late is : **51.5 minutes** and rarely above : **284 minutes**\n
    Median of time delta is : **180 minutes**\n
    My recommendation is to have a **time delta between 222 and 263 minutes**, an increase from 43 to 83 minutes\n
    """)