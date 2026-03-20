import json
from quart import websocket
from .db import write_queue
from .stream import broadcast


async def ingest_ws():
    while True:
        msg = await websocket.receive()
        data = json.loads(msg)

        await write_queue.put(data)

        await broadcast({
            "uuid": data["uuid"],
            "url": data["url"],
            "timestamp": data["timestamp"]
        })
