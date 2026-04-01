import requests
import base64
from django.conf import settings

def is_url_safe(url):
    """
    Check if a URL is safe using VirusTotal API.
    Returns True if safe, False if malicious.
    """

    try:
        headers = {"x-apikey": settings.VIRUSTOTAL_KEY}

        # Encode URL for VirusTotal lookup
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")

        # Query the URL report directly
        endpoint = f"https://www.virustotal.com/api/v3/urls/{url_id}"
        response = requests.get(endpoint, headers=headers)

        if response.status_code != 200:
            # If API fails, assume safe
            return True

        data = response.json().get("data", {}).get("attributes", {})
        stats = data.get("last_analysis_stats", {})

        # Safe if malicious count == 0
        return stats.get("malicious", 0) == 0

    except Exception:
        # Fail gracefully — don’t block shortening
        return True