#!/usr/bin/env python3
"""Fix products packages schema by adding missing type and price fields."""
import asyncio
import asyncpg
import json
import sys
import os

# Database connection
DATABASE_URL = "postgresql://seafood_user:seafood123@host.docker.internal:5432/seafood_store"

async def fix_products_schema():
    """Fix products packages to include type and price fields."""
    print("🔧 Fixing products packages schema...")
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Get all products with their packages
        print("\n📖 Reading current products...")
        rows = await conn.fetch("SELECT id, name, packages, price_per_kg FROM products")
        print(f"Found {len(rows)} products")
        
        fixed_count = 0
        
        for row in rows:
            product_id = row['id']
            product_name = row['name']
            packages_raw = row['packages']
            price_per_kg = row['price_per_kg']
            
            # Parse packages JSON if it's a string
            if isinstance(packages_raw, str):
                packages = json.loads(packages_raw)
            else:
                packages = packages_raw
            
            print(f"\n🔍 Checking product: {product_id} ({product_name})")
            print(f"   Price per kg: {price_per_kg}")
            print(f"   Current packages: {json.dumps(packages, ensure_ascii=False)}")
            
            # Check if packages need fixing
            needs_fix = False
            fixed_packages = []
            
            for pkg in packages:
                if 'type' not in pkg or 'price' not in pkg:
                    needs_fix = True
                    
                    # Create fixed package
                    fixed_pkg = pkg.copy()
                    
                    # Add type field if missing
                    if 'type' not in fixed_pkg:
                        weight = pkg.get('weight', 1.0)
                        unit = pkg.get('unit', 'кг')
                        if unit == 'пласт':
                            fixed_pkg['type'] = 'пласт'
                        else:
                            # Convert weight to readable format
                            if weight < 1:
                                fixed_pkg['type'] = f"{int(weight * 1000)}г"
                            else:
                                fixed_pkg['type'] = f"{weight:g}{unit}"
                    
                    # Add price field if missing
                    if 'price' not in fixed_pkg:
                        weight = pkg.get('weight', 1.0)
                        fixed_pkg['price'] = float(price_per_kg * weight)
                    
                    fixed_packages.append(fixed_pkg)
                else:
                    # Package is already correct
                    fixed_packages.append(pkg)
            
            if needs_fix:
                print(f"   ⚠️  Needs fixing")
                print(f"   ✅ Fixed packages: {json.dumps(fixed_packages, ensure_ascii=False)}")
                
                # Update the product in database
                await conn.execute(
                    "UPDATE products SET packages = $1 WHERE id = $2",
                    json.dumps(fixed_packages),
                    product_id
                )
                fixed_count += 1
                print(f"   💾 Updated in database")
            else:
                print(f"   ✅ Already correct")
        
        await conn.close()
        
        print(f"\n🎉 Schema fix completed!")
        print(f"   Fixed products: {fixed_count}/{len(rows)}")
        
        return fixed_count > 0
        
    except Exception as e:
        print(f"❌ Error fixing schema: {e}")
        import traceback
        traceback.print_exc()
        return False

async def verify_fix():
    """Verify that the fix worked."""
    print("\n🧪 Verifying fix...")
    
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Check a few products
        rows = await conn.fetch("SELECT id, name, packages FROM products LIMIT 3")
        
        all_good = True
        for row in rows:
            product_id = row['id']
            packages_raw = row['packages']
            
            # Parse packages JSON if it's a string
            if isinstance(packages_raw, str):
                packages = json.loads(packages_raw)
            else:
                packages = packages_raw
            
            print(f"\n✅ Product {product_id}:")
            for pkg in packages:
                has_type = 'type' in pkg
                has_price = 'price' in pkg
                print(f"   Package {pkg['id']}: type={'✅' if has_type else '❌'} price={'✅' if has_price else '❌'}")
                if not has_type or not has_price:
                    all_good = False
        
        await conn.close()
        
        if all_good:
            print("\n🎉 All packages have required fields!")
        else:
            print("\n⚠️  Some packages still missing fields")
        
        return all_good
        
    except Exception as e:
        print(f"❌ Error verifying fix: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting products schema fix...")
    
    # Fix the schema
    fixed = asyncio.run(fix_products_schema())
    
    if fixed:
        # Verify the fix
        verified = asyncio.run(verify_fix())
        if verified:
            print("\n✅ SUCCESS: Products schema fixed and verified!")
        else:
            print("\n⚠️  Schema fixed but verification failed")
    else:
        print("\n❌ Schema fix failed")
        sys.exit(1)