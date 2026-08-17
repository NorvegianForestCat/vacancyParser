import aiosqlite
from pathlib import Path

DB_PATH = Path("data/vacancies.db")


async def get_db() -> aiosqlite.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    dbContext = await aiosqlite.connect(DB_PATH)
    await dbContext.execute("PRAGMA foreign_keys = ON;")
    
    return dbContext

async def init_db(dbContext: aiosqlite.Connection) -> None:
    await dbContext.execute("""
        CREATE TABLE IF NOT EXISTS vacancies (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            company TEXT,
            url TEXT UNIQUE,
            salary_from INTEGER,
            salary_to INTEGER,
            currency TEXT,
            source TEXT,
            published_at TEXT
        )                        
    """)
    
    await dbContext.execute("""
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY,
                vacancy_id INT NOT NULL REFERENCES Vacancies(id),
                name TEXT NOT NULL,
                UNIQUE(vacancy_id, name)
            )                        
        """)
    
    await dbContext.commit()
    
async def save_vacancies(dbContext: aiosqlite.Connection, vacancies: list[dict]) -> int:
    saved_cnt = 0
    
    for vacancy in vacancies:
        cursor = await dbContext.execute(
            """
            INSERT INTO vacancies (title, company, url, salary_from, salary_to, currency, source, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                title = excluded.title,
                company =      excluded.company,
                salary_from =  excluded.salary_from,
                salary_to =    excluded.salary_to,
                currency =     excluded.currency
                
            RETURNING id
            """,
            (
                vacancy.get("title"),
                vacancy.get("company"),
                vacancy.get("url"),
                vacancy.get("salary_from"),
                vacancy.get("salary_to"),
                vacancy.get("currency"),
                vacancy.get("source", "hh"),
                vacancy.get("published_at"),
            )
        )
        
        last_id = (await cursor.fetchone())[0]
        
        for skill in vacancy.get("skills", []):
            if skill:
                await dbContext.execute(
                    "INSERT OR IGNORE INTO skills (vacancy_id, name) VALUES (?, ?)",
                    (last_id, skill.strip().lower().replace(' ', '_'))
                )
        
        saved_cnt += cursor.rowcount
        
    await dbContext.commit()
        
    return saved_cnt

async def get_topskills(dbContext: aiosqlite.Connection, limit: int = 10) -> list[tuple]:
    
    cursor = await dbContext.execute(
        """
        SELECT name, COUNT(*) AS cnt
        FROM skills
        GROUP BY name
        ORDER BY cnt DESC
        LIMIT ?
        """,
        (limit,)
    )
    
    return await cursor.fetchall()
