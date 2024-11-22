import random  # Импортируем библиотеку для генерации случайных чисел
from enum import Enum  # Импортируем класс Enum для создания перечислений

from pygame import Surface  # Импортируем класс Surface из Pygame для работы с изображениями

from config import ATLAS  # Импортируем конфигурацию ATLAS для доступа к спрайтам
from util import GameObject  # Импортируем класс GameObject для создания игровых объектов


class BonusType(Enum):  # Определяем класс перечисления для типов бонусов
    # value is sprite sheet location
    CASK = (32, 14)  # Бонус "Бочка"
    TIMER = (34, 14)  # Бонус "Таймер"
    STIFF_BASE = (36, 14)  # Бонус "Жесткая база"
    UPGRADE = (38, 14)  # Бонус "Улучшение"
    DESTRUCTION = (40, 14)  # Бонус "Разрушение"
    TOP_TANK = (42, 14)  # Бонус "Верхний танк"
    GUN = (44, 14)  # Бонус "Оружие"

    @classmethod
    def random(cls):  # Класс-метод для получения случайного типа бонуса
        return random.choice(list(cls))  # Возвращаем случайно выбранный элемент из перечисления


class Bonus(GameObject):  # Определяем класс для бонусов, наследующий от GameObject
    def __init__(self, bonus_type: BonusType, x, y):
        super().__init__()  # Вызываем конструктор родительского класса
        self.type = bonus_type  # Сохраняем тип бонуса

        # Загружаем изображение бонуса из спрайт-листа, используя его координаты
        self.sprite = ATLAS().image_at(*bonus_type.value, 2, 2)

        sz = ATLAS().real_sprite_size  # Получаем реальный размер спрайта
        self.position = x - sz, y - sz  # Устанавливаем позицию бонуса, центрируя его

        self.size = (sz * 2, sz * 2)  # Устанавливаем размер бонуса в два раза больше реального размера спрайта

    def render(self, screen: Surface):  # Метод для отрисовки бонуса на экране
        screen.blit(self.sprite, self.position)  # Отрисовываем спрайт бонуса в его позиции
