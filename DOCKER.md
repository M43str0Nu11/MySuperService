# Запуск проекта в Docker

## Быстрый старт

1. Открой терминал в папке проекта
2. Запусти:
```bash
docker-compose up -d
```

3. Открой браузер: http://localhost:8080/pages/index.html

## Команды

**Запуск:**
```bash
docker-compose up -d
```

**Остановка:**
```bash
docker-compose down
```

**Перезапуск:**
```bash
docker-compose restart
```

**Логи:**
```bash
docker-compose logs -f
```

**Подключение к БД:**
```bash
docker exec -it mysuperservice-db-1 psql -U weather_user -d weather_db
```

## Проверка БД

После запуска выполни в БД:
```sql
SELECT * FROM weather_avg;
```

Увидишь усреднённые температуры по периодам.

## Структура

- **web** (nginx) - http://localhost:8080
- **db** (postgres) - localhost:5432
  - База: weather_db
  - Юзер: weather_user
  - Пароль: weather_pass

## Следующий шаг

Добавить парсер погоды (Python/Node.js) как третий контейнер.
