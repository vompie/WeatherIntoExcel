import pandas as pd


class ExcelWorker:
    def __init__(self, file_name: str):
        """
        Инициализирует экземпляр класса для работы с Excel.
        
        :param file_name(`str`): имя файла для сохранения (например, 'weather.xlsx')
        """

        self.file_name = file_name
    
    def __datas_to_dicts(self, data: list[object]) -> list[dict]:
        """
        Преобразует данные из списка объектов в список словарей.
        
        :param data(`list[object]`): список объектов с данными
        :return `list[dict]`: список словарей с данными
        """

        data_dicts = [
            {
                'Температура (С)': record.temperature,
                'Скорость ветра (м/с)': record.wind_speed,
                'Направление ветра': record.wind_direction,
                'Давление (мм. рт. ст.)': record.pressure,
                'Осадки (мм.)': record.precipitation,
                'Тип осадков': record.precipitation_type,
                'Дата обновления (GMT +0)': record.created_at,
                'Широта': record.latitude,
                'Долгота': record.longitude
            }
            for record in data
        ]
        return data_dicts

    def save_data_to_excel(self, data: list[object]) -> None:
        """
        Сохраняет данные в таблицу Excel.

        :param data(`list[object]`): список данных для сохранения в Excel
        """

        data_dicts = self.__datas_to_dicts(data=data) # преобразование данных в список словарей
        df = pd.DataFrame(data_dicts) # преобразование данных в DataFrame

        # сохранение DataFrame в Excel
        try:
            df.to_excel(self.file_name, index=False)
            print(f"Данные сохранены в {self.file_name}")
        except PermissionError as e:
            # ошибка, возникающая, если где-то файл открыт
            print(f"Закройте файл {self.file_name} и попробуйте еще раз")
