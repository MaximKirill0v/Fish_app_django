import ctypes

import branca
import clipboard
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import render
from django.http import HttpResponseNotFound, response
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from abc import ABC, abstractmethod
import requests
import datetime
import folium
from django.views.generic import CreateView
from folium.plugins import MarkerCluster
from folium.plugins import Geocoder

from .cities import cities_tuple
from .forms import AddCatchForm

from .models import Catch


class GetWhetherError(Exception):
    def __init__(self, text):
        self.__text = text


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
    __name_city = "Ярославль"

    @property
    def name_city(self):
        return self.__name_city

    @name_city.setter
    def name_city(self, other):
        self.__name_city = other

    @classmethod
    def get_whether_today(cls, name_city: str = __name_city):
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

        except GetWhetherError as e:
            print("Ошибка в получении данных о погоде на 1 день:", e)

    @classmethod
    def get_whether_for_four_days(cls, name_city: str = __name_city):
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

        except GetWhetherError as e:
            print("Ошибка в получении данных о погоде на 4 дня:", e)

    @classmethod
    def get_coord_city(cls, name_city: str = __name_city):
        try:
            res = requests.get("http://api.openweathermap.org/data/2.5/find",
                               params={'q': name_city, 'type': 'like', 'units': 'metric', 'lang': 'ru',
                                       'APPID': cls.__app_id})
            data = res.json()

            lat = data['list'][0]['coord']['lat']
            lon = data['list'][0]['coord']['lon']
            return lat, lon
        except GetWhetherError as e:
            print("Ошибка в получении координат населённого пункта:", e)

    @classmethod
    def get_whether_today_by_coord(cls, coord: list[float, float]):
        try:
            weather = Whether()
            res = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?lat={coord[0]}&lon={coord[1]}&type=like&units=metric&lang=ru&appid={cls.__app_id}&")
            data = res.json()
            temperature = round(data['main']['temp'])
            pressure = round(data['main']['pressure'] / 1.33, 2)
            humidity = data['main']['humidity']
            wind_speed = round(data['wind']['speed'], 1)
            wind_deg = data['wind']['deg']
            wind_vector = weather.get_wind_vector(wind_deg)
            cloudiness = data['clouds']['all']
            name_of_the_area = data['name']
            description = data['weather'][0]['description']

            return temperature, pressure, humidity, wind_speed, wind_vector, cloudiness, name_of_the_area, description

        except GetWhetherError as e:
            print("Ошибка в получении погоды по координатам населённого пункта:", e)


class MapFolium:
    map = None
    coord_default = (57.6299, 39.8737)

    def start_map(self, coord: tuple = coord_default, zoom: int = 10):
        if coord is None:
            coord = (57.6299, 39.8737)
        self.map = folium.Map(
            location=list(coord),
            tiles=None,
            zoom_start=zoom,
            control_scale=True,
            zoom_control=False,
        )
        return self.map

    def save_to_html_file(self, path):
        self.map.save(path)

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

    def click_marker(self):
        self.map.add_child(folium.ClickForMarker("<b>Широта:</b> ${lat}<br /><b>Долгота:</b> ${lng}"))
        self.map.add_child(folium.ClickForLatLng(format_str='lat + "," + lng', alert=True))

    def place_marker(self, data_tuple: tuple = None, coord: list[float, float] = None):
        if coord is None:
            return self.map
        html = f'''
            <img src="/static/image/background/image_1.jpg" width="300px" height="200px">
         
                <p style="font-size: 16px">
                Название местности: <b>{data_tuple[0]}</b><br>
                Дата: <b>{data_tuple[1]}</b> Время: <b>{data_tuple[2]}</b><br>
                Рыба: <b>{data_tuple[3]}</b> Вес: <b>{data_tuple[4] / 1000}кг.</b><br>
                Приманка: <b>{data_tuple[5]}</b><br>
                Погода: <b>{data_tuple[6]}</b><br>
                Температура: <b>{data_tuple[7]} &deg;С</b> Давление: <b>{data_tuple[8]}</b><br>
                Влажность: <b>{data_tuple[9]}</b> Облачность: <b>{data_tuple[12]}</b></br>
                Скорость и направление ветра: <b>{data_tuple[10]} {data_tuple[11]}</b>
                </p>
                '''
        folium.Marker(coord, popup=html).add_to(self.map)


