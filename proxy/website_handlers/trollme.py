regex_match = r".*"

def handle_response(url, request, response, timestamp):
    # juste une ânerie..
    flow.response.content = flow.response.content.replace(b"Nice", b"Brice de Nice").replace(b"mine de rien", bytes("ce gisement est épuisé",'utf-8'))

    # GOOD LESSON LEARNED: always read the code you execute on your device! (NOTE: this messes everything up, not just the text! you wanted to take down the Internet?")
    flow.response.content = flow.response.content.replace(b'e',b'3').replace(b'l',b'1').replace(b'i',b'l').replace(b'L',b'7')
