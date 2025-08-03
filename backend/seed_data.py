"""
Seed data script to populate the database with initial data for testing
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionLocal
from app.db.models.product import Category, Product, District, PromoCode


async def create_categories():
    """Create product categories"""
    categories = [
        Category(
            id="salmon",
            name="Лосось",
            icon="🐟",
            order=1,
            is_active=True
        ),
        Category(
            id="shellfish",
            name="Молюски",
            icon="🦐",
            order=2,
            is_active=True
        ),
        Category(
            id="tomyum",
            name="Tom Yum набір",
            icon="🍜",
            order=3,
            is_active=True
        ),
        Category(
            id="caviar",
            name="Ікра",
            icon="🥚",
            order=4,
            is_active=True
        )
    ]
    return categories


async def create_products():
    """Create sample products"""
    products = [
        # Salmon products
        Product(
            id="salmon_salted_001",
            category_id="salmon",
            name="Лосось солений",
            description="Свіжий норвезький лосось слабосолений",
            price_per_kg=750,
            image_url="/static/images/salmon_salted.jpg",
            packages=[
                {"id": "05kg", "weight": 0.5, "unit": "кг", "available": True},
                {"id": "1kg", "weight": 1, "unit": "кг", "available": True},
                {"id": "plate", "weight": 1.6, "unit": "пласт", "available": True, "note": "Середня вага пласта"}
            ],
            is_active=True,
            is_featured=True
        ),
        Product(
            id="salmon_smoked_001",
            category_id="salmon",
            name="Лосось копчений",
            description="Свіжий норвезький лосось холодного копчення",
            price_per_kg=850,
            image_url="/static/images/salmon_smoked.jpg",
            packages=[
                {"id": "05kg", "weight": 0.5, "unit": "кг", "available": True},
                {"id": "1kg", "weight": 1, "unit": "кг", "available": True},
                {"id": "plate", "weight": 1.6, "unit": "пласт", "available": True, "note": "Середня вага пласта"}
            ],
            is_active=True,
            is_featured=True
        ),
        Product(
            id="salmon_fresh_001",
            category_id="salmon",
            name="Лосось холоджений",
            description="Свіжий норвезький лосось для приготування",
            price_per_kg=650,
            image_url="/static/images/salmon_fresh.jpg",
            packages=[
                {"id": "05kg", "weight": 0.5, "unit": "кг", "available": True},
                {"id": "1kg", "weight": 1, "unit": "кг", "available": True},
                {"id": "2kg", "weight": 2, "unit": "кг", "available": True}
            ],
            is_active=True
        ),
        Product(
            id="trout_001",
            category_id="salmon",
            name="Форель солена",
            description="Свіжа форель слабосолена",
            price_per_kg=550,
            image_url="/static/images/trout.jpg",
            packages=[
                {"id": "05kg", "weight": 0.5, "unit": "кг", "available": True},
                {"id": "1kg", "weight": 1, "unit": "кг", "available": True}
            ],
            is_active=True
        ),
        
        # Shellfish products
        Product(
            id="shrimp_001",
            category_id="shellfish",
            name="Креветки королівські",
            description="Великі очищені креветки",
            price_per_kg=450,
            image_url="/static/images/shrimp.jpg",
            packages=[
                {"id": "1kg", "weight": 1, "unit": "кг", "available": True}
            ],
            is_active=True,
            is_featured=True
        ),
        Product(
            id="mussels_001",
            category_id="shellfish",
            name="Мідії варені",
            description="Варені мідії в раковинах",
            price_per_kg=200,
            image_url="/static/images/mussels.jpg",
            packages=[
                {"id": "1kg", "weight": 1, "unit": "кг", "available": True},
                {"id": "2kg", "weight": 2, "unit": "кг", "available": True}
            ],
            is_active=True
        ),
        Product(
            id="crab_001",
            category_id="shellfish",
            name="Краб варений",
            description="М'ясо краба варене",
            price_per_kg=800,
            image_url="/static/images/crab.jpg",
            packages=[
                {"id": "05kg", "weight": 0.5, "unit": "кг", "available": True}
            ],
            is_active=True
        ),
        
        # Tom Yum kit
        Product(
            id="tomyum_kit_001",
            category_id="tomyum",
            name="Tom Yum набір повний",
            description="Повний набір для приготування супу Tom Yum: паста, трави, креветки",
            price_per_kg=350,
            image_url="/static/images/tomyum_kit.jpg",
            packages=[
                {"id": "set", "weight": 1, "unit": "набір", "available": True, "note": "Набір на 4 порції"}
            ],
            is_active=True,
            is_featured=True
        ),
        
        # Caviar products
        Product(
            id="caviar_red_001",
            category_id="caviar",
            name="Ікра лососева зерниста",
            description="Свіжа зерниста ікра лососевих риб",
            price_per_kg=1200,
            image_url="/static/images/caviar_red.jpg",
            packages=[
                {"id": "100g", "weight": 0.1, "unit": "100г", "available": True},
                {"id": "250g", "weight": 0.25, "unit": "250г", "available": True},
                {"id": "500g", "weight": 0.5, "unit": "500г", "available": True}
            ],
            is_active=True,
            is_featured=True
        ),
        Product(
            id="caviar_black_001",
            category_id="caviar",
            name="Ікра осетрова",
            description="Преміум ікра осетрових риб",
            price_per_kg=3500,
            image_url="/static/images/caviar_black.jpg",
            packages=[
                {"id": "50g", "weight": 0.05, "unit": "50г", "available": True},
                {"id": "100g", "weight": 0.1, "unit": "100г", "available": True}
            ],
            is_active=True
        )
    ]
    return products


async def create_districts():
    """Create delivery districts"""
    districts = [
        District(name="Шевченківський", is_active=True),
        District(name="Печерський", is_active=True),
        District(name="Подільський", is_active=True),
        District(name="Оболонський", is_active=True),
        District(name="Дарницький", is_active=True),
        District(name="Дніпровський", is_active=True),
        District(name="Деснянський", is_active=True),
        District(name="Солом'янський", is_active=True),
        District(name="Святошинський", is_active=True),
        District(name="Голосіївський", is_active=True)
    ]
    return districts


async def create_promo_codes():
    """Create sample promo codes"""
    promo_codes = [
        PromoCode(
            code="GOLD2024",
            discount_percent=10,
            is_active=True,
            is_gold_code=True,
            usage_limit=100
        ),
        PromoCode(
            code="WELCOME50",
            discount_amount=50,
            is_active=True,
            usage_limit=50
        ),
        PromoCode(
            code="SEAFOOD15",
            discount_percent=15,
            is_active=True,
            usage_limit=200
        )
    ]
    return promo_codes


async def seed_database():
    """Main function to seed the database"""
    async with AsyncSessionLocal() as session:
        try:
            print("🌱 Starting database seeding...")
            
            # Create categories
            print("📁 Creating categories...")
            categories = await create_categories()
            for category in categories:
                session.add(category)
            
            # Create products
            print("🐟 Creating products...")
            products = await create_products()
            for product in products:
                session.add(product)
            
            # Create districts
            print("🗺️ Creating districts...")
            districts = await create_districts()
            for district in districts:
                session.add(district)
            
            # Create promo codes
            print("🎫 Creating promo codes...")
            promo_codes = await create_promo_codes()
            for promo_code in promo_codes:
                session.add(promo_code)
            
            # Commit all changes
            await session.commit()
            
            print("✅ Database seeding completed successfully!")
            print(f"   - Created {len(categories)} categories")
            print(f"   - Created {len(products)} products")
            print(f"   - Created {len(districts)} districts")
            print(f"   - Created {len(promo_codes)} promo codes")
            
        except Exception as e:
            print(f"❌ Error seeding database: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())