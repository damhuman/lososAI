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
    
    await message.answer(
        WELCOME_MESSAGE,
        reply_markup=keyboard
    )


@router.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    """Handle data from Web App (order submission)"""
    try:
        # Parse order data from Web App
        order_data = json.loads(message.web_app_data.data)
        
        # Extract order information
        user_id = order_data.get("user_id")
        user_name = order_data.get("user_name")
        items = order_data.get("items", [])
        delivery = order_data.get("delivery", {})
        total = order_data.get("total", 0)
        promo_code = order_data.get("promo_code")
        
        # Format order message for admin
        order_text = format_order_message(user_id, user_name, items, delivery, total, promo_code)
        
        # Send order confirmation to user
        await message.answer(
            "✅ Дякуємо за замовлення!\n\n"
            "Ваше замовлення прийнято і передано менеджеру. "
            "Незабаром з вами зв'яжуться для підтвердження деталей доставки.\n\n"
            f"Сума замовлення: {total} грн"
        )
        
        # Forward order to admin if configured
        if ADMIN_CHAT_ID:
            keyboard = get_admin_order_keyboard(0)  # We'll need order ID from backend
            await message.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=f"🆕 Нове замовлення!\n\n{order_text}",
                reply_markup=keyboard
            )
        
        # Submit order to backend API
        await submit_order_to_backend(order_data)
        
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
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_API_URL}/orders",
                json=order_data,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"tma {order_data.get('init_data', '')}"
                }
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error submitting order to backend: {e}")
        return None


async def update_order_status(order_id: str, status: str):
    """Update order status in backend"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{BACKEND_API_URL}/admin/orders/{order_id}",
                json={"status": status}
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error updating order status: {e}")
        return None