import base64

import requests
from django.conf import settings


def get_auth_header():
    api_key = settings.BEEM_API_KEY
    secret_key = settings.BEEM_SECRET_KEY
    credentials = f"{api_key}:{secret_key}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def send_bulk_sms(source_addr, message, recipients):
    """
    Send bulk SMS via Beem API.

    source_addr: str — Sender ID (e.g. "ST-AGNES" or "NOTIFI")
    message: str — Message content (max 160 chars for 1 credit)
    recipients: list of dicts — [{"recipient_id": "1", "dest_addr": "255712345678"}]

    Returns: dict with success status and response data
    """
    url = "https://apisms.beem.africa/v1/send"

    payload = {
        "source_addr": source_addr,
        "encoding": 0,
        "message": message,
        "recipients": recipients,
    }

    headers = {
        "Authorization": get_auth_header(),
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        data = response.json()

        return {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "data": data,
            "request_id": data.get("request_id", ""),
        }
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_beem_balance():
    """Check remaining SMS credits on Beem account."""
    url = "https://apisms.beem.africa/v1/vendors/balance"
    headers = {"Authorization": get_auth_header()}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def calculate_sms_count(message):
    """Calculate how many SMS credits a message will use."""
    length = len(message)
    if length <= 160:
        return 1
    elif length <= 306:
        return 2
    else:
        return 3
