import logging
from aiogram import Dispatcher, Router, F
from aiogram.types import Message, PhotoSize, Document
from aiogram.filters import Command
from io import BytesIO
import uuid

from services.classification_service import ClassificationService
from utils.file_validator import validate_image_file
from utils.response_formatter import format_classification_result
from keyboards.reply import get_main_keyboard
from config import Config
from middlewares.album import AlbumMiddleware

logger = logging.getLogger(__name__)
router = Router()
router.message.middleware(AlbumMiddleware())


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

async def extract_file_and_name(msg: Message, image_filename: str = None) -> tuple[BytesIO, str] | None:
    """Extracts file and filename from a message if it's a supported image.
    For photos, uses image_filename if provided. For documents, always uses the original filename."""
    if msg.photo:
        file = msg.photo[-1]
        filename = image_filename or f"photo_{file.file_id}.jpg"
    elif msg.document and is_supported(msg.document.file_name):
        file = msg.document
        filename = msg.document.file_name  # Always use original name for documents
    else:
        return None
    file_info = await msg.bot.get_file(file.file_id)
    file_data = await msg.bot.download_file(file_info.file_path)
    file_bytes = file_data.read()
    return BytesIO(file_bytes), filename

async def process_images(message: Message, files: list[tuple[BytesIO, str]]):
    """Sends images for classification and returns results to the user."""
    processing_msg = await message.answer("🔄 Обрабатываю изображение(я)...")
    classification_service = ClassificationService()
    try:
        result = await classification_service.classify_multiple_images(files)
    except Exception as e:
        logger.error(f"Error during classification: {e}")
        await processing_msg.edit_text("❌ Произошла ошибка при классификации. Попробуйте позже.")
        return
    # Format and send results
    for res in result.get("results", []):
        formatted = format_classification_result(res)
        await message.answer(formatted, parse_mode="HTML")
    await processing_msg.delete()

@router.message(F.photo | F.document)
async def handle_images(message: Message, album: list[Message] = None):
    """
    Universal handler for single and batch images.
    If album is not None, it's a batch; otherwise, it's a single image.
    """
    files = []

    if album:
        # Batch of images (album)
        for idx, msg in enumerate(album, start=1):
            if msg.photo:
                result = await extract_file_and_name(msg, image_filename=f"image_{idx}.jpg")
            else:
                result = await extract_file_and_name(msg)
            if result:
                files.append(result)
        if not files:
            await message.answer("❌ Не удалось найти подходящие изображения в альбоме.")
            return
        await process_images(message, files)
    else:
        # Single image
        if message.photo:
            result = await extract_file_and_name(message, image_filename="image.jpg")
        else:
            result = await extract_file_and_name(message)
        if not result:
            await message.answer("❌ Неподдерживаемый формат файла. Поддерживаются JPG, JPEG, PNG, WEBP.")
            return
        await process_images(message, [result])


def register_image_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров для работы с изображениями"""
    dp.include_router(router)
