import pandas as pd
import altair as alt
import streamlit as st

# Load the data
df = pd.read_csv("/Users/drakoriz/Documents/RATPDEV_AL-ULA/passenger_RATPdev_alula.csv", sep=';')

data = df.copy()
data['vehicle'] = data['vehicle'].str.extract(r'\((\d+)\)')
data['date2'] = pd.to_datetime(data['server_ts'], unit='s')
data['heure_renseignee'] = data['trip_formatted_name'].str.extract(r'(\d{2}:\d{2})')
# Title for the passenger evolution graph
st.title("Passenger Evolution Over Time")

# Group by date and vehicle to get the total number of passengers per day and per vehicle
passengers_over_time = data.groupby(['date2', 'vehicle', 'route_id', 'day_of_week'])['boarding'].sum().reset_index()

# Extract available vehicles, routes, and days of the week from the data
available_vehicles = passengers_over_time['vehicle'].unique()
available_routes = passengers_over_time['route_id'].unique()
available_days_of_week = passengers_over_time['day_of_week'].unique()

# Add a vehicle selector (dropdown), restricted to available vehicles
selected_vehicle = st.selectbox(
    "Select a vehicle to filter data",
    options=['All Vehicles'] + list(available_vehicles),  # 'All Vehicles' option to show all vehicles
    index=0  # Default to 'All Vehicles'
)

# Add a route selector (dropdown), restricted to available routes
selected_route = st.selectbox(
    "Select a route to filter data",
    options=['All Routes'] + list(available_routes),  # 'All Routes' option to show all routes
    index=0  # Default to 'All Routes'
)

# Add a day of week selector (dropdown), restricted to available days of the week
selected_day_of_week = st.selectbox(
    "Select a day of the week to filter data",
    options=['All Days'] + list(available_days_of_week),  # 'All Days' option to show all days
    index=0  # Default to 'All Days'
)

# Filter data based on the selected vehicle
if selected_vehicle != 'All Vehicles':
    filtered_data_by_vehicle = passengers_over_time[passengers_over_time['vehicle'] == selected_vehicle]
else:
    filtered_data_by_vehicle = passengers_over_time

# Filter data based on the selected route
if selected_route != 'All Routes':
    filtered_data_by_route = filtered_data_by_vehicle[filtered_data_by_vehicle['route_id'] == selected_route]
else:
    filtered_data_by_route = filtered_data_by_vehicle

# Filter data based on the selected day of week
if selected_day_of_week != 'All Days':
    filtered_data_by_day = filtered_data_by_route[filtered_data_by_route['day_of_week'] == selected_day_of_week]
else:
    filtered_data_by_day = filtered_data_by_route

# Extract available dates based on the filtered data
available_dates = filtered_data_by_day['date2'].dt.date.unique()

# Add a date selector only if there are available dates for the selected vehicle and route
if available_dates.size > 0:
    selected_date = st.date_input(
        "Select a date to filter data",
        value=None,
        min_value=min(available_dates),
        max_value=max(available_dates),
        key="date_input"
    )
else:
    selected_date = None  # No date selected if no available dates

# Add a reset button to return to the global view
reset_filter = st.button("Monthly View")

# If the user selects a date and the reset button is not clicked
if selected_date and not reset_filter:
    # Filter for the selected date
    filtered_data = filtered_data_by_day[filtered_data_by_day['date2'].dt.date == selected_date]

    if not filtered_data.empty:
        # Display the time on the x-axis when a single day is selected
        filtered_data['time'] = filtered_data['date2'].dt.strftime('%H:%M')
        
        # Use Altair to create a bar chart filtered for the selected date, vehicle, route, and day
        chart = alt.Chart(filtered_data).mark_bar(color='orange').encode(
            x=alt.X('date2:T', title='Hour', axis=alt.Axis(format='%H:%M')),  # Display hours on the X-axis
            y=alt.Y('boarding:Q', title='Number of Passengers'),  # Change Y-axis label
            tooltip=['time', 'boarding']  # Add tooltip to display values
        ).properties(
            title=f'Number of passengers for {selected_vehicle} on {selected_date} for route {selected_route} ({selected_day_of_week})'
        )
        # Display the chart for the selected date, vehicle, route, and day
        st.altair_chart(chart, use_container_width=True)
    else:
        # If no data is available for the selected date, vehicle, route, and day
        st.write("No data available for the selected date, vehicle, route, and day.")
else:
    # If no date is selected or the reset button is clicked, display the global bar chart
    chart = alt.Chart(filtered_data_by_day).mark_bar().encode(
        x=alt.X('date2:T', title='Date', axis=alt.Axis(format='%Y-%m-%d')),  # Change X-axis label to date
        y=alt.Y('boarding:Q', title='Number of Passengers'),  # Change Y-axis label
        tooltip=['date2', 'boarding']  # Add tooltip to display values
    ).properties(
        title='Total Number of Passengers Over Time'
    )
    
    # Display the global chart
    st.altair_chart(chart, use_container_width=True)

