from django.db import models
from django.utils import timezone


class Catch(models.Model):

    login = models.ForeignKey(
        'auth.user',
        null=True,
        on_delete=models.CASCADE
    )

    name_of_the_area = models.CharField(
        max_length=50,
        default="Не определено",
    )

    description_weather = models.CharField(
        max_length=200,
        default="Не определено",
    )

    date = models.DateField(
        default=timezone.now,
        help_text="Дата поимки в формате: ГГГГ-ММ-ДД",
        verbose_name="Дата поимки",
    )

    time = models.TimeField(
        null=True,
        blank=True,
        help_text="Введите время поимки(необязательное поле)",
        verbose_name="Время поимки")

    temperature = models.IntegerField(
        default=0,
        verbose_name="Температура"
    )

    pressure = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.0,
        verbose_name="Атмосферное давление"
    )

    humidity = models.IntegerField(
        default=0,
        verbose_name="Влажность"
    )

    wind_speed = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0,
        verbose_name="Скорость ветра"
    )

    wind_vector = models.CharField(
        max_length=10,
        default="Не определено",
        verbose_name="Направление ветра")

    cloudy = models.IntegerField(
        default=0,
        verbose_name="Облачность"
    )

    type_of_fish = models.CharField(
        max_length=50,
        verbose_name="Вид пойманной рыбы")

    fish_weight = models.DecimalField(
        default=50,
        max_digits=15,
        decimal_places=3,
        verbose_name="Вес рыбы в граммах"
    )

    description = models.CharField(
        max_length=1000,
        blank=True,
        help_text="Можете описать особенности поимки рыбы или в целом про рыбалку(необязательное поле)",
        verbose_name="Краткое описание"
    )

    bait = models.CharField(
        max_length=100,
        blank=True,
        help_text="Название приманки(необязательное поле)",
        verbose_name="Приманка"
    )

    image = models.ImageField(
        null=True,
        blank=True,
        upload_to='images/catch',
        verbose_name='Вы можете добавить фотографию'
    )

    latitude = models.DecimalField(
        max_digits=8,
        decimal_places=5,
        default=0.0,
        verbose_name="Координата широты"
    )

    longitude = models.DecimalField(
        max_digits=8,
        decimal_places=5,
        default=0.0,
        verbose_name="Координата долготы"
    )

    def __str__(self):
        return f"{self.login}, {self.name_of_the_area},{self.date}, {self.time}, {self.description_weather}, {self.temperature}," \
               f"{self.pressure}, {self.humidity}, {self.wind_speed}, {self.wind_vector}, {self.cloudy}," \
               f"{self.type_of_fish}, {self.fish_weight}, {self.bait}, {self.image}, {self.latitude}, {self.longitude}"
