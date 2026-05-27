#!/usr/bin/python
import json
import requests
import datetime
from dateutil import parser
import sys

# Find the weather forecast API endpoint for the given coordinates
def get_forecast_endpoint(latitude, longitude):
    # Set the headers to identify the application
    headers = {
        'User-Agent': 'my-weather-app',
        'Accept': 'application/geo+json'
    }

    # Make a request to the points API to get the forecast endpoint
    points_url = f"https://api.weather.gov/points/{latitude},{longitude}"
    response = requests.get(points_url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        # Get the forecast URL from the response
        forecast_url = data['properties']['forecast']
        return forecast_url
    else:
        # If the request was not successful, return None
        return None

# Get the weather forecast for the given endpoint
def get_weather_forecast(forecast_url):
    # Set the headers to identify the application
    headers = {
        'User-Agent': 'my-weather-app',
        'Accept': 'application/geo+json'
    }

    # Make a request to the forecast endpoint
    response = requests.get(forecast_url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Return the JSON response
        return response.json()
    else:
        # If the request was not successful, return None
        return None

# Filter the weather forecast to a 24-hour period
def filter_forecast_to_24_hours(forecast_data):
    if not forecast_data or 'properties' not in forecast_data or 'periods' not in forecast_data['properties']:
        return None

    periods = forecast_data['properties']['periods']
    if not periods:
        return None

    # Get the start time of the first period
    start_time_str = periods[0].get('startTime')
    if not start_time_str:
        return None

    start_time = parser.isoparse(start_time_str)
    
    # Calculate the end time (24 hours after the start time)
    end_time = start_time + datetime.timedelta(hours=24)

    # Filter the periods
    filtered_periods = [p for p in periods if parser.isoparse(p.get('startTime')) < end_time]

    # Create a new forecast data object with the filtered periods
    filtered_forecast = forecast_data.copy()
    filtered_forecast['properties']['periods'] = filtered_periods
    
    return filtered_forecast

# Print the usage of the script
def print_usage():
    print("Usage: python nws_api.py [ --raw ]")
    print("  --raw: Print the raw JSON output")

# Print the weather forecast in a human-readable format
def print_human_readable_forecast(forecast_data, long=False):
    if not forecast_data or 'properties' not in forecast_data or 'periods' not in forecast_data['properties']:
        print("No forecast data available.")
        return

    periods = forecast_data['properties']['periods']
    if not periods:
        print("No forecast periods available.")
        return

#    print(f"\t\tTemperature:\tWind:\tForecast:")
    degree='°'
    if not long:
        for period in periods:
            print(f"{period['name']}\t{period['temperature']}{degree}{period['temperatureUnit']} wind {period['windSpeed']} {period['windDirection']}\t{period['shortForecast']}")
    else:
        for period in periods:
            print(f"{period['name']}\t{period['detailedForecast']}")


if __name__ == "__main__":
    # The latitude and longitude for JFK airport
    jfk_latitude = 40.6413
    jfk_longitude = -73.7781

    # Get the forecast endpoint for JFK airport
    forecast_endpoint = get_forecast_endpoint(jfk_latitude, jfk_longitude)
    if not forecast_endpoint:
        print("Could not get forecast endpoint.")
        sys.exit(1)

    # Get the weather forecast
    weather_forecast = get_weather_forecast(forecast_endpoint)
    if not weather_forecast:
        print("Could not get weather forecast.")
        sys.exit(1)

    # Filter the forecast to a 24-hour period
    filtered_forecast = filter_forecast_to_24_hours(weather_forecast)
    if not filtered_forecast:
        print("Could not filter weather forecast.")
        sys.exit(1)

    # Check for the --raw flag
    if "--raw" in sys.argv:
        print(json.dumps(filtered_forecast, indent=2))
    elif "--long" in sys.argv:
        print_human_readable_forecast(filtered_forecast,True)
    elif len(sys.argv) > 1:
        print_usage()
    else:
        print_human_readable_forecast(filtered_forecast)
