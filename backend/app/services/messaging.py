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
        try:
            print(f"🔄 Formatting client confirmation for order #{order.order_id}, user {order.user_id}")
            message = self._format_client_confirmation_message(order)
            print(f"📝 Message length: {len(message)} chars")
            
            async with httpx.AsyncClient() as client:
                print(f"📡 Sending to Telegram API: {self.bot_api_url}/sendMessage")
                response = await client.post(
                    f"{self.bot_api_url}/sendMessage",
                    json={
                        "chat_id": order.user_id,
                        "text": message,
                        "parse_mode": "HTML"
                    }
                )
                print(f"📊 Telegram API response: {response.status_code}")
                response.raise_for_status()
                return True
        except Exception as e:
            print(f"❌ Error sending client confirmation: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def send_order_notification_to_admin(self, order: Order) -> bool:
        """Send order notification to admin chat"""
        try:
            if not settings.ADMIN_CHAT_ID:
                print("⚠️ No admin chat ID configured")
                return False
            
            print(f"🔄 Formatting admin notification for order #{order.order_id}")
            message = self._format_admin_notification_message(order)
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
            
            async with httpx.AsyncClient() as client:
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
                print(f"📊 Admin API response: {response.status_code}")
                response.raise_for_status()
                return True
        except Exception as e:
            print(f"❌ Error sending admin notification: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _format_client_confirmation_message(self, order: Order) -> str:
        """Format order confirmation message for client"""
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
        
        message = f"""
✅ <b>Замовлення #{order.order_id} підтверджено!</b>

👤 <b>Замовник:</b> {order.contact_name}
📦 <b>Товарів:</b> {total_items} шт.

<b>📋 Список товарів:</b>
{items_text}
📍 <b>Район доставки:</b> {order.district.name if order.district else 'Не вказано'}
📅 <b>Дата доставки:</b> {delivery_date}
⏰ <b>Час доставки:</b> {time_slot_text}
"""
        
        if order.comment:
            message += f"💬 <b>Коментар:</b> {order.comment}\n"
        
        if order.promo_code_used:
            message += f"🎫 <b>Промокод:</b> {order.promo_code_used}\n"
            message += f"💸 <b>Знижка:</b> {order.discount_amount} грн\n"
        
        message += f"""
💰 <b>Загальна сума:</b> {order.total_amount} грн

📞 Незабаром з вами зв'яжеться менеджер для уточнення деталей доставки.

📅 <i>Замовлення створено: {order.created_at.strftime('%d.%m.%Y %H:%M')}</i>
"""
        
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