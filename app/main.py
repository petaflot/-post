import asyncio
from quart import Quart, websocket, render_template, request, send_file
from .db import init_db, db_writer
from .ingest import ingest_ws
from .stream import register, unregister
from . import api
from pathlib import Path

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

EXTENSION_DIR = Path(__file__).parent / "browser_extension"

def generate_zip():
    import zipfile, os
    zip_path = Path(__file__).parent / "crosspost.zip"

    # Create a ZIP file with the content of the extension directory
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(EXTENSION_DIR):
            for file in files:
                # Add each file to the ZIP file, preserving the directory structure
                file_path = Path(root) / file
                zipf.write(file_path, file_path.relative_to(EXTENSION_DIR))
    
    return zip_path

@app.route('/download')
async def download():
    # Generate the ZIP file on the fly
    zip_path = generate_zip()

    # Serve the ZIP file to the user for download
    return await send_file(str(zip_path), mimetype='application/zip', as_attachment=True)

@app.route("/about")
async def about_page():
    return await render_template("about.html")

