import math
import sys
from random import random

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QPainter, QBrush, QColor, QMouseEvent
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QSlider, QLabel, QHBoxLayout
from PyQt6.QtWidgets import QDialog, QFormLayout, QSpinBox


# Анимация поедания
# Редактировние стад

class CircleAnimation(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Sheeps Animation')
        self.setGeometry(25, 25, 900, 600)
        self.radius = 200  # радиус окружности
        self.center_x = (self.width() - 300) // 2
        self.center_y = self.height() // 2
        self.speed = 2  # скорость анимации
        self.pause = False

        self.cabbages = [Cabbage(self.radius, [self.center_x, self.center_y]) for _ in range(5)]
        self.sheeps = [Sheep(20, [self.center_x, self.center_y])]
        # Таймер для обновления игры
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.timer.start(16)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Основная область визуализации
        self.canvas = QWidget(self)
        self.canvas.setMinimumSize(600, 600)
        main_layout.addWidget(self.canvas)

        # Панель управления
        control_panel = QVBoxLayout()

        self.speed_slider = self.create_slider("Скорость овец", 1, 10, 5, control_panel)
        self.eat_speed_slider = self.create_slider("Скорость поедания", 1, 5, 2, control_panel)
        self.endurance_slider = self.create_slider("Выносливость", 100, 1000, 500, control_panel)
        self.reproduction_slider = self.create_slider("Плодовитость", 100, 2000, 1000, control_panel)

        add_sheep_btn = QPushButton("Добавить стадо", self)
        add_sheep_btn.clicked.connect(self.add_new_sheep)
        control_panel.addWidget(add_sheep_btn)

        main_layout.addLayout(control_panel)
        self.setLayout(main_layout)

    def create_slider(self, label_text, min_val, max_val, default_val, layout):
        label = QLabel(label_text, self)
        slider = QSlider(Qt.Orientation.Horizontal, self)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue(default_val)
        slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        slider.setTickInterval((max_val - min_val) // 5)

        layout.addWidget(label)
        layout.addWidget(slider)

        return slider

    def update_position(self):
        if not self.pause:
            self.update()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            x, y = event.position().x(), event.position().y()
            for sheep in self.sheeps:
                distance = math.sqrt((sheep.x - x) ** 2 + (sheep.y - y) ** 2)
                if distance <= sheep.size:  # Проверяем попадание клика в овцу
                    self.edit_sheep(sheep)
                    return
            self.cabbages.append(Cabbage(self.radius, [x, y], generate_coords=False))
            self.update()

    def add_cabbage(self):
        new_cabbage = Cabbage(self.radius, [self.center_x, self.center_y])

        # Проверка перекрытий с другими капустами
        while any(self.is_overlapping(new_cabbage, existing) for existing in self.cabbages):
            new_cabbage.generate_coords()  # Генерируем новые координаты, если есть перекрытие
        return new_cabbage

    def add_new_sheep(self):
        new_sheep = Sheep(20, [self.center_x, self.center_y])
        new_sheep.speed = self.speed_slider.value()
        new_sheep.eat_speed = self.eat_speed_slider.value()
        new_sheep.hungry = self.endurance_slider.value()
        new_sheep.reproduction_threshold = self.reproduction_slider.value()
        self.sheeps.append(new_sheep)

    def is_overlapping(self, cabbage1, cabbage2):
        distance = math.sqrt((cabbage1.x - cabbage2.x) ** 2 + (cabbage1.y - cabbage2.y) ** 2)
        # Проверка на пересечение с учетом радиусов капуст
        return distance < cabbage1.size + cabbage2.size

    def get_purpose_cabbage(self):
        min_distance = float('inf')
        nearest_cabbage = None

        for cabbage in self.cabbages:
            for sheep in self.sheeps:
                distance = math.sqrt((cabbage.x - sheep.x) ** 2 + (cabbage.y - sheep.y) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_cabbage = cabbage
        return nearest_cabbage

    def paintEvent(self, event, **kwargs):
        painter = QPainter(self)

        # Рисуем окружность
        painter.setBrush(QBrush(Qt.GlobalColor.white, Qt.BrushStyle.SolidPattern))
        painter.drawEllipse(self.center_x - self.radius, self.center_y - self.radius, self.radius * 2, self.radius * 2)
        self.purpose_cabbage = self.get_purpose_cabbage()
        for cabbage in self.cabbages:
            # Координаты капусты
            cabbage_x = cabbage.x
            cabbage_y = cabbage.y

            # Рисуем капусту
            painter.setBrush(QBrush(QColor(0, 255, 0), Qt.BrushStyle.SolidPattern))
            painter.drawEllipse(int(cabbage_x - 5), int(cabbage_y) - 5, int(cabbage.size), int(cabbage.size))

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
                    print("All sheep dead. Unlucky :(")
                    # sys.exit(app.exec())
            else:
                sheep_x = sheep.x
                sheep_y = sheep.y

                if id < len(distances) and distances[id] < 20:
                    sheep.hungry += sheep.eat_speed
                    self.purpose_cabbage.value -= sheep.eat_speed
                    if self.purpose_cabbage.value <= 0:
                        self.cabbages.remove(self.purpose_cabbage)
                        self.purpose_cabbage = self.add_cabbage()
                        self.cabbages.append(self.purpose_cabbage)
                else:
                    sheep.hungry -= 1  # Логика для уменьшения голода овец

                if sheep.hungry > sheep.reproduction_threshold:
                    if sheep.size > 40:
                        self.sheeps.append(Sheep(20, [sheep_x, sheep_y]))
                    else:
                        sheep.size += 10
                    sheep.hungry -= 300

                painter.setBrush(QBrush(QColor(0, 0, 0), Qt.BrushStyle.SolidPattern))
                painter.drawEllipse(int(sheep_x - 5), int(sheep_y - 5), sheep.size, sheep.size)

    def sheeps_going(self):
        distance_list = []
        for sheep in self.sheeps:
            dx = self.purpose_cabbage.x - sheep.x
            dy = self.purpose_cabbage.y - sheep.y

            distance = math.sqrt(dx ** 2 + dy ** 2)
            distance_list.append(distance)
            if distance > self.purpose_cabbage.size - 2:
                sheep.x += sheep.speed * (dx / distance)
                sheep.y += sheep.speed * (dy / distance)
        return distance_list

    def edit_sheep(self, sheep):

        dialog = QDialog(self)
        dialog.setWindowTitle("Редактирование овцы")
        layout = QFormLayout(dialog)

        speed_spin = QSpinBox(dialog)
        speed_spin.setValue(int(sheep.speed * 100))
        layout.addRow("Скорость", speed_spin)

        eat_speed_spin = QSpinBox(dialog)
        eat_speed_spin.setValue(int(sheep.eat_speed * 33))
        layout.addRow("Скорость поедания", eat_speed_spin)

        hungry_spin = QSpinBox(dialog)
        hungry_spin.setValue(int(sheep.hungry / 12))
        layout.addRow("Голод", hungry_spin)

        reproduction_spin = QSpinBox(dialog)
        reproduction_spin.setValue(int(sheep.reproduction_threshold / 24))
        layout.addRow("Плодовитость", reproduction_spin)

        ok_button = QPushButton("Применить", dialog)
        ok_button.clicked.connect(
            lambda: self.apply_sheep_settings(dialog, sheep, speed_spin, eat_speed_spin, hungry_spin,
                                              reproduction_spin))
        layout.addWidget(ok_button)
        dialog.setLayout(layout)
        dialog.exec()

    def apply_sheep_settings(self, dialog, sheep, speed_spin, eat_speed_spin, hungry_spin, reproduction_spin):
        sheep.speed = speed_spin.value() / 100  # mean value: 0.5
        sheep.eat_speed = eat_speed_spin.value() / 33  # mean value: 1.5
        sheep.hungry = hungry_spin.value() * 15  # mean value: 600
        sheep.size = int(hungry_spin.value() * 12 / 40)
        sheep.reproduction_threshold = reproduction_spin.value() * 24  # mean value: 1200
        dialog.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Up:
            self.cabbages.append(self.add_cabbage())
        if event.key() == Qt.Key.Key_Down:
            cords = [self.sheeps[-1].x, self.sheeps[-1].y]
            self.sheeps.append(Sheep(20, cords))
        if event.key() == Qt.Key.Key_P:
            self.pause = not self.pause


class Cabbage:
    def __init__(self, circle_radius, center, generate_coords=True):
        self.center = center
        self.circle_radius = circle_radius
        self.exist = False
        if generate_coords:
            self.generate_coords()
        else:
            self.x = center[0]
            self.y = center[1]
        self.value = int((random() + 0.1) * 400)
        self.size = 2 * math.log(self.value)
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
        self.size = int(self.hungry // 40)
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
