from config import *                        # Импортируем конфигурацию (например, настройки игры)
from util import *                          # Импортируем вспомогательные функции и классы


class Explosion(GameObject):                 # Класс Explosion, наследующий от GameObject
    # Определяем параметры спрайтов для различных состояний взрыва
    SPRITE_DESCRIPTORS = (
        (32, 16, 2, 2),                      # Параметры для первого спрайта (x, y, width, height)
        (34, 16, 2, 2),                      # Параметры для второго спрайта
        (36, 16, 2, 2),                      # И так далее...
        (38, 16, 4, 4),
        (42, 16, 4, 4)
    )

    # Определяем типы взрывов
    TYPE_SUPER_SHORT = 'super_short'        # Тип супер-краткого взрыва
    TYPE_SHORT = 'short'                    # Тип краткого взрыва
    TYPE_FULL = 'full'                      # Полный тип взрыва

    # Определяем количество состояний для каждого типа взрыва
    _n_states = {
        TYPE_FULL: len(SPRITE_DESCRIPTORS),  # Полный взрыв имеет длину, равную количеству дескрипторов спрайтов
        TYPE_SHORT: 3,                       # Краткий взрыв имеет 3 состояния
        TYPE_SUPER_SHORT: 2                   # Супер-краткий взрыв имеет 2 состояния
    }

    def __init__(self, x, y, type=TYPE_FULL):  # Конструктор класса, принимает координаты и тип взрыва
        super().__init__()                     # Вызываем конструктор родительского класса

        self.position = x, y                   # Устанавливаем позицию взрыва
        n = self._n_states[type]               # Получаем количество состояний для данного типа
        self.animator = Animator(0.08, n, once=True)  # Создаем аниматор, который будет управлять состояниями взрыва
        # Загружаем спрайты для различных состояний взрыва из атласа
        self.sprites = [ATLAS().image_at(x, y, sx, sy) for
                        x, y, sx, sy in self.SPRITE_DESCRIPTORS]

    def render(self, screen):                 # Функция для отрисовки взрыва на экране
        state = self.animator()                # Получаем текущее состояние анимации

        if self.animator.done:                 # Проверяем, закончилась ли анимация
            self.remove_from_parent()          # Если да, то удаляем объект взрыва из родительского объекта
        else:
            # Получаем параметры текущего спрайта
            _, _, w, h = self.SPRITE_DESCRIPTORS[state]
            half_sprite_size = ATLAS().real_sprite_size // 2  # Вычисляем половину размера спрайта
            # Преобразовываем ширину и высоту спрайта в пикселях
            w_pix = w * half_sprite_size
            h_pix = h * half_sprite_size
            x, y = self.position                  # Получаем текущие координаты взрыва
            x -= w_pix                           # Центруем спрайт по x
            y -= h_pix                           # Центруем спрайт по y
            sprite = self.sprites[state]        # Получаем текущий спрайт по состоянию
            screen.blit(sprite, (x, y))         # Рисуем спрайт на экране в указанных координатах
