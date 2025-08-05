"""Test configuration and fixtures."""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import base64
import os

# Mark all test functions in this module as asyncio
pytestmark = pytest.mark.asyncio

from app.main import app
from app.db.session import Base, get_async_session
from app.db.models.product import Category, Product, District, PromoCode
from app.db.models.user import User
from app.db.models.order import Order, OrderItem


# Test database URL - using PostgreSQL test database
TEST_DATABASE_URL = "postgresql+asyncpg://seafood_user:seafood123@db:5432/seafood_test"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
)


# Removed event_loop fixture to use pytest-asyncio's default


@pytest.fixture(scope="function")
async def test_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(test_engine) as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(test_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client."""
    app.dependency_overrides[get_async_session] = lambda: test_session
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def admin_headers():
    """Create admin authentication headers."""
    credentials = base64.b64encode(b"admin:admin123").decode("ascii")
    return {"Authorization": f"Basic {credentials}"}


@pytest.fixture
async def sample_category(test_session: AsyncSession) -> Category:
    """Create a sample category."""
    category = Category(
        id="test_category",
        name="Test Category",
        description="Test category description",
        icon="🐟",
        order=1,
        is_active=True
    )
    test_session.add(category)
    await test_session.commit()
    return category


@pytest.fixture
async def sample_product(test_session: AsyncSession, sample_category: Category) -> Product:
    """Create a sample product."""
    product = Product(
        id="test_product",
        category_id=sample_category.id,
        name="Test Product",
        description="Test product description",
        price_per_kg=100.0,
        packages=[
            {
                "id": "1kg",
                "type": "1кг",
                "weight": 1.0,
                "unit": "кг",
                "price": 100.0,
                "available": True
            }
        ],
        is_active=True,
        is_featured=False
    )
    test_session.add(product)
    await test_session.commit()
    return product


@pytest.fixture
async def sample_user(test_session: AsyncSession) -> User:
    """Create a sample user."""
    user = User(
        telegram_id=123456789,
        username="testuser",
        first_name="Test",
        last_name="User",
        language_code="uk",
        is_bot=False
    )
    test_session.add(user)
    await test_session.commit()
    return user


@pytest.fixture
async def sample_district(test_session: AsyncSession) -> District:
    """Create a sample district."""
    district = District(
        name="Test District",
        delivery_cost=50.0,
        is_active=True
    )
    test_session.add(district)
    await test_session.commit()
    return district


@pytest.fixture
async def sample_promo_code(test_session: AsyncSession) -> PromoCode:
    """Create a sample promo code."""
    promo = PromoCode(
        code="TEST10",
        discount_percent=10.0,
        is_active=True,
        is_gold_code=False
    )
    test_session.add(promo)
    await test_session.commit()
    return promo


@pytest.fixture
async def sample_order(
    test_session: AsyncSession, 
    sample_user: User, 
    sample_district: District,
    sample_product: Product
) -> Order:
    """Create a sample order."""
    order = Order(
        user_id=sample_user.id,
        district_id=sample_district.id,
        delivery_address="Test Address",
        phone_number="+380123456789",
        total_amount=150.0,
        delivery_cost=50.0,
        status="pending"
    )
    test_session.add(order)
    await test_session.flush()
    
    # Add order item
    order_item = OrderItem(
        order_id=order.id,
        product_id=sample_product.id,
        package_id="1kg",
        quantity=1,
        price_per_unit=100.0,
        total_price=100.0
    )
    test_session.add(order_item)
    await test_session.commit()
    return order


# Valid Telegram init data for testing
@pytest.fixture
def valid_telegram_init_data():
    """Valid Telegram Web App init data for testing."""
    return {
        "query_id": "test_query_id",
        "user": '{"id":123456789,"first_name":"Test","last_name":"User","username":"testuser","language_code":"uk"}',
        "auth_date": "1234567890",
        "hash": "test_hash"
    }


@pytest.fixture
def telegram_headers(valid_telegram_init_data):
    """Create Telegram authentication headers."""
    init_data_str = "&".join([f"{k}={v}" for k, v in valid_telegram_init_data.items()])
    return {"Authorization": f"tma {init_data_str}"}