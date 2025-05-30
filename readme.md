# Telegram Modbus Temperature Monitoring Bot

## Описание

Асинхронный Telegram-бот для мониторинга промышленных датчиков температуры, подключённых к контроллеру ОВЕН ТРМ200 по Modbus RTU (RS-485).

- Считывание температуры с датчиков по Modbus RTU (разные COM-порты)
- Уведомления в Telegram при выходе за пороги, скачках, потере связи
- Админка через Telegram: добавление/удаление/настройка датчиков, управление пользователями
- Логирование событий и температур в SQLite/PostgreSQL
- Просмотр графиков и экспорт логов
- Расширяемая архитектура для новых устройств

## Используемые технологии
- Python 3.11+
- aiogram (Telegram Bot API)
- pymodbus (Modbus RTU)
- apscheduler (планировщик)
- SQLAlchemy (ORM)
- matplotlib (графики)
- SQLite/PostgreSQL (БД)

## Быстрый старт

1. Установите зависимости:
   ```sh
   pip install -r requirements.txt
   ```
2. Укажите токен Telegram-бота в `main.py`:
   ```python
   API_TOKEN = "<ваш_токен>"
   ```
3. Запустите бота:
   ```sh
   python main.py
   ```

## Основные команды

- `/start` — справка
- `/add_sensor [имя] [modbus_addr] [min_temp] [max_temp] [com_port]` — добавить датчик
- `/calibrate [имя] [коррекция]` — автокалибровка датчика
- `/logs [имя] [дата]` — график температуры за дату
- `/block [имя]` — временно отключить уведомления по датчику
- `/sensors` — список всех датчиков

## Структура проекта

- `main.py` — точка входа
- `db.py` — модели и инициализация БД
- `modbus.py` — работа с Modbus RTU
- `scheduler.py` — опрос датчиков и тревоги
- `bot/handlers.py` — Telegram-команды
- `bot/notifications.py` — уведомления
- `bot/plots.py` — построение графиков
- `logic/alarms.py` — обработка тревог
- `logic/calibration.py` — автокалибровка

## Схема базы данных

- **sensors**: id, name, modbus_addr, min_temp, max_temp, poll_interval, calibration_offset, is_blocked, last_value, last_poll, last_status, com_port
- **users**: id, telegram_id, username, is_admin, receive_notifications
- **events**: id, sensor_id, event_type, value, timestamp, description, user_id
- **temperature_log**: id, sensor_id, value, timestamp

## Примечания
- Для работы с реальным оборудованием укажите правильный COM-порт и параметры в /add_sensor.
- Для PostgreSQL измените строку подключения в `db.py`.
- Для добавления новых типов устройств реализуйте новый класс и зарегистрируйте его в системе.

---

**Автор:** [0xd5f](https://github.com/0xd5f)
---
BTC: `bc1q20yn32a9ykkgcf7r8g23n7gwqzzfj9u932w4ww`
