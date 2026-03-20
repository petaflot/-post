import asyncio
import aiosqlite

DB_PATH = "data/traffic.db"
write_queue = asyncio.Queue(maxsize=10000)
BATCH_SIZE = 1


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript("""
        PRAGMA journal_mode=WAL;

        CREATE TABLE IF NOT EXISTS posts (
            post_uuid TEXT PRIMARY KEY,
            url TEXT NOT NULL,
            timestamp INTEGER NOT NULL
        );

        CREATE TABLE IF NOT EXISTS fields (
            post_uuid TEXT NOT NULL,
            field_name TEXT NOT NULL,
            field_content TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_posts_timestamp
            ON posts(timestamp DESC);

        CREATE INDEX IF NOT EXISTS idx_fields_post_uuid
            ON fields(post_uuid);
        """)
        await db.commit()


async def db_writer(batchlen=BATCH_SIZE):
    async with aiosqlite.connect(DB_PATH) as db:
        batch = []

        while True:
            item = await write_queue.get()
            batch.append(item)

            if len(batch) >= batchlen:
                await _flush(db, batch)
                batch.clear()


async def _flush(db, batch):
    for post in batch:
        await db.execute(
            "INSERT OR IGNORE INTO posts VALUES (?, ?, ?)",
            (post["uuid"], post["url"], post["timestamp"])
        )

        await db.executemany(
            "INSERT INTO fields VALUES (?, ?, ?)",
            [
                (post["uuid"], k, v)
                for k, v in post["fields"].items()
            ]
        )

    await db.commit()
