import dash
from dash import dcc, html, dash_table, Input, Output
import plotly.graph_objs as go
import pandas as pd
from API_weather_2 import get_weather_dataframe
from apscheduler.schedulers.background import BackgroundScheduler
import time

# Initialize the weather data globally
df = get_weather_dataframe()

# Weather data auto-update function
def update_weather_data():
    global df
    try:
        df = get_weather_dataframe()
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Weather data updated.")
    except Exception as e:
        print(f"Failed to update weather data: {e}")

# Start the background scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(update_weather_data, 'interval', hours=6)  # Refresh every 6 hours
scheduler.start()

# Weather icon mapping
weather_icons = {
    0: "https://www.weatherbit.io/static/img/icons/c01d.png",
    1: "https://www.weatherbit.io/static/img/icons/c02d.png",
    2: "https://www.weatherbit.io/static/img/icons/c03d.png",
    3: "https://www.weatherbit.io/static/img/icons/c04d.png",
    45: "https://www.weatherbit.io/static/img/icons/a05d.png",
    48: "https://www.weatherbit.io/static/img/icons/a05d.png",
    51: "https://www.weatherbit.io/static/img/icons/d01d.png",
    53: "https://www.weatherbit.io/static/img/icons/d02d.png",
    55: "https://www.weatherbit.io/static/img/icons/d03d.png",
    61: "https://www.weatherbit.io/static/img/icons/r01d.png",
    63: "https://www.weatherbit.io/static/img/icons/r02d.png",
    65: "https://www.weatherbit.io/static/img/icons/r03d.png",
    71: "https://www.weatherbit.io/static/img/icons/s01d.png",
    73: "https://www.weatherbit.io/static/img/icons/s02d.png",
    75: "https://www.weatherbit.io/static/img/icons/s03d.png",
    80: "https://www.weatherbit.io/static/img/icons/r04d.png",
    81: "https://www.weatherbit.io/static/img/icons/r05d.png",
    82: "https://www.weatherbit.io/static/img/icons/r06d.png",
    95: "https://www.weatherbit.io/static/img/icons/t04d.png",
}

app = dash.Dash(__name__)
app.title = "London Weather Dashboard"
app.layout = html.Div([
    html.H1("London Weather Forecast", style={"textAlign": "center"}),

    dcc.DatePickerRange(
        id='date-picker',
        min_date_allowed=df['date'].min(),
        max_date_allowed=df['date'].max(),
        start_date=df['date'].min(),
        end_date=df['date'].max()
    ),

    html.Div([
        html.Div(
            "⚠️ Maximum date range within the next 15 days from today.",
            style={
                "color": "#856404",
                "backgroundColor": "#fff3cd",
                "padding": "8px",
                "borderRadius": "6px",
                "textAlign": "center",
                "fontSize": "14px",
                "border": "1px solid #ffeeba",
                "display": "inline-block",
                "width": "fit-content"
            }
        )
    ], style={"marginTop": "8px"}),

    html.Br(),

    html.Div(id='highlight-card', style={
        'textAlign': 'center', 'padding': '20px', 'margin': '20px auto',
        'maxWidth': '500px', 'border': '2px solid #ccc', 'borderRadius': '12px',
        'backgroundColor': '#e6f7ff', 'boxShadow': '0 4px 8px rgba(0,0,0,0.1)'
    }),

    html.Br(), html.Br(),

    html.Div(id='weather-icons'),

    html.Br(),

    dash_table.DataTable(
        id='weather-table',
        columns=[
            {"name": "Date", "id": "date"},
            {"name": "Weather", "id": "weather_desc"},
            {"name": "Precipitation Probability (%)", "id": "precipitation_probability_max"},
            {"name": "Precipitation (mm)", "id": "precipitation_sum"},
            {"name": "Min Temp (°C)", "id": "temperature_2m_min"},
            {"name": "Max Temp (°C)", "id": "temperature_2m_max"},
            {"name": "Wind Speed (km/h)", "id": "wind_speed_10m_mean"},
        ],
        data=[],
        style_table={'overflowX': 'auto'},
        style_cell={'textAlign': 'center'},
        style_header={'backgroundColor': 'lightgrey', 'fontWeight': 'bold'},
    ),

    html.Br(),

    dcc.Graph(id='temp-graph'),
    dcc.Graph(id='precip-graph'),
    dcc.Graph(id='wind-graph')
])


