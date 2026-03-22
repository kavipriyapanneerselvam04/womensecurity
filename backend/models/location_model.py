from database import get_db_connection


from config import Config


def create_location(latitude, longitude, user_phone=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO locations (user_phone, latitude, longitude)
        VALUES (%s, %s, %s)
        """,
        (user_phone, latitude, longitude),
    )
    conn.commit()
    location_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return location_id


def get_locations(limit=200, user_phone=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if user_phone:
        cursor.execute(
            """
            SELECT id, user_phone, latitude, longitude, timestamp
            FROM locations
            WHERE user_phone = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (user_phone, limit),
        )
    else:
        cursor.execute(
            """
            SELECT id, user_phone, latitude, longitude, timestamp
            FROM locations
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (limit,),
        )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_latest_location(user_phone=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if user_phone:
        cursor.execute(
            """
            SELECT id, user_phone, latitude, longitude, timestamp
            FROM locations
            WHERE user_phone = %s
            ORDER BY timestamp DESC
            LIMIT 1
            """,
            (user_phone,),
        )
    else:
        cursor.execute(
            """
            SELECT id, user_phone, latitude, longitude, timestamp
            FROM locations
            ORDER BY timestamp DESC
            LIMIT 1
            """
        )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def upsert_geofence_setting(user_phone, center_latitude, center_longitude, radius_meters):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO geofence_settings (user_phone, center_latitude, center_longitude, radius_meters)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            center_latitude = VALUES(center_latitude),
            center_longitude = VALUES(center_longitude),
            radius_meters = VALUES(radius_meters)
        """,
        (user_phone, center_latitude, center_longitude, radius_meters),
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_geofence_setting_row(user_phone):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT user_phone, center_latitude, center_longitude, radius_meters, updated_at
        FROM geofence_settings
        WHERE user_phone = %s
        LIMIT 1
        """,
        (user_phone,),
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_geofence_setting(user_phone):
    row = get_geofence_setting_row(user_phone)
    if row:
        return row
    return {
        "user_phone": user_phone,
        "center_latitude": Config.GEOFENCE_CENTER_LAT,
        "center_longitude": Config.GEOFENCE_CENTER_LON,
        "radius_meters": Config.GEOFENCE_RADIUS_METERS,
    }
