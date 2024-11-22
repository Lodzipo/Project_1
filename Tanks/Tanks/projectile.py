from util import *                           # Импортируем вспомогательные функции и классы
from config import *                         # Импортируем настройки игры
import pygame                                # Импортируем библиотеку Pygame


class Projectile(GameObject):                # Класс Projectile, наследующий от GameObject, представляет снаряд
    CENTRAL_SHIFT_X = -8                     # Смещение центра по оси X
    CENTRAL_SHIFT_Y = -15                    # Смещение центра по оси Y
    SPEED = 8                                 # Скорость снаряда

    SHIFT_BACK = -2                           # Смещение снаряда для отрисовки

    # Мощность снаряда
    POWER_NORMAL = 1                          # Нормальная мощность
    POWER_HIGH = 2                            # Высокая мощность

    def __init__(self, x, y, d: Direction, power=POWER_NORMAL, sender=None):
        super().__init__()                    # Вызываем конструктор родительского класса

        self.sender = sender                    # Хранит информацию об объекте, который выстрелил (танк)
        self.position = x, y                   # Устанавливаем начальные координаты снаряда
        self.direction = d                      # Устанавливаем направление снаряда
        self.power = power                      # Устанавливаем мощность снаряда

        # Словарь с изображениями для разных направлений
        self.sprite = {
            (0, -1): ATLAS().image_at(40, 12, 1, 2),  # вверх
            (-1, 0): ATLAS().image_at(41, 12, 1, 2),  # влево
            (0, 1): ATLAS().image_at(42, 12, 1, 2),   # вниз
            (1, 0): ATLAS().image_at(43, 12, 1, 2)    # вправо
        }[d.vector]                               # Выбираем изображение в зависимости от направления снаряда

    @property
    def on_screen(self):                        # Свойство, проверяющее, находится ли снаряд на экране
        x, y = self.position                    # Извлекаем текущее положение снаряда
        return 0 < x < GAME_WIDTH and 0 < y < GAME_HEIGHT  # Проверяем координаты на нахождение в пределах экрана

    @property
    def bounding_rect(self):                    # Свойство, возвращающее границы снаряда для коллизий
        x, y = self.position                    # Извлекаем текущее положение
        w, h = abs(self.CENTRAL_SHIFT_X), abs(self.CENTRAL_SHIFT_Y)  # Определяем ширину и высоту снаряда
        if self.direction in (Direction.UP, Direction.DOWN):
            w, h = h, w                         # Если снаряд направлен вверх или вниз, меняем ширину и высоту местами
        return x - w, y - h, w * 2, h * 2      # Возвращаем границы снаряда

    def render(self, screen: pygame.Surface):  # Метод для отрисовки снаряда на экране
        x, y = self.position                    # Извлекаем текущие координаты
        sbx, sby = self.direction.vector         # Получаем вектор направления снаряда
        sbx *= self.SHIFT_BACK                   # Применяем смещение по X
        sby *= self.SHIFT_BACK                   # Применяем смещение по Y
        screen.blit(self.sprite, (x + self.CENTRAL_SHIFT_X - sbx,
                                  y + self.CENTRAL_SHIFT_Y - sby))  # Отрисовываем снаряд

        if PROJECTILE_DEBUG:                     # Если включен режим отладки
            pygame.draw.circle(screen, (0, 200, 0), (x, y), 4)  # Рисуем окружность в текущей позиции снаряда для отладки

        if not self.on_screen:                   # Если снаряд вышел за пределы экрана
            self.remove_from_parent()            # Удаляем снаряд из родительского объекта

    def update(self):                           # Метод для обновления состояния снаряда
        vx, vy = self.direction.vector          # Получаем вектор направления снаряда
        self.move(vx * self.SPEED, vy * self.SPEED)  # Двигаем снаряд по направлению с заданной скоростью

    def split_for_aim(self):                    # Метод для разбивки снаряда на 3 виртуальных для равномерности разрушения
        """разбивает снаряд на 3 виртуальных для равномерности разрушения"""
        x, y = self.position                     # Извлекаем текущее положение
        distance = int(ATLAS().real_sprite_size / 1.4)  # Вычисляем расстояние для разбивки
        vx, vy = self.direction.vector           # Получаем направление движения
        px, py = (vy * distance), (-vx * distance)  # Вычисляем смещения по осям

        return (
            (x, y),                             # Основная координата снаряда
            (x + px, y + py),                  # Первая виртуальная точка
            (x - px, y - py)                   # Вторая виртуальная точка
        )

    def __hash__(self):                        # Переопределяем метод hash для использования в множествах и словарях
        return id(self)                        # Используем id объекта как уникальный хэш
