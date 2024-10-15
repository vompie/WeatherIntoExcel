import aiohttp
import asyncio


class WeatherAPI:
    def __init__(self, latitude: float, longitude: float, interval: int, stream_output_data: callable):
        """
        Инициализирует экземпляр класса для работы с API open-meteo.

        :param latitude(`float`): широта
        :param longitude(`float`): долгота
        :param interval(`int`): интервал между запросами в секундах
        :param stream_output_data(`callable`): функция для передачи полученных данных в БД
        """

        self.latitude = latitude
        self.longitude = longitude
        self.interval = interval
        self.url = 'https://api.open-meteo.com/v1/forecast'
        self.params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ["temperature_2m", "precipitation", "rain", "showers", "snowfall", "surface_pressure", "wind_speed_10m", "wind_direction_10m"],
            "wind_speed_unit": "ms",
            "timezone": "Europe/Moscow",
            "forecast_days": 1
        }
        self.stream_output_data: callable = stream_output_data

    async def fetch_weather_periodically(self) -> None:
        """
        В цикле повторяет запрос погоды каждые `self.interval` секунд.
        Получает данные погоды и отправлят полученные данные в переданную функцию.
        """

        while True:
            weather_data = await self.get_weather() # асинхронный запрос погоды
            if weather_data:
                # если данные успешно получены
                await self.stream_output_data(weather_data) # отправляет данные в переданную функцию
            await asyncio.sleep(self.interval)

    async def get_weather(self) -> dict:
        """
        Запрашивает данные погоды и возвращает полученные данные в случае успеха, или пустой `dict` в случае ошибки.
        """

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url=self.url, params=self.params) as response:
                    if response.status == 200:
                        weather_data = await response.json() # получаем json из ответа

                        weather_data: dict = weather_data['current'] # вытаскиваем данные о текущей погоде
                        weather = {
                            'latitude': self.latitude, # широта
                            'longitude': self.longitude, # долгота
                            'temperature': weather_data.get('temperature_2m', None), # температура С
                            'wind_speed': weather_data.get('wind_speed_10m', None), # скорость ветра м/с
                            'wind_direction': weather_data.get('wind_direction_10m', None), # направление ветра *
                            'pressure': weather_data.get('surface_pressure', None), # давление hPa
                            'precipitation': weather_data.get('precipitation', None), # осадки мм
                            'rain': weather_data.get('rain', None), # дождь мм
                            'showers': weather_data.get('showers', None), # ливень см
                            'snowfall': weather_data.get('snowfall', None), # снег смм
                        }

                        # преобразовываем данные о направлении ветра, давлении в нужные ед. изм. и тип осадков
                        weather['wind_direction'] = self.wind_direction(degree=weather['wind_direction'])
                        weather['pressure'] = self.surface_pressure(hPa=weather['pressure'])
                        weather['precipitation_type'] = self.precipitation_type(rain=weather['rain'], showers=weather['showers'], snowfall=weather['snowfall'])

                        return weather
                    print(f"Ошибка при обращение к API. Код: {response.status}")
            except Exception as e:
                print(f"Ошибка при выполнение запроса: {e}")
        return {}

    def wind_direction(self, degree: int) -> str:
        """
        Преобразовывает угол направления ветра в текстовое описание направления.
        
        :param degree(`int`): угол направления в градусах
        :return (`str`): текстовое описание направления
        """

        if not degree:
            return "Неверное направление"

        match degree:
            case degree if (degree >= 338 or degree < 23):
                return "С"
            case degree if 23 <= degree < 68:
                return "СВ"
            case degree if 68 <= degree < 113:
                return "В"
            case degree if 113 <= degree < 158:
                return "ЮВ"
            case degree if 158 <= degree < 203:
                return "Ю"
            case degree if 203 <= degree < 248:
                return "ЮЗ"
            case degree if 248 <= degree < 293:
                return "З"
            case degree if 293 <= degree < 338:
                return "СЗ"
            case _:
                return "Неизвестное направление"
            
    def surface_pressure(self, hPa: float) -> int:
        """
        Преобразовывает давление из hPa в мм рт. ст.
        
        :param hPa(`float`): давление в hPa
        :return (`int`): давление в мм рт. ст.
        """

        if not hPa:
            return 0.0
        return int(hPa / 133.322 * 100)  # перевод из диапазона hPa в мм рт. ст. 

    def precipitation_type(self, rain: float, showers: float, snowfall: float) -> str:
        """
        Определяет вид осадков
        
        :param rain(`float`): дождь
        :param showers(`float`): ливень
        :param snowfall(`float`): снег
        :return (`str`): вид осадков
        """
        
        precipitation_list = []

        if snowfall > 0:
            precipitation_list.append('снег')
        if showers > 0:
            precipitation_list.append('ливень')
        if rain > 0:
            precipitation_list.append('дождь')

        if not precipitation_list:
            return 'Без осадков'
        
        return (', '.join(precipitation_list)).capitalize()      
