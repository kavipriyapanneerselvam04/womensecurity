import math

from config import Config


def haversine_distance_meters(lat1, lon1, lat2, lon2):
    radius_earth = 6371000
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_lat / 2) ** 2
        + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_earth * c


def check_geofence(latitude, longitude, center_lat=None, center_lon=None, radius_meters=None):
    if center_lat is None:
        center_lat = Config.GEOFENCE_CENTER_LAT
    if center_lon is None:
        center_lon = Config.GEOFENCE_CENTER_LON
    if radius_meters is None:
        radius_meters = Config.GEOFENCE_RADIUS_METERS

    distance = haversine_distance_meters(
        center_lat,
        center_lon,
        latitude,
        longitude,
    )
    inside = distance <= radius_meters
    return {"inside": inside, "distance_meters": round(distance, 2)}
