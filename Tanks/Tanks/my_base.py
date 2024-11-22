from config import ATLAS                    # Импортируем атлас для работы со спрайтами
from util import GameObject, point_in_rect   # Импортируем класс GameObject и функцию для проверки попадания в прямоугольник


class MyBase(GameObject):                    # Класс MyBase, наследующий от GameObject, представляет базу игрока
    def __init__(self):
        super().__init__()                    # Вызываем конструктор родительского класса
        self._normal_img = ATLAS().image_at(38, 4, 2, 2)  # Загружаем изображение нормальной базы
        self._broken_img = ATLAS().image_at(40, 4, 2, 2)   # Загружаем изображение разрушенной базы
        self.broken = False                    # Инициализируем состояние базы (разрушена/нет)
        size = ATLAS().real_sprite_size * 2 - 1  # Вычисляем размер базы
        self.size = (size, size)              # Устанавливаем размер базы

    def render(self, screen):                  # Метод для отрисовки базы на экране
        img = self._broken_img if self.broken else self._normal_img  # Выбираем изображение в зависимости от состояния базы
        screen.blit(img, self.position)        # Отрисовываем изображение базы в текущей позиции

    @property
    def center_point(self):                    # Свойство для получения центра базы
        x, y = self.position                    # Извлекаем текущие координаты позиции
        w, h = self.size                        # Извлекаем размер базы
        return x + w // 2, y + h // 2          # Возвращаем координаты центра базы

    def check_hit(self, x, y):                 # Метод для проверки попадания в базу по координатам
        return point_in_rect(x, y, self.bounding_rect)  # Проверяем, находится ли точка внутри границ базы
