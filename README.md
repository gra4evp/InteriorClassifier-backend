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
git clone <repository-url>
cd InteriorClassifier-backend
```

2. **Настройте переменные окружения:**
```bash
# Для бэкенда
cp services/python-backend/.env.example services/python-backend/.env
# Отредактируйте файл под ваши нужды

# Для бота
cp services/telegram-bot/env.example services/telegram-bot/.env
# Укажите токен бота и настройки
```

3. **Запустите все сервисы:**
```bash
docker-compose up -d
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
2. **Создайте файл `.env`:**
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
python run_bot.py
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
      "class_name": "A0",
      "probabilities": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
      "image_name": "interior.jpg"
    }
  ]
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
│   │   ├── Dockerfile
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
│       ├── requirements.txt
│       └── run_bot.py
├── pictures/                    # Тестовые изображения
├── docker-compose.yml
└── README.md
```

## 🛠️ Разработка

### Добавление новых хендлеров в бота

1. Создайте файл в `services/telegram-bot/bot/handlers/`
2. Создайте роутер и функции-обработчики
3. Зарегистрируйте в `handlers/__init__.py`

### Добавление новых API endpoints

1. Создайте новый роутер в `services/python-backend/app/routers/`
2. Добавьте обработчики
3. Зарегистрируйте в `main.py`

## 📊 Логирование

- Backend логи: в консоли и файлах
- Bot логи: в `bot.log` и консоли
- Docker логи: `docker-compose logs -f`

## 🔒 Безопасность

- Валидация файлов по типу и размеру
- Ограничение частоты запросов
- Обработка ошибок сети и API
- Логирование всех действий

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи сервисов
2. Убедитесь, что все переменные окружения настроены
3. Проверьте доступность бэкенда для бота