import pygame
import numpy as np
import random

# Размеры экрана и размер ячейки
WIDTH, HEIGHT = 1600, 600
CELL_SIZE = 10  # Размер клетки сетки

running = True

# Инициализация Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Переменные для времени
time_passed = 0  # Время в секундах
day_duration = 5  # Длительность дня в секундах
days = 0  # Количество прошедших дней
time_speed = 1.0  # Начальная скорость времени (1.0 - обычная скорость)


class Leaf:
    def __init__(self, x, y):
        # Привязываем координаты к сетке
        self.x = x // CELL_SIZE * CELL_SIZE
        self.y = y // CELL_SIZE * CELL_SIZE
        self.energy = 10  # Энергия, которую можно получить, съев листок

    def draw(self):
        pygame.draw.circle(screen, (0, 255, 0), (int(self.x), int(self.y)), 5)  # Зеленый цвет

class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        # Инициализация весов случайными значениями
        self.weights_input_hidden = np.random.rand(input_size, hidden_size)
        self.weights_hidden_output = np.random.rand(hidden_size, output_size)

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def predict(self, inputs):
        hidden_layer_input = np.dot(inputs, self.weights_input_hidden)
        hidden_layer_output = self.sigmoid(hidden_layer_input)
        output_layer_input = np.dot(hidden_layer_output, self.weights_hidden_output)
        output = self.sigmoid(output_layer_input)
        return output


class Bot:
    def __init__(self, x, y):
        # Привязываем координаты к сетке
        self.x = x // CELL_SIZE * CELL_SIZE
        self.y = y // CELL_SIZE * CELL_SIZE
        self.energy = 100
        self.speed = random.uniform(1, 5)  # Случайная скорость от 1 до 5
        self.nn = NeuralNetwork(input_size=4, hidden_size=30, output_size=4)  # 4 входа, 30 скрытых нейронов, 4 выхода (действия)
        self.eating_type = random.randint(0, 2)  # Случайный тип питания (0, 1 или 2)
        self.age = 0  # Начальный возраст бота
        self.max_age = random.randint(500, 2000)  # Максимальный срок жизни бота
        self.color = (255, 0, 0)  # Начальный цвет (красный)

    def mutate(self):
        # С вероятностью 10% изменяем тип питания
        if random.random() < 0.1:  # 10% вероятность мутации
            self.eating_type = random.randint(0, 2)

    def update(self, bots, leaves):
        self.age += 1  # Увеличиваем возраст бота
        if self.age > self.max_age:
            return bots.remove(self)  # Удаляем бота, если он старше максимального возраста

        inputs = np.array([self.x, self.y, self.energy, self.get_energy_preference()])  # Добавляем предпочтение

        # Предсказание действий
        actions = self.nn.predict(inputs)
        # Получаем индекс действия с максимальным значением
        action_index = np.argmax(actions)

        # Добавим логику, чтобы боты двигались, если их энергия слишком низкая
        if self.energy < 20:  # Если энергия слишком низкая
            action_index = 1  # Устанавливаем действие "движение"

        if action_index == 0:  # Фотосинтез
            self.photosynthesis()
        elif action_index == 1:  # Движение
            self.move(bots)
        elif action_index == 2:  # Атака
            self.attack(bots)
        elif action_index == 3:  # Деление
            return self.divide()

        # Логика для поедания листочков
        if self.eating_type == 0 or self.eating_type == 2:  # Если бот может есть листья
            self.eat_leaves(leaves)

        self.energy -= 0.05  # Затраты энергии на жизнь

        return None

    def photosynthesis(self):
        self.energy += 0.5  # Увеличиваем энергию от фотосинтеза

    def get_energy_preference(self):
        preference = 0
        # Предпочтение для листьев
        if self.energy < 100:  # Предпочитать листья, если энергия меньше 100
            preference = 0
        # Предпочтение для фотосинтеза
        elif self.energy < 20:  # Фотосинтез предпочтительнее, если энергия очень низкая
            preference = 1

        return preference


    def eat_leaves(self, leaves):
        for leaf in leaves:
            if self.is_near(leaf):
                self.energy += leaf.energy  # Восстанавливаем энергию
                leaves.remove(leaf)  # Удаляем съеденный листок
                break  # Можно съесть только один листок за раз

    def move(self, bots):
        direction = random.choice(['up', 'down', 'left', 'right'])

        if direction == 'up':
            new_y = self.y - CELL_SIZE  # Перемещение на одну клетку вверх
            if new_y >= 0:  # Проверка границ экрана
                self.y = new_y
        elif direction == 'down':
            new_y = self.y + CELL_SIZE  # Перемещение на одну клетку вниз
            if new_y < HEIGHT:  # Проверка границ экрана
                self.y = new_y
        elif direction == 'left':
            new_x = self.x - CELL_SIZE  # Перемещение на одну клетку влево
            if new_x >= 0:  # Проверка границ экрана
                self.x = new_x
        elif direction == 'right':
            new_x = self.x + CELL_SIZE  # Перемещение на одну клетку вправо
            if new_x < WIDTH:  # Проверка границ экрана
                self.x = new_x

        # Округляем координаты до ближайшей клетки
        self.x = round(self.x / CELL_SIZE) * CELL_SIZE
        self.y = round(self.y / CELL_SIZE) * CELL_SIZE

    def attack(self, bots):
        for bot in bots:
            if bot != self and self.is_near(bot):
                damage = 50  # Урон, который бот наносит другому
                bot.energy -= damage
                if bot.energy <= 0:
                    return bots.remove(bot)  # Удаляем бот из мира

    def is_near(self, other_bot):
        distance = np.sqrt((self.x - other_bot.x) ** 2 + (self.y - other_bot.y) ** 2)
        return distance < 30  # Расстояние для атаки

    def divide(self):
        if self.energy >= 50:  # Условие для деления (достаточно энергии)
            # Создаем нового бота с мутацией
            new_bot = Bot(self.x, self.y)
            new_bot.mutate()  # Возможная мутация
            new_bot.color = (
            random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))  # Новый случайный цвет
            self.energy -= 50  # Уменьшаем энергию бота
            return new_bot
        return None  # Если недостаточно энергии, возвращаем None

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 5)


