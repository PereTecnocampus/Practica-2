import sdl2
import sdl2.ext
from sdl2.ext import get_events, quit_requested
import sdl2.sdlgfx
import sys
from game import Game
import numpy as np
from board import PieceType
from board import WIDTH as BOARD_WIDTH
from board import HEIGHT as BOARD_HEIGHT
import math

WIDTH = 1050
HEIGHT = 800
BOARD_SCREEN_WIDTH = 800
SCALE = BOARD_SCREEN_WIDTH // (BOARD_WIDTH + 6)

game = Game()

def board_to_screen(x, y):
    return (
        int((x - BOARD_WIDTH / 2) * SCALE + BOARD_SCREEN_WIDTH // 2) + SCALE // 2,
        int((BOARD_HEIGHT / 2 - y) * SCALE + HEIGHT // 2) - SCALE // 2
    )

def to_sdl_color(color):
    return (color.r << 24) | (color.g << 16) | (color.b << 8) | 255

def draw_coin(renderer, x, y, coin_type):
    if coin_type == PieceType.BRONZE.value:
        color = sdl2.ext.Color(165, 113, 100)
    elif coin_type == PieceType.SILVER.value:
        color = sdl2.ext.Color(211, 211, 211)
    else:
        color = sdl2.ext.Color(255, 223, 0)

    sx, sy = board_to_screen(x, y)
    
    sdl2.sdlgfx.filledCircleColor(renderer.renderer, sx, sy, (SCALE // 3) - 2, to_sdl_color(color))


def draw_wall(renderer, x, y):
    sx, sy = board_to_screen(x, y)
    sx1, sy1 = sx - SCALE // 2, sy - SCALE // 2
    sx2, sy2 = sx + SCALE // 2, sy + SCALE // 2
    sdl2.sdlgfx.boxColor(renderer.renderer, sx1, sy1, sx2, sy2, 0xFF0000FF)

def draw_outer_walls(renderer):
    left, top = board_to_screen(-1, BOARD_HEIGHT)
    right, _ = board_to_screen(BOARD_WIDTH, BOARD_HEIGHT)
    _, bottom = board_to_screen(-1, -1)
    wall_thickness = SCALE

    sdl2.sdlgfx.boxColor(renderer.renderer, left, top - wall_thickness // 2, right, top + wall_thickness // 2, 0xFF0000FF)
    sdl2.sdlgfx.boxColor(renderer.renderer, left, bottom - wall_thickness // 2, right, bottom + wall_thickness // 2, 0xFF0000FF)
    sdl2.sdlgfx.boxColor(renderer.renderer, left - wall_thickness // 2, bottom, left + wall_thickness // 2, top, 0xFF0000FF)
    sdl2.sdlgfx.boxColor(renderer.renderer, right + wall_thickness // 2, bottom, right - wall_thickness // 2, top, 0xFF0000FF)

def draw_board(renderer):
    draw_outer_walls(renderer)
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

    angle = math.degrees(math.atan2(last_dir[1], last_dir[0]))
    flip = sdl2.SDL_FLIP_NONE if last_dir[0] >= 0 else sdl2.SDL_FLIP_HORIZONTAL
    if tx:
        sdl2.SDL_RenderCopyEx(renderer.renderer, tx.tx, None, r, angle, None, flip)
    else:
        sdl2.sdlgfx.filledCircleColor(renderer.renderer, sx, sy, SCALE // 2, 0xFFFFFFFF)

def draw_route(renderer, route, color, single_step=False):
    if not route or len(route) < 2: return
    points = []
    limit = 2 if single_step else len(route)
    for i in range(limit):
        sx, sy = board_to_screen(route[i][0], route[i][1])
        points.append((sx, sy))
        
    for i in range(len(points) - 1):
        sdl2.sdlgfx.thickLineColor(renderer.renderer, points[i][0], points[i][1], points[i+1][0], points[i+1][1], 4, color)

def draw_ui(renderer, hint_mode, god_mode):
    sdl2.sdlgfx.stringColor(renderer.renderer, 820, 50, b"--- STATISTICS ---", 0xFFFFFFFF)
    status_str = f"Steps: {game.steps_taken} / {game.max_steps}".encode()
    sdl2.sdlgfx.stringColor(renderer.renderer, 820, 80, status_str, 0xFFFFFFFF)
    
    anells_str = f"Bronze: {game.bronze_collected}/6 | Silver: {game.silver_collected}/3".encode()
    sdl2.sdlgfx.stringColor(renderer.renderer, 820, 110, anells_str, 0xFFFFFFFF)

    # Hint Mode
    h_col = 0xFF00FF00 if hint_mode else 0xFF444444
    sdl2.sdlgfx.boxColor(renderer.renderer, 820, 150, 1000, 200, h_col)
    sdl2.sdlgfx.stringColor(renderer.renderer, 870, 170, b"HINT MODE", 0xFFFFFFFF)

    # God Mode
    g_col = 0xFFFF0000 if god_mode else 0xFF444444
    sdl2.sdlgfx.boxColor(renderer.renderer, 820, 220, 1000, 270, g_col)
    sdl2.sdlgfx.stringColor(renderer.renderer, 870, 240, b"GOD MODE", 0xFFFFFFFF)

    # End game message
    if game.state == "WON":
        sdl2.sdlgfx.stringColor(renderer.renderer, 820, 320, b"YOU WIN!", 0xFF00FFFF)
    elif game.state == "LOST":
        sdl2.sdlgfx.stringColor(renderer.renderer, 820, 320, b"GAME OVER!", 0xFF0000FF)

    # RESTART
    r_col = 0xFFD2691E
    sdl2.sdlgfx.boxColor(renderer.renderer, 820, 360, 1000, 410, r_col)
    sdl2.sdlgfx.stringColor(renderer.renderer, 870, 380, b"RESTART", 0xFFFFFFFF)

def main():
    game.start()
    sdl2.ext.init()
    window = sdl2.ext.Window("El Senyor dels Anells", size=(WIDTH, HEIGHT))
    window.show()
    renderer = sdl2.ext.Renderer(window, flags=sdl2.render.SDL_RENDERER_SOFTWARE)
    
    try:
        player_tx = sdl2.ext.Texture(renderer, sdl2.ext.load_img("player.png"))
    except:
        player_tx = None

    last_dir = np.array([1, 0])
    hint_mode = False
    god_mode = False

    running = True
    while running:
        events = get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
            elif event.type == sdl2.SDL_MOUSEBUTTONDOWN:
                x, y = event.button.x, event.button.y
                if 820 <= x <= 1000 and 150 <= y <= 200:
                    hint_mode = not hint_mode
                elif 820 <= x <= 1000 and 220 <= y <= 270:
                    god_mode = not god_mode
                elif 820 <= x <= 1000 and 360 <= y <= 410:
                    game.start() 
                    hint_mode = False 
                    god_mode = False
            elif event.type == sdl2.SDL_KEYDOWN and game.state == "PLAYING":
                if event.key.keysym.sym == sdl2.SDLK_w:
                    game.move_player(np.array([0, 1]))
                    last_dir = np.array([0, 1])
                elif event.key.keysym.sym == sdl2.SDLK_a:
                    game.move_player(np.array([-1, 0]))
                    last_dir = np.array([-1, 0])
                elif event.key.keysym.sym == sdl2.SDLK_s:
                    game.move_player(np.array([0, -1]))
                    last_dir = np.array([0, -1])
                elif event.key.keysym.sym == sdl2.SDLK_d:
                    game.move_player(np.array([1, 0]))
                    last_dir = np.array([1, 0])

        renderer.clear(0)
        draw_board(renderer)
        
        if game.state == "PLAYING" and game.best_route:
            if hint_mode:
                draw_route(renderer, game.best_route[1], 0xFF00FF00, single_step=True)
            if god_mode:
                draw_route(renderer, game.best_route[1], 0xFFFF0000, single_step=False)

        draw_player(renderer, player_tx, game.player_pos[0], game.player_pos[1], last_dir)
        draw_ui(renderer, hint_mode, god_mode)

        renderer.present()
        sdl2.SDL_Delay(16)

    sdl2.ext.quit()
    return 0

if __name__ == "__main__":
    sys.exit(main())