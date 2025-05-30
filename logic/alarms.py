from db import SessionLocal, Sensor, Event
import datetime

async def check_spike(sensor_row, value, session, window_minutes=5, spike_delta=5.0):
    from db import TemperatureLog
    since = datetime.datetime.utcnow() - datetime.timedelta(minutes=window_minutes)
    logs = (await session.execute(
        TemperatureLog.__table__.select().where(
            (TemperatureLog.sensor_id == sensor_row.id) &
            (TemperatureLog.timestamp >= since)
        )
    )).scalars().all()
    if not logs:
        return None
    prev = logs[0].value
    if abs(value - prev) >= spike_delta:
        return f"Резкий скачок температуры: {prev} → {value} за {window_minutes} мин."
    return None

async def check_alarms(sensor_row, value):
    alarms = []
    if value < sensor_row.min_temp:
        alarms.append(f"Температура ниже порога: {value} < {sensor_row.min_temp}")
    if value > sensor_row.max_temp:
        alarms.append(f"Температура выше порога: {value} > {sensor_row.max_temp}")
    async with SessionLocal() as session:
        spike = await check_spike(sensor_row, value, session)
        if spike:
            alarms.append(spike)
        for alarm in alarms:
            session.add(Event(sensor_id=sensor_row.id, event_type='alarm', value=value, description=alarm))
        await session.commit()
    return alarms
