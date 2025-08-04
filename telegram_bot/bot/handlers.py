import json
import httpx
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, WebAppData
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from bot.keyboards import get_main_keyboard, get_admin_order_keyboard
from config import BACKEND_API_URL, ADMIN_CHAT_ID

router = Router()

# Messages
WELCOME_MESSAGE = """
🐟 Ласкаво просимо до магазину морепродуктів!

Тут ви знайдете:
• Свіжий лосось та форель
• Креветки та молюски
• Набори для Tom Yum
• Різні види ікри

📦 Замовлення, оформлені до 18:00, доставляються наступного дня
⚠️ Увага! Фактична вага може відрізнятися на ±10%
"""

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.clear()
    
    keyboard = get_main_keyboard()
    
    print(f"🚀 /start command from user {message.from_user.id} ({message.from_user.first_name})")
    
    await message.answer(
        WELCOME_MESSAGE,
        reply_markup=keyboard
    )

@router.message()
async def handle_any_message(message: Message):
    """Handle any other message for debugging"""
    print(f"📨 Received message from {message.from_user.id}: {message.text}")
    if message.web_app_data:
        print(f"🌐 Has web app data: {message.web_app_data.data}")
    else:
        print("❌ No web app data in this message")


@router.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    """Handle data from Web App (order submission)"""
    print(f"📱 Received web app data from user {message.from_user.id}")
    print(f"📝 Raw data: {message.web_app_data.data}")
    
    try:
        # Parse order data from Web App
        order_data = json.loads(message.web_app_data.data)
        print(f"📦 Parsed order data: {order_data}")
        
        # Extract order information
        user_id = order_data.get("user_id")
        user_name = order_data.get("user_name")
        items = order_data.get("items", [])
        delivery = order_data.get("delivery", {})
        total = order_data.get("total", 0)
        promo_code = order_data.get("promo_code")
        
        print(f"👤 Order from: {user_name} ({user_id})")
        print(f"📋 Items count: {len(items)}")
        print(f"💰 Total: {total} грн")
        
        # Submit order to backend API - backend will handle messaging
        backend_result = await submit_order_to_backend(order_data)
        
        if backend_result:
            print(f"✅ Order submitted successfully to backend")
            # Backend handles all messaging now
        else:
            # Fallback message if backend submission fails
            await message.answer(
                "❌ Виникла помилка при обробці замовлення. Спробуйте ще раз."
            )
        
    except json.JSONDecodeError:
        await message.answer(
            "❌ Помилка обробки замовлення. Спробуйте ще раз."
        )
    except Exception as e:
        print(f"Error handling web app data: {e}")
        await message.answer(
            "❌ Виникла помилка. Спробуйте оформити замовлення ще раз."
        )


@router.callback_query(F.data.startswith("confirm_order:"))
async def confirm_order(callback: CallbackQuery):
    """Handle order confirmation by admin"""
    order_id = callback.data.split(":")[1]
    
    # Update order status in backend
    await update_order_status(order_id, "confirmed")
    
    await callback.message.edit_text(
        f"{callback.message.text}\n\n✅ Замовлення підтверджено",
        reply_markup=None
    )
    await callback.answer("Замовлення підтверджено")


@router.callback_query(F.data.startswith("cancel_order:"))
async def cancel_order(callback: CallbackQuery):
    """Handle order cancellation by admin"""
    order_id = callback.data.split(":")[1]
    
    # Update order status in backend
    await update_order_status(order_id, "cancelled")
    
    await callback.message.edit_text(
        f"{callback.message.text}\n\n❌ Замовлення скасовано",
        reply_markup=None
    )
    await callback.answer("Замовлення скасовано")


@router.callback_query(F.data.startswith("contact_client:"))
async def contact_client(callback: CallbackQuery):
    """Handle contact client request"""
    order_id = callback.data.split(":")[1]
    
    await callback.answer(
        "Дані клієнта вказані у замовленні. Зв'яжіться з ним найближчим часом.",
        show_alert=True
    )


def format_order_message(user_id: int, user_name: str, items: list, delivery: dict, total: float, promo_code: str = None) -> str:
    """Format order message for admin notification"""
    
    # Format items
    items_text = ""
    for item in items:
        items_text += f"• {item['product_name']} ({item['weight']} {item['unit']}) x{item['quantity']} = {item['total_price']} грн\n"
    
    # Format delivery info
    district = delivery.get("district", "Не вказано")
    time_slot_map = {
        "morning": "🌅 Ранок (8:00-12:00)",
        "afternoon": "☀️ День (12:00-16:00)",
        "evening": "🌆 Вечір (16:00-20:00)"
    }
    time_slot = time_slot_map.get(delivery.get("time_slot"), "Не вказано")
    comment = delivery.get("comment", "Немає")
    
    order_text = f"""
👤 Клієнт: {user_name} (ID: {user_id})
📦 Товари:
{items_text}
📍 Район доставки: {district}
⏰ Час доставки: {time_slot}
💬 Коментар: {comment}
💰 Загальна сума: {total} грн
"""
    
    if promo_code:
        order_text += f"🎫 Промокод: {promo_code}\n"
    
    order_text += f"\n📅 Замовлення від: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    
    return order_text


async def submit_order_to_backend(order_data: dict):
    """Submit order to backend API"""
    try:
        print(f"🔄 Submitting order to backend: {BACKEND_API_URL}/orders/")
        print(f"📊 Order data keys: {list(order_data.keys())}")
        print(f"👤 User: {order_data.get('user_name')} (ID: {order_data.get('user_id')})")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_API_URL}/orders/",
                json=order_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"tma {order_data.get('init_data', '')}"
                }
            )
            print(f"📊 Backend response status: {response.status_code}")
            response.raise_for_status()
            result = response.json()
            print(f"✅ Backend returned: order #{result.get('order_id', 'unknown')}")
            return result
    except Exception as e:
        print(f"❌ Error submitting order to backend: {e}")
        import traceback
        traceback.print_exc()
        return None


async def update_order_status(order_id: str, status: str):
    """Update order status in backend by order_id"""
    try:
        async with httpx.AsyncClient() as client:
            # First find the order by order_id
            response = await client.get(
                f"{BACKEND_API_URL}/admin/orders",
                params={"order_id": order_id}
            )
            response.raise_for_status()
            orders = response.json()
            
            if not orders:
                print(f"Order #{order_id} not found")
                return None
            
            order = orders[0]
            # Update using internal ID
            response = await client.patch(
                f"{BACKEND_API_URL}/admin/orders/{order['id']}",
                json={"status": status}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error updating order status: {e}")
        return None