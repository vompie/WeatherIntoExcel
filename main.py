import asyncio
import os
from dotenv import load_dotenv

from weather_api import WeatherAPI
from database import DataBase
from export_to_excel import ExcelWorker


# Получение переменных окружения
load_dotenv('.env')
INTERVAL = int(os.getenv("INTERVAL"))
LATITUDE = float(os.getenv("LATITUDE"))
LONGITUDE = float(os.getenv("LONGITUDE"))
ROW_COUNT = int(os.getenv("ROW_COUNT"))


async def menu(database: DataBase) -> None:
    """
    Меню приложения. Принимает в качестве аргумента экземпляр базы данных.
    
    :param database(`DataBase`): экземпляр базы данных
    """

    # Получение экземпляра экспортера в Excel
    excel = ExcelWorker(file_name='weather.xlsx')

    try:
        while True:
            # Меню
            choose = await asyncio.to_thread(input, f"1. Выгрузить последние {ROW_COUNT} записей в Excel\n0. Выход\n\nВыбор: ")
            if choose == '0':
                # выход из программы
                raise SystemExit("Программа завершена")

            elif choose == '1':
                # получение последних ROW_COUNT записей
                last_records = await database.get_last_n_weather_data(ROW_COUNT)

                if not last_records:
                    print("Данные не найдены")
                    continue

                # сохранение данных в Excel
                excel.save_data_to_excel(data=last_records)
    except SystemExit as e:
        raise


async def main() -> None:
    """
    Основной цикл приложения.
    
    1. Создание базы данных и таблиц.
    2. Запуск потока для получения погоды с указаным интервалом.
    3. Запуск меню для взаимодействия с пользователем.
    """

    # Получение экземпляра базы данных и создание таблиц
    database = DataBase()
    await database.create_tables()

    # Получение экземпляра класса для работы с API open-meteo
    weather_api = WeatherAPI(latitude=LATITUDE, longitude=LONGITUDE, interval=INTERVAL, stream_output_data=database.save_weather_data)

    # Список задач
    tasks = [
        asyncio.create_task(weather_api.fetch_weather_periodically()),
        asyncio.create_task(menu(database=database))
    ]

    try:
        # Одновременное выполнение нескольких корутин: запрос данных о погоде и обработка пользовательского ввода
        await asyncio.gather(*tasks)
    except SystemExit:
        # Завершение работы программы
        for task in tasks:
            task.cancel()  # отмена задач
        await asyncio.gather(*tasks, return_exceptions=True)  # завершение задач


if __name__ == '__main__':
    """
    Запуск основного цикла с использованием asyncio.run().
    """
    
    asyncio.run(main())
