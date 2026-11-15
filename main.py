from pathlib import Path
from time import perf_counter

from pico2d import (
    SDL_KEYDOWN,
    SDL_QUIT,
    SDLK_ESCAPE,
    clear_canvas,
    close_canvas,
    delay,
    get_events,
    load_image,
    open_canvas,
    update_canvas,
)

CANVAS_WIDTH = 1280
CANVAS_HEIGHT = 720
IDLE_FRAME_SIZE = 160
IDLE_FRAME_BOTTOM = 816
IDLE_FRAME_LEFTS = (50, 200, 360, 515)
IDLE_FOOT_ANCHORS = (79.5, 79.5, 80.5, 80)
IDLE_FRAME_DURATION = 0.18
PLAYER_SIZE = 320


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        sprite_sheet = load_image(
            str(Path(__file__).with_name("robot_sheet_transparent.png"))
        )
        animation_start = perf_counter()
        running = True

        while running:
            frame_index = (
                int((perf_counter() - animation_start) / IDLE_FRAME_DURATION)
                % len(IDLE_FRAME_LEFTS)
            )
            frame_left = IDLE_FRAME_LEFTS[frame_index]
            frame_x = CANVAS_WIDTH // 2 + round(
                (IDLE_FRAME_SIZE / 2 - IDLE_FOOT_ANCHORS[frame_index])
                * PLAYER_SIZE
                / IDLE_FRAME_SIZE
            )

            clear_canvas()
            sprite_sheet.clip_draw(
                frame_left,
                IDLE_FRAME_BOTTOM,
                IDLE_FRAME_SIZE,
                IDLE_FRAME_SIZE,
                frame_x,
                CANVAS_HEIGHT // 2,
                PLAYER_SIZE,
                PLAYER_SIZE,
            )
            update_canvas()

            for event in get_events():
                if event.type == SDL_QUIT:
                    running = False
                elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
                    running = False

            delay(1 / 60)
    finally:
        close_canvas()


if __name__ == "__main__":
    main()
