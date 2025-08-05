#!/usr/bin/env python3
"""
Data migration script to migrate existing JSON packages to ProductPackage table.
Run this after the database migration is applied.
"""

import asyncio
import json
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.db.models.product import Product, ProductPackage


async def migrate_packages_data():
    """Migrate packages from JSON field to ProductPackage table."""
    async with AsyncSessionLocal() as session:
        # Get all products
        result = await session.execute(select(Product))
        products = result.scalars().all()
        
        print(f"Found {len(products)} products with packages to migrate")
        
        migrated_count = 0
        for product in products:
            if not product.packages or product.packages == [] or len(product.packages) == 0:
                continue
                
            print(f"Migrating packages for product {product.id}: {product.name}")
            migrated_count += 1
            
            # Convert JSON packages to ProductPackage records
            for i, pkg_data in enumerate(product.packages):
                # Handle different package data formats
                package_id = pkg_data.get('id') or pkg_data.get('type', f"pkg_{i}")
                name = pkg_data.get('name') or f"{pkg_data.get('weight', 0)}{pkg_data.get('unit', '')}"
                weight = float(pkg_data.get('weight', 0))
                unit = pkg_data.get('unit', 'кг')
                price = float(pkg_data.get('price', product.price_per_kg * weight))
                available = pkg_data.get('available', True)
                note = pkg_data.get('note')
                
                # Create ProductPackage record
                package = ProductPackage(
                    product_id=product.id,
                    package_id=package_id,
                    name=name,
                    weight=weight,
                    unit=unit,
                    price=price,
                    available=available,
                    sort_order=i,
                    note=note
                )
                
                session.add(package)
                print(f"  - Created package: {package_id} ({name})")
        
        await session.commit()
        print(f"Migration completed successfully! Migrated {migrated_count} products.")


async def verify_migration():
    """Verify that migration was successful."""
    async with AsyncSessionLocal() as session:
        # Count products with JSON packages
        result = await session.execute(select(Product))
        products = result.scalars().all()
        products_with_json = len([p for p in products if p.packages and len(p.packages) > 0])
        
        # Count ProductPackage records
        result = await session.execute(select(ProductPackage))
        package_records = len(result.scalars().all())
        
        print(f"Verification:")
        print(f"  - Products with JSON packages: {products_with_json}")
        print(f"  - ProductPackage records: {package_records}")
        
        if package_records > 0:
            print("Migration appears successful!")
        else:
            print("Warning: No ProductPackage records found!")


async def main():
    print("Starting packages data migration...")
    await migrate_packages_data()
    await verify_migration()

if __name__ == "__main__":
    asyncio.run(main())