#!/usr/bin/env python3
"""
Script to seed default admin settings for the enhanced order management system
"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.db.models.admin_settings import AdminSetting
from app.schemas.admin_settings import DEFAULT_ADMIN_SETTINGS


async def seed_admin_settings():
    """Seed default admin settings if they don't exist"""
    async with AsyncSessionLocal() as session:
        print("🌱 Seeding default admin settings...")
        
        created_count = 0
        updated_count = 0
        
        for setting_data in DEFAULT_ADMIN_SETTINGS:
            # Check if setting already exists
            result = await session.execute(
                select(AdminSetting).where(AdminSetting.key == setting_data["key"])
            )
            existing_setting = result.scalar_one_or_none()
            
            if existing_setting:
                print(f"⚠️  Setting '{setting_data['key']}' already exists, skipping")
                updated_count += 1
            else:
                # Create new setting
                new_setting = AdminSetting(**setting_data)
                session.add(new_setting)
                print(f"✅ Created setting: {setting_data['key']} = {setting_data['value']}")
                created_count += 1
        
        await session.commit()
        
        print(f"""
🎉 Admin settings seeding completed!
   
📊 Summary:
   • Created: {created_count} new settings
   • Existing: {updated_count} settings (skipped)
   • Total: {len(DEFAULT_ADMIN_SETTINGS)} settings
        """)
        
        # Display all current settings
        print("📋 Current admin settings:")
        result = await session.execute(select(AdminSetting).order_by(AdminSetting.category, AdminSetting.key))
        all_settings = result.scalars().all()
        
        current_category = None
        for setting in all_settings:
            if setting.category != current_category:
                current_category = setting.category
                print(f"\n📂 {current_category or 'Uncategorized'}:")
            
            typed_value = setting.get_typed_value()
            print(f"   • {setting.name}: {typed_value} ({setting.setting_type})")


if __name__ == "__main__":
    print("🚀 Starting admin settings seeding process...")
    asyncio.run(seed_admin_settings())
    print("✅ Seeding process completed successfully!")