class BuilderMap:
    map = MapFolium()
    path_to_save_map_on_main = \
        r'C:\Users\NoteBook\Desktop\Академия шаг\Django_fish_app\Fish_app_django\templates\map_on_main.html'
    path_to_save_map_on_add_cath = \
        r'C:\Users\NoteBook\Desktop\Академия шаг\Django_fish_app\Fish_app_django\templates\map_on_add_catch.html'

    def change_path_on_main(self, new_path: str):
        self.path_to_save_map_on_main = new_path

    def change_path_on_add_catch(self, new_path: str):
        self.path_to_save_map_on_add_cath = new_path

    def map_on_main(self, coord_city: tuple):
        self.map.start_map(coord_city)
        self.map.full_screen()
        self.map.tile_layer_map()
        self.map.save_to_html_file(self.path_to_save_map_on_main)

    def map_on_add_catch(self):
        self.map.start_map()
        self.map.full_screen()
        self.map.tile_layer_map()
        self.map.click_marker()
        self.map.save_to_html_file(self.path_to_save_map_on_add_cath)


class InputState:
    __data_citi = ['Ярославль']

    def get_data_citi(self):
        return self.__data_citi[0]

    def add(self, citi_name: str):
        self.__data_citi[0] = citi_name


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
        city_state = InputState()

        map = BuilderMap()

        if city_name is None:
            city_name = city_state.get_data_citi()

        if city_name.lower() in cities_tuple:
            city_state.add(city_name)

            whether_today = ManagerFromOpenWhether.get_whether_today(city_state.get_data_citi())
            whether_four_days = ManagerFromOpenWhether.get_whether_for_four_days(city_state.get_data_citi())

            get_coord_city = ManagerFromOpenWhether.get_coord_city(city_state.get_data_citi())

            map.map_on_main(get_coord_city)

            data = {'whether_today': whether_today, 'whether_four_days': whether_four_days,
                    'city_name': city_state.get_data_citi().capitalize()}

            return render(request, 'main.html', context=data)

        elif city_name == '':
            whether_today = ManagerFromOpenWhether.get_whether_today(city_state.get_data_citi())
            whether_four_days = ManagerFromOpenWhether.get_whether_for_four_days(city_state.get_data_citi())

            get_coord_city = ManagerFromOpenWhether.get_coord_city(city_state.get_data_citi())

            map.map_on_main(get_coord_city)

            data = {'whether_today': whether_today, 'whether_four_days': whether_four_days,
                    'city_name': city_state.get_data_citi().capitalize()}

            return render(request, 'main.html', context=data)

        else:
            whether_today = ManagerFromOpenWhether.get_whether_today(city_state.get_data_citi())
            whether_four_days = ManagerFromOpenWhether.get_whether_for_four_days(city_state.get_data_citi())

            get_coord_city = ManagerFromOpenWhether.get_coord_city(city_state.get_data_citi().capitalize())

            map.map_on_main(get_coord_city)

            return render(request, 'main.html', {
                "notification": """
                                                <svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
                                                  <symbol id="exclamation-triangle-fill" fill="currentColor" viewBox="0 0 16 16">
                                                    <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
                                                  </symbol>
                                                </svg>
                                                <div class="alert alert-dark d-flex alert-dismissible pl-5" role="alert" style="display: block; float: right; margin-right: 12%; width: 17%;">
                                                     <svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg>

                                                    <strong style="font-size: 16px; padding-left: 20px;"> Город не найден </strong>
                                                    <button type="button" class="btn-close" data-bs-dismiss="alert" style="padding-top: 10%;" aria-label="Close"></button>
                                                 </div>
                                             """,
                'whether_today': whether_today, 'whether_four_days': whether_four_days,
                'city_name': city_state.get_data_citi().capitalize()})

    def catch(request):

        user_id = request.user.id

        user_data = Catch.objects.filter(login_id=user_id).values('name_of_the_area', 'description_weather', 'date',
                                                                  'time', 'temperature', 'pressure', 'humidity',
                                                                  'wind_speed', 'wind_vector', 'cloudy', 'type_of_fish',
                                                                  'fish_weight', 'bait', 'image', 'latitude',
                                                                  'longitude')

        path_to_save_map_on_catch = \
            r'C:\Users\NoteBook\Desktop\Академия шаг\Django_fish_app\Fish_app_django\templates\map_on_catch.html'
        map_on_catch = MapFolium()
        map_on_catch.start_map(zoom=7)
        map_on_catch.full_screen()
        map_on_catch.tile_layer_map()

        if user_data:
            for element in user_data:
                name_of_the_area = element['name_of_the_area']
                description_weather = element['description_weather']
                date = element['date']
                time = element['time']
                temperature = element['temperature']
                pressure = element['pressure']
                humidity = element['humidity']
                wind_speed = element['wind_speed']
                wind_vector = element['wind_vector']
                cloudy = element['cloudy']
                type_of_fish = element['type_of_fish']
                fish_weight = element['fish_weight']
                bait = element['bait']
                image = element['image']
                latitude = element['latitude']
                longitude = element['longitude']

                data_tuple = (name_of_the_area, date, time, type_of_fish, fish_weight, bait, description_weather,
                              temperature, pressure, humidity, wind_speed, wind_vector, cloudy)

                map_on_catch.place_marker(data_tuple, [latitude, longitude])

        map_on_catch.save_to_html_file(path_to_save_map_on_catch)

        return render(request, 'catch.html')


