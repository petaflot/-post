"""
    mon-net.org handler
"""
HANDLER_NAME = "mon-net.org"

regex_match = r"https?://(?:[a-zA-Z0-9-]+\.)*mon-net\.org.*"

def handle_request(url, request, timestamp):
    #print(f"{HANDLER_NAME}: ignoring request")
    return None

