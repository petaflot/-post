#!/usr/bin/python

import json
import re
import os
from mitmproxy import http
from datetime import datetime
from pathlib import Path
import urllib.parse
from urllib.parse import urlparse
import websockets
import asyncio

DEBUG_OUTPUT = False

# -----------------------------
# Load external JSON config
# -----------------------------
CONFIG_FILE = Path(__file__).parent / "config.json"
with open(CONFIG_FILE, "r", encoding="utf-8") as f:
    config = json.load(f)

METHOD_FILTERS = config.get("method_filters", {})
FIELD_RULES = config.get("field_rules", [])

LOG_TO_FILE = False
LOG_DIR = config.get("log_dir", '/tmp/xpost_log')

# -----------------------------
# Helper functions
# -----------------------------

if not LOG_TO_FILE:
    WS_URL = "ws://127.0.0.1:12345/ingest"  # WebSocket endpoint    # TODO read HOST/PORT from config or something.. redundancy with ../run.sh !!!
    write_queue = asyncio.Queue(maxsize=10000)  # Queue for WebSocket logging

    async def send_to_websocket(data: dict):
        try:
            async with websockets.connect(WS_URL) as ws:
                await ws.send(json.dumps(data))
        except Exception as e:
            print(f"Error sending to WebSocket: {e}")

def should_log(method: str, url: str) -> bool:
    method = method.upper()
    regex = METHOD_FILTERS.get(method)
    return regex is not None and re.search(regex, url) is not None

def process_field(key: str, value: str):
    """Return (pattern, log_name, processed_value) or None if never log"""
    for rule in FIELD_RULES:
        pattern = rule.get("pattern")
        if re.search(pattern, key, re.IGNORECASE):
            mode = rule.get("mode", "obfuscate")
            log_name = rule.get("log_name") or key
            value_regex = rule.get("value_regex")

            if mode == "never":
                return None

            if mode == "log":
                return pattern, log_name, value

            if mode == "obfuscate":
                if value_regex:
                    try:
                        value = re.sub(value_regex, "*", value)
                    except Exception:
                        pass
                return pattern, log_name, value
    return None  # fallback: never log

def format_log_data(url: str, fields: dict, timestamp: str):
    log_data = f"# {urlparse(url).hostname} {timestamp}\n"
    log_data += f"url: {url}\n"
    for key, value in fields.items():
        log_data += f"{key}: {value}\n"
    return log_data

def generate_logfile(method: str, url: str) -> str:
    parsed_url = urlparse(url)
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

def log_entry(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(text + "\n")

def log_form(method, url, form_data, timestamp):
    log_data = format_log_data(url, form_data, timestamp)

    if LOG_TO_FILE:
        log_path = generate_logfile(method, url)
        log_entry(log_path, log_data)
    else:
        # Send log data through WebSocket
        log_data_dict = {
            "uuid": str(datetime.utcnow().timestamp()),  # placeholder for actual UUID generation
            "url": url,
            "timestamp": int(datetime.utcnow().timestamp()),
            "fields": {k: v for k, v in form_data.items()}
        }
        #"fields": [{"name": k, "content": v} for k, v in form_data.items()]
        asyncio.get_event_loop().create_task(send_to_websocket(log_data_dict))

def log_json(method, url, json_data, timestamp):
    """Log JSON data to a file or send via WebSocket."""
    log_data = format_log_data(url, json_data, timestamp)

    if LOG_TO_FILE:
        log_path = generate_logfile(method, url)
        log_entry(log_path, log_data)
    else:
        # Send log data through WebSocket
        log_data_dict = {
            "uuid": str(datetime.utcnow().timestamp()),  # Placeholder for actual UUID generation
            "url": url,
            "timestamp": int(datetime.utcnow().timestamp()),
            "fields": flatten_json(json_data)  # Flatten the JSON data
        }
        asyncio.get_event_loop().create_task(send_to_websocket(log_data_dict))

def flatten_json(data):
    """Flatten a JSON object, converting nested objects into key-value pairs."""
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

# -----------------------------
# mitmproxy request hook
# -----------------------------
def request(flow: http.HTTPFlow) -> None:
    method = flow.request.method
    url = flow.request.url
    timestamp = datetime.now().astimezone().isoformat()

    if not should_log(method, url):
        if DEBUG_OUTPUT: print(f"Not logging {url}")
        return


    if method.upper() == "POST":
        content_type = flow.request.headers.get("content-type", "")
        if DEBUG_OUTPUT: print(f"{content_type=}")

        body = flow.request.get_text()

        # For form data like application/x-www-form-urlencoded
        if "application/x-www-form-urlencoded" in content_type:
            parsed = flow.request.urlencoded_form

            log_form(method, url, parsed, timestamp)

        elif "application/json" in content_type:
            try:
                data = json.loads(body)
                if isinstance(data, dict):
                    log_json(method, url, data, timestamp)
            except Exception:
                log_path = generate_logfile(method, url)
                log_entry(log_path, "JSON PARSE ERROR\n")

        elif "multipart/form-data" in content_type:
            try:
                form_data = flow.request.multipart_form
                log_form(method, url, form_data, timestamp)

            except Exception:
                log_path = generate_logfile(method, url)
                log_entry(log_path, "MULTIPART PARSE ERROR\n")

        else:
            log_path = generate_logfile(method, url)
            log_entry(log_path, body + "\n")

    elif method.upper() == "GET":
        parsed = flow.request.query
        log_form(method, url, parsed, timestamp)
