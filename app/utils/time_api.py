"""
Time API Module
Provides time-related information and utilities
"""
from datetime import datetime, timezone
import requests

def get_timezone_info(location_data):
    """
    Get timezone information for a location

    Args:
        location_data: Dictionary with 'latitude' and 'longitude' keys

    Returns:
        Dictionary with timezone information or None
    """
    if not location_data or 'latitude' not in location_data or 'longitude' not in location_data:
        return None

    try:
        lat = location_data['latitude']
        lon = location_data['longitude']

        # Use TimeAPI.io (free, no key required)
        url = f"https://timeapi.io/api/TimeZone/coordinate"
        params = {
            'latitude': lat,
            'longitude': lon
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        return {
            'timezone': data.get('timeZone'),
            'current_time': data.get('currentLocalTime'),
            'utc_offset': data.get('currentUtcOffset', {}).get('seconds', 0) / 3600,
            'is_dst': data.get('dstActive', False)
        }

    except Exception as e:
        print(f"Error fetching timezone data: {e}")
        return None

def get_time_of_day(hour):
    """
    Determine time of day category from hour

    Args:
        hour: Hour of day (0-23)

    Returns:
        String category
    """
    if 5 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 17:
        return 'afternoon'
    elif 17 <= hour < 21:
        return 'evening'
    else:
        return 'night'

def analyze_photo_time(datetime_obj):
    """
    Analyze when a photo was taken

    Args:
        datetime_obj: Datetime object from EXIF data

    Returns:
        Dictionary with time analysis
    """
    if not datetime_obj:
        return None

    return {
        'date': datetime_obj.strftime('%Y-%m-%d'),
        'time': datetime_obj.strftime('%H:%M:%S'),
        'hour': datetime_obj.hour,
        'time_of_day': get_time_of_day(datetime_obj.hour),
        'day_of_week': datetime_obj.strftime('%A'),
        'month': datetime_obj.strftime('%B'),
        'year': datetime_obj.year
    }

def get_sun_times(location_data, date=None):
    """
    Get sunrise and sunset times for a location

    Args:
        location_data: Dictionary with 'latitude' and 'longitude' keys
        date: Date string (YYYY-MM-DD) or None for today

    Returns:
        Dictionary with sunrise/sunset times or None
    """
    if not location_data or 'latitude' not in location_data or 'longitude' not in location_data:
        return None

    try:
        lat = location_data['latitude']
        lon = location_data['longitude']

        # Use sunrise-sunset.org API (free, no key required)
        url = "https://api.sunrise-sunset.org/json"
        params = {
            'lat': lat,
            'lng': lon,
            'formatted': 0
        }

        if date:
            params['date'] = date

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get('status') == 'OK':
            results = data.get('results', {})
            return {
                'sunrise': results.get('sunrise'),
                'sunset': results.get('sunset'),
                'solar_noon': results.get('solar_noon'),
                'day_length': results.get('day_length'),
                'civil_twilight_begin': results.get('civil_twilight_begin'),
                'civil_twilight_end': results.get('civil_twilight_end')
            }

    except Exception as e:
        print(f"Error fetching sun times: {e}")

    return None
