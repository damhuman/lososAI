import asyncio
import json

async def check_packages():
    from app.db.session import AsyncSessionLocal
    from app.db.models.product import Product
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        # Get all products
        query = select(Product).limit(5)
        result = await session.execute(query)
        products = result.scalars().all()
        
        print(f"Found {len(products)} products")
        for product in products:
            print(f"\nProduct: {product.name}")
            print(f"Packages type: {type(product.packages)}")
            print(f"Packages content: {json.dumps(product.packages, indent=2)}")
            
            # Check if any package is missing 'id' field
            for i, package in enumerate(product.packages):
                if isinstance(package, dict):
                    print(f"  Package {i}: {package.keys()}")
                    if 'id' not in package:
                        print(f"    ❌ Missing 'id' field!")
                    if 'type' in package:
                        print(f"    📝 Has 'type' field: {package['type']}")
                    if 'price' in package:
                        print(f"    💰 Has 'price' field: {package['price']}")

if __name__ == "__main__":
    asyncio.run(check_packages())