"""
    fallback website handler, matches everything
"""
HANDLER_NAME = "Fallback"

regex_match = r".*"

import re, json

def handle_request(url, request, timestamp):
    # this is to filter out false positives such as technical background noise
    exclusion_regex = {
        'HEAD':     r"^$",
        'POST':     r".*",
        'GET':      r"(ajay\.app|cisco\.com)",
        'DELETE':   r"^$",
        'OPTIONS':  r"^$",
    }
    method = request.method
    if re.search(exclusion_regex[method], url):
        return

    print(f"{HANDLER_NAME}: handling request for {url} at {timestamp}")

    # Perform custom processing here
    if method.upper() == "POST":
        content_type = request.headers.get("content-type", "")

        if "application/json" in content_type:
            try:
                body = request.get_text()
                data = json.loads(body)
                if isinstance(data, dict):
                    return data
            except Exception as e:
                print(f"{HANDLER_NAME} ({e}): {method} {url} {body}")
        elif content_type in ("multipart/form-data", "application/x-www-form-urlencoded"):
            try:
                form_data = request.multipart_form
                return form_data
            except Exception:
                print(f"{HANDLER_NAME} ({e}): {method} {url} {body}")
        else:
            pass # TODO

    elif method.upper() == "GET":
        return request.query