class RegisterUser(SuccessMessageMixin, CreateView):
    form_class = UserCreationForm
    template_name = 'registration.html'
    success_message = "Регистрация прошла успешно! Авторизуйтесь на сайте!"

    def get_success_url(self):
        return reverse_lazy('catch')


class AddCatch(SuccessMessageMixin, CreateView):
    form_class = AddCatchForm
    template_name = 'add_catch.html'
    success_message = 'Улов успешно добавлен'

    map = BuilderMap()
    map.map_on_add_catch()

    def form_valid(self, form):
        lat_and_lon_lst = clipboard.paste().split(",")

        if len(lat_and_lon_lst) != 2:
            return render(self.request, 'add_catch.html', {
                "notification": """
                                                <svg xmlns="http://www.w3.org/2000/svg" style="display: none;">
                                                  <symbol id="exclamation-triangle-fill" fill="currentColor" viewBox="0 0 16 16">
                                                    <path d="M8.982 1.566a1.13 1.13 0 0 0-1.96 0L.165 13.233c-.457.778.091 1.767.98 1.767h13.713c.889 0 1.438-.99.98-1.767L8.982 1.566zM8 5c.535 0 .954.462.9.995l-.35 3.507a.552.552 0 0 1-1.1 0L7.1 5.995A.905.905 0 0 1 8 5zm.002 6a1 1 0 1 1 0 2 1 1 0 0 1 0-2z"/>
                                                  </symbol>
                                                </svg>
                                                <div class="alert alert-dark d-flex alert-dismissible pl-5" role="alert" style="margin-right: 12%; margin-left: 5%; width: 45%;">
                                                     <svg class="bi flex-shrink-0 me-2" width="24" height="24" role="img" aria-label="Danger:"><use xlink:href="#exclamation-triangle-fill"/></svg>

                                                    <strong style="font-size: 16px; padding-left: 10%;"> Поставьте маркер на карте в месте, где поймали рыбу </strong>
                                                    <button type="button" class="btn-close" data-bs-dismiss="alert" style="padding-top: 4%;" aria-label="Close"></button>
                                                 </div>
                                             """})
        else:
            catch = form.save(commit=False)
            catch.save()

            catch.latitude = lat_and_lon_lst[0]
            catch.longitude = lat_and_lon_lst[1]

            whether = ManagerFromOpenWhether()
            data_tuple = whether.get_whether_today_by_coord(lat_and_lon_lst)

            catch.login = self.request.user

            catch.temperature = data_tuple[0]
            catch.pressure = data_tuple[1]
            catch.humidity = data_tuple[2]
            catch.wind_speed = data_tuple[3]
            catch.wind_vector = data_tuple[4]
            catch.cloudy = data_tuple[5]
            catch.name_of_the_area = data_tuple[6]
            catch.description_weather = data_tuple[7]

            # Очищение буфера обмена
            ctypes.windll.user32.OpenClipboard(0)
            ctypes.windll.user32.EmptyClipboard()
            ctypes.windll.user32.CloseClipboard()

            response = super().form_valid(form)

            return response

    def get_success_url(self):
        return reverse_lazy('catch')
