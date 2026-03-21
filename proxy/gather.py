import json
import re
import os
import importlib.util
from mitmproxy import http
from datetime import datetime
from pathlib import Path
import urllib.parse
import websockets
import asyncio

DEBUG_OUTPUT = True

# -----------------------------
# Load external JSON config
# -----------------------------
CONFIG_FILE = Path(__file__).parent / "config.json"
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

LOG_TO_FILE = False
LOG_DIR = config.get("log_dir", '/tmp/xpost_log')
HANDLERS = config.get("configured_handlers", ['fallback'])


# -----------------------------
# Helper functions
# -----------------------------
WS_URL = "ws://127.0.0.1:12345/ingest"  # WebSocket endpoint
write_queue = asyncio.Queue(maxsize=10000)  # Queue for WebSocket logging

async def send_to_websocket(data: dict):
    try:
        async with websockets.connect(WS_URL) as ws:
            await ws.send(json.dumps(data))
    except Exception as e:
        print(f"Error sending to WebSocket: {e}")

def generate_logfile(url: str) -> str:
    parsed_url = urllib.parse.urlparse(url)
    fqdn = parsed_url.hostname
    path = parsed_url.path

    last_part = path.rstrip('/').split('/')[-1]  # Remove trailing slashes and split by '/'
    last_part = os.path.splitext(last_part)[0]  # Remove file extension
    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    log_dir = os.path.join(LOG_DIR, fqdn)
    os.makedirs(log_dir, exist_ok=True)
    log_filename = f"{timestamp}_{last_part}.log" if last_part else f"{timestamp}.log"
    log_path = os.path.join(log_dir, log_filename)

    return log_path

"""
def log_entry(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(text + "\n")
"""

def format_log_data(url: str, fields: dict, timestamp: str):
    log_data = f"# {urllib.parse.urlparse(url).hostname} {timestamp}\n"
    log_data += f"url: {url}\n"
    for key, value in fields.items():
        log_data += f"{key}: {value}\n"
    return log_data

def log_form(url, form_data, timestamp):
    log_data = format_log_data(url, form_data, timestamp)

    if LOG_TO_FILE:
        log_path = generate_logfile(url)
        log_entry(log_path, log_data)
    else:
        log_data_dict = {
            "uuid": str(datetime.utcnow().timestamp()),  
            "url": url,
            "timestamp": int(datetime.utcnow().timestamp()),
            "fields": {k: v for k, v in form_data.items()}
        }
        asyncio.get_event_loop().create_task(send_to_websocket(log_data_dict))

def log_json(url, json_data, timestamp):
    if json_data is None:
        return

    log_data = format_log_data(url, json_data, timestamp)

    if LOG_TO_FILE:
        log_path = generate_logfile(url)
        log_entry(log_path, log_data)
    else:
        log_data_dict = {
            "uuid": str(datetime.utcnow().timestamp()),
            "url": url,
            "timestamp": int(datetime.utcnow().timestamp()),
            "fields": flatten_json(json_data)
        }
        asyncio.get_event_loop().create_task(send_to_websocket(log_data_dict))

def flatten_json(data):
    flat = {}
    
    def flatten(data, parent_key=''):
        if isinstance(data, dict):
            for k, v in data.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                flatten(v, new_key)
        elif isinstance(data, list):
            for i, v in enumerate(data):
                new_key = f"{parent_key}[{i}]"
                flatten(v, new_key)
        else:
            flat[parent_key] = data

    flatten(data)
    return flat

def import_handler(handler_name: str):
    """Dynamically import handler module."""
    handler_path = Path(__file__).parent / "website_handlers" / f"{handler_name}.py"
    spec = importlib.util.spec_from_file_location(handler_name, handler_path)
    handler_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(handler_module)
    return handler_module

def should_log(url: str) -> str:
    # Determine the handlers for POST and GET mehods
    handlers_dir = Path(__file__).parent / "website_handlers"

    for handler_name in HANDLERS:
        handler_module = import_handler(handler_name)

        # Check if the handler defines a regex match
        if hasattr(handler_module, "regex_match"):
            if re.search(handler_module.regex_match, url):
                return handler_name

    return None

# -----------------------------
# mitmproxy request hook
# -----------------------------
def request(flow: http.HTTPFlow) -> None:
    #print(f"{flow.request.url=} {flow.request.pretty_url=}")
    url = flow.request.pretty_url
    handler_name = should_log(url)
    if handler_name is None:
        if DEBUG_OUTPUT: print(f"No handler matching {url}")
        return

    timestamp = datetime.now().astimezone().isoformat()
    handler_module = import_handler(handler_name)
    try:
        result = handler_module.handle_request(url, flow.request, timestamp)
    except AttributeError:
        pass
    else:
        if type(result) is dict:
            log_form(url, result, timestamp)
        else:
            log_json(url, result, timestamp)


def response(flow: http.HTTPFlow) -> None:
    url = flow.request.pretty_url
    handler_name = should_log(url)
    if handler_name is None:
        if DEBUG_OUTPUT: print(f"No handler matching {url}")
        return

    timestamp = datetime.now().astimezone().isoformat()
    handler_module = import_handler(handler_name)
    try:
        result = handler_module.handle_response(url, flow.request, flow.response, timestamp)
    except AttributeError:
        pass
