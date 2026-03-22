from flask import Blueprint, jsonify, request, session

from models.alert_model import get_alert_counts, get_alerts
from models.location_model import get_latest_location
from services.fall_detection_service import trigger_fall_alert
from services.panic_service import trigger_boundary_alert, trigger_panic_alert

alert_bp = Blueprint("alert_bp", __name__)


def _extract_coordinates(payload):
    latitude = payload.get("latitude")
    longitude = payload.get("longitude")

    if latitude is None or longitude is None:
        return (
            None,
            None,
            {"success": False, "message": "latitude and longitude are required"},
            400,
        )

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except ValueError:
        return None, None, {"success": False, "message": "Invalid coordinates"}, 400

    return latitude, longitude, None, None


@alert_bp.route("/fall-alert", methods=["POST"])
def fall_alert():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    latitude, longitude, error_payload, status_code = _extract_coordinates(payload)
    if error_payload:
        return jsonify(error_payload), status_code

    user_phone = current_user["phone"]
    alert_id = trigger_fall_alert(latitude, longitude, user_phone)
    return jsonify({"success": True, "alert_id": alert_id, "alert_type": "FALL"})


@alert_bp.route("/panic-alert", methods=["POST"])
def panic_alert():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    latitude, longitude, error_payload, status_code = _extract_coordinates(payload)
    if error_payload:
        return jsonify(error_payload), status_code

    user_phone = current_user["phone"]
    alert_id = trigger_panic_alert(latitude, longitude, user_phone)
    return jsonify({"success": True, "alert_id": alert_id, "alert_type": "PANIC"})


@alert_bp.route("/boundary-alert", methods=["POST"])
def boundary_alert():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    latitude, longitude, error_payload, status_code = _extract_coordinates(payload)
    if error_payload:
        return jsonify(error_payload), status_code

    user_phone = current_user["phone"]
    alert_id = trigger_boundary_alert(latitude, longitude, user_phone)
    return jsonify({"success": True, "alert_id": alert_id, "alert_type": "BOUNDARY"})


@alert_bp.route("/alerts", methods=["GET"])
def alerts():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    user_phone = current_user["phone"]
    rows = get_alerts(user_phone=user_phone)
    return jsonify({"success": True, "alerts": rows})


@alert_bp.route("/dashboard-summary", methods=["GET"])
def dashboard_summary():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    user_phone = current_user["phone"]
    counts = get_alert_counts(user_phone=user_phone)
    latest_location = get_latest_location(user_phone=user_phone)
    recent_alerts = get_alerts(limit=8, user_phone=user_phone)
    return jsonify(
        {
            "success": True,
            "counts": counts,
            "latest_location": latest_location,
            "recent_alerts": recent_alerts,
        }
    )
