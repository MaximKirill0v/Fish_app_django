from django.shortcuts import render
from django.http import HttpResponseNotFound
from abc import ABC, abstractmethod
import requests
import datetime
import folium
from folium.plugins import MarkerCluster
from folium.plugins import Geocoder


class Whether:

    def __init__(self, icon: str = 'Не определено', icon_id: str = 'Не определено', temperature: float = 0,
                 pressure: float = 0, humidity: int = 0, wind_speed: float = 0, wind_deg: int = 0, cloudiness: int = 0,
                 date_whether: str = datetime.date.today()):

        self.__date = date_whether
        self.__icon = icon
        self.__icon_id = icon_id
        self.__temperature = temperature
        self.__pressure = pressure
        self.__humidity = humidity
        self.__wind_speed = wind_speed
        self.__wind_deg = wind_deg
        self.__wind_vector = self.get_wind_vector(self.__wind_deg)
        self.__cloudiness = cloudiness
        self.__path_to_image = self.get_path_to_image_whether()

    @property
    def date_(self):
        return self.__date

    @property
    def icon(self):
        return self.__icon

    @property
    def icon_id(self):
        return self.__icon_id

    @property
    def temperature(self):
        return self.__temperature

    @property
    def pressure(self):
        return self.__pressure

    @property
    def humidity(self):
        return self.__humidity

    @property
    def wind_speed(self):
        return self.__wind_speed

    @property
    def wind_vector(self):
        return self.__wind_vector

    @property
    def cloudiness(self):
        return self.__cloudiness

    @property
    def path(self):

        return self.__path_to_image

    def __str__(self):
        return f'Дата : {self.__date}\n' \
               f'Погода: {self.__icon}, код иконки: {self.__icon_id}\n' \
               f'Температура = {round(self.__temperature)} C\n' \
               f'Давление = {round(self.__pressure / 1.333, 2)} мм.рт.столба\n' \
               f'Влажность = {self.__humidity}%\n' \
               f'Скорость ветра = {round(self.__wind_speed, 1)}м/с, направление = {self.__wind_vector}\n' \
               f'Облачность = {self.__cloudiness} %'

    @staticmethod
    def get_wind_vector(deg: int):
        if 0 <= deg <= 10 or 350 <= deg <= 360:
            return 'С'
        elif 11 <= deg <= 80:
            return 'СВ'
        elif 11 <= deg <= 80:
            return 'СВ'
        elif 81 <= deg <= 100:
            return 'В'
        elif 101 <= deg <= 170:
            return 'ЮВ'
        elif 171 <= deg <= 190:
            return 'Ю'
        elif 191 <= deg <= 260:
            return 'ЮЗ'
        elif 261 <= deg <= 280:
            return 'З'
        elif 281 <= deg <= 349:
            return 'СЗ'

    def get_path_to_image_whether(self):
        return "image/logo/" + self.__icon_id + ".png"


class Date:
    __day_of_week_dict = {0: "Пн", 1: "Вт", 2: "Ср", 3: "Чт", 4: "Пт", 5: "Сб", 6: "Вс"}

    @classmethod
    def get_format_day_by_datetime(cls):
        date_today = datetime.date.today()
        day_of_week = datetime.datetime.weekday(date_today)
        date_today_str = str(date_today)

        date_str = cls.__day_of_week_dict[day_of_week] + ' ' + str(date_today_str[8:]) + '.' + str(
            date_today_str[5:7]) + '.'
        return date_str

    @classmethod
    def get_format_day_by_str(cls, date):
        day_form = datetime.date(int(date[:4]), int(date[5:7]), int(date[8:]))
        day_of_week = datetime.datetime.weekday(day_form)
        day_str = str(day_form)
        date_str = cls.__day_of_week_dict[day_of_week] + ' ' + str(day_str[8:]) + '.' + str(
            day_str[5:7]) + '.'

        return date_str


class ManagerWhether(ABC):

    @abstractmethod
    def get_whether_today(self, name_city):
        raise NotImplementedError

    @abstractmethod
    def get_whether_for_four_days(self, name_city):
        raise NotImplementedError


