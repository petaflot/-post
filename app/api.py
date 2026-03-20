from quart import jsonify
import aiosqlite
from .db import DB_PATH


async def list_posts():
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT post_uuid, url, timestamp
            FROM posts
            ORDER BY timestamp DESC
            LIMIT 100
        """)
        rows = await cursor.fetchall()

    return jsonify([
        {"uuid": r[0], "url": r[1], "timestamp": r[2]}
        for r in rows
    ])

async def get_post(uuid):
    async with aiosqlite.connect(DB_PATH) as db:
        # Get post details
        cursor = await db.execute(
            "SELECT url, timestamp FROM posts WHERE post_uuid = ?",
            (uuid,)
        )
        post = await cursor.fetchone()

        # If the post is not found, return a 404 response
        if post is None:
            return {"error": "Post not found"}, 404

        # Get the associated fields for the post
        cursor = await db.execute(
            "SELECT field_name, field_content FROM fields WHERE post_uuid = ?",
            (uuid,)
        )
        fields = await cursor.fetchall()

    return {
        "uuid": uuid,
        "url": post[0],
        "timestamp": post[1],
        "fields": [
            {"name": f[0], "content": f[1]}
            for f in fields
        ]
    }

async def delete_post(uuid):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("DELETE FROM fields WHERE post_uuid = ?", (uuid,))
        await db.execute("DELETE FROM posts WHERE post_uuid = ?", (uuid,))
        await db.commit()

    return {"status": "deleted"}
