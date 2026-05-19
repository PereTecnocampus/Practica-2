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
import math

WIDTH = 800
HEIGHT = 800
SCALE = WIDTH // (BOARD_WIDTH + 6)

game = Game()

def board_to_screen(x, y):
    return (
        int((x - BOARD_WIDTH / 2) * SCALE + WIDTH // 2) + SCALE // 2,
        int((BOARD_HEIGHT / 2 - y) * SCALE + HEIGHT // 2) - SCALE // 2
    )


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
        renderer.renderer,
        sx,
        sy,
        SCALE // 3,
        to_sdl_color(color)
    )


def draw_wall(renderer, x, y):
    sx, sy = board_to_screen(x, y)
    sx1, sy1 = sx - SCALE // 2, sy - SCALE // 2
    sx2, sy2 = sx + SCALE // 2, sy + SCALE // 2

    sdl2.sdlgfx.boxColor(
        renderer.renderer,
        sx1, sy1, sx2, sy2,
        0xFF0000FF
    )

def draw_outer_walls(renderer):

    # Board corners in screen space
    left, top = board_to_screen(-1, BOARD_HEIGHT)
    right, _ = board_to_screen(BOARD_WIDTH, BOARD_HEIGHT)
    _, bottom = board_to_screen(-1, -1)

    wall_thickness = SCALE

    # Top
    sdl2.sdlgfx.boxColor(
        renderer.renderer,
        left,
        top - wall_thickness // 2,
        right,
        top + wall_thickness // 2,
        0xFF0000FF
    )

    # Bottom
    sdl2.sdlgfx.boxColor(
        renderer.renderer,
        left,
        bottom - wall_thickness // 2,
        right,
        bottom + wall_thickness // 2,
        0xFF0000FF
    )

    # Left
    sdl2.sdlgfx.boxColor(
        renderer.renderer,
        left - wall_thickness // 2,
        bottom,
        left + wall_thickness // 2,
        top,
        0xFF0000FF
    )

    # Right
    sdl2.sdlgfx.boxColor(
        renderer.renderer,
        right + wall_thickness // 2,
        bottom,
        right - wall_thickness // 2,
        top,
        0xFF0000FF
    )

def draw_board(renderer):

    draw_outer_walls(renderer)

    # Draw inner
    for x in range(BOARD_WIDTH):
        for y in range(BOARD_HEIGHT):
            piece = game.get_piece(x, y)

            if piece == PieceType.EMPTY.value: continue
            elif piece == PieceType.WALL.value:
                draw_wall(renderer, x, y)
            else:
                draw_coin(renderer, x, y, piece)

def draw_player(renderer, tx, x, y, last_dir):

    sx, sy = board_to_screen(x, y)

    r = sdl2.SDL_Rect()
    r.x = sx - SCALE // 2
    r.y = sy - SCALE // 2
    r.w, r.h = SCALE, SCALE

    angle = math.degrees(math.atan(last_dir[1] / last_dir[0]))
    flip = sdl2.SDL_FLIP_NONE if last_dir[0] != 1 else sdl2.SDL_FLIP_HORIZONTAL

    sdl2.SDL_RenderCopyEx(renderer.renderer, tx.tx, None, r, angle, None, flip)

def main():

    game.start()

    sdl2.ext.init()

    window = sdl2.ext.Window("Test", size=(WIDTH, HEIGHT))
    window.show()

    renderer = sdl2.ext.Renderer(
        window,
        flags=sdl2.render.SDL_RENDERER_SOFTWARE
    )

    player_tx = sdl2.ext.Texture(renderer, sdl2.ext.load_img("player.png"))
    last_dir = np.array([1, 0])

    running = True
    while running:
        events = get_events()

        if quit_requested(events):
            running = False

        # Input
        if key_pressed(events, "w"):
            game.move_player(np.array([0, 1]))
            last_dir = np.array([0, 1])
        elif key_pressed(events, "a"):
            game.move_player(np.array([-1, 0]))
            last_dir = np.array([-1, 0])
        elif key_pressed(events, "s"):
            game.move_player(np.array([0, -1]))
            last_dir = np.array([0, -1])
        elif key_pressed(events, "d"):
            game.move_player(np.array([1, 0]))
            last_dir = np.array([1, 0])

        # Draw 
        renderer.clear(0)

        draw_board(renderer)
        draw_player(renderer, player_tx, game.player_pos[0], game.player_pos[1], last_dir)

        renderer.present()

        sdl2.SDL_Delay(16)

    sdl2.ext.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())