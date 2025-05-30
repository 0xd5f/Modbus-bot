from apscheduler.schedulers.asyncio import AsyncIOScheduler
from db import SessionLocal, Sensor, TemperatureLog, Event
from modbus import ModbusSensor
from bot.notifications import notify_admins
from logic.alarms import check_alarms
import datetime
import asyncio

async def poll_sensor(sensor_row, bot=None):
    sensor = ModbusSensor(
        port=sensor_row.com_port,
        baudrate=9600,
        address=sensor_row.modbus_addr,
        calibration_offset=sensor_row.calibration_offset
    )
    try:
        value = await sensor.read_temperature()
        async with SessionLocal() as session:
            sensor_row.last_value = value
            sensor_row.last_poll = datetime.datetime.utcnow()
            sensor_row.last_status = 'ok'
            session.add(sensor_row)
            session.add(TemperatureLog(sensor_id=sensor_row.id, value=value))
            await session.commit()
        alarms = await check_alarms(sensor_row, value)
        if alarms and bot:
            for alarm in alarms:
                await notify_admins(bot, f"[{sensor_row.name}] {alarm}")
    except Exception as e:
        async with SessionLocal() as session:
            sensor_row.last_status = 'error'
            session.add(sensor_row)
            session.add(Event(sensor_id=sensor_row.id, event_type='connection_lost', value=None, description=str(e)))
            await session.commit()
        if bot:
            await notify_admins(bot, f"[{sensor_row.name}] Потеря связи: {e}")
    finally:
        await sensor.close()

def start_polling(scheduler: AsyncIOScheduler, bot=None):
    async def schedule_all():
        async with SessionLocal() as session:
            sensors = (await session.execute(Sensor.__table__.select())).scalars().all()
            for sensor in sensors:
                if hasattr(sensor, 'is_blocked') and not sensor.is_blocked:
                    scheduler.add_job(
                        poll_sensor,
                        'interval',
                        seconds=sensor.poll_interval,
                        args=[sensor, bot],
                        id=f'sensor_{sensor.id}',
                        replace_existing=True
                    )
    asyncio.create_task(schedule_all())