class ManagerFromOpenWhether(ManagerWhether):
    __app_id = "379d91fde3e91016c1663606393c4afc"

    @classmethod
    def get_whether_today(cls, name_city: str = "Ярославль"):
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/find",
                               params={'q': name_city, 'type': 'like', 'units': 'metric', 'lang': 'ru',
                                       'APPID': cls.__app_id})
            data = res.json()

            icon = data['list'][0]['weather'][0]['description']
            icon_id = data['list'][0]['weather'][0]['icon']

            temperature = round(data['list'][0]['main']['temp'])

            pressure = round(data['list'][0]['main']['pressure'] / 1.33, 2)

            humidity = data['list'][0]['main']['humidity']

            wind_speed = round(data['list'][0]['wind']['speed'], 1)
            wind_deg = data['list'][0]['wind']['deg']

            cloudiness = data['list'][0]['clouds']['all']

            date_str = Date.get_format_day_by_datetime()

            return Whether(icon, icon_id, temperature, pressure, humidity, wind_speed, wind_deg, cloudiness, date_str)

        except Exception as e:
            print("Ошибка в получении данных о погоде на 1 день:", e)

    @classmethod
    def get_whether_for_four_days(cls, name_city: str = "Ярославль"):
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/forecast",
                               params={'q': name_city, 'units': 'metric', 'lang': 'ru', 'APPID': cls.__app_id})
            data = res.json()

            res_list = []

            for num, elem in enumerate(data['list']):
                if num in (0, 1, 2, 3, 4):
                    continue

                time = elem['dt_txt'][11:]
                if time == '12:00:00':
                    date_str = elem['dt_txt'][:10]
                    date = Date.get_format_day_by_str(date_str)

                    icon = elem['weather'][0]['description']
                    icon_id = elem['weather'][0]['icon']

                    temperature = round(elem['main']['temp'])

                    pressure = round(elem['main']['pressure'] / 1.33, 2)

                    humidity = elem['main']['humidity']

                    wind_speed = round(elem['wind']['speed'], 1)
                    wind_deg = elem['wind']['deg']

                    cloudiness = elem['clouds']['all']

                    res_list.append(Whether(icon, icon_id, temperature, pressure, humidity, wind_speed, wind_deg,
                                            cloudiness, date))
                    if len(res_list) == 4:
                        break

            return res_list

        except Exception as e:
            print("Ошибка в получении данных о погоде на 4 дня:", e)

    @classmethod
    def get_coord_city(cls, name_city: str):
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/find",
                               params={'q': name_city, 'type': 'like', 'units': 'metric', 'lang': 'ru',
                                       'APPID': cls.__app_id})
            data = res.json()
            lat = data['list'][0]['coord']['lat']
            lon = data['list'][0]['coord']['lon']
            return lat, lon
        except Exception as e:
            print("Ошибка в получении координат населённого пункта:", e)


class MapFolium:
    map = None
    path_to_save_map = r'C:\Users\NoteBook\Desktop\Академия шаг\Django_fish_app\Fish_app_django\templates\map.html'

    def start_map(self, coord: tuple = (57.6299, 39.8737)):
        if coord is None:
            coord = (57.6299, 39.8737)
        self.map = folium.Map(
            location=list(coord),
            tiles=None,
            zoom_start=10,
            control_scale=True,
            zoom_control=False,
        )
        return self.map

    def save_to_html_file(self):
        self.map.save(self.path_to_save_map)

    def change_path(self, new_path: str):
        self.path_to_save_map = new_path

    def get_geocoder(self):
        Geocoder(collapsed=True, add_marker=False).add_to(self.map)

    def locate_control(self):
        folium.plugins.LocateControl(auto_start=True).add_to(self.map)

    def full_screen(self):
        folium.plugins.Fullscreen(
            position="bottomright",
            title="На весь экран",
            title_cancel="Выход из полноэкранного режима",
            force_separate_button=True,
        ).add_to(self.map)

    def tile_layer_map(self):
        folium.TileLayer("OpenStreetMap", max_zoom=16).add_to(self.map)
        folium.TileLayer("Stamen Toner", show=False, max_zoom=16).add_to(self.map)
        folium.TileLayer("Stamen Terrain", show=False, max_zoom=13).add_to(self.map)
        folium.TileLayer("Stamen Watercolor", show=False, max_zoom=13).add_to(self.map)

        folium.LayerControl(position="topright").add_to(self.map)


class TemplateWebSite(ABC):

    @abstractmethod
    def main(request):
        return HttpResponseNotFound("Not found")

    @abstractmethod
    def catch(request):
        return HttpResponseNotFound("Not found")


class PageFishWebSite(TemplateWebSite):

    def main(request):
        city_name = request.POST.get("city")
        print(city_name)

        whether_today = ManagerFromOpenWhether.get_whether_today(city_name)
        whether_four_days = ManagerFromOpenWhether.get_whether_for_four_days(city_name)

        get_coord_city = ManagerFromOpenWhether.get_coord_city(city_name)
        print(get_coord_city)

        map = MapFolium()
        map.start_map(get_coord_city)
        map.full_screen()
        map.tile_layer_map()
        map.save_to_html_file()

        data = {'whether_today': whether_today, 'whether_four_days': whether_four_days, 'city_name': city_name}

        return render(request, 'main.html', context=data)

    def catch(request):
        return render(request, 'catch.html')
