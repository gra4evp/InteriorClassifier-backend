#!/usr/bin/env python3
"""
Скрипт для запуска телеграм бота
"""

import os
import sys
from pathlib import Path

# Добавляем путь к модулям бота
bot_path = Path(__file__).parent / "bot"
sys.path.insert(0, str(bot_path))

# Загружаем переменные окружения из .env файла
def load_env():
    """Загрузка переменных окружения из .env файла"""
    env_file = Path(__file__).parent / ".env"
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Переменные окружения загружены из .env")
    else:
        print("⚠️ Файл .env не найден. Используются системные переменные окружения.")

if __name__ == "__main__":
    # Загружаем переменные окружения
    load_env()
    
    # Импортируем и запускаем бота
    try:
        from bot.main import main
        import asyncio
        
        print("🚀 Запуск телеграм бота...")
        asyncio.run(main())
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Убедитесь, что все зависимости установлены: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        sys.exit(1) 