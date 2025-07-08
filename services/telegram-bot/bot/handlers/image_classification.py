import logging
from aiogram import Dispatcher, Router, F
from aiogram.types import Message, PhotoSize, Document
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.media_group import m
from io import BytesIO
import uuid

from services.classification_service import ClassificationService
from utils.file_validator import validate_image_file
from utils.response_formatter import format_classification_result
from keyboards.reply import get_main_keyboard
from config import Config

logger = logging.getLogger(__name__)
router = Router()


SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


@router.message(Command("classify"))
async def cmd_classify(message: Message):
    """Команда для начала классификации"""
    await message.answer(
        "📸 Отправьте изображение интерьера для классификации.\n\n"
        "Поддерживаемые форматы: JPG, JPEG, PNG, WEBP\n"
        "Максимальный размер: 10MB\n"
        "Можно отправить до 5 изображений одновременно."
    )


# @router.message(F.photo)
# async def handle_photo(message: Message):
#     """Обработчик фотографий"""
#     await process_image(message, message.photo[-1])


# @router.message(F.document)
# async def handle_document(message: Message):
#     """Обработчик документов (изображений)"""
#     document = message.document
    
#     # Проверяем, что это изображение
#     if not validate_image_file(document):
#         await message.answer(
#             "❌ Неподдерживаемый формат файла.\n"
#             "Пожалуйста, отправьте изображение в формате JPG, JPEG, PNG или WEBP."
#         )
#         return
    
#     await process_image(message, document)


# async def process_image(message: Message, file):
#     """Обработка изображения и отправка на классификацию"""
#     try:
#         # Отправляем сообщение о начале обработки
#         processing_msg = await message.answer("🔄 Обрабатываю изображение...")
        
#         # Получаем файл
#         file_info = await message.bot.get_file(file.file_id)
#         file_path = file_info.file_path
        
#         # Скачиваем файл
#         file_data = await message.bot.download_file(file_path)
        
#         # Читаем данные в BytesIO
#         file_bytes = file_data.read()
        
#         # Проверяем размер файла
#         if len(file_bytes) > Config.MAX_FILE_SIZE:
#             await processing_msg.edit_text(
#                 "❌ Файл слишком большой.\n"
#                 f"Максимальный размер: {Config.MAX_FILE_SIZE // 1024 // 1024}MB"
#             )
#             return
        
#         # Создаем BytesIO объект
#         file_io = BytesIO(file_bytes)
        
#         # Определяем имя файла в зависимости от типа
#         if isinstance(file, PhotoSize):
#             # Для фотографий генерируем имя файла
#             filename = f"photo_{uuid.uuid4().hex[:8]}.jpg"
#         elif isinstance(file, Document):
#             # Для документов используем оригинальное имя
#             filename = file.file_name or "document.jpg"
#         else:
#             # Для других типов файлов
#             filename = f"file_{uuid.uuid4().hex[:8]}.jpg"
        
#         # Создаем сервис для классификации
#         classification_service = ClassificationService()
        
#         # Отправляем на классификацию
#         result = await classification_service.classify_single_image(
#             file_io, 
#             filename
#         )
        
#         # Форматируем и отправляем результат
#         formatted_result = format_classification_result(result)
#         await processing_msg.edit_text(formatted_result, parse_mode="HTML")
        
#         logger.info(f"Successfully classified image for user {message.from_user.id}")
        
#     except Exception as e:
#         logger.error(f"Error processing image: {e}")
#         await processing_msg.edit_text(
#             "❌ Произошла ошибка при обработке изображения.\n"
#             "Пожалуйста, попробуйте еще раз или обратитесь к администратору."
#         )


def is_supported(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in SUPPORTED_EXTENSIONS)


@router.message(F.media_group_id | F.photo | F.document)
async def handle_images(message: Message):

    # Отправляем сообщение о начале обработки
    processing_msg = await message.answer("🔄 Обрабатываю изображение...")

    files = []
    file_names = []
    bot = message.bot

    # 1. Если это альбом (media group)
    if message.media_group_id is not None:
        # Получаем все сообщения из альбома
        
        media_group = await bot.get_media_group(message.chat.id, message.message_id)
        for idx, msg in enumerate(media_group, start=1):
            if msg.photo:
                file = msg.photo[-1]
                filename = f"photo_{idx}.jpg"
            elif msg.document and is_supported(msg.document.file_name):
                file = msg.document
                filename = msg.document.file_name
            else:
                continue
            file_info = await bot.get_file(file.file_id)
            file_data = await bot.download_file(file_info.file_path)
            file_bytes = file_data.read()
            files.append(BytesIO(file_bytes))
            file_names.append(filename)
    else:
        # Одиночное фото или документ
        if message.photo:
            file = message.photo[-1]
            filename = f"photo.jpg"
        elif message.document and is_supported(message.document.file_name):
            file = message.document
            filename = message.document.file_name
        else:
            await processing_msg.edit_text("❌ Неподдерживаемый формат файла. Поддерживаются JPG, JPEG, PNG, WEBP.")
            return
        file_info = await bot.get_file(file.file_id)
        file_data = await bot.download_file(file_info.file_path)
        file_bytes = file_data.read()
        files.append(BytesIO(file_bytes))
        file_names.append(filename)

    if not files:
        await processing_msg.edit_text("❌ Не удалось найти подходящие изображения в сообщении.")
        return

    # 2. Отправляем батч на backend
    classification_service = ClassificationService()
    try:
        result = await classification_service.classify_multiple_images(list(zip(files, file_names)))
    except Exception as e:
        logger.error(f"Error during classification: {e}")
        await processing_msg.edit_text("❌ Произошла ошибка при классификации. Попробуйте позже.")
        return

    # 3. Форматируем и отправляем результат
    formatted = format_classification_result(result)
    await processing_msg.edit_text(formatted, parse_mode="HTML")


def register_image_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров для работы с изображениями"""
    dp.include_router(router)
