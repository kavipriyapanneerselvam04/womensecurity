import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FALLBACK_PYTHON = BASE_DIR / "venv" / "Scripts" / "python.exe"

try:
    from flask import Flask, jsonify, redirect, render_template, request, session
except ModuleNotFoundError as exc:
    if exc.name != "flask":
        raise
    if Path(sys.executable).resolve() != FALLBACK_PYTHON.resolve() and FALLBACK_PYTHON.exists():
        os.execv(str(FALLBACK_PYTHON), [str(FALLBACK_PYTHON), __file__, *sys.argv[1:]])
    raise ModuleNotFoundError(
        "Flask is not installed for the active Python interpreter. "
        "Activate the project's 'venv' or run 'venv\\Scripts\\python.exe -m pip install -r requirements.txt'."
    ) from exc

from config import Config
from database import initialize_database
from routes.alert_routes import alert_bp
from routes.auth_routes import auth_bp
from routes.location_routes import location_bp

TEMPLATE_DIR = BASE_DIR / "frontend" / "templates"
STATIC_DIR = BASE_DIR / "frontend" / "static"


def create_app():
    app = Flask(
        __name__,
        template_folder=str(TEMPLATE_DIR),
        static_folder=str(STATIC_DIR),
    )
    app.config.from_object(Config)

    initialize_database()

    app.register_blueprint(auth_bp)
    app.register_blueprint(location_bp)
    app.register_blueprint(alert_bp)

    public_paths = {"/", "/login", "/register", "/register-page", "/health"}

    @app.before_request
    def protect_routes():
        if request.path.startswith("/static/"):
            return None
        if request.path in public_paths:
            return None
        if session.get("user"):
            return None
        if request.method == "GET":
            return redirect("/")
        return jsonify({"success": False, "message": "Unauthorized"}), 401

    @app.route("/", methods=["GET"])
    def root():
        return render_template("login.html")

    @app.route("/register-page", methods=["GET"])
    def register_page():
        return render_template("register.html")

    @app.route("/dashboard", methods=["GET"])
    def dashboard():
        return render_template("dashboard.html")

    @app.route("/live-location", methods=["GET"])
    def live_location():
        return render_template("live_location.html")

    @app.route("/alerts-page", methods=["GET"])
    def alerts_page():
        return redirect("/alert-history")

    @app.route("/geofence-page", methods=["GET"])
    def geofence_page():
        return render_template("geofence.html")

    @app.route("/device-status", methods=["GET"])
    def device_status():
        return render_template("device_status.html")

    @app.route("/user-management", methods=["GET"])
    def user_management():
        return render_template("user_management.html")

    @app.route("/alert-history", methods=["GET"])
    def alert_history():
        return render_template("alert_history.html")

    @app.route("/profile-page", methods=["GET"])
    def profile_page():
        return render_template("profile.html")

    @app.route("/self-defense", methods=["GET"])
    def self_defense_page():
        return render_template("self_defense.html")

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"success": True, "status": "ok"})

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
