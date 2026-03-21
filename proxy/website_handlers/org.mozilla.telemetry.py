"""
    Mozilla handler (telemetry, ads, settings) (ignore)"
"""
HANDLER_NAME = "Mozilla"

regex_match = r"https?://(?:[a-zA-Z0-9-]+\.)*(telemetry|ads)\.mozilla\.org|(firefox\.settings|push)\.services\.mozilla\.com.*"

def handle_request(url, request, timestamp):
    #print(f"{HANDLER_NAME}: ignoring request")
    return None
