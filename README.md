# 📦 Contest skazka design (backend)

Этот проект является дипломной работой и представляет собой RESTful backend-сервис на основе [Django](https://www.djangoproject.com/) и [Django REST Framework](https://www.django-rest-framework.org/) для проведения творческих онлайн-конкурсов.

## 🚀 Возможности

- 🌐 Полноценная RESTful API для управления всем жизненным циклом конкурса
- 🔐 JWT-аутентификация и ✉️ подтверждение по email
- 🎯 Гибкая система критериев, 🏆 номинаций и 📅 возрастных категорий
- ☁️ Поддержка S3-хранилища (Yandex Cloud) для файлов
- 🔄 Интеграция с внешними платформами (например, 📘 VK)
- 👥 Ролевая модель доступа к системе для точного контроля прав пользователей

## 🛠️ Стек технологий

- 🐍 Python 3.12+
- 🌐 Django 5.2.2
- 🔧 Django REST Framework 3.16
- 🔐 JWT (djangorestframework-simplejwt)
- 🧩 django-filter — фильтрация данных
- 🌍 django-cors-headers — поддержка CORS
- ⚙️ pydantic-settings — конфигурация приложения через .env
- 🛢️ PostgreSQL — основная база данных
- ⚙️ Redis — кэширование данных
- ☁️ S3 (boto3) — хранение файлов в облаке
- 🐳 Docker / Docker Compose — контейнеризация
- 🔥 Nginx — прокси-сервер
- 🧪 Gunicorn — продакшн WSGI-сервер


## 🧩 Основные модули системы

- `applications` — Заявки участников
- `authentication` — Регистрация, вход, JWT
- `block_user` — Блокировка пользователей
- `contest_categories` — Категории конкурсов
- `contest_criteria` — Критерии оценивания
- `contest_file_constraints` — Ограничения по файлам
- `contest_nominations` — Номинации в рамках конкурсов
- `contest_stage` — Этапы конкурсов
- `contests` — Основная логика конкурсов
- `participants` — Участники конкурсов
- `email_confirmation` — Подтверждение регистрации по email
- `file_constraints` — Ограничения форматов загрузки конкурсных работ
- `storage_s3` — Работа с хранилищем S3
- `users` — Информация о пользователе
- `vk_news`, `vk_news_attachments` — Интеграция с VK для получения новостей
- `winners` — Победители
- `work_rate` — Оценки работ
- `criteria`, `competencies`, `nomination`, `age_categories` — Дополнительные параметры конкурсов

## 📂 Установка

1. **Клонируй репозиторий:**

```bash
  git clone git@github.com:kaiffan/contest_skazka_design.git
  cd ./contest_skazka_design.git
```

2. **Создание виртуального окружения**
```bash
  python -m venv .venv
  source .venv/bin/activate  # для Linux/Mac
  .venv\Scripts\activate # для Windows
```

3. **Установка зависимостей**
```bash
  pip install -r requirements.txt
```

4. **Применение миграций**
```bash
  python manage.py migrate
```

5. **Запуск контейнеров из docker-compose**
```bash
  docker-compose up --build
```
6. **Переменные окружения**
```bash
  nano .env
```
И нужно его заполнить в следующем формате:
```
TOKEN_REFRESH_COOKIE_KEY=refresh_token
TOKEN_REFRESH_COOKIE_PATH=api/v1/auth/
TOKEN_REFRESH_COOKIE_MAX_AGE=
TOKEN_SECRET_KEY=

POSTGRES_DATABASE_NAME=
POSTGRES_USERNAME=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=

REDIS_PASSWORD=
REDIS_USER=
REDIS_USER_PASSWORD=
REDIS_HOST=
REDIS_PORT=
REDIS_DB=
REDIS_CHARSET=

VK_TOKEN=
VK_DOMAIN=
VK_COUNT_POSTS=
VK_API_VERSION=

YANDEX_S3_ID_KEY=
YANDEX_S3_SECRET_KEY=
YANDEX_S3_ENDPOINT_URL=
YANDEX_S3_BACKET_NAME=

EMAIL_HOST=
EMAIL_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_CODE_DIGITS=
EMAIL_CODE_CONFIRMATION_SALT=
```

7. **Запуск сервера для локальной разработки**
```bash
  python manage.py runserver 127.0.0.1:8000
```

## ✍️ Автор

- **👨‍💻 Разработчик:** Баев Павел
- **✉️ Email:** [pavel.baev44@gmail.com](mailto:pavel.baev44@gmail.com)  
- **🐱 GitHub:** [https://github.com/kaiffan](https://github.com/kaiffan) 



