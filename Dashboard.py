# Import necessary libraries
import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import requests
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv  # Library to load environment variables from a .env file
from datetime import datetime, timezone  # Libraries for datetime manipulation

# Load environment variables from a .env file
load_dotenv()

# Initialize the Dash app
app = dash.Dash(__name__)

# Define color scheme for the app
colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

# Define font settings for the app
fonts = {
    'font': 'sans-serif'
}

# Define the layout of the app
app.layout = html.Div(
    style={'backgroundColor': colors['background'], 'fontFamily': fonts['font']},
    children=[
        # Geolocation component to get the user's location
        dcc.Geolocation(id='geolocation'),
        # Header for the dashboard
        html.H1(
            children='Echtzeit Wetterdaten Dashboard',
            style={'color': colors['text']}
        ),
        # Interval component to update the data every 10 minutes
        dcc.Interval(
            id='interval-component',
            interval=10*60*1000,  # in milliseconds
            n_intervals=0
        ),
        # Graph component to display the temperature data
        dcc.Graph(id='live-update-temp')
    ]
)

# Function to convert Unix timestamp to datetime
def unix_to_hours(unix_timestamp):
    dt = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    return dt

# Callback to update the graph with live data
@app.callback(
    Output('live-update-temp', 'figure'),  # Output component to update the figure
    Output('geolocation', 'update_now'),  # Output component to update the geolocation
    Input('interval-component', 'n_intervals'),  # Input component to trigger the update
    Input('geolocation', 'position')  # Input component to get the position
)
def update_graph_live(n, position):
    # Debug print statement to check the position
    print(f"Geolocation position: {position}")

    # Check if the position is valid
    if position is None or 'lat' not in position or 'lon' not in position:
        return dash.no_update, dash.no_update

    # Get the API key from environment variables
    api_key = os.getenv('API_KEY')
    latitude = position['lat']
    longitude = position['lon']
    location = f'{latitude},{longitude}'
    units = 'units=ca'
    url = f'https://api.pirateweather.net/forecast/{api_key}/{location}?&{units}'
    
    # Request weather data from the API
    response = requests.get(url)
    data = response.json()

    # Convert Unix timestamps to datetime objects
    for hour_data in data['hourly']['data']:
        unix_time = hour_data['time']
        hour_data['datetime'] = unix_to_hours(unix_time)

    # Create a DataFrame from the hourly data
    hourly_data = data['hourly']['data']
    df = pd.DataFrame(hourly_data)

    # Create a line plot for temperature
    fig_temp = px.line(df, x='datetime', y='temperature', title='Temperatur')

    # Update the layout of the plot
    fig_temp.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
    )

    return fig_temp, dash.no_update

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True)