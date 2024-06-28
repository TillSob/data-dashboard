import dash
from dash import dcc, html
from dash.dependencies import Output, Input
import requests
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Echtzeit Wetterdaten Dashboard'),
    dcc.Interval(
        id='interval-component',
        interval=10*60*1000,  # in milliseconds
        n_intervals=0
    ),
    dcc.Graph(id='live-update-graph'),
    dcc.Graph(id='live-update-temp')
])

def unix_to_hours(unix_timestamp):
    dt = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    return dt

@app.callback(
    [Output('live-update-graph', 'figure'),
     Output('live-update-temp', 'figure')],
    [Input('interval-component', 'n_intervals')]
)


def update_graph_live(n):
    api_key = os.getenv('API_KEY')
    location = '52.52,13.4049'
    units = 'units=ca'
    url = f'https://api.pirateweather.net/forecast/{api_key}/{location}?&{units}'
    response = requests.get(url)
    data = response.json()

    for hour_data in data['hourly']['data']:
        unix_time = hour_data['time']
        hour_data['datetime'] = unix_to_hours(unix_time)

        
    hourly_data = data['hourly']['data']
    df = pd.DataFrame(hourly_data)
    
    fig_precip = px.line(df, x='datetime', y='precipIntensity', title='Niederschlagsintensität')
    fig_temp = px.line(df, x='datetime', y='temperature', title='Temperatur')

    return [fig_precip, fig_temp]

if __name__ == '__main__':
    app.run_server(debug=True)