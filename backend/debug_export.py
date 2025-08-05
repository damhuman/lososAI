import asyncio
import pytest_asyncio
from httpx import AsyncClient
from datetime import datetime, timedelta
import base64

async def test_export():
    from app.main import app
    from app.db.session import get_async_session
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
    from sqlalchemy.pool import StaticPool
    from app.db.session import Base
    
    # Test database setup
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    TestSessionLocal = async_sessionmaker(bind=test_engine, class_=AsyncSession, expire_on_commit=False)
    
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create test session
    async with TestSessionLocal() as test_session:
        def override_get_db():
            return test_session
        
        app.dependency_overrides[get_async_session] = override_get_db
        
        # Admin headers
        credentials = base64.b64encode(b"admin:admin123").decode("ascii")
        headers = {"Authorization": f"Basic {credentials}"}
        
        # Test dates
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as client:
            response = await client.get(
                f"/api/v1/admin/orders/export?start_date={start_date}&end_date={end_date}",
                headers=headers
            )
            print(f"Status: {response.status_code}")
            if response.status_code != 200:
                print(f"Response: {response.text}")
            else:
                print("Export successful!")
        
        app.dependency_overrides.clear()

if __name__ == "__main__":
    asyncio.run(test_export())