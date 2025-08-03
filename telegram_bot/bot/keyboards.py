from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from config import WEB_APP_URL


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Main keyboard with Web App button"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Відкрити магазин",
                    web_app=WebAppInfo(url=WEB_APP_URL)
                )
            ]
        ]
    )
    return keyboard


def get_admin_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Admin keyboard for order management"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Підтвердити",
                    callback_data=f"confirm_order:{order_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Скасувати",
                    callback_data=f"cancel_order:{order_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📞 Зв'язатися з клієнтом",
                    callback_data=f"contact_client:{order_id}"
                )
            ]
        ]
    )
    return keyboard