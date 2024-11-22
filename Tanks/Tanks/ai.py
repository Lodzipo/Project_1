from tank import Tank, Direction  # Импортируем классы для танков и направления
from field import Field  # Импортируем класс поля игры
from util import ArmedTimer, GameObject  # Импортируем классы для работы с таймерами и игровыми объектами
import random  # Импортируем модуль для генерации случайных чисел
from itertools import cycle  # Импортируем цикл для итерации по элементам


class TankAI:
    SPAWNING_DELAY = 1.5  # Задержка спавна танка
    FIRE_TIMER = 1.0  # Таймер для стрельбы

    @staticmethod
    def dir_delay():  # Метод для получения случайной задержки направления
        return random.uniform(0.3, 3.0)  # Возвращаем случайное значение в диапазоне

    def pick_direction(self):  # Метод для выбора направления движения танка
        c, r = self.field.map.col_row_from_coords(*self.tank.position)  # Получаем текущие координаты танка
        prohibited_dir = set()  # Множество для запрещенных направлений

        # Запрещаем направление в зависимости от положения танка
        if c <= 1:
            prohibited_dir.add(Direction.LEFT)  # Запрещаем движение налево
        if r <= 1:
            prohibited_dir.add(Direction.UP)  # Запрещаем движение вверх
        if c >= self.field.map.width - 2:
            prohibited_dir.add(Direction.RIGHT)  # Запрещаем движение направо
        if r >= self.field.map.height - 2:
            prohibited_dir.add(Direction.DOWN)  # Запрещаем движение вниз

        return random.choice(list(Direction.all() - prohibited_dir))  # Возвращаем случайное направление

    def __init__(self, tank: Tank, field: Field):  # Конструктор класса
        self.tank = tank  # Сохраняем танк
        self.field = field  # Сохраняем поле

        self.fire_timer = ArmedTimer(delay=self.FIRE_TIMER)  # Инициализируем таймер для стрельбы
        self.dir_timer = ArmedTimer(delay=self.dir_delay())  # Инициализируем таймер для изменения направления
        self.spawn_timer = ArmedTimer(delay=self.SPAWNING_DELAY)  # Инициализируем таймер спавна

    def _destroy(self):  # Метод для уничтожения танка
        self.tank.to_destroy = True  # Устанавливаем флаг на уничтожение

    def _degrade(self):  # Метод для деградации танка
        if self.tank.color == Tank.Color.PLAIN:  # Если танк обычный
            self.tank.color = Tank.Color.GREEN  # Меняем цвет на зелёный
        else:  # Если цвет не обычный, уничтожаем танк
            self._destroy()

    def update(self):  # Метод для обновления состояния танка
        if self.tank.is_spawning:  # Если танк находится в процессе спавна
            if self.spawn_timer.tick():  # Проверяем таймер спавна
                if self.field.oc_map.test_rect(self.tank.bounding_rect,
                                               good_values=(None, self.tank)):  # Проверка на свободное место
                    self.tank.is_spawning = False  # Если место свободно, завершаем спавн
                else:
                    return  # Если нет - выходим
            else:
                return  # Если таймер спавна ещё не завершился, просто выходим

        if self.tank.hit:  # Если танк был подбит
            if self.tank.tank_type == Tank.Type.ENEMY_HEAVY:  # Если это тяжёлый танк
                self._degrade()  # Деградируем танк
            else:
                self._destroy()  # Иначе уничтожаем танк
            self.tank.hit = False  # Сбрасываем флаг попадания

        if self.fire_timer.tick():  # Если таймер стрельбы сработал
            self.tank.fire()  # Даём разрешение на стрельбу
            self.fire_timer.start()  # Запускаем таймер снова

        if self.dir_timer.tick():  # Если таймер направления сработал
            self.tank.direction = self.pick_direction()  # Поворачиваем танк в новую случайную сторону
            self.dir_timer.delay = self.dir_delay()  # Устанавливаем новую задержку
            self.dir_timer.start()  # Запускаем таймер

        self.tank.move_tank(self.tank.direction)  # Двигаем танк в выбранном направлении

    def reset(self):  # Метод для сброса танка
        self.tank.direction = Direction.random()  # Случайным образом устанавливаем новое направление танка


