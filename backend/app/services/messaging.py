"""
Messaging service for sending notifications about orders
"""
import httpx
from typing import Optional
from datetime import datetime

from app.core.config import settings
from app.db.models.order import Order, DeliveryTimeSlot


class MessagingService:
    def __init__(self):
        self.bot_api_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"
    
    async def send_order_confirmation_to_client(self, order: Order) -> bool:
        """Send order confirmation message to client"""
        # Skip sending messages during tests
        if settings.TESTING:
            print(f"🧪 Test mode: Skipping client confirmation for order #{order.order_id}")
            return True
            
        try:
            print(f"🔄 Formatting client confirmation for order #{order.order_id}, user {order.user_id}")
            message = self._format_client_confirmation_message(order)
            print(f"📝 Client message preview: {message[:100]}...")
            print(f"📝 Message length: {len(message)} chars")
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"📡 Sending client confirmation to Telegram API...")
                response = await client.post(
                    f"{self.bot_api_url}/sendMessage",
                    json={
                        "chat_id": order.user_id,
                        "text": message,
                        "parse_mode": "HTML"
                    }
                )
                print(f"📊 Client message API response: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    message_id = result.get('result', {}).get('message_id')
                    print(f"✅ Client confirmation sent successfully! Message ID: {message_id}")
                    return True
                else:
                    print(f"❌ Client message failed with status {response.status_code}: {response.text}")
                    response.raise_for_status()
                    
        except httpx.TimeoutException:
            print(f"⏰ Timeout sending client confirmation for order #{order.order_id}")
            return False
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP error sending client confirmation: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error sending client confirmation: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def send_order_notification_to_admin(self, order: Order) -> bool:
        """Send order notification to admin chat"""
        # Skip sending messages during tests
        if settings.TESTING:
            print(f"🧪 Test mode: Skipping admin notification for order #{order.order_id}")
            return True
            
        try:
            if not settings.ADMIN_CHAT_ID:
                print("⚠️ No admin chat ID configured in environment")
                return False
            
            print(f"🔄 Formatting admin notification for order #{order.order_id}")
            message = self._format_admin_notification_message(order)
            print(f"📝 Admin message preview: {message[:100]}...")
            print(f"📝 Admin message length: {len(message)} chars")
            
            # Create inline keyboard for order management
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "✅ Підтвердити", "callback_data": f"confirm_order:{order.order_id}"},
                        {"text": "❌ Скасувати", "callback_data": f"cancel_order:{order.order_id}"}
                    ],
                    [
                        {"text": "📞 Зв'язатися", "callback_data": f"contact_client:{order.order_id}"}
                    ]
                ]
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                print(f"📡 Sending admin notification to chat {settings.ADMIN_CHAT_ID}")
                response = await client.post(
                    f"{self.bot_api_url}/sendMessage",
                    json={
                        "chat_id": settings.ADMIN_CHAT_ID,
                        "text": message,
                        "parse_mode": "HTML",
                        "reply_markup": keyboard
                    }
                )
                print(f"📊 Admin notification API response: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    message_id = result.get('result', {}).get('message_id')
                    print(f"✅ Admin notification sent successfully! Message ID: {message_id}")
                    return True
                else:
                    print(f"❌ Admin notification failed with status {response.status_code}: {response.text}")
                    response.raise_for_status()
                    
        except httpx.TimeoutException:
            print(f"⏰ Timeout sending admin notification for order #{order.order_id}")
            return False
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP error sending admin notification: {e.response.status_code} - {e.response.text}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error sending admin notification: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _format_client_confirmation_message(self, order: Order) -> str:
        """Format order confirmation message for client"""
        # Simple format as requested by user
        message = f"""🎉 <b>Замовлення #{order.order_id} прийнято!</b>

Ваше замовлення успішно оформлено. Менеджер зв'яжеться з вами найближчим часом для уточнення часу доставки.

📋 <b>Деталі замовлення:</b>"""
        
        # Add simplified items list
        total_items = 0
        for item in order.items:
            message += f"\n• {item.product_name} ({item.weight} {item.unit}) x{item.quantity}"
            total_items += item.quantity
        
        message += f"""

📦 <b>Кількість товарів:</b> {total_items} шт.
💰 <b>Загальна сума:</b> {order.total_amount} грн"""
        
        # Add promo code info if used
        if order.promo_code_used:
            message += f"\n🎫 <b>Промокод:</b> {order.promo_code_used} (знижка {order.discount_amount} грн)"
        
        message += f"\n\n📅 <i>Замовлення від {order.created_at.strftime('%d.%m.%Y %H:%M')}</i>"
        
        return message
    
    def _format_admin_notification_message(self, order: Order) -> str:
        """Format order notification message for admin"""
        time_slot_map = {
            DeliveryTimeSlot.MORNING: "🌅 Ранок (8:00-12:00)",
            DeliveryTimeSlot.AFTERNOON: "☀️ День (12:00-16:00)",
            DeliveryTimeSlot.EVENING: "🌆 Вечір (16:00-20:00)"
        }
        
        time_slot_text = time_slot_map.get(order.delivery_time_slot, "Не вказано")
        delivery_date = order.delivery_date.strftime("%d.%m.%Y")
        
        # Format items list
        items_text = ""
        total_items = 0
        for item in order.items:
            items_text += f"• <b>{item.product_name}</b> ({item.weight} {item.unit}) x{item.quantity} = {item.total_price} грн\n"
            total_items += item.quantity
        
        # User profile link
        user_link = f"<a href='tg://user?id={order.user_id}'>👤 {order.contact_name}</a>"
        
        message = f"""
🆕 <b>НОВЕ ЗАМОВЛЕННЯ #{order.order_id}</b>

{user_link} (ID: {order.user_id})
📞 <b>Телефон:</b> {order.contact_phone or 'Не вказано'}
📦 <b>Товарів:</b> {total_items} шт.

<b>📋 Список товарів:</b>
{items_text}
📍 <b>Район:</b> {order.district.name if order.district else 'Не вказано'}
📅 <b>Дата доставки:</b> {delivery_date}
⏰ <b>Час:</b> {time_slot_text}
"""
        
        if order.comment:
            message += f"💬 <b>Коментар:</b> {order.comment}\n"
        
        if order.promo_code_used:
            message += f"🎫 <b>Промокод:</b> {order.promo_code_used} (-{order.discount_amount} грн)\n"
        
        message += f"""
💰 <b>Сума:</b> {order.total_amount} грн

📅 <i>Створено: {order.created_at.strftime('%d.%m.%Y %H:%M')}</i>
"""
        
        return message


# Singleton instance
messaging_service = MessagingService()