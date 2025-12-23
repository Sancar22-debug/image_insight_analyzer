"""
Weather API Module
Fetches weather data based on location coordinates
Uses Open-Meteo API (free, no API key required)
"""
import requests
from datetime import datetime

def get_weather(location_data):
    """
    Get current weather for a location

    Args:
        location_data: Dictionary with 'latitude' and 'longitude' keys

    Returns:
        Dictionary with weather information or None
    """
    if not location_data or 'latitude' not in location_data or 'longitude' not in location_data:
        return None

    try:
        lat = location_data['latitude']
        lon = location_data['longitude']

        # Use Open-Meteo API (free, no key required)
        url = f"https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'current_weather': True,
            'temperature_unit': 'celsius',
            'windspeed_unit': 'kmh'
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        current = data.get('current_weather', {})

        # Map weather codes to descriptions
        weather_code = current.get('weathercode', 0)
        weather_description = get_weather_description(weather_code)

        return {
            'temperature': current.get('temperature'),
            'temperature_unit': 'Celsius',
            'windspeed': current.get('windspeed'),
            'windspeed_unit': 'km/h',
            'wind_direction': current.get('winddirection'),
            'weather_code': weather_code,
            'weather_description': weather_description,
            'time': current.get('time')
        }

    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def get_weather_description(code):
    """
    Convert WMO weather code to description

    Args:
        code: WMO weather code

    Returns:
        String description of weather
    """
    weather_codes = {
        0: 'Clear sky',
        1: 'Mainly clear',
        2: 'Partly cloudy',
        3: 'Overcast',
        45: 'Foggy',
        48: 'Depositing rime fog',
        51: 'Light drizzle',
        53: 'Moderate drizzle',
        55: 'Dense drizzle',
        61: 'Slight rain',
        63: 'Moderate rain',
        65: 'Heavy rain',
        71: 'Slight snow',
        73: 'Moderate snow',
        75: 'Heavy snow',
        77: 'Snow grains',
        80: 'Slight rain showers',
        81: 'Moderate rain showers',
        82: 'Violent rain showers',
        85: 'Slight snow showers',
        86: 'Heavy snow showers',
        95: 'Thunderstorm',
        96: 'Thunderstorm with slight hail',
        99: 'Thunderstorm with heavy hail'
    }

    return weather_codes.get(code, 'Unknown')

def get_forecast(location_data, days=7):
    """
    Get weather forecast for upcoming days

    Args:
        location_data: Dictionary with 'latitude' and 'longitude' keys
        days: Number of days to forecast (1-16)

    Returns:
        Dictionary with forecast data or None
    """
    if not location_data or 'latitude' not in location_data or 'longitude' not in location_data:
        return None

    try:
        lat = location_data['latitude']
        lon = location_data['longitude']

        url = f"https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': lat,
            'longitude': lon,
            'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,weathercode',
            'forecast_days': min(days, 16),
            'temperature_unit': 'celsius'
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        daily = data.get('daily', {})

        forecast = []
        for i in range(len(daily.get('time', []))):
            forecast.append({
                'date': daily['time'][i],
                'max_temp': daily['temperature_2m_max'][i],
                'min_temp': daily['temperature_2m_min'][i],
                'precipitation': daily['precipitation_sum'][i],
                'weather_code': daily['weathercode'][i],
                'weather_description': get_weather_description(daily['weathercode'][i])
            })

        return forecast

    except Exception as e:
        print(f"Error fetching forecast data: {e}")
        return None
