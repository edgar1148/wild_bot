from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def keyboard_start():
    """Клавиатура для старта"""
    buttons = [
        [
            InlineKeyboardButton(text="Получить информацию о товаре", callback_data="product_info"),
        ],
        [
            InlineKeyboardButton(text="Остановить уведомления", callback_data="stop_not"),
        ],
        [
            InlineKeyboardButton(text="Получить информацию из БД", callback_data="get_history"),
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, one_time_keyboard=True)
    return keyboard


def keyboard_handle_product_sku():
    """Клавиатура для подписки на уведомления"""
    buttons = [
        [
            InlineKeyboardButton(text="Подписаться", callback_data="subscribe"),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, one_time_keyboard=True)
    return keyboard


def keyboard_stop_not():
    """Клавиатура для отписки от уведомлений"""
    buttons = [
        [
            InlineKeyboardButton(text="Отписаться от уведомлений", callback_data="stop_not"),
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons, one_time_keyboard=True)
    return keyboard
