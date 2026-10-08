# My Eats

Клиент-серверное приложение для просмотра меню и оформления заказов. Backend построен на FastAPI, frontend — на React/Vite, данные хранятся в PostgreSQL.

## Локальный запуск через Docker Compose

Требования: Docker и Docker Compose.

1. Создайте локальный файл конфигурации из шаблона:

   ```bash
   cp .env.example .env
   ```

2. При необходимости измените значения в `.env`. Файл `.env` содержит локальные настройки и пароли, поэтому не добавляйте его в Git и не передавайте вместе с исходным кодом.

3. Соберите и запустите приложение:

   ```bash
   docker compose up --build
   ```

4. Откройте frontend по адресу `http://localhost:8080`.

Backend доступен на `http://localhost:8000`, проверка состояния — `http://localhost:8000/health`. Документация API FastAPI доступна по адресу `http://localhost:8000/docs`.

## Остановка

```bash
docker compose down
```

Данные PostgreSQL сохраняются в Docker volume `postgres_data`. Для остановки с удалением данных используйте `docker compose down -v`.

## Конфигурация

Шаблон `.env.example` содержит следующие группы параметров:

- параметры PostgreSQL;
- порт backend и уровень логирования;
- внешний порт frontend;
- строку подключения SQLAlchemy.

Для production-среды секреты следует передавать через защищенное хранилище секретов или переменные окружения CI/CD, а не хранить в файле рядом с исходным кодом.
