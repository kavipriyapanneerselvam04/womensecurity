from flask import Blueprint, jsonify, request, session

from config import Config
from models.location_model import (
    get_geofence_setting_row,
    get_geofence_setting,
    get_locations,
    upsert_geofence_setting,
)
from services.geofence_service import check_geofence
from services.gps_service import update_location
from services.panic_service import trigger_boundary_alert

location_bp = Blueprint("location_bp", __name__)


def _is_near_default_center(lat, lon):
    return abs(float(lat) - float(Config.GEOFENCE_CENTER_LAT)) < 0.0001 and abs(
        float(lon) - float(Config.GEOFENCE_CENTER_LON)
    ) < 0.0001


@location_bp.route("/update-location", methods=["POST"])
def update_location_route():
    payload = request.get_json(silent=True) or {}
    latitude = payload.get("latitude")
    longitude = payload.get("longitude")
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    user_phone = current_user["phone"]

    if latitude is None or longitude is None:
        return jsonify({"success": False, "message": "latitude and longitude are required"}), 400

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return jsonify({"success": False, "message": "Invalid coordinates"}), 400

    # Auto-fix: first real GPS update becomes geofence center for this user
    # when no personal geofence row exists yet.
    existing_setting = get_geofence_setting_row(user_phone)
    if not existing_setting:
        upsert_geofence_setting(
            user_phone,
            latitude,
            longitude,
            float(Config.GEOFENCE_RADIUS_METERS),
        )

    setting = get_geofence_setting(user_phone)

    # Migration fix: if user still has untouched default center (e.g. Bangalore)
    # and current live GPS is far away, auto-shift center to current location once.
    if _is_near_default_center(setting["center_latitude"], setting["center_longitude"]):
        probe = check_geofence(
            latitude,
            longitude,
            center_lat=float(setting["center_latitude"]),
            center_lon=float(setting["center_longitude"]),
            radius_meters=float(setting["radius_meters"]),
        )
        if float(probe["distance_meters"]) > max(5000.0, float(setting["radius_meters"]) * 10):
            upsert_geofence_setting(
                user_phone,
                latitude,
                longitude,
                float(setting["radius_meters"]),
            )
            setting = get_geofence_setting(user_phone)
    center_lat = float(setting["center_latitude"])
    center_lon = float(setting["center_longitude"])
    radius = float(setting["radius_meters"])

    location = update_location(latitude, longitude, user_phone=user_phone)
    geofence_info = check_geofence(
        latitude,
        longitude,
        center_lat=center_lat,
        center_lon=center_lon,
        radius_meters=radius,
    )

    boundary_alert_id = None
    if not geofence_info["inside"]:
        boundary_alert_id = trigger_boundary_alert(latitude, longitude, user_phone)

    return jsonify(
        {
            "success": True,
            "location": location,
            "geofence": geofence_info,
            "boundary_alert_id": boundary_alert_id,
            "safe_zone": {
                "center_latitude": center_lat,
                "center_longitude": center_lon,
                "radius_meters": radius,
            },
        }
    )


@location_bp.route("/locations", methods=["GET"])
def locations():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    user_phone = current_user["phone"]
    rows = get_locations(user_phone=user_phone)
    return jsonify({"success": True, "locations": rows})


@location_bp.route("/geofence-settings", methods=["GET"])
def geofence_settings_get():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    user_phone = current_user["phone"]
    return jsonify({"success": True, "setting": get_geofence_setting(user_phone)})


@location_bp.route("/geofence-settings", methods=["POST"])
def geofence_settings_set():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    user_phone = current_user["phone"]
    center_latitude = payload.get("center_latitude")
    center_longitude = payload.get("center_longitude")
    radius_meters = payload.get("radius_meters")

    if center_latitude is None or center_longitude is None or radius_meters is None:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "center_latitude, center_longitude and radius_meters are required",
                }
            ),
            400,
        )

    try:
        center_latitude = float(center_latitude)
        center_longitude = float(center_longitude)
        radius_meters = float(radius_meters)
    except ValueError:
        return jsonify({"success": False, "message": "Invalid geofence values"}), 400

    upsert_geofence_setting(user_phone, center_latitude, center_longitude, radius_meters)
    return jsonify({"success": True, "setting": get_geofence_setting(user_phone)})
