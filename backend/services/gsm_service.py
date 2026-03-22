import requests

from config import Config


def _send_via_twilio(to_number, message):
    account_sid = getattr(Config, "TWILIO_ACCOUNT_SID", "")
    auth_token = getattr(Config, "TWILIO_AUTH_TOKEN", "")
    from_number = getattr(Config, "TWILIO_FROM_NUMBER", "")

    if not (
        account_sid
        and auth_token
        and from_number
    ):
        return False, "Twilio credentials missing"

    url = (
        f"https://api.twilio.com/2010-04-01/Accounts/"
        f"{account_sid}/Messages.json"
    )
    response = requests.post(
        url,
        data={"From": from_number, "To": to_number, "Body": message},
        auth=(account_sid, auth_token),
        timeout=10,
    )
    if response.status_code >= 300:
        return False, response.text
    return True, "sent"


def send_sms_alert(message, recipients):
    if not recipients:
        print("SMS SENT: Emergency alert with location (no contacts configured)")
        return []

    results = []
    provider = (getattr(Config, "SMS_PROVIDER", None) or "console").lower()
    for recipient in recipients:
        label = f"{recipient['name']} ({recipient['role']}) {recipient['phone']}"
        print(f"SMS SENT: Emergency alert with location -> {label}")
        status = {"recipient": recipient, "sent": True, "detail": "console"}

        if provider == "twilio":
            sent, detail = _send_via_twilio(recipient["phone"], message)
            status["sent"] = sent
            status["detail"] = detail
            print(f"TWILIO STATUS [{recipient['phone']}]: {detail}")

        results.append(status)

    return results
