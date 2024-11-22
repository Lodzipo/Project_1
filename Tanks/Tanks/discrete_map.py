from math import floor                     # Импортируем функцию floor для округления вниз
from config import *                      # Импортируем конфигурацию (например, размер поля)
from util import DEMO_COLORS              # Импортируем цвета для отрисовки
import pygame                             # Импортируем библиотеку Pygame для графики


class DiscreteMap:
    def __init__(self, position, cell_size, cells_width=FIELD_WIDTH, cells_height=FIELD_HEIGHT, default_value=None):
        self.width = cells_width               # Ширина карты в ячейках
        self.height = cells_height             # Высота карты в ячейках
        self.position = position                # Позиция карты на экране
        self.default_value = default_value      # Значение по умолчанию для ячеек
        self.step = cell_size                  # Размер клетки
        self._cells = []                       # Список ячеек карты
        self.clear()                          # Очистка карты

    def clear(self):                          # Функция для очистки карты
        dv = self.default_value                # Значение по умолчанию
        self._cells = [[dv] * self.height for _ in range(self.width)]  # Создаем сетку с заданным значением

    def coord_by_col_and_row(self, col, row):
        xs, ys = self.position                  # Получаем позицию
        x = xs + col * self.step                # Вычисляем x координату
        y = ys + row * self.step                # Вычисляем y координату
        return x, y                             # Возвращаем координаты

    def col_row_from_coords(self, x, y):      # Функция для получения колонки и строки по координатам
        xs, ys = self.position                  # Получаем позицию
        col = floor((x - xs) / self.step)      # Рассчитываем колонку
        row = floor((y - ys) / self.step)      # Рассчитываем строку
        return col, row                         # Возвращаем колонку и строку

    def inside_col_row(self, col, row):        # Функция для проверки, находятся ли колонка и строка внутри границ карты
        return 0 <= col < self.width and 0 <= row < self.height  # Проверка на границы

    # адресация: self.cells[x or column][y or row]
    def get_cell_by_col_row(self, col, row):   # Получение ячейки по колонке и строке
        if self.inside_col_row(col, row):       # Если координаты внутри границей
            return self._cells[col][row]         # Возвращаем значение ячейки
        else:
            return None                           # Если вне границ, возвращаем None

    def get_cell_by_coords(self, x, y):         # Получение ячейки по координатам
        return self.get_cell_by_col_row(*self.col_row_from_coords(x, y))  # Используем вспомогательную функцию

    def set_cell_col_row(self, col, row, cell):  # Установка значения ячейки по колонке и строке
        if self.inside_col_row(col, row):        # Если координаты внутри границ
            self._cells[col][row] = cell          # Устанавливаем значение ячейки

    def set_cell_by_coord(self, x, y, cell):    # Установка значения ячейки по координатам
        self.set_cell_col_row(*self.col_row_from_coords(x, y), cell)  # Используем вспомогательную функцию

    def render(self, screen):                  # Функция для отрисовки карты
        step = self.step                       # Получаем размер ячейки
        for col in range(self.width):          # Перебираем колонки
            for row in range(self.height):     # И строки
                occupied = self.get_cell_by_col_row(col, row)  # Получаем значение ячейки
                if occupied is not None:        # Если ячейка занята
                    x, y = self.coord_by_col_and_row(col, row)  # Получаем координаты
                    color = DEMO_COLORS[id(occupied) % len(DEMO_COLORS)]  # Определяем цвет
                    pygame.draw.rect(screen, color, (x, y, step, step))  # Рисуем плитку


class OccupancyMap(DiscreteMap):             # Класс OccupancyMap, который наследует DiscreteMap
    def find_col_row_of_rect(self, r):        # Функция для поиска ячеек по прямоугольнику
        x, y, w, h = r                        # Получение координат и размеров прямоугольника
        assert w >= 0 and h >= 0              # Проверка на положительные размеры

        c1, r1 = self.col_row_from_coords(x, y)  # Получаем колонку и строку для верхнего левого угла
        c2, r2 = self.col_row_from_coords(x + w, y + h)  # Для нижнего правого угла
        min_c = min(c1, c2, self.width - 1)   # Минимальная колонка
        max_c = max(c1, c2, 0)                 # Максимальная колонка
        min_r = min(r1, r2, self.height - 1)   # Минимальная строка
        max_r = max(r1, r2, 0)                 # Максимальная строка

        for col in range(min_c, max_c + 1):    # Перебираем колонки
            for row in range(min_r, max_r + 1):  # И строки
                yield col, row                  # Генерируем колонки и строки в области

    def fill_rect(self, rect, v=1, only_if_empty=False):  # Заполнение прямоугольника значением
        for col, row in self.find_col_row_of_rect(rect):  # Получаем ячейки, попадающие в прямоугольник
            if not only_if_empty or self.get_cell_by_col_row(col, row) is None:  # Заполняем только если пусто
                self.set_cell_col_row(col, row, v)                # Устанавливаем значение ячейки

    def test_rect(self, rect, good_values=(0, 1)):           # Проверяем значения в прямоугольнике
        cells_to_test = self.find_col_row_of_rect(rect)       # Получаем ячейки для проверки
        return self.test_cells(cells_to_test, good_values)     # Проверяем все ячейки

    def test_cells(self, cols_rows, good_values=(0,)):        # Проверка значений в ячейках
        return all(self.get_cell_by_col_row(c, r) in good_values for c, r in cols_rows)  # Возвращаем True, если все значения подходят
