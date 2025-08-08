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
    
    # Record user interaction
    await record_user_interaction(message.from_user, "start", message.text)
    
    keyboard = get_main_keyboard()
    
    print(f"🚀 /start command from user {message.from_user.id} ({message.from_user.first_name})")
    
    await message.answer(
        WELCOME_MESSAGE,
        reply_markup=keyboard
    )

@router.message()
async def handle_any_message(message: Message):
    """Handle any other message for debugging"""
    # Record user interaction
    await record_user_interaction(message.from_user, "message", message.text)
    
    print(f"📨 Received message from {message.from_user.id}: {message.text}")
    if message.web_app_data:
        print(f"🌐 Has web app data: {message.web_app_data.data}")
    else:
        print("❌ No web app data in this message")


@router.message(F.web_app_data)
async def handle_web_app_data(message: Message):
    """Handle data from Web App (order submission)"""
    # Record user interaction
    await record_user_interaction(message.from_user, "web_app", "Order submission")
    
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
            order_id = backend_result.get('order_id', 'невідомий')
            print(f"📋 Order ID: {order_id}")
            
            # Backend handles client confirmation message automatically
            # If backend messaging fails, send fallback confirmation
            if not backend_result.get('client_message_sent', False):
                print("⚠️ Backend didn't send client message, sending fallback")
                await send_fallback_confirmation(message.from_user, order_data, order_id)
                
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
    # Record user interaction
    await record_user_interaction(callback.from_user, "callback", f"confirm_order:{callback.data}")
    
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
    # Record user interaction
    await record_user_interaction(callback.from_user, "callback", f"cancel_order:{callback.data}")
    
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
    # Record user interaction
    await record_user_interaction(callback.from_user, "callback", f"contact_client:{callback.data}")
    
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


async def record_user_interaction(user, interaction_type: str, message_text: str = None):
    """Record user interaction with the bot in backend"""
    try:
        user_data = {
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "language_code": user.language_code,
                "is_bot": user.is_bot
            },
            "interaction_type": interaction_type,
            "message_text": message_text
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_API_URL}/bot/interactions",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"📊 Recorded interaction for {user.first_name} ({user.id}): {interaction_type}")
                return result
            else:
                print(f"⚠️ Failed to record interaction: {response.status_code}")
                return None
    except Exception as e:
        print(f"❌ Error recording user interaction: {e}")
        return None


async def send_fallback_confirmation(user, order_data: dict, order_id: str):
    """Send fallback order confirmation if backend messaging fails"""
    try:
        items = order_data.get("items", [])
        delivery = order_data.get("delivery", {})
        total = order_data.get("total", 0)
        user_name = order_data.get("user_name", "Користувач")
        
        # Format items
        items_text = ""
        total_items = 0
        for item in items:
            items_text += f"• {item.get('product_name', 'Товар')} ({item.get('weight', '?')} {item.get('unit', 'шт')}) x{item.get('quantity', 1)} = {item.get('total_price', 0)} грн\n"
            total_items += item.get('quantity', 1)
        
        # Format delivery info
        district = delivery.get("district", "Не вказано")
        time_slot_map = {
            "morning": "🌅 Ранок (8:00-12:00)",
            "afternoon": "☀️ День (12:00-16:00)",
            "evening": "🌆 Вечір (16:00-20:00)"
        }
        time_slot = time_slot_map.get(delivery.get("time_slot"), "Не вказано")
        comment = delivery.get("comment", "")
        promo_code = order_data.get("promo_code")
        
        # Use the same simple format as in messaging service
        message = f"""🎉 <b>Замовлення #{order_id} прийнято!</b>

Ваше замовлення успішно оформлено. Менеджер зв'яжеться з вами найближчим часом для уточнення часу доставки.

📋 <b>Деталі замовлення:</b>"""
        
        # Add simplified items list
        for item in items:
            message += f"\n• {item.get('product_name', 'Товар')} ({item.get('weight', '?')} {item.get('unit', 'шт')}) x{item.get('quantity', 1)}"
        
        message += f"""

📦 <b>Кількість товарів:</b> {total_items} шт.
💰 <b>Загальна сума:</b> {total} грн"""
        
        # Add promo code info if used
        if promo_code:
            message += f"\n🎫 <b>Промокод:</b> {promo_code}"
        
        message += f"\n\n📅 <i>Замовлення від {datetime.now().strftime('%d.%m.%Y %H:%M')}</i>"

        # Send using bot instance from main module
        try:
            from main import bot
            if bot:
                await bot.send_message(
                    chat_id=user.id,
                    text=message,
                    parse_mode="HTML"
                )
                print(f"✅ Fallback confirmation sent to user {user.id}")
            else:
                print(f"❌ Bot instance not available for fallback message")
        except ImportError as e:
            print(f"❌ Could not import bot instance: {e}")
        except Exception as e:
            print(f"❌ Error sending fallback message: {e}")
        
    except Exception as e:
        print(f"❌ Error sending fallback confirmation: {e}")


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