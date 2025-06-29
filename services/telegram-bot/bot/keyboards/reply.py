from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главная клавиатура бота"""
    keyboard = [
        [
            KeyboardButton(text="📸 Классифицировать изображение"),
            KeyboardButton(text="ℹ️ Помощь")
        ],
        [
            KeyboardButton(text="🏠 О классах интерьеров")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Отправьте изображение или выберите действие"
    )


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    keyboard = [
        [KeyboardButton(text="❌ Отмена")]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_classes_info_keyboard() -> InlineKeyboardMarkup:
    """Инлайн клавиатура с информацией о классах"""
    keyboard = [
        [
            InlineKeyboardButton(text="🏢 Классы A", callback_data="class_info_a"),
            InlineKeyboardButton(text="🏠 Классы B", callback_data="class_info_b")
        ],
        [
            InlineKeyboardButton(text="🏘️ Классы C", callback_data="class_info_c"),
            InlineKeyboardButton(text="🏚️ Классы D", callback_data="class_info_d")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 