import sdl2
import sdl2.ext
from sdl2.ext import get_events, quit_requested, key_pressed
import sdl2.sdlgfx
import sys
from game import Game
import numpy as np
from board import PieceType
from board import WIDTH as BOARD_WIDTH
from board import HEIGHT as BOARD_HEIGHT

WIDTH = 800
HEIGHT = 800
SCALE = 20

game = Game()

def board_to_screen(x, y):
    return int(x * SCALE + WIDTH // 2), int(y * SCALE + HEIGHT // 2)


def to_sdl_color(color):
    return (color.r << 24) | (color.g << 16) | (color.b << 8) | 255


def draw_coin(renderer, x, y, coin_type):

    if coin_type == PieceType.BRONZE.value:
        color = sdl2.ext.Color(255, 0, 255)
    elif coin_type == PieceType.SILVER.value:
        color = sdl2.ext.Color(255, 255, 255)
    else:
        color = sdl2.ext.Color(255, 255, 0)

    sx, sy = board_to_screen(x, y)

    sdl2.sdlgfx.filledCircleColor(
        renderer.renderer,   # IMPORTANT: raw SDL_Renderer
        sx,
        sy,
        SCALE // 2,
        to_sdl_color(color)
    )


def draw_wall(renderer, x, y):
    pass

def draw_board(renderer):

    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            piece = game.get_piece(x, y)

            if piece == PieceType.EMPTY.value: continue
            elif piece == PieceType.WALL.value:
                pass
            else:
                draw_coin(renderer, x, y, piece)

def draw_player(renderer, x, y):
    pass

def main():

    game.start()

    sdl2.ext.init()

    window = sdl2.ext.Window("Test", size=(WIDTH, HEIGHT))
    window.show()

    renderer = sdl2.ext.Renderer(
        window,
        flags=sdl2.render.SDL_RENDERER_SOFTWARE
    )

    running = True
    while running:
        events = get_events()

        if quit_requested(events):
            running = False

        # Input
        if key_pressed(events, "w"):
            game.move_player(np.array([0, 1]))
        if key_pressed(events, "a"):
            game.move_player(np.array([-1, 0]))
        if key_pressed(events, "s"):
            game.move_player(np.array([0, -1]))
        if key_pressed(events, "d"):
            game.move_player(np.array([1, 0]))

        # Draw 
        renderer.clear(0)

        draw_board(renderer)

        renderer.present()

        sdl2.SDL_Delay(16)

    sdl2.ext.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())