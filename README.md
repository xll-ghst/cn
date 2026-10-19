# Django-Arch — контрольная работа: Auth, роли и Google OAuth 2.0

Реализация следует архитектурным правилам репозитория `Django-Arch`: приложения находятся в `apps/`, конфигурация — в `core/`, внешняя интеграция вынесена в `apps/users/services.py`, секреты читаются из `.env`.

## Что реализовано по ТЗ

1. Кастомный `User(AbstractUser)`: уникальный обязательный email как `USERNAME_FIELD`, роли `student` (по умолчанию) и `teacher`.
2. SimpleJWT:
   - `POST /api/v1/auth/jwt/create/`
   - `POST /api/v1/auth/jwt/refresh/`
3. `IsTeacherOrReadOnly`: анонимные пользователи не допускаются; чтение доступно авторизованным пользователям; запись — только `teacher`.
4. `POST /api/v1/auth/google/`: обменивает OAuth code на токен Google, получает профиль, находит/создаёт пользователя и выдаёт JWT.
5. Google credentials берутся из переменных окружения, не из исходного кода.

## Запуск на Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
py manage.py makemigrations users
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

Открой `http://127.0.0.1:8000/admin/`.

> Важно: `AUTH_USER_MODEL` задан заранее. Для нового проекта сначала выполни миграции этого проекта. Если ты переносишь код в уже существующую базу с применёнными миграциями `auth`, не переключай модель пользователя без отдельного плана миграции.

## JWT: получить токены

`POST http://127.0.0.1:8000/api/v1/auth/jwt/create/`

```json
{
  "email": "student@example.com",
  "password": "your-password"
}
```

Ответ содержит `access` и `refresh`. Для защищённого API передавай заголовок:

```http
Authorization: Bearer <access_token>
```

Обновить access:

`POST http://127.0.0.1:8000/api/v1/auth/jwt/refresh/`

```json
{
  "refresh": "<refresh_token>"
}
```

## Уроки

- `GET /api/v1/lessons/` — список уроков, доступен авторизованным студентам и преподавателям.
- `POST /api/v1/lessons/` — создать урок, доступно только преподавателю.

Пример POST:

```json
{
  "title": "Введение в Python",
  "description": "Первый урок"
}
```

Для теста роли преподавателя создай пользователя через админку и установи `role=teacher`.

## Google OAuth 2.0

В Google Cloud Console настрой OAuth client и точный Redirect URI, который использует клиентское приложение. Заполни `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` и `GOOGLE_REDIRECT_URI` в `.env`.

Клиентское приложение отправляет полученный от Google authorization `code`:

`POST /api/v1/auth/google/`

```json
{
  "code": "authorization_code_from_google"
}
```

Серверный ответ — `access`, `refresh`, `is_new_user` и публичные поля пользователя. Нельзя отправлять `client_secret` в браузер или коммитить `.env`.

## Проверка прав

1. Без JWT запрос `GET /api/v1/lessons/` должен вернуть `401 Unauthorized`.
2. Студент с JWT может сделать GET, но POST должен вернуть `403 Forbidden`.
3. Преподаватель с JWT может сделать GET и POST.
4. Неверный/просроченный Google code должен вернуть безопасную ошибку `400`, без утечки секретов или stack trace.

## Структура

```text
core/
  settings/base.py
  settings/development.py
  urls.py
apps/
  users/
    models.py
    managers.py
    serializers.py
    views.py
    services.py
    urls.py
    permissions.py
  lessons/
    models.py
    serializers.py
    views.py
    urls.py
```