@app.callback(
    [Output('highlight-card', 'children'),
     Output('weather-table', 'data'),
     Output('temp-graph', 'figure'),
     Output('precip-graph', 'figure'),
     Output('wind-graph', 'figure'),
     Output('weather-icons', 'children')],
    [Input('date-picker', 'start_date'),
     Input('date-picker', 'end_date')]
)
def update_output(start_date, end_date):
    filtered_df = df[(df["date"] >= pd.to_datetime(start_date).date()) &
                     (df["date"] <= pd.to_datetime(end_date).date())]

    fig_temp = go.Figure()
    fig_temp.add_trace(go.Scatter(
        x=filtered_df["date"], y=filtered_df["temperature_2m_min"],
        name='Min Temp (°C)', mode='lines+markers', line=dict(color='blue')
    ))
    fig_temp.add_trace(go.Scatter(
        x=filtered_df["date"], y=filtered_df["temperature_2m_max"],
        name='Max Temp (°C)', mode='lines+markers', line=dict(color='red')
    ))
    fig_temp.update_layout(
        title="Daily Temperatures",
        xaxis_title="Date", yaxis_title="Temperature (°C)", template="plotly_white"
    )

    fig_precip = go.Figure()
    fig_precip.add_trace(go.Bar(
        x=filtered_df["date"], y=filtered_df["precipitation_probability_max"],
        name="Precipitation Probability (%)", marker_color="skyblue", yaxis='y'
    ))
    fig_precip.add_trace(go.Scatter(
        x=filtered_df["date"], y=filtered_df["precipitation_sum"],
        name="Precipitation Amount (mm)", mode='lines+markers',
        line=dict(color='royalblue', dash='dash'), yaxis='y2'
    ))
    fig_precip.update_layout(
        title="Precipitation Overview",
        xaxis_title="Date",
        yaxis=dict(title="Probability (%)", side='left'),
        yaxis2=dict(title="Precipitation (mm)", overlaying='y', side='right'),
        template="plotly_white",
        legend=dict(x=0.01, y=1.1, orientation="h")
    )

    fig_wind = go.Figure()
    fig_wind.add_trace(go.Scatter(
        x=filtered_df["date"], y=filtered_df["wind_speed_10m_mean"],
        name='Wind Speed (km/h)', mode='lines+markers', line=dict(color='green')
    ))
    fig_wind.update_layout(
        title="Wind Speed (10m Mean)",
        xaxis_title="Date", yaxis_title="Wind Speed (km/h)", template="plotly_white"
    )

    icon_row = html.Div([
        html.Div([
            html.Img(src=weather_icons.get(code, ""), style={'height': '50px'}),
            html.Div(date.strftime("%b %d"), style={'textAlign': 'center', 'fontSize': '12px'})
        ], style={'display': 'inline-block', 'margin': '10px'})
        for code, date in zip(filtered_df["weather_code"], filtered_df["date"])
    ], style={'textAlign': 'center'})

    if not filtered_df.empty:
        rainiest_day = filtered_df.loc[filtered_df['precipitation_probability_max'].idxmax()]
        highlight_card = html.Div([
            html.H3("🌧️ Rain Alert: Highest Chance", style={'color': '#005580'}),
            html.P(f"Date: {rainiest_day['date'].strftime('%A, %b %d')}"),
            html.P(f"Probability: {rainiest_day['precipitation_probability_max']}%"),
            html.P(f"Weather: {rainiest_day['weather_desc']}"),
            html.Img(src=weather_icons.get(rainiest_day['weather_code'], ""), style={'height': '60px'})
        ])
    else:
        highlight_card = html.Div()

    return highlight_card, filtered_df.to_dict("records"), fig_temp, fig_precip, fig_wind, icon_row


if __name__ == '__main__':
    app.run(debug=True)
