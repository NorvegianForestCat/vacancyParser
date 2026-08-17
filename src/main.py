from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Query
import aiosqlite
from src.dbContext import init_db, save_vacancies, get_db, get_topskills


@asynccontextmanager
async def lifespan(app: FastAPI):
    dbContext = await get_db()
    await init_db(dbContext)
    app.state.db = dbContext
    
    yield
    
    await dbContext.close()

app = FastAPI(
    title="Vacancy Parser",
    version="0.0.1",
    lifespan=lifespan
)

async def get_db_dependency() -> aiosqlite.Connection:
    return app.state.db


@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/topskills")
async def get_top_skills(
    limit: int = Query(10, ge=1, le=100),
    dbContext: aiosqlite.Connection = Depends(get_db_dependency)
):
    skills = await get_topskills(dbContext, limit)
    return {
        "skills": [
            {"name": name, "count": count}
            for name, count in skills
        ]
    }

@app.post("/parse")
async def parse_vacancies(
    query: str = "python developer",
    page: int = Query(0, ge=0),
    dbContext: aiosqlite.Connection = Depends(get_db_dependency)
):
    return {
        "message": f"Parsing vacancies for query '{query}' on page {page}...",
        "saved": 0
    }
    