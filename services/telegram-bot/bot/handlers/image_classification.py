import logging
import asyncio
from typing import List
from aiogram import Dispatcher, Router, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from io import BytesIO

from services.classification_service import ClassificationService
from utils.file_validator import validate_image_file
from utils.response_formatter import format_classification_result
from keyboards.reply import get_main_keyboard
from config import Config

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("classify"))
async def cmd_classify(message: Message):
    """Команда для начала классификации"""
    await message.answer(
        "📸 Отправьте изображение интерьера для классификации.\n\n"
        "Поддерживаемые форматы: JPG, JPEG, PNG, WEBP\n"
        "Максимальный размер: 10MB\n"
        "Можно отправить до 5 изображений одновременно."
    )


@router.message(F.photo)
async def handle_photo(message: Message):
    """Обработчик фотографий"""
    await process_image(message, message.photo[-1])


@router.message(F.document)
async def handle_document(message: Message):
    """Обработчик документов (изображений)"""
    document = message.document
    
    # Проверяем, что это изображение
    if not validate_image_file(document):
        await message.answer(
            "❌ Неподдерживаемый формат файла.\n"
            "Пожалуйста, отправьте изображение в формате JPG, JPEG, PNG или WEBP."
        )
        return
    
    await process_image(message, document)


async def process_image(message: Message, file):
    """Обработка изображения и отправка на классификацию"""
    try:
        # Отправляем сообщение о начале обработки
        processing_msg = await message.answer("🔄 Обрабатываю изображение...")
        
        # Получаем файл
        file_info = await message.bot.get_file(file.file_id)
        file_path = file_info.file_path
        
        # Скачиваем файл
        file_data = await message.bot.download_file(file_path)
        
        # Читаем данные в BytesIO
        file_bytes = file_data.read()
        
        # Проверяем размер файла
        if len(file_bytes) > Config.MAX_FILE_SIZE:
            await processing_msg.edit_text(
                "❌ Файл слишком большой.\n"
                f"Максимальный размер: {Config.MAX_FILE_SIZE // 1024 // 1024}MB"
            )
            return
        
        # Создаем BytesIO объект
        file_io = BytesIO(file_bytes)
        
        # Создаем сервис для классификации
        classification_service = ClassificationService()
        
        # Отправляем на классификацию
        result = await classification_service.classify_single_image(
            file_io, 
            file.file_name or "image.jpg"
        )
        
        # Форматируем и отправляем результат
        formatted_result = format_classification_result(result)
        await processing_msg.edit_text(formatted_result, parse_mode="HTML")
        
        logger.info(f"Successfully classified image for user {message.from_user.id}")
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        await processing_msg.edit_text(
            "❌ Произошла ошибка при обработке изображения.\n"
            "Пожалуйста, попробуйте еще раз или обратитесь к администратору."
        )


@router.message(F.media_group_id)
async def handle_media_group(message: Message):
    """Обработчик группы медиафайлов"""
    # Для групп медиафайлов мы будем обрабатывать каждый файл отдельно
    # в handle_photo или handle_document
    pass


def register_image_handlers(dp: Dispatcher) -> None:
    """Регистрация хендлеров для работы с изображениями"""
    dp.include_router(router) 