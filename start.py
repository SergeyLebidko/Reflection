import math
import random
import pygame as pg

# -------------------- Параметры работы программы --------------------

H, W = 800, 1200
WINDOW_TITLE = 'Reflection'
FPS = 60
SPARKLE_COUNT = 50
BACKGROUND_COLOR = (50, 50, 50)
SPARKLE_COLOR = (200, 200, 200)
BOX_BORDER_COLOR = (220, 220, 220)
BOX_BACKGROUND_COLOR = (120, 120, 120)

# Коэффициент для перевода градусов в радианы
K_RADIAN = math.pi / 180

# Словарь для хранения всех отрезков
ALL_SEGMENTS = {}

# Словарь для хренения всех фигур
ALL_BOXES = []

# Список для хранения всех светлячков
ALL_SPARKLE_ITERATORS = []


# -------------------- Функции отрисовки --------------------


def draw_background(sc):
    sc.fill(BACKGROUND_COLOR)


def draw_sparkle(sc, sparkle_iterators):
    for sparkle_iterator in sparkle_iterators:
        x, y = next(sparkle_iterator)
        pg.draw.rect(sc, SPARKLE_COLOR, (int(x - 1), int(y - 1), 3, 3))


def draw_boxes(sc, boxes, font):
    for box in boxes:
        x = min(box.dots, key=lambda val: val[0])[0]
        y = min(box.dots, key=lambda val: val[1])[1]
        center_x, center_y = x + box.width // 2, y + box.height // 2
        pg.draw.rect(sc, BOX_BACKGROUND_COLOR, (x, y, box.width, box.height))
        pg.draw.rect(sc, BOX_BORDER_COLOR, (x, y, box.width, box.height), 1)

        text = font.render(str(box.collision_count), 0, (0, 0, 0))
        sc.blit(text, (center_x - text.get_rect().width // 2, center_y - text.get_rect().height // 2))


# -------------------- Вспомогательные функции --------------------

def create_borders_segment():
    """Функция создает отрезки - границы окна"""
    segments_data = [
        ((0, 0), (0, H)),
        ((0, H), (W, H)),
        ((W, H), (W, 0)),
        ((W, 0), (0, 0))
    ]
    for dot1, dot2 in segments_data:
        ALL_SEGMENTS[Segment(dot1, dot2)] = None


def create_sparkle_iterators():
    """Функция создает итераторы всех светлячков"""
    for _ in range(SPARKLE_COUNT):
        sparkle = Sparkle((W // 2, H // 2))
        ALL_SPARKLE_ITERATORS.append(iter(sparkle))


def create_boxes():
    """Функция создает фигуры"""
    preset = [(100, 100), (300, 100), (300, 300), (100, 300)]
    for y0 in range(0, H, 400):
        for x0 in range(0, W, 400):
            dots = [(x0 + dx, y0 + dy) for dx, dy in preset]
            figure = Box(dots)
            ALL_BOXES.append(figure)
            for segment in figure.segments:
                ALL_SEGMENTS[segment] = figure


def get_distance(dot1, dot2):
    """Функция возвращает расстояние между двумя точками"""
    x1, y1 = dot1
    x2, y2 = dot2
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def get_intersection(segment1, segment2):
    """Функция возвращает точку пересечения двух отрезков или None, если отрезки не пересекаются"""
    a1, b1, c1 = segment1.a, segment1.b, segment1.c
    a2, b2, c2 = segment2.a, segment2.b, segment2.c
    if (a1 * b2) == (a2 * b1):
        return None
    x = - (c1 * b2 - c2 * b1) / (a1 * b2 - a2 * b1)
    y = - (a1 * c2 - a2 * c1) / (a1 * b2 - a2 * b1)
    distance1 = get_distance((x, y), segment1.center)
    distance2 = get_distance((x, y), segment2.center)
    if (distance1 > (segment1.length / 2)) or (distance2 > (segment2.length / 2)):
        return None
    return x, y


def get_scalar_mul(vector1, vector2):
    """Функция возвращает скалярное произведение векторов"""
    return vector1[0] * vector2[0] + vector1[1] * vector2[1]


def get_vector_sum(vector1, vector2):
    """Функция возвращает сумму двух векторов"""
    return vector1[0] + vector2[0], vector1[1] + vector2[1]


def get_vector_value_mul(vector, value):
    """Функция возвращает произведение вектора на число"""
    return vector[0] * value, vector[1] * value


def get_reflect_vector(vector, segment):
    """Функция возвращает отраженный вектор"""
    normal = segment.a, segment.b
    result = get_vector_sum(
        vector,
        get_vector_value_mul(normal, -2 * get_scalar_mul(vector, normal) / get_scalar_mul(normal, normal))
    )
    return result


# -------------------- Основные классы --------------------


class Sparkle:
    STEP = 5

    def __init__(self, dot):
        self.dot = dot
        angle = K_RADIAN * random.randint(0, 359)
        self.vector = self.STEP * math.cos(angle), self.STEP * math.sin(angle)
        self.last_reflect_segment = None

    def __iter__(self):
        while True:
            yield self.dot
            next_dot = self.dot[0] + self.vector[0], self.dot[1] + self.vector[1]

            segments = []
            step_segment = Segment(self.dot, next_dot)
            for segment in ALL_SEGMENTS.keys():
                if segment is self.last_reflect_segment:
                    continue
                intersection_dot = get_intersection(segment, step_segment)
                if intersection_dot:
                    segments.append((intersection_dot, segment))

            if segments:
                self.dot, self.last_reflect_segment = min(
                    segments,
                    key=lambda val: get_distance(self.dot, val[0])
                )
                self.vector = get_reflect_vector(self.vector, self.last_reflect_segment)
                box = ALL_SEGMENTS[self.last_reflect_segment]
                if box:
                    box.collision_count += 1
            else:
                self.dot = next_dot


class Segment:

    def __init__(self, dot1, dot2):
        self.dot1, self.dot2 = dot1, dot2
        x1, y1 = dot1
        x2, y2 = dot2
        self.center = (x1 + x2) / 2, (y1 + y2) / 2
        self.a, self.b, self.c = y2 - y1, x1 - x2, y1 * (x2 - x1) - x1 * (y2 - y1)
        self.length = get_distance(dot1, dot2)


class Box:

    def __init__(self, dots):
        self.dots = dots
        self.segments = []
        prev_dot = None
        for dot in dots + [dots[0]]:
            if prev_dot:
                self.segments.append(Segment(prev_dot, dot))
            prev_dot = dot
        self.width = max(dots, key=lambda val: val[0])[0] - min(dots, key=lambda val: val[0])[0]
        self.height = max(dots, key=lambda val: val[1])[1] - min(dots, key=lambda val: val[1])[1]
        self.collision_count = 0


def main():
    pg.init()
    sc = pg.display.set_mode((W, H))
    pg.display.set_caption(WINDOW_TITLE)
    clock = pg.time.Clock()
    font = pg.font.SysFont('Arial', 50)

    create_borders_segment()
    create_sparkle_iterators()
    create_boxes()

    while True:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                exit()

        draw_background(sc)
        draw_sparkle(sc, ALL_SPARKLE_ITERATORS)
        draw_boxes(sc, ALL_BOXES, font)
        pg.display.update()

        clock.tick(FPS)


if __name__ == '__main__':
    main()
