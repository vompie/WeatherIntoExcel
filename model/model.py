from sqlalchemy import Column, Integer, Float, DateTime, String, func
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class WeatherBase(Base):
    __tablename__ = 'weather'

    id = Column(Integer, primary_key=True, autoincrement=True)
    temperature = Column(Float)
    wind_speed = Column(Float)
    wind_direction = Column(String)
    pressure = Column(Integer)
    precipitation = Column(Float)
    precipitation_type = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    created_at = Column(DateTime, default=func.now())
