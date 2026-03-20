import json

subscribers = set()


async def register(ws):
    subscribers.add(ws)


async def unregister(ws):
    subscribers.discard(ws)


async def broadcast(data):
    dead = []
    print(f"broadcasting {data}")

    for ws in subscribers:
        try:
            await ws.send(json.dumps(data))
        except:
            dead.append(ws)

    for ws in dead:
        subscribers.discard(ws)
