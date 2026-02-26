## Docker запуск

1. Скопировать `.env.example` в `.env` и заполнить `TG_BOT_TOKEN`, `CHANNEL_ID`, `ADMIN_TG_ID`.
2. Запустить контейнеры:

```bash
docker compose up --build -d
```

3. Проверить логи бота:

```bash
docker compose logs -f bot
```

## Что поднимается

- `postgres` (PostgreSQL 16, база `kabaevbot`)
- `bot` (aiogram бот)

Бот подключается к PostgreSQL по `DATABASE_URL` из `.env`.
