from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select


from model.model import WeatherBase, Base


class DataBase:
    def __init__(self):
        """
        Инициализируем подключение к базе данных SQLite.
        """

        self.engine = create_async_engine(url=f'sqlite+aiosqlite:///weather.db', echo=False)
        self.async_session = sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def create_tables(self) -> None:
        """
        Создание таблицы, если ее еще нет.
        """

        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def save_weather_data(self, data: dict) -> None:
        """
        Преобразование словаря в экземпляр модели `WeatherBase` и сохранение в БД.

        :param data(`dict`): словарь с данными о погоде
        """
        
        async with self.async_session() as session:
            new_weather = WeatherBase(
                temperature=data['temperature'],
                wind_speed=data['wind_speed'],
                wind_direction=data['wind_direction'],
                pressure=data['pressure'],
                precipitation=data['precipitation'],
                precipitation_type=data['precipitation_type'],
                latitude=data['latitude'],
                longitude=data['longitude']
            )
            session.add(new_weather)
            await session.commit()

    async def get_last_n_weather_data(self, n: int) -> list[WeatherBase]:
        """
        Получение последних `n` записей из БД.
        
        :param n(`int`): количество записей
        :return (`list[WeatherBase]`): список последних `n` записей
        """

        async with self.async_session() as session:
            result = await session.execute(select(WeatherBase).order_by(WeatherBase.id.desc()).limit(n))
            return result.scalars().all()