class EnemyFractionAI:
    MAX_ENEMIES = 5  # Максимум врагов на поле

    RESPAWN_TIMER = 5.0  # Таймер для спавна врагов

    def __init__(self, field: Field, tanks: GameObject):  # Конструктор класса
        self.tanks = tanks  # Сохраняем объект танков
        self.field = field  # Сохраняем поле
        self.spawn_points = {  # Инициализируем точки спавна
            (x, y): None for x, y in field.respawn_points(True)
        }
        self.spawn_timer = ArmedTimer(self.RESPAWN_TIMER)  # Инициализируем таймер спавна врагов

        self.enemy_queue = cycle([  # Циклическая очередь типов танков
            Tank.Type.ENEMY_SIMPLE,
            Tank.Type.ENEMY_FAST,
            Tank.Type.ENEMY_MIDDLE,
            Tank.Type.ENEMY_HEAVY,
        ])
        self._enemy_queue_iter = iter(self.enemy_queue)  # Создаём итератор для очереди

        self.try_to_spawn_tank()  # Пробуем заспавнить танк

    @property
    def all_enemies(self):  # Свойство для получения всех врагов
        return [t for t in self.tanks if t.fraction == Tank.ENEMY]  # Фильтруем танки по фракции

    def get_next_enemy(self, pos):  # Метод для получения следующего врага
        t_type = next(self._enemy_queue_iter)  # Получаем следующий тип танка из очереди
        new_tank = Tank(Tank.ENEMY, Tank.Color.PLAIN, t_type)  # Создаем нового врага
        new_tank.is_spawning = True  # Устанавливаем флаг спавна

        new_tank.ai = TankAI(new_tank, self.field)  # Присоединяем ИИ к новому танку

        if random.uniform(0, 1) > 0.35:  # 35% шанс того, что танк будет бонусом
            new_tank.is_bonus = True

        new_tank.place(self.field.get_center_of_cell(*pos))  # Устанавливаем танк в центр клетки
        return new_tank  # Возвращаем новый танк

    def try_to_spawn_tank(self):  # Метод для попытки спавна танка
        free_locations = list()  # Список для хранения свободных точек
        for loc, tank in self.spawn_points.items():  # Перебираем точки спавна
            if isinstance(tank, Tank):  # Если на месте есть танк
                if not tank.is_spawning:  # И он не спавнится
                    self.spawn_points[loc] = None  # Освобождаем точку
            else:
                free_locations.append(loc)  # Если точка свободна, добавляем её в список

        # Если есть свободные места и количество врагов меньше максимума
        if free_locations and len(self.all_enemies) < self.MAX_ENEMIES:
            pos = random.choice(free_locations)  # Выбираем случайное свободное место
            tank = self.get_next_enemy(pos)  # Получаем нового врага
            self.spawn_points[pos] = tank  # Запоминаем танк на месте
            self.tanks.add_child(tank)  # Добавляем танк в объект танков

    def stop_all_moving(self):  # Метод для остановки всех врагов
        for t in self.all_enemies:  # Перебираем всех врагов
            t.stop()  # Останавливаем каждого танка

    def update(self):  # Метод для обновления состояния врагов
        if self.spawn_timer.tick():  # Если таймер спавна сработал
            self.spawn_timer.start()  # Перезапускаем таймер
            self.try_to_spawn_tank()  # Пробуем заспавнить новый танк

        for enemy_tank in self.all_enemies:  # Перебираем всех врагов
            self.update_one_tank(enemy_tank)  # Обновляем состояние каждого танка

    def update_one_tank(self, t: Tank):  # Метод для обновления состояния одного танка
        t.to_destroy = False  # Сбрасываем флаг уничтожения
        t.ai.update()  # Обновляем логику ИИ танка
