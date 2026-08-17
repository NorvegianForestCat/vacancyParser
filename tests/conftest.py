import pytest
import aiosqlite
import src.dbContext


@pytest.fixture(scope="function")
async def db():
    conn = await aiosqlite.connect(":memory:")
    await conn.execute("PRAGMA foreign_keys = ON;")
    await src.dbContext.init_db(conn)
    
    yield conn
    
    await conn.close()
