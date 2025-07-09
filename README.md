# InteriorClassifier-backend

Система для классификации интерьеров квартир с веб-API и телеграм ботом.

## 🏗️ Архитектура

Проект состоит из двух основных компонентов:

1. **Python Backend** - FastAPI сервер для классификации изображений
2. **Telegram Bot** - aiogram 3 бот для удобного взаимодействия с пользователями

## 🚀 Быстрый старт

### Запуск через Docker Compose

1. **Клонируйте репозиторий:**
```bash
git clone https://github.com/gra4evp/InteriorClassifier-backend.git
cd InteriorClassifier-backend
```

2. **Настройте переменные окружения:**
```bash
# Для бэкенда
cp services/python-backend/.env.example services/python-backend/.env
# Отредактируйте файл под ваши нужды

# Для бота
cp services/telegram-bot/.env.example services/telegram-bot/.env
# Укажите токен бота и настройки
```

3. **Запустите все сервисы:**
```bash
docker-compose up -d --build
```

### Локальный запуск

#### Backend
```bash
cd services/python-backend
pip install -r requirements.txt
python app/main.py
```

#### Telegram Bot
```bash
cd services/telegram-bot
pip install -r requirements.txt
python run_bot.py
```

## 📱 Telegram Bot

### Возможности
- 📸 Загрузка и анализ изображений интерьеров
- 🏠 Классификация по 8 классам (A0, A1, B0, B1, C0, C1, D0, D1)
- 📊 Красивое отображение результатов с вероятностями
- 🎨 Современный UI с эмодзи и клавиатурами

### Настройка бота

1. **Получите токен у @BotFather**
2. **Переименуйте файл `.env.example` в `.env` и заполните его:**
```env
BOT_TOKEN=your_bot_token_here
BACKEND_URL=http://localhost:8015
API_TIMEOUT=30
MAX_FILE_SIZE=10485760
MAX_IMAGES_PER_REQUEST=5
LOG_LEVEL=INFO
```

3. **Запустите бота:**
```bash
python services/telegram-bot/bot/main.py
```

### Использование бота

1. Отправьте `/start` для начала работы
2. Загрузите изображение интерьера
3. Получите результат классификации с вероятностями

## 🔧 API Endpoints

### POST /classify_batch
Классификация пакета изображений

**Параметры:**
- `images`: Список файлов изображений

**Ответ:**
```json
{
  "results": [
    {
      "predicted_class": "A0",
      "top_confidence": 0.92,
      "class_confidences": {
        "A0": 0.82,
        "A1": 0.03,
        "B0": 0.01,
        "B1": 0.08,
        "C0": 0.01,
        "C1": 0.03,
        "D0": 0.01,
        "D1": 0.01
      },
      "image_name": "kitchen.jpg",
      "error": null
    },
    {
      "predicted_class": null,
      "top_confidence": null,
      "class_confidences": {},
      "image_name": "broken.png",
      "error": "File is not a supported image format. Supported formats: jpg, jpeg, png, bmp, gif, tiff, webp, ico."
    }
  ],
  "meta": {
    "total_images": 2,
    "total_processing_time_ms": 250,
    "model_version": "1.0.0",
    "backbone_name": "EfficientNet-B3"
  }
}
```

## 📁 Структура проекта

```
InteriorClassifier-backend/
├── services/
│   ├── python-backend/          # FastAPI сервер
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── models/
│   │   │   ├── routers/
│   │   │   └── pydantic_models.py
│   │   ├── Dockerfile_cpu # для запуска на CPU
│   │   ├── Dockerfile_gpu # для запуска на GPU
│   │   ├── .env.example # замените на свой .env файл
│   │   └── requirements.txt
│   └── telegram-bot/            # Telegram бот
│       ├── bot/
│       │   ├── main.py
│       │   ├── config.py
│       │   ├── handlers/
│       │   ├── services/
│       │   ├── utils/
│       │   ├── keyboards/
│       │   └── middlewares/
│       ├── Dockerfile
│       ├── .env.example  # замените на свой .env файл
│       └── requirements.txt
├── pictures/                    # Тестовые изображения
├── docker-compose.yml
├── .env.example # замените на свой .env файл
└── README.md
```

## 🛠️ Разработка

### Установка зависимостей

```bash
pip install -r dev_requirements.txt
```

### Добавление новых хендлеров в бота

1. Создайте файл в `services/telegram-bot/bot/handlers/`
2. Создайте роутер и функции-обработчики
3. Зарегистрируйте в `handlers/__init__.py`

### Добавление новых API endpoints

1. Создайте новый роутер в `services/python-backend/app/routers/`
2. Добавьте обработчики
3. Зарегистрируйте в `main.py`
