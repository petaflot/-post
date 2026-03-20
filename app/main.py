import asyncio
from quart import Quart, websocket, render_template, request
from .db import init_db, db_writer
from .ingest import ingest_ws
from .stream import register, unregister
from . import api

app = Quart(__name__, template_folder="templates")


@app.before_serving
async def startup():
    await init_db()
    asyncio.create_task(db_writer())


# ---- WebSockets ----

@app.websocket("/ingest")
async def ingest():
    await ingest_ws()


@app.websocket("/stream")
async def stream():
    ws = websocket._get_current_object()
    await register(ws)

    try:
        while True:
            await asyncio.sleep(60)
    finally:
        await unregister(ws)


# ---- HTTP ----

@app.route("/")
async def index():
    return await render_template("index.html")


@app.route("/post")
async def post_page():
    return await render_template("post.html")


@app.route("/posts")
async def posts():
    return await api.list_posts()


@app.route("/posts/<uuid>")
async def post(uuid):
    return await api.get_post(uuid)

@app.route("/posts/<uuid>", methods=["DELETE"])
async def delete(uuid):
    return await api.delete_post(uuid)

@app.route("/test", methods=["GET", "POST"])
async def form():
    if request.method == "POST":
        data = await request.form
        print("##### RAW TEST FORM DATA #####")
        for k, v in data.items():
            print(f"{k:<12}{v}")
        print("##############################")
        return f"Thanks! your comment was posted into nothingness ; <a href='/'>verify interception now</a>"

    return await render_template("test.html")
