from database import get_db_connection


def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT id, name, phone, role, notification_enabled, linked_user_phone FROM users ORDER BY id DESC"
    )
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users


def validate_login(name, phone):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, name, phone, role, address, parent_name, warden_name, date_of_birth,
               college_address, home_address, profile_photo
        FROM users
        WHERE name = %s AND phone = %s
        LIMIT 1
        """,
        (name, phone),
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def get_user_by_phone(phone):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, name, phone, role, address, parent_name, warden_name, date_of_birth,
               college_address, home_address, profile_photo
        FROM users
        WHERE phone = %s
        LIMIT 1
        """,
        (phone,),
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def create_user(name, phone, role, notification_enabled=True):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (name, phone, role, notification_enabled, linked_user_phone)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (name, phone, role, 1 if notification_enabled else 0, None),
    )
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return user_id


def get_notification_contacts_for_user(user_phone):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT name, phone, role
        FROM users
        WHERE role IN ('warden', 'guardian', 'parent')
          AND notification_enabled = 1
          AND linked_user_phone = %s
        ORDER BY id DESC
        """,
        (user_phone,),
    )
    contacts = cursor.fetchall()
    cursor.close()
    conn.close()
    return contacts


def create_contact_for_user(name, phone, role, linked_user_phone, notification_enabled=True):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO users (name, phone, role, notification_enabled, linked_user_phone)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (name, phone, role, 1 if notification_enabled else 0, linked_user_phone),
    )
    conn.commit()
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return user_id


def get_registered_users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, name, phone
        FROM users
        WHERE role = 'user'
        ORDER BY id DESC
        """
    )
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users


def get_contacts_for_user(linked_user_phone):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, name, phone, role, notification_enabled, linked_user_phone
        FROM users
        WHERE role IN ('warden', 'guardian', 'parent')
          AND linked_user_phone = %s
        ORDER BY id DESC
        """,
        (linked_user_phone,),
    )
    contacts = cursor.fetchall()
    cursor.close()
    conn.close()
    return contacts


def delete_contact_for_user(contact_id, linked_user_phone):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM users
        WHERE id = %s
          AND role IN ('warden', 'guardian', 'parent')
          AND linked_user_phone = %s
        """,
        (contact_id, linked_user_phone),
    )
    conn.commit()
    deleted = cursor.rowcount
    cursor.close()
    conn.close()
    return deleted > 0


def get_user_profile_by_phone(phone):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        """
        SELECT id, name, phone, role, address, parent_name, warden_name, date_of_birth,
               college_address, home_address, created_at
             , profile_photo
        FROM users
        WHERE phone = %s
        LIMIT 1
        """,
        (phone,),
    )
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def update_user_profile(
    phone,
    name=None,
    address=None,
    profile_photo=None,
    parent_name=None,
    warden_name=None,
    date_of_birth=None,
    college_address=None,
    home_address=None,
):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE users
        SET name = COALESCE(%s, name),
            address = COALESCE(%s, address),
            profile_photo = COALESCE(%s, profile_photo),
            parent_name = COALESCE(%s, parent_name),
            warden_name = COALESCE(%s, warden_name),
            date_of_birth = COALESCE(%s, date_of_birth),
            college_address = COALESCE(%s, college_address),
            home_address = COALESCE(%s, home_address)
        WHERE phone = %s
        """,
        (
            name,
            address,
            profile_photo,
            parent_name,
            warden_name,
            date_of_birth,
            college_address,
            home_address,
            phone,
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()


def delete_account_permanently(phone):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE linked_user_phone = %s", (phone,))
        cursor.execute("DELETE FROM alerts WHERE user_phone = %s", (phone,))
        cursor.execute("DELETE FROM locations WHERE user_phone = %s", (phone,))
        cursor.execute("DELETE FROM geofence_settings WHERE user_phone = %s", (phone,))
        cursor.execute("DELETE FROM users WHERE phone = %s", (phone,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()
