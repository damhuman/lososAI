"""Test configuration and fixtures - Fixed version."""
import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
import base64

from app.main import app
from app.db.session import Base, get_async_session
from app.db.models.product import Category, Product, District, PromoCode
from app.db.models.user import User
from app.db.models.order import Order, OrderItem


# Test database URL - using in-memory SQLite for faster tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create test engine with proper settings for SQLite
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={
        "check_same_thread": False,
    },
)

TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest_asyncio.fixture
async def test_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async with TestSessionLocal() as session:
        try:
            yield session
        finally:
            await session.rollback()

    # Drop all tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(test_session: AsyncSession, sample_user: User) -> AsyncGenerator[AsyncClient, None]:
    """Create a test client with database override."""
    def override_get_db():
        return test_session
    
    # Mock the get_current_user dependency for tests
    def mock_get_current_user():
        return sample_user
    
    from app.api.deps import get_current_user
    app.dependency_overrides[get_async_session] = override_get_db
    app.dependency_overrides[get_current_user] = mock_get_current_user
    
    try:
        async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as ac:
            yield ac
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def admin_headers():
    """Create admin authentication headers."""
    credentials = base64.b64encode(b"admin:admin123").decode("ascii")
    return {"Authorization": f"Basic {credentials}"}


@pytest_asyncio.fixture
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
    await test_session.refresh(category)
    return category


@pytest_asyncio.fixture
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
    await test_session.refresh(product)
    return product


@pytest_asyncio.fixture
async def sample_user(test_session: AsyncSession) -> User:
    """Create a sample user."""
    user = User(
        id=123456789,  # This is the telegram_id
        username="testuser",
        first_name="Test",
        last_name="User",
        language_code="uk"
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def sample_district(test_session: AsyncSession) -> District:
    """Create a sample district."""
    district = District(
        name="Test District",
        delivery_cost=50.0,
        is_active=True
    )
    test_session.add(district)
    await test_session.commit()
    await test_session.refresh(district)
    return district


@pytest_asyncio.fixture
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
    await test_session.refresh(promo)
    return promo


@pytest_asyncio.fixture
async def sample_order(
    test_session: AsyncSession, 
    sample_user: User, 
    sample_district: District,
    sample_product: Product
) -> Order:
    """Create a sample order."""
    from datetime import datetime, timedelta
    from app.db.models.order import OrderStatus, DeliveryTimeSlot
    
    order = Order(
        order_id=1001,
        user_id=sample_user.id,
        district_id=sample_district.id,
        status=OrderStatus.PENDING,
        total_amount=150.0,
        delivery_time_slot=DeliveryTimeSlot.MORNING,
        delivery_date=datetime.now() + timedelta(days=1),
        delivery_address="Test Address",
        contact_name=f"{sample_user.first_name} {sample_user.last_name}",
        contact_phone="+380123456789"
    )
    test_session.add(order)
    await test_session.flush()
    
    # Add order item
    order_item = OrderItem(
        order_id=order.id,
        product_id=sample_product.id,
        product_name=sample_product.name,
        package_id="1kg",
        weight=1.0,
        unit="кг",
        quantity=1,
        price_per_unit=100.0,
        total_price=100.0
    )
    test_session.add(order_item)
    await test_session.commit()
    await test_session.refresh(order)
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