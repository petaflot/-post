"""
    youtube handler ; keeps a copy of a user's posted comments

    TODO watcher for comments on a specific URL (typically replies to one's own comment)
"""
HANDLER_NAME = "Youtube"

regex_match = r"https?://(?:[a-zA-Z0-9-]+\.)*(youtube|youtu|ytimg)\.(com|ch|de|be).*"

import re, json

def handle_request(url, request, timestamp):
    # this is to filter out false positives (technical background noise)
    comments_regex = {
        'POST':     r"https?://www.youtube.com/youtubei/v1/comment/create_comment.*",
    }
    method = request.method

    try:
        if not re.search(comments_regex[method], url):
            print(f"{HANDLER_NAME}: ignoring {method} request for {url} at {timestamp}")
            return None
    except KeyError:
        return

    print(f"{HANDLER_NAME}: handling {method} request for {url} at {timestamp}")

    # Perform custom processing here
    if method.upper() == "POST":
        content_type = request.headers.get("content-type", "")
        print(f"{HANDLER_NAME} {content_type=}")

        if "application/json" in content_type:
            try:
                body = request.get_text()
                data = json.loads(body)
                # TODO is this a reply to another existing comment?
                #from pprint import pprint
                #pprint(f"{data=}")
                return {
                    'originalUrl': data['context']['client']['originalUrl'],
                    'commentText': data['commentText'],
                }
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


