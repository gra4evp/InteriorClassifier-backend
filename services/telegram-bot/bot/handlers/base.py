import logging
from aiogram import Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards.reply import get_main_keyboard, get_classes_info_keyboard
from utils.messages import get_welcome_message

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    await state.clear()
    
    welcome_text = get_welcome_message(message.from_user.first_name)
    keyboard = get_main_keyboard()
    
    await message.answer(
        welcome_text,
        reply_markup=keyboard
    )
    
    logger.info(f"User {message.from_user.id} started the bot")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
🤖 <b>Помощь по использованию бота</b>

📸 <b>Как отправить изображения:</b>
• Отправьте одно или несколько изображений интерьера
• Поддерживаемые форматы: JPG, JPEG, PNG, WEBP
• Максимальный размер файла: 10MB
• Максимум 5 изображений за раз

🏠 <b>Что анализируется:</b>
• Тип интерьера квартиры
• Класс помещения (A0, A1, B0, B1, C0, C1, D0, D1)
• Вероятность каждого класса

📊 <b>Результат:</b>
• Класс интерьера с наибольшей вероятностью
• Распределение вероятностей по всем классам

💡 <b>Дополнительные команды:</b>
/start - Главное меню
/help - Эта справка
    """
    
    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Отмена текущего состояния"""
    await state.clear()
    keyboard = get_main_keyboard()
    
    await message.answer(
        "❌ Операция отменена. Выберите действие:",
        reply_markup=keyboard
    )


@router.message(F.text == "📸 Классифицировать изображение")
async def handle_classify_button(message: Message):
    """Обработчик кнопки классификации"""
    await message.answer(
        "📸 Отправьте изображение интерьера для классификации.\n\n"
        "Поддерживаемые форматы: JPG, JPEG, PNG, WEBP\n"
        "Максимальный размер: 10MB\n"
        "Можно отправить до 5 изображений одновременно."
    )


@router.message(F.text == "ℹ️ Помощь")
async def handle_help_button(message: Message):
    """Обработчик кнопки помощи"""
    await cmd_help(message)


@router.message(F.text == "🏠 О классах интерьеров")
async def handle_classes_info_button(message: Message):
    """Обработчик кнопки информации о классах"""
    keyboard = get_classes_info_keyboard()
    
    await message.answer(
        "🏠 <b>Классы интерьеров квартир</b>\n\n"
        "Выберите категорию для получения подробной информации:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("class_info_"))
async def handle_class_info_callback(callback: CallbackQuery):
    """Обработчик callback для информации о классах"""
    class_type = callback.data.split("_")[-1]
    
    class_info = {
        "a": """
🏢 <b>Классы A - Элитные интерьеры</b>

<b>A0:</b> Премиум элитный интерьер
• Высококачественные материалы
• Дизайнерская мебель
• Современные технологии
• Просторные помещения

<b>A1:</b> Стандартный элитный интерьер
• Качественные материалы
• Стильная мебель
• Хорошее освещение
• Комфортные условия
        """,
        "b": """
🏠 <b>Классы B - Стандартные интерьеры</b>

<b>B0:</b> Высокий стандарт
• Хорошие материалы
• Современная мебель
• Функциональное планирование
• Уютная атмосфера

<b>B1:</b> Базовый стандарт
• Качественные материалы
• Практичная мебель
• Удобная планировка
• Комфортные условия
        """,
        "c": """
🏘️ <b>Классы C - Экономные интерьеры</b>

<b>C0:</b> Высокий эконом
• Доступные материалы
• Функциональная мебель
• Рациональное планирование
• Удобство использования

<b>C1:</b> Базовый эконом
• Простые материалы
• Необходимая мебель
• Простая планировка
• Основные удобства
        """,
        "d": """
🏚️ <b>Классы D - Базовые интерьеры</b>

<b>D0:</b> Минимальный комфорт
• Простые материалы
• Базовая мебель
• Простое планирование
• Основные функции

<b>D1:</b> Базовые условия
• Минимальные материалы
• Необходимая мебель
• Простая планировка
• Основные удобства
        """
    }
    
    info = class_info.get(class_type, "Информация не найдена")
    
    await callback.message.edit_text(
        info,
        parse_mode="HTML"
    )
    
    await callback.answer()


def register_base_handlers(dp: Dispatcher) -> None:
    """Регистрация базовых хендлеров"""
    dp.include_router(router) 