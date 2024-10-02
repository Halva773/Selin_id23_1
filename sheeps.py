import math
import sys
from random import random

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QBrush, QColor
from PyQt6.QtWidgets import QApplication, QWidget


class CircleAnimation(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sheeps Animation')
        self.setGeometry(100, 100, 600, 600)
        self.radius = 200  # радиус окружности
        self.center_x = self.width() // 2
        self.center_y = self.height() // 2
        self.speed = 2  # скорость анимации

        self.cabbage = Cabbage(self.radius, [self.center_x, self.center_y])

        self.sheeps = [Sheep(self.radius, [self.center_x, self.center_y])]

        # Таймер для обновления игры
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(16)  # обновление каждые 30 миллисекунд

    def update_position(self):
        if not self.cabbage.exist:
            self.cabbage.generate_coords()
            self.cabbage.exist = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Рисуем окружность
        painter.setBrush(QBrush(Qt.GlobalColor.white, Qt.BrushStyle.SolidPattern))
        painter.drawEllipse(self.center_x - self.radius, self.center_y - self.radius, self.radius * 2, self.radius * 2)

        # Координаты капусты
        cabbage_x = self.cabbage.x
        cabbage_y = self.cabbage.y

        # Рисуем капусту
        painter.setBrush(QBrush(QColor(0, 255, 0), Qt.BrushStyle.SolidPattern))
        self.size = 2 * math.log(self.cabbage.value)
        painter.drawEllipse(int(cabbage_x - 5), int(cabbage_y) - 5, int(self.size), int(self.size))

        # Вычисляем расстояния
        distances = self.sheeps_going()

        # Создаем копию списка овец, чтобы избежать ошибок индексации
        sheeps_copy = self.sheeps[:]

        for id, sheep in enumerate(sheeps_copy):
            if sheep.hungry <= 0:
                sheep.exist = False
                self.sheeps.remove(sheep)
                Sheep.SHEEP_COUNT -= 1
                if Sheep.SHEEP_COUNT == 0:
                    sys.exit(app.exec())
            else:
                sheep_x = sheep.x
                sheep_y = sheep.y

                if id < len(distances) and distances[id] < 20:
                    sheep.hungry += sheep.eat_speed
                    self.cabbage.value -= sheep.eat_speed
                    if self.cabbage.value <= 0:
                        self.cabbage.generate_coords()
                else:
                    sheep.hungry -= 1  # Логика для уменьшения голода овец

                if sheep.hungry > sheep.reproduction_threshold:
                    self.sheeps.append(Sheep(20, [sheep_x, sheep_y]))
                    sheep.hungry -= 100

                painter.setBrush(QBrush(QColor(0, 0, 0), Qt.BrushStyle.SolidPattern))
                painter.drawEllipse(int(sheep_x - 5), int(sheep_y - 5), 15, 15)

    def sheeps_going(self):
        distance_list = []
        for sheep in self.sheeps:
            dx = self.cabbage.x - sheep.x
            dy = self.cabbage.y - sheep.y

            distance = math.sqrt(dx ** 2 + dy ** 2)
            distance_list.append(distance)
            if distance > self.size - 2:
                sheep.x += sheep.speed * (dx / distance)
                sheep.y += sheep.speed * (dy / distance)
        return distance_list

    def keyPressEvent(self, event):
        # Управление скоростью анимации с помощью стрелок
        if event.key() == Qt.Key.Key_Up:
            self.cabbage.generate_coords()
        if event.key() == Qt.Key.Key_Down:
            cords = [self.sheeps[-1].x, self.sheeps[-1].y]
            self.sheeps.append(Sheep(20, cords))


class Cabbage:
    def __init__(self, circle_radius, center):
        self.center = center
        self.circle_radius = circle_radius
        self.exist = False
        self.generate_coords()
        self.value = int((random() + 0.1) * 400)
        # print(self.value)

    def generate_coords(self):
        range = random() * (self.circle_radius * 0.95)
        angle = random() * 360
        self.x = self.center[0] + range * math.cos(math.radians(angle))
        self.y = self.center[1] + range * math.sin(math.radians(angle))
        self.value = int((random() + 0.1) * 400)
        # print(self.value)


class Sheep:
    SHEEP_COUNT = 0

    def __init__(self, circle_radius, center):
        Sheep.SHEEP_COUNT += 1
        self.center = center
        self.circle_radius = circle_radius
        self.speed = random()  # Скорость передвижения
        self.hungry = (random() + 0.1) * 1000  # Голод
        self.reproduction_threshold = (random() + 0.1) * 2000  # Нужно еды для увеличения стада
        self.eat_speed = random() + 1  # Скорость поедания
        self.generate_coords()  # Генерируем координаты овцы
        print(
            f'Spawn: ({self.x}, {self.y});\nSpeed: {self.speed};\nHungry: {self.hungry};\nNeeds for reproduction: '
            f'{self.reproduction_threshold};\nEat speed: {self.eat_speed};\nTOTAL SHEEPS: {Sheep.SHEEP_COUNT}')

    def generate_coords(self):
        range = random() * (self.circle_radius * 0.95)
        angle = random() * 360
        self.x = self.center[0] + range * math.cos(math.radians(angle))
        self.y = self.center[1] + range * math.sin(math.radians(angle))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CircleAnimation()
    window.show()
    sys.exit(app.exec())
