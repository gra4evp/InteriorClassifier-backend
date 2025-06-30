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
            InlineKeyboardButton(text="🧱 A0 [Unfinished | Без отделки]", callback_data="class_label_A0")
        ],
        [
            InlineKeyboardButton(text="🏚️ A1 [Major repair | Капитальный ремонт]", callback_data="class_label_A1")
        ],
        [
            InlineKeyboardButton(text="🏠 B0 [WhiteBox | Под чистовую]", callback_data="class_label_B0")
        ],
        [
            InlineKeyboardButton(text="🎨 B1 [Cosmetic repair | Косметический ремонт]", callback_data="class_label_B1")
        ],
        [
            InlineKeyboardButton(text="☑️ C0 [Finished | Чистовая]", callback_data="class_label_C0")
        ],
        [
            InlineKeyboardButton(text="🏠 C1 [Excellent | Отличное состояние]", callback_data="class_label_C1")
        ],
        [
            InlineKeyboardButton(text="✨ D0 [Euro-style | Евроремонт]", callback_data="class_label_D0")
        ],
        [
            InlineKeyboardButton(text="💎 D1 [Luxury | Люкс]", callback_data="class_label_D1")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 