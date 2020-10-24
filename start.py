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
FIGURE_COLOR = (150, 150, 150)

# Коэффициент для перевода градусов в радианы
K_RADIAN = math.pi / 180

# Словарь для хранения всех отрезков
ALL_SEGMENTS = {}

# Словарь для хренения всех фигур
ALL_FIGURES = []

# Список для хранения всех светлячков
ALL_SPARKLE_ITERATORS = []


# -------------------- Функции отрисовки --------------------


def draw_background(sc):
    sc.fill(BACKGROUND_COLOR)


def draw_sparkle(sc, sparkle_iterators):
    for sparkle_iterator in sparkle_iterators:
        x, y = next(sparkle_iterator)
        pg.draw.rect(sc, SPARKLE_COLOR, (int(x - 1), int(y - 1), 3, 3))


def draw_figures(sc, figures):
    for figure in figures:
        pg.draw.polygon(sc, FIGURE_COLOR, figure.dots)


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


def create_figures():
    """Функция создает фигуры"""
    data = [
        [(100, 100), (300, 200), (200, 300)],
        [(200, 400), (300, 500), (200, 600), (100, 500)],
        [(400, 400), (600, 600), (400, 700), (500, 600)],
        [(600, 100), (800, 200), (600, 200), (500, 300), (400, 200)],
        [(1000, 100), (1100, 200), (1100, 400), (1000, 300)],
        [(1100, 500), (1100, 700), (800, 700), (1000, 600), (1000, 500)],
        [(800, 300), (900, 500), (800, 600), (800, 500), (700, 400)]
    ]
    for dots in data:
        figure = Figure(dots)
        ALL_FIGURES.append(figure)
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


class Figure:

    def __init__(self, dots):
        self.dots = dots
        self.segments = []
        prev_dot = None
        tmp_dots = dots[:]
        tmp_dots.append(dots[0])
        for dot in tmp_dots:
            if prev_dot:
                self.segments.append(Segment(prev_dot, dot))
            prev_dot = dot


def main():
    pg.init()
    sc = pg.display.set_mode((W, H))
    pg.display.set_caption(WINDOW_TITLE)
    clock = pg.time.Clock()

    create_borders_segment()
    create_sparkle_iterators()
    create_figures()

    while True:
        events = pg.event.get()
        for event in events:
            if event.type == pg.QUIT:
                pg.quit()
                exit()

        draw_background(sc)
        draw_sparkle(sc, ALL_SPARKLE_ITERATORS)
        draw_figures(sc, ALL_FIGURES)
        pg.display.update()

        clock.tick(FPS)


if __name__ == '__main__':
    main()
