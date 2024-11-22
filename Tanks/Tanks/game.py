import pygame
from field import Field                   # Импортируем класс Field, который управляет игровым полем
from projectile import Projectile          # Импортируем класс Projectile, который представляет снаряды
from tank import Tank                     # Импортируем класс Tank, который отвечает за танки
from util import *                        # Импортируем вспомогательные методы и классы
from ui import *                          # Импортируем интерфейсные элементы
from explosion import Explosion            # Импортируем класс Explosion для обработки взрывов
from my_base import MyBase                # Импортируем класс MyBase, который представляет базу игрока
from bonus import Bonus, BonusType         # Импортируем классы для бонусов
from ai import EnemyFractionAI            # Импортируем класс ИИ для врагов
from bonus_field_protect import FieldProtector  # Импортируем класс для защиты поля бонусами
from score_node import ScoreLayer          # Импортируем класс для отображения счёта
import random                             # Импортируем модуль для работы с случайными числами


class Game:
    def __init__(self):
        self.r = random.Random()            # Создаем объект random для генерации случайных чисел

        self.scene = GameObject()           # Создаем объект сцены для управления дочерними объектами

        # Инициализация игрового поля
        self.field = Field()                 # Создаем игровое поле
        self.field.load_from_file('data/level1.txt')  # Загружаем уровень из файла
        self.scene.add_child(self.field)      # Добавляем поле в сцену

        self.field_protector = FieldProtector(self.field)  # Создаем защитника поля

        self.my_base = MyBase()              # Создаем базу игрока
        self.my_base.position = self.field.map.coord_by_col_and_row(12, 24)  # Устанавливаем позицию базы
        self.scene.add_child(self.my_base)    # Добавляем базу в сцену

        # Инициализация танков
        self.tanks = GameObject()             # Создаем объект для хранения танков
        self.scene.add_child(self.tanks)       # Добавляем танки в сцену

        self.make_my_tank()                   # Создаем танк игрока

        self.ai = EnemyFractionAI(self.field, self.tanks)  # Создаем ИИ для врагов

        # Инициализация снарядов
        self.projectiles = GameObject()       # Создаем объект для хранения снарядов
        self.scene.add_child(self.projectiles)  # Добавляем снаряды в сцену

        # Инициализация бонусов
        self.bonues = GameObject()            # Создаем объект для хранения бонусов
        self.scene.add_child(self.bonues)      # Добавляем бонусы в сцену

        self.score = 0                        # Инициируем счёт
        self.score_layer = ScoreLayer()        # Создаем объект для отображения счёта
        self.scene.add_child(self.score_layer) # Добавляем слой счёта в сцену

        self.freeze_timer = Timer(10)         # Создаем таймер заморозки на 10 секунд
        self.freeze_timer.done = True           # Устанавливаем таймер в состояние 'завершено'

        # Шрифт для отладки
        self.font_debug = pygame.font.Font(None, 18)

        # Для тестирования бонуса
        self.make_bonus(*self.field.map.coord_by_col_and_row(13, 22), BonusType.TOP_TANK)

    def respawn_tank(self, t: Tank):          # Функция для респауна танка
        is_friend = self.is_friend(t)          # Проверка, является ли танк другом
        pos = random.choice(self.field.respawn_points(not is_friend))  # Получение случайной точки для респауна
        t.place(self.field.get_center_of_cell(*pos))  # Установка расположения танка
        if is_friend:
            t.tank_type = t.Type.LEVEL_1       # Установка типа танка для друга

    def make_my_tank(self):                    # Функция для создания танка игрока
        self.my_tank = Tank(Tank.FRIEND, Tank.Color.YELLOW, Tank.Type.LEVEL_1)  # Создаем танк
        self.respawn_tank(self.my_tank)       # Респаун танка
        self.my_tank.activate_shield()         # Активация щита танка
        self.tanks.add_child(self.my_tank)     # Добавляем танк в список танков
        self.my_tank_move_to_direction = None  # Инициализируем направление движения танка

    @property
    def frozen_enemy_time(self):               # Свойство для проверки, заморожено ли время врагов
        return not self.freeze_timer.done      # Пробуем получить состояние таймера

    def _on_destroyed_tank(self, t: Tank):    # Вспомогательная функция, вызываемая при уничтожении танка
        if t.is_bonus:                         # Если танк - бонус
            self.make_bonus(*t.center_point)   # Создаем бонус на месте танка

        if t.fraction == t.ENEMY:              # Если танк - враг
            ds = 0                              # Инициализируем очки
            if t.tank_type == t.Type.ENEMY_SIMPLE:
                ds = 100                        # Простое враг
            elif t.tank_type == t.Type.ENEMY_FAST:
                ds = 200                        # Быстрое враг
            elif t.tank_type == t.Type.ENEMY_MIDDLE:
                ds = 300                        # Среднее враг
            elif t.tank_type == t.Type.ENEMY_HEAVY:
                ds = 400                        # Тяжёлое враг
            self.score += ds                    # Увеличиваем счёт
            self.score_layer.add(*t.center_point, ds)  # Обновляем визуализацию счёта

    def make_bonus(self, x, y, t=None):        # Функция для создания бонуса
        bonus = Bonus(BonusType.random() if t is None else t, x, y)  # Создание бонуса
        self.bonues.add_child(bonus)           # Добавляем бонус в группу бонусов

    def switch_my_tank(self):                   # Функция для переключения типа танка игрока
        tank = self.my_tank                    # Сохраняем текущий танк
        t, d, p = tank.tank_type, tank.direction, tank.position  # Сохраняем тип, направление и позицию
        tank.remove_from_parent()               # Убираем танк из родительского объекта

        # Получаем следующий тип танка
        types = list(Tank.Type)                 # Преобразуем перечисление типов танков в список
        current_index = types.index(t)         # Находим текущий индекс
        next_type = types[(current_index + 1) % len(types)]  # Получаем следующий тип
        tank = Tank(Tank.Color.PLAIN, next_type)  # Создаем новый танк
        tank.position = tank.old_position = p   # Устанавливаем позицию танка
        tank.direction = d                      # Устанавливаем направление
        tank.shielded = True                    # Активируем щит
        tank.activate_shield()                  # Активация щита
        self.tanks.add_child(tank)              # Добавляем танк обратно в группу
        self.my_tank = tank                      # Обновляем ссылку на танк игрока

    def make_explosion(self, x, y, expl_type):  # Функция для создания взрыва
        self.scene.add_child(Explosion(x, y, expl_type))  # Добавляем взрыв на сцену

    def is_friend(self, tank):                  # Функция для проверки, является ли танк другом
        return tank.fraction == tank.FRIEND    # Сравниваем фракции

    def fire(self, tank=None):                  # Функция для стрельбы
        tank = self.my_tank if tank is None else tank  # Используем танк игрока, если не указан другой
        tank.want_to_fire = False                # Сброс флага на стрельбу

        # Проверяем, завершилась ли игра и является ли танк другом
        if self.is_game_over and self.is_friend(tank):
            return                              # Если игра завершена, выходим

        if tank.try_fire():                     # Если танк может стрелять
            # Определяем мощность снаряда
            power = Projectile.POWER_HIGH if tank.tank_type.can_crash_concrete else Projectile.POWER_NORMAL
            projectile = Projectile(*tank.gun_point, tank.direction, sender=tank, power=power)  # Создаем снаряд
            self.projectiles.add_child(projectile)  # Добавляем снаряд в список снарядов

    def move_tank(self, direction: Direction, tank=None):  # Функция для движения танка
        tank = self.my_tank if tank is None else tank  # Используем танк игрока, если не указан другой
        tank.remember_position()                       # Сохраняем текущую позицию
        tank.move_tank(direction)                      # Двигаем танк в указанном направлении

    def apply_bonus(self, t: Tank, bonus: BonusType):  # Функция для применения бонуса к танку
        if bonus == bonus.DESTRUCTION:                 # Если бонус - разрушение
            for t in self.tanks:                       # Уничтожаем всех врагов
                if not t.is_spawning and t.fraction == Tank.ENEMY:
                    self.kill_tank(t)
        elif bonus == bonus.CASK:                      # Если бонус - бочка
            t.shielded = True                           # Даем танку щит
        elif bonus == bonus.UPGRADE:                   # Если бонус - улучшение
            t.upgrade()                                 # Улучшаем танк
        elif bonus == bonus.TIMER:                     # Если бонус - таймер заморозки
            self.freeze_timer.start()                   # Запускаем таймер
        elif bonus == bonus.STIFF_BASE:                # Если бонус - жесткая база
            self.field_protector.activate()            # Активируем защиту
        elif bonus == bonus.TOP_TANK:                  # Если бонус - верхний танк
            t.upgrade(maximum=True)                    # Улучшаем танк до максимума
        else:
            print(f'Bonus {bonus} not implemented yet.')  # Сообщение об отсутствующем бонусе

    def update_bonuses(self):                         # Функция для обновления бонусов
        for b in self.bonues:                        # Перебираем бонусы
            if b.intersects_rect(self.my_tank.bounding_rect):  # Если бонус пересекает танк игрока
                b.remove_from_parent()                # Удаляем бонус с родителя
                self.apply_bonus(self.my_tank, b.type)  # Применяем бонус к танку игрока

    @property
    def all_mature_tanks(self):                      # Свойство для получения всех зрелых танков
        return (t for t in self.tanks if not t.is_spawning)  # Возвращаем танки, которые не появляются

    @property
    def is_game_over(self):                          # Свойство, определяющее окончание игры
        return self.my_base.broken                   # Проверяем, разрушена ли база игрока

    def update_tanks(self):                          # Функция для обновления состояния танков
        for tank in self.all_mature_tanks:          # Перебираем все зрелые танки
            self.field.oc_map.fill_rect(tank.bounding_rect, tank, only_if_empty=True)  # Заполняем карту объектов

        if not self.is_game_over:                    # Если игра не завершена
            if self.my_tank_move_to_direction is None:  # Если направление движения не указано
                self.my_tank.stop()                    # Останавливаем танк
                self.my_tank.align()                   # Выравниваем танк
            else:
                self.move_tank(self.my_tank_move_to_direction, self.my_tank)  # Двигаем танк

        self.freeze_timer.tick()                       # Обновляем таймер
        if self.frozen_enemy_time:                     # Если время врагов заморожено
            self.ai.stop_all_moving()                  # Останавливаем всех врагов
        else:
            self.ai.update()                            # Обновляем действия врагов

        for tank in self.all_mature_tanks:           # Перебираем все зрелые танки
            if tank.want_to_fire:                     # Если танк хочет стрелять
                self.fire(tank)                       # Стреляет

            if tank.to_destroy:                       # Если танк нужно уничтожить
                tank.remove_from_parent()              # Убираем танк из родителя

            bb = tank.bounding_rect                    # Получаем прямоугольную границу танка
            if not self.field.oc_map.test_rect(bb, good_values=(None, tank)):  # Проверяем пересечение
                push_back = True                       # Если есть пересечение, действуем по правилам
            else:
                push_back = self.field.intersect_rect(bb)  # Проверяем пересечение с полем

            if push_back:
                tank.undo_move()                       # Возвращаем танк на прежнее место

    def is_player_tank(self, t: Tank):              # Проверка, является ли танк игрока
        return t is self.my_tank                      # Сравниваем с танком игрока

    def hit_tank(self, t: Tank):                    # Обработка попадания в танк
        destroy = False                              # Флаг уничтожения
        if self.is_friend(t):                        # Если танк - друг
            destroy = True                           # Уничтожаем и респауним
            self.respawn_tank(t)
        else:
            t.hit = True                              # Устанавливаем флаг попадания
            self.ai.update_one_tank(t)              # Обновляем ИИ для этого танка
            if t.to_destroy:                         # Если танк нужно уничтожить
                destroy = True                       # Устанавливаем флаг уничтожения
                t.remove_from_parent()               # Убираем танк из родительского объекта
                self._on_destroyed_tank(t)          # Вызываем обработку уничтоженного танка

        if destroy:
            self.make_explosion(*t.center_point, Explosion.TYPE_FULL)  # СоздаемExplosion при разрушении танка

    def kill_tank(self, t: Tank):                  # Уничтожение танка
        self.make_explosion(*t.center_point, Explosion.TYPE_FULL)  # Создаем взрыв на месте танка

        if self.is_friend(t):                       # Если танк - друг
            self.respawn_tank(t)                   # Респаун танка
        else:
            self.ai.update_one_tank(t)             # Обновляем ИИ для врага
            t.remove_from_parent()                   # Убираем танк из сцены

    def make_game_over(self):                       # Функция для обработки окончания игры
        self.my_base.broken = True                   # Разрушаем базу
        go = GameOverLabel()                         # Создаем объект окончания игры
        go.place_at_center(self.field)               # Устанавливаем его в центр поля
        self.scene.add_child(go)                     # Добавляем на сцену

    def update_projectiles(self):                   # Функция для обновления снарядов
        for p in self.projectiles:                   # Перебираем все снаряды
            r = extend_rect((*p.position, 0, 0), 2)  # Увеличиваем прямоугольник снаряда
            self.field.oc_map.fill_rect(r, p)       # Заполняем карту объектов

        remove_projectiles_waitlist = set()        # Создаем набор для удаления снарядов

        for p in self.projectiles:                   # Перебираем все снаряды
            p.update()                              # Обновляем состояние снаряда

            something = self.field.oc_map.get_cell_by_coords(*p.position)  # Получаем объект в клетке
            if something and something is not p and isinstance(something, Projectile):  # Если есть другой снаряд
                remove_projectiles_waitlist.add(p)  # Добавляем снаряд в список на удаление
                remove_projectiles_waitlist.add(something)  # И другой снаряд

            was_stricken_object = False
            x, y = p.position
            if self.field.check_hit(p):              # Проверяем попадание в стену или объект
                was_stricken_object = True
                self.make_explosion(*p.position, Explosion.TYPE_SUPER_SHORT)  # Создаем маленький взрыв
            elif self.my_base.check_hit(x, y):       # Проверяем попадание в базу
                self.make_game_over()                 # Обработка конца игры
                was_stricken_object = True
                self.make_explosion(*self.my_base.center_point, Explosion.TYPE_FULL)  # Взрыв на базе
            else:                                    # Проверяем попадание в танк
                for t in self.all_mature_tanks:      # Перебираем все зрелые танки
                    if t is not p.sender and t.check_hit(x, y):  # Если танк не является отправителем снаряда
                        was_stricken_object = True
                        if not t.shielded and p.sender.fraction != t.fraction:  # Если танк не защищен
                            self.make_explosion(*p.position, Explosion.TYPE_SHORT)  # Маленький взрыв
                            self.hit_tank(t)     # Обрабатываем попадание в танк
                        break

            if was_stricken_object:                  # Если произошло попадание
                remove_projectiles_waitlist.add(p)  # Добавляем снаряд в список на удаление

        for p in remove_projectiles_waitlist:      # Удаляем снаряды, которые были помечены
            p.remove_from_parent()

    def update(self):                              # Функция для обновления состояния игры
        self.field.oc_map.clear()                  # Очищаем карту объектов
        self.field.oc_map.fill_rect(self.my_base.bounding_rect, self.my_base)  # Обновляем состояние базы

        self.field_protector.update()              # Обновляем защитника поля
        self.score_layer.update()                   # Обновляем отображение счёта

        self.update_tanks()                        # Обновляем состояние танков
        self.update_bonuses()                      # Обновляем состояние бонусов
        self.update_projectiles()                  # Обновляем состояние снарядов

    # ---- render ----

    def render(self, screen):                     # Функция для отрисовки на экране
        self.scene.visit(screen)                   # Отрисовываем все объекты на сцене

        score_label = self.font_debug.render(str(self.score), 1, (255, 255, 255))  # Отображаем счёт
        screen.blit(score_label, (GAME_WIDTH - 50, 5))  # Помещаем счёт в верхний угол

        # - 1, потому что сцена не является буквально объектом
        dbg_text = f'Objects: {self.scene.total_children - 1}'  # Общее количество объектов в сцене
        if self.is_game_over:                       # Если игра закончена
            dbg_text = 'Press R to restart! ' + dbg_text  # Показать сообщение для перезапуска

        dbg_label = self.font_debug.render(dbg_text, 1, (255, 255, 255))  # Отображаем отладочную информацию
        screen.blit(dbg_label, (5, 5))             # Помещаем текст отладки в угол экрана

    # --- test ---

    def testus(self):                              # Тестовая функция для респауна танка
        self.respawn_tank(self.my_tank)           # Респаун танка игрока

