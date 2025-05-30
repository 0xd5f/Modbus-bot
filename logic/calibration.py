from db import SessionLocal, Sensor, Event

async def calibrate_sensor(name, offset):
    async with SessionLocal() as session:
        sensor = (await session.execute(Sensor.__table__.select().where(Sensor.name == name))).scalar_one_or_none()
        if not sensor:
            return False
        sensor.calibration_offset = offset
        session.add(sensor)
        session.add(Event(sensor_id=sensor.id, event_type='admin_action', value=offset, description=f'Калибровка на {offset}'))
        await session.commit()
    return True
