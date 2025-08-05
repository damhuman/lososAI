import asyncio
import pytest_asyncio
from httpx import AsyncClient
import base64

async def test_products_500():
    from app.main import app
    from app.db.session import get_async_session
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
    from sqlalchemy.pool import StaticPool
    from app.db.session import Base
    
    # Test database setup
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=True,  # Enable SQL logging
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
        
        # Test the exact failing request
        async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as client:
            try:
                response = await client.get(
                    "/api/v1/admin/products?page=1&size=100",
                    headers=headers
                )
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                
                if response.status_code == 500:
                    print("ERROR: 500 Internal Server Error!")
                    # Try to get more details
                    print("Headers:", dict(response.headers))
                else:
                    print("Success!")
                    data = response.json()
                    print(f"Total items: {data.get('total', 0)}")
                    print(f"Items length: {len(data.get('items', []))}")
                    
            except Exception as e:
                print(f"Exception: {e}")
                import traceback
                traceback.print_exc()
        
        app.dependency_overrides.clear()

if __name__ == "__main__":
    asyncio.run(test_products_500())