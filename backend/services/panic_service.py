from models.alert_model import create_alert
from models.user_model import get_notification_contacts_for_user
from services.gsm_service import send_sms_alert


def trigger_panic_alert(latitude, longitude, user_phone):
    alert_id = create_alert(
        "PANIC",
        latitude,
        longitude,
        status="OPEN",
        user_phone=user_phone,
    )
    contacts = get_notification_contacts_for_user(user_phone)
    send_sms_alert(
        f"Emergency PANIC alert. Location: {latitude}, {longitude}",
        contacts,
    )
    return alert_id


def trigger_boundary_alert(latitude, longitude, user_phone):
    alert_id = create_alert(
        "BOUNDARY",
        latitude,
        longitude,
        status="OPEN",
        user_phone=user_phone,
    )
    contacts = get_notification_contacts_for_user(user_phone)
    send_sms_alert(
        f"Emergency BOUNDARY breach. Location: {latitude}, {longitude}",
        contacts,
    )
    return alert_id
