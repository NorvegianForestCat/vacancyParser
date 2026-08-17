import pytest
import src.dbContext

class TestDbContext:
    async def test_init_db(self, db):
        # Check if the tables exist
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = await cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        assert "vacancies" in table_names
        assert "skills" in table_names
    
    async def test_init_db_idempotent(self, db):
        # Call init_db again to ensure it doesn't raise an error
        await src.dbContext.init_db(db)
        
        # Check if the tables still exist
        cursor = await db.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = await cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        assert "vacancies" in table_names
        assert "skills" in table_names
    
    async def test_upsert_vacancy(self, db):
        vacancy_1 = {"title": "Old",
                    "company": "Company A",
                    "url": "http://example.com/vacancy1",
                    "salary_from": 50000,
                    "salary_to": 70000,
                    "currency": "USD",
                    "source": "Example Source",
                    "published_at": "2023-01-01T00:00:00Z",
                    "skills": ["Django"]}
        vacancy_2 = {"title": "New",
                    "company": "Company A",
                    "url": "http://example.com/vacancy1",
                    "skills": ["ASP.NET"]}
        
        await src.dbContext.save_vacancies(db, [vacancy_1])
        saved_count = await src.dbContext.save_vacancies(db, [vacancy_2])
        
        assert saved_count == 1
        
        cursor = await db.execute("SELECT COUNT(*) from vacancies")
        count = (await cursor.fetchone())[0]
        
        assert count == 1
        
        cursor = await db.execute("SELECT title from vacancies WHERE url = 'http://example.com/vacancy1'")
        title = (await cursor.fetchone())[0]
                
        assert title == "New"


    async def test_save_vacancies(self, db):
        vacancies = [
            {
                "title": "Python Developer",
                "company": "Tech Corp",
                "url": "http://example.com/vacancy1",
                "salary_from": 50000,
                "salary_to": 70000,
                "currency": "USD",
                "source": "Example Source",
                "published_at": "2023-01-01T00:00:00Z",
                "skills": ["Python", "Django"]
            },
            {
                "title": "Frontend Developer",
                "company": "Web Solutions",
                "url": "http://example.com/vacancy2",
                "salary_from": 40000,
                "salary_to": 60000,
                "currency": "USD",
                "source": "Example Source",
                "published_at": "2023-01-02T00:00:00Z",
                "skills": ["JavaScript", "React"]
            }
        ]
        
        saved_count = await src.dbContext.save_vacancies(db, vacancies)
        assert saved_count == 2
        
    async def test_get_topskills(self, db):
        vacancies = [
                {
                    "title": "Python Developer",
                    "company": "Tech Corp",
                    "url": "http://example.com/vacancy1",
                    "salary_from": 50000,
                    "salary_to": 70000,
                    "currency": "USD",
                    "source": "Example Source",
                    "published_at": "2023-01-01T00:00:00Z",
                    "skills": ["Python", "Django"]
                },
                {
                    "title": "Frontend Developer",
                    "company": "Web Solutions",
                    "url": "http://example.com/vacancy2",
                    "salary_from": 40000,
                    "salary_to": 60000,
                    "currency": "USD",
                    "source": "Example Source",
                    "published_at": "2023-01-02T00:00:00Z",
                    "skills": ["JavaScript", "React", "python", " JaVaScRipt", "ASP.NET "]
                }
            ]
        await src.dbContext.save_vacancies(db, vacancies)
        
        topskills = await src.dbContext.get_topskills(db, limit=8)
        assert len(topskills) == 5
        
        name, count = topskills[0]
        assert name == "python"
        assert count == 2
