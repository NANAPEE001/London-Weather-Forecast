
import openmeteo_requests
import pandas as pd
import requests
import requests_cache
from retry_requests import retry
 
 
 
def get_weather_dataframe():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 51.5072,  # London
        "longitude": -0.1276,
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum", 
            "precipitation_probability_max",
            "wind_speed_10m_mean"
        ],
        "timezone": "Europe/London",
        "forecast_days": 16
    }
 
    response = requests.get(url, params=params)
    data = response.json()
 
    daily_data = {
        "date": pd.to_datetime(data["daily"]["time"]),
        "weather_code": data["daily"]["weather_code"],
        "temperature_2m_max": data["daily"]["temperature_2m_max"],
        "temperature_2m_min": data["daily"]["temperature_2m_min"],
        "precipitation_sum": data["daily"]["precipitation_sum"],  # ✅ Added here
        "precipitation_probability_max": data["daily"]["precipitation_probability_max"],
        "wind_speed_10m_mean": data["daily"]["wind_speed_10m_mean"]
    }
 
    daily_dataframe = pd.DataFrame(data=daily_data)
    daily_dataframe["date"] = daily_dataframe["date"].dt.date  # Optional: simplify datetime
 
    # Decode weather codes
    weather_code_map = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
        55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow", 80: "Rain showers",
        81: "Moderate showers", 82: "Violent showers", 95: "Thunderstorm"
    }
    daily_dataframe["weather_desc"] = daily_dataframe["weather_code"].map(weather_code_map)
 
    # Save to CSV 
    daily_dataframe.to_csv("london_weather.csv", index=False)
 
    return daily_dataframe