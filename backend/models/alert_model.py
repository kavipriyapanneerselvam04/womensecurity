from database import get_db_connection


def create_alert(alert_type, latitude, longitude, status="OPEN", user_phone=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO alerts (alert_type, user_phone, latitude, longitude, status)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (alert_type, user_phone, latitude, longitude, status),
    )
    conn.commit()
    alert_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return alert_id


def get_alerts(limit=100, user_phone=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if user_phone:
        cursor.execute(
            """
            SELECT id, alert_type, user_phone, latitude, longitude, timestamp, status
            FROM alerts
            WHERE user_phone = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (user_phone, limit),
        )
    else:
        cursor.execute(
            """
            SELECT id, alert_type, user_phone, latitude, longitude, timestamp, status
            FROM alerts
            ORDER BY timestamp DESC
            LIMIT %s
            """,
            (limit,),
        )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_alert_counts(user_phone=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if user_phone:
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_alerts,
                SUM(CASE WHEN alert_type = 'FALL' THEN 1 ELSE 0 END) AS fall_alerts,
                SUM(CASE WHEN alert_type = 'BOUNDARY' THEN 1 ELSE 0 END) AS boundary_alerts,
                SUM(CASE WHEN alert_type = 'PANIC' THEN 1 ELSE 0 END) AS panic_alerts
            FROM alerts
            WHERE user_phone = %s
            """,
            (user_phone,),
        )
    else:
        cursor.execute(
            """
            SELECT
                COUNT(*) AS total_alerts,
                SUM(CASE WHEN alert_type = 'FALL' THEN 1 ELSE 0 END) AS fall_alerts,
                SUM(CASE WHEN alert_type = 'BOUNDARY' THEN 1 ELSE 0 END) AS boundary_alerts,
                SUM(CASE WHEN alert_type = 'PANIC' THEN 1 ELSE 0 END) AS panic_alerts
            FROM alerts
            """
        )
    counts = cursor.fetchone()
    cursor.close()
    conn.close()
    return {
        "total_alerts": counts["total_alerts"] or 0,
        "fall_alerts": counts["fall_alerts"] or 0,
        "boundary_alerts": counts["boundary_alerts"] or 0,
        "panic_alerts": counts["panic_alerts"] or 0,
    }
