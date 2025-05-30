import sqlalchemy as sa
import sqlalchemy.ext.asyncio as async_sa
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, BigInteger, ForeignKey, DateTime, Text
from sqlalchemy.sql import func

DATABASE_URL = "sqlite+aiosqlite:///modbus.db"
Base = declarative_base()

class Sensor(Base):
    __tablename__ = 'sensors'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    modbus_addr = Column(Integer, nullable=False)
    min_temp = Column(Float, nullable=False)
    max_temp = Column(Float, nullable=False)
    poll_interval = Column(Integer, default=30)
    calibration_offset = Column(Float, default=0)
    is_blocked = Column(Boolean, default=False)
    last_value = Column(Float)
    last_poll = Column(DateTime)
    last_status = Column(String)
    com_port = Column(String, nullable=False, default='COM1')

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String)
    is_admin = Column(Boolean, default=False)
    receive_notifications = Column(Boolean, default=True)

class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensors.id'))
    event_type = Column(String)
    value = Column(Float)
    timestamp = Column(DateTime, server_default=func.now())
    description = Column(Text)
    user_id = Column(Integer, ForeignKey('users.id'))

class TemperatureLog(Base):
    __tablename__ = 'temperature_log'
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey('sensors.id'))
    value = Column(Float)
    timestamp = Column(DateTime, server_default=func.now())

engine = async_sa.create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = async_sa.async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
