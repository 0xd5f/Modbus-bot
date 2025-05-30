from aiogram import types, Dispatcher
from db import SessionLocal, Sensor, User, Event, TemperatureLog
from bot.notifications import notify_admins, notify_users
from bot.plots import send_temperature_plot
import datetime

async def cmd_add_sensor(message: types.Message):
    args = message.get_args().split()
    if len(args) < 5:
        await message.reply("Usage: /add_sensor [имя] [modbus_addr] [min_temp] [max_temp] [com_port]")
        return
    name, addr, min_temp, max_temp, com_port = args[0], int(args[1]), float(args[2]), float(args[3]), args[4]
    async with SessionLocal() as session:
        sensor = Sensor(name=name, modbus_addr=addr, min_temp=min_temp, max_temp=max_temp, com_port=com_port)
        session.add(sensor)
        await session.commit()
    await message.reply(f"Sensor {name} added on {com_port}.")

async def cmd_calibrate(message: types.Message):
    args = message.get_args().split()
    if len(args) < 2:
        await message.reply("Usage: /calibrate [имя] [коррекция]")
        return
    name, offset = args[0], float(args[1])
    async with SessionLocal() as session:
        sensor = (await session.execute(Sensor.__table__.select().where(Sensor.name == name))).scalar_one_or_none()
        if not sensor:
            await message.reply("Sensor not found.")
            return
        sensor.calibration_offset = offset
        session.add(sensor)
        await session.commit()
    await message.reply(f"Sensor {name} calibrated by {offset}.")

async def cmd_logs(message: types.Message):
    args = message.get_args().split()
    if len(args) < 2:
        await message.reply("Usage: /logs [имя] [дата YYYY-MM-DD]")
        return
    name, date_str = args[0], args[1]
    async with SessionLocal() as session:
        sensor = (await session.execute(Sensor.__table__.select().where(Sensor.name == name))).scalar_one_or_none()
        if not sensor:
            await message.reply("Sensor not found.")
            return
        date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        logs = (await session.execute(TemperatureLog.__table__.select().where(
            (TemperatureLog.sensor_id == sensor.id) &
            (TemperatureLog.timestamp >= date) &
            (TemperatureLog.timestamp < date + datetime.timedelta(days=1))
        ))).scalars().all()
        if not logs:
            await message.reply("No logs for this date.")
            return
        await send_temperature_plot(message, logs, sensor.name)

async def cmd_block(message: types.Message):
    args = message.get_args().split()
    if len(args) < 1:
        await message.reply("Usage: /block [имя]")
        return
    name = args[0]
    async with SessionLocal() as session:
        sensor = (await session.execute(Sensor.__table__.select().where(Sensor.name == name))).scalar_one_or_none()
        if not sensor:
            await message.reply("Sensor not found.")
            return
        sensor.is_blocked = True
        session.add(sensor)
        await session.commit()
    await message.reply(f"Sensor {name} notifications blocked.")

async def cmd_sensors(message: types.Message):
    async with SessionLocal() as session:
        sensors = (await session.execute(Sensor.__table__.select())).scalars().all()
        if not sensors:
            await message.reply("Нет добавленных датчиков.")
            return
        lines = []
        for s in sensors:
            lines.append(
                f"<b>{s.name}</b> | addr: <code>{s.modbus_addr}</code> | min: <code>{s.min_temp}</code> | max: <code>{s.max_temp}</code> | port: <code>{s.com_port}</code> | blocked: <code>{'да' if s.is_blocked else 'нет'}</code> | last: <code>{s.last_value if s.last_value is not None else '-'}°C</code>"
            )
        await message.reply("\n".join(lines), parse_mode="HTML")

async def cmd_start(message: types.Message):
    await message.reply(
        "Бот для мониторинга промышленных датчиков температуры.\n"
        "Доступные команды:\n"
        "/add_sensor [имя] [modbus_addr] [min_temp] [max_temp] [com_port]\n"
        "/calibrate [имя] [коррекция]\n"
        "/logs [имя] [дата]\n"
        "/block [имя]\n"
        "/sensors — список всех датчиков"
    )

def register_handlers(dp: Dispatcher, scheduler):
    dp.register_message_handler(cmd_start, commands=["start"])
    dp.register_message_handler(cmd_add_sensor, commands=["add_sensor"])
    dp.register_message_handler(cmd_calibrate, commands=["calibrate"])
    dp.register_message_handler(cmd_logs, commands=["logs"])
    dp.register_message_handler(cmd_block, commands=["block"])
    dp.register_message_handler(cmd_sensors, commands=["sensors"])
