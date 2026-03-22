from pathlib import Path
from uuid import uuid4

from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename

from models.user_model import (
    create_contact_for_user,
    create_user,
    delete_contact_for_user,
    delete_account_permanently,
    get_contacts_for_user,
    get_user_profile_by_phone,
    get_user_by_phone,
    update_user_profile,
    validate_login,
)

auth_bp = Blueprint("auth_bp", __name__)


def build_session_user(profile):
    return {
        "id": profile["id"],
        "name": profile["name"],
        "phone": profile["phone"],
        "role": profile["role"],
        "address": profile.get("address"),
        "parent_name": profile.get("parent_name"),
        "warden_name": profile.get("warden_name"),
        "date_of_birth": profile.get("date_of_birth"),
        "college_address": profile.get("college_address"),
        "home_address": profile.get("home_address"),
        "profile_photo": profile.get("profile_photo"),
    }


@auth_bp.route("/login", methods=["POST"])
def login():
    payload = request.get_json(silent=True) or {}
    name = payload.get("name", "").strip()
    phone = payload.get("phone", "").strip()

    if not name or not phone:
        return jsonify({"success": False, "message": "name and phone are required"}), 400

    user = validate_login(name, phone)
    if not user:
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

    session["user"] = build_session_user(user)
    return jsonify({"success": True, "user": user}), 200


@auth_bp.route("/users", methods=["GET"])
def users():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return jsonify({"success": True, "users": get_contacts_for_user(current_user["phone"])}), 200


@auth_bp.route("/users", methods=["POST"])
def add_user():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    name = payload.get("name", "").strip()
    phone = payload.get("phone", "").strip()
    role = payload.get("role", "guardian").strip().lower()
    notification_enabled = bool(payload.get("notification_enabled", True))

    if not name or not phone:
        return jsonify({"success": False, "message": "name and phone are required"}), 400

    if role not in {"warden", "guardian", "parent"}:
        return jsonify({"success": False, "message": "invalid role"}), 400
    user_id = create_contact_for_user(
        name=name,
        phone=phone,
        role=role,
        linked_user_phone=current_user["phone"],
        notification_enabled=notification_enabled,
    )
    return jsonify({"success": True, "user_id": user_id}), 201


@auth_bp.route("/users/<int:contact_id>", methods=["DELETE"])
def delete_user_contact(contact_id):
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    deleted = delete_contact_for_user(contact_id, current_user["phone"])
    if not deleted:
        return jsonify({"success": False, "message": "Contact not found"}), 404
    return jsonify({"success": True}), 200


@auth_bp.route("/register", methods=["POST"])
def register():
    payload = request.get_json(silent=True) or {}
    name = payload.get("name", "").strip()
    phone = payload.get("phone", "").strip()

    if not name or not phone:
        return jsonify({"success": False, "message": "name and phone are required"}), 400

    existing = get_user_by_phone(phone)
    if existing:
        return jsonify({"success": False, "message": "Phone already registered"}), 409

    user_id = create_user(name, phone, "user", notification_enabled=False)
    return jsonify({"success": True, "user_id": user_id, "message": "Registration successful"}), 201


@auth_bp.route("/registered-users", methods=["GET"])
def registered_users():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    return jsonify({"success": True, "users": [current_user]}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user", None)
    return jsonify({"success": True}), 200


@auth_bp.route("/api/account", methods=["DELETE"])
def delete_account():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    delete_account_permanently(current_user["phone"])
    session.pop("user", None)
    return jsonify({"success": True, "message": "Account deleted permanently"}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    profile = get_user_profile_by_phone(current_user["phone"])
    if profile:
        session["user"] = build_session_user(profile)
    return jsonify({"success": True, "user": session["user"]}), 200


@auth_bp.route("/api/profile", methods=["GET"])
def profile_get():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    profile = get_user_profile_by_phone(current_user["phone"])
    return jsonify({"success": True, "profile": profile}), 200


@auth_bp.route("/api/profile", methods=["PUT"])
def profile_update():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    address = payload.get("address")
    parent_name = payload.get("parent_name")
    warden_name = payload.get("warden_name")
    date_of_birth = payload.get("date_of_birth")
    college_address = payload.get("college_address")
    home_address = payload.get("home_address")
    if name is not None:
        name = str(name).strip()
    if address is not None:
        address = str(address).strip()
    if parent_name is not None:
        parent_name = str(parent_name).strip()
    if warden_name is not None:
        warden_name = str(warden_name).strip()
    if date_of_birth is not None:
        date_of_birth = str(date_of_birth).strip() or None
    if college_address is not None:
        college_address = str(college_address).strip()
    if home_address is not None:
        home_address = str(home_address).strip()

    update_user_profile(
        current_user["phone"],
        name=name,
        address=address,
        parent_name=parent_name,
        warden_name=warden_name,
        date_of_birth=date_of_birth,
        college_address=college_address,
        home_address=home_address,
    )
    profile = get_user_profile_by_phone(current_user["phone"])
    session["user"] = build_session_user(profile)
    return jsonify({"success": True, "profile": profile}), 200


@auth_bp.route("/api/profile-photo", methods=["POST"])
def profile_photo_upload():
    current_user = session.get("user")
    if not current_user:
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    if "photo" not in request.files:
        return jsonify({"success": False, "message": "photo file is required"}), 400
    file = request.files["photo"]
    if not file or not file.filename:
        return jsonify({"success": False, "message": "Invalid file"}), 400

    allowed_ext = {".png", ".jpg", ".jpeg", ".webp"}
    extension = Path(file.filename).suffix.lower()
    if extension not in allowed_ext:
        return jsonify({"success": False, "message": "Only png/jpg/jpeg/webp allowed"}), 400

    safe_name = secure_filename(file.filename)
    new_name = f"{current_user['phone'].replace('+', '')}_{uuid4().hex}{Path(safe_name).suffix}"
    base_dir = Path(__file__).resolve().parents[2]
    upload_dir = base_dir / "frontend" / "static" / "uploads"
    upload_dir.mkdir(parents=True, exist_ok=True)
    save_path = upload_dir / new_name
    file.save(save_path)

    relative_path = f"/static/uploads/{new_name}"
    update_user_profile(current_user["phone"], profile_photo=relative_path)
    profile = get_user_profile_by_phone(current_user["phone"])
    session["user"] = build_session_user(profile)
    return jsonify({"success": True, "profile_photo": relative_path})
