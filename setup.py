import pygame as pg
import random

pg.init()
pg.display.set_caption("Tangrams")

COLOR_MAP = (
    (),
    (0, 0, 0),
    (213, 186, 182),
    (0, 255, 255),
    (0, 0, 255),
    (255, 0, 255),
    (255, 255, 0),
    (128, 128, 128),
    (255, 0, 0),
    (0, 255, 0),
    (45, 170, 45),
    (128, 0, 255),
    (255, 128, 0),
    (128, 0, 0),
    (128, 128, 0)
)

TITLE_FONT = pg.font.Font("assets/OstrichSans-Black.otf", 70)
NUM_ITERATIONS_FONT = pg.font.Font("assets/OstrichSans-Black.otf", 50)
CURRENT_PIECE_FONT = pg.font.Font("assets/ostrich-regular.ttf", 50)

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
SCREEN = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

SQUARE_WIDTH = 30
SQUARE_HEIGHT = 30
SQUARE_MARGIN = 2

BOARD_X_OFFSET = SCREEN_WIDTH // 6
BOARD_Y_OFFSET = SCREEN_HEIGHT // 7

CURR_PIECE_X_OFFSET = 480
CURR_PIECE_Y_OFFSET = 650

LINE_THICKNESS = 5

BACKGROUND = pg.image.load("assets/white_background.png")