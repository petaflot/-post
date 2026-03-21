"""
    ChatGPT handler
"""
HANDLER_NAME = "OpenAI/ChatGPT"

regex_match = r"https?://(?:[a-zA-Z0-9-]+\.)*chatgpt\.com.*"

import re, json


def handle_request(url, request, timestamp):
    #dir_request = "['__abstractmethods__', '__annotations__', '__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__firstlineno__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__static_attributes__', '__str__', '__subclasshook__', '__weakref__', '_abc_impl', '_get_cookies', '_get_multipart_form', '_get_query', '_get_urlencoded_form', '_set_cookies', '_set_multipart_form', '_set_query', '_set_urlencoded_form', '_update_host_and_authority', 'anticache', 'anticomp', 'authority', 'constrain_encoding', 'content', 'cookies', 'copy', 'data', 'decode', 'encode', 'first_line_format', 'from_state', 'get_content', 'get_state', 'get_text', 'headers', 'host', 'host_header', 'http_version', 'is_http10', 'is_http11', 'is_http2', 'is_http3', 'json', 'make', 'method', 'multipart_form', 'path', 'path_components', 'port', 'pretty_host', 'pretty_url', 'query', 'raw_content', 'scheme', 'set_content', 'set_state', 'set_text', 'stream', 'text', 'timestamp_end', 'timestamp_start', 'trailers', 'url', 'urlencoded_form']"
    #pprint(request)

    if re.match(r"https://chatgpt\.com/ces/statsc/flush.*", url): return

    # https://chatgpt.com/backend-anon/f/conversation/prepare streams the input to the LLM!

    # https://chatgpt.com/backend-anon/sentinel/chat-requirements/finalize if I remember well, this is where the prompt is sent

    print(f"{HANDLER_NAME}: ignoring request : {url}")
    #pprint(request.raw_content)

    return None

def handle_response(url, request, response, timestamp):
    if re.search("chatgpt\\.com/backend.*/conversation$", url):
        response_text = ''
        response_content = response.content.decode('utf-8')
        events = response_content.split('\n\ndata:')

        for event in events:
            if event.strip():  # Skip empty events
                event = event.split('\n')
                for line in range(0,len(event),1):
                    if event[line].startswith('data: '):
                        try:
                            line_data = json.loads(event[line][6:])
                        except json.JSONDecodeError:
                            print(f"JSONDecodeError[{HANDLER_NAME}]: {event[line]}")
                        else:
                            if type(line_data) is dict and type(line_data['v']) is list:
                                response_text += line_data['v'][0]['v']
                            else:
                                pass
                            try:
                                # this appears a LOT of times, but we catch it only once
                                conversation_id = line_data['v']['conversation_id']
                            except:
                                pass

                    """
                    else:
                        # NOTE: this kinda gets the original message posted back.. but it used to be caught in handle_request() see f32f5ee610bffbd242cb2f6f427b420530c78c7d
                        #from pprint import pprint
                        try:
                            # Direct JSON handling for other parts of the event
                            line_data = json.loads(event[line])
                        except json.JSONDecodeError:
                            print(f"JSONDecodeError [1b]: {event[line]}")
                        else:
                            # Capture conversation_id from direct JSON data
                            conversation_id = line_data.get('conversation_id', conversation_id)
                            if 'messages' in line_data:
                                for msg in line_data['messages']:
                                    print(f"\t{msg['id']=}")
                                    print(f"\t{msg['content']['content_type']=}")
                                    response_text = '\n'.join(msg['content']['parts'])
                            
                    """
        # TODO log, do some tracking.. etc.
        try:
            print(f"ChatGPT[{HANDLER_NAME}] {conversation_id=} {response_text=}")
        except:
            pass
    #else:
    #    print(f"IGNORED {url}")
    #    print(dir(response))