# Функция для отрисовки мира
def draw_world():
    screen.fill((0, 192, 192))  # Устанавливаем серый цвет фона

    # Рисуем сетку
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, (0, 0, 0), (x, 0), (x, HEIGHT))  # Вертикальные линии
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, (0, 0, 0), (0, y), (WIDTH, y))  # Горизонтальные линии

# Генерация случайных листочков
def generate_leaves(num_leaves):
    leaves = []
    for _ in range(num_leaves):
        x = random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE
        y = random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE
        leaves.append(Leaf(x, y))
    return leaves

# функция для обновления заголовка окна
def update_window_title():
    pygame.display.set_caption(f'Day: {days}')  # Обновляем заголовок окна


def reset_simulation():
    global bots, leaves, days, time_passed

    bots = [Bot(random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
                random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE) for _ in range(100)]

    leaves = generate_leaves(10)  # Генерируем начальные листочки
    days = 0  # Сбрасываем количество дней
    time_passed = 0  # Сбрасываем время


# Основной цикл симуляции
bots = [Bot(random.randint(0, (WIDTH // CELL_SIZE) - 1) * CELL_SIZE,
            random.randint(0, (HEIGHT // CELL_SIZE) - 1) * CELL_SIZE) for _ in range(300)]

leaves = generate_leaves(30)  # Генерируем 10 листочков

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Обновляем время
    time_passed += clock.get_time() / 1000.0  # Получаем время в секундах
    if time_passed >= day_duration:
        days += 1  # Увеличиваем количество дней
        leaves.extend(generate_leaves(50))  # Генерируем 50 новых листочков
        time_passed = 0  # Сбрасываем время

    draw_world()

    # Удаляем мертвых ботов перед обновлением
    bots = [bot for bot in bots if bot.age <= bot.max_age]

    new_bots = []  # Список для новых ботов
    # Обновляем и рисуем ботов, передавая список ботов
    for bot in bots[:]:
        new_bot = bot.update(bots, leaves)  # Обновляем ботов
        if new_bot:  # Если новый бот создан
            new_bots.append(new_bot)  # Добавляем нового бота в список
            bots.remove(bot)  # Удаляем старого бота, если он разделился
        else:
            bot.draw()  # Отрисовка ботов
    # Добавляем новых ботов в общий список
    bots.extend(new_bots)

    # Рисуем листья
    for leaf in leaves:
        leaf.draw()

    update_window_title()  # Обновляем заголовок окна

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

