from models.location_model import create_location, get_latest_location


def update_location(latitude, longitude, user_phone=None):
    location_id = create_location(latitude, longitude, user_phone=user_phone)
    return {
        "location_id": location_id,
        "user_phone": user_phone,
        "latitude": latitude,
        "longitude": longitude,
    }


def fetch_latest_location(user_phone=None):
    return get_latest_location(user_phone=user_phone)
