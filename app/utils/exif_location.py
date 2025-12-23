"""
EXIF Location Extraction Module
Extracts GPS coordinates and location data from image EXIF metadata
"""
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
from datetime import datetime

def get_exif_data(image_path):
    """
    Extract all EXIF data from an image

    Args:
        image_path: Path to the image file

    Returns:
        Dictionary of EXIF data
    """
    try:
        image = Image.open(image_path)
        exif_data = {}

        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                exif_data[decoded] = value

        return exif_data

    except Exception as e:
        print(f"Error extracting EXIF data: {e}")
        return {}

def get_gps_data(exif_data):
    """
    Extract GPS data from EXIF data

    Args:
        exif_data: Dictionary of EXIF data

    Returns:
        Dictionary of GPS data
    """
    if 'GPSInfo' not in exif_data:
        return None

    gps_info = {}
    for key in exif_data['GPSInfo'].keys():
        decode = GPSTAGS.get(key, key)
        gps_info[decode] = exif_data['GPSInfo'][key]

    return gps_info

def convert_to_degrees(value):
    """
    Convert GPS coordinates to degrees

    Args:
        value: GPS coordinate in degrees, minutes, seconds format

    Returns:
        Decimal degrees
    """
    d, m, s = value
    return d + (m / 60.0) + (s / 3600.0)

def get_coordinates(gps_data):
    """
    Extract latitude and longitude from GPS data

    Args:
        gps_data: Dictionary of GPS data

    Returns:
        Tuple of (latitude, longitude) or None
    """
    if not gps_data:
        return None

    try:
        lat = convert_to_degrees(gps_data['GPSLatitude'])
        lon = convert_to_degrees(gps_data['GPSLongitude'])

        # Check for hemisphere
        if gps_data['GPSLatitudeRef'] == 'S':
            lat = -lat
        if gps_data['GPSLongitudeRef'] == 'W':
            lon = -lon

        return (lat, lon)

    except Exception as e:
        print(f"Error converting coordinates: {e}")
        return None

def get_location_name(latitude, longitude):
    """
    Get location name from coordinates using reverse geocoding

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        Dictionary with location information
    """
    try:
        geolocator = Nominatim(user_agent="image_insight_analyzer")
        location = geolocator.reverse(f"{latitude}, {longitude}", language='en')

        if location:
            address = location.raw.get('address', {})
            return {
                'full_address': location.address,
                'city': address.get('city') or address.get('town') or address.get('village'),
                'country': address.get('country'),
                'state': address.get('state'),
                'postal_code': address.get('postcode')
            }

    except Exception as e:
        print(f"Error getting location name: {e}")

    return None

def extract_location(image_path):
    """
    Main function to extract complete location information from image

    Args:
        image_path: Path to the image file

    Returns:
        Dictionary with location data or None
    """
    try:
        # Get EXIF data
        exif_data = get_exif_data(image_path)
        if not exif_data:
            return None

        # Get GPS data
        gps_data = get_gps_data(exif_data)
        if not gps_data:
            return None

        # Get coordinates
        coords = get_coordinates(gps_data)
        if not coords:
            return None

        latitude, longitude = coords

        # Get location name
        location_info = get_location_name(latitude, longitude)

        # Combine all information
        result = {
            'latitude': latitude,
            'longitude': longitude,
            'altitude': gps_data.get('GPSAltitude'),
        }

        if location_info:
            result.update(location_info)

        return result

    except Exception as e:
        print(f"Error extracting location: {e}")
        return None

def get_datetime(image_path):
    """
    Extract date and time when photo was taken

    Args:
        image_path: Path to the image file

    Returns:
        Datetime object or None
    """
    try:
        exif_data = get_exif_data(image_path)
        if 'DateTime' in exif_data:
            dt_str = exif_data['DateTime']
            return datetime.strptime(dt_str, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        print(f"Error extracting datetime: {e}")

    return None
