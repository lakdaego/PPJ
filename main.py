from pathlib import Path
from time import perf_counter

from pico2d import (
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDL_QUIT,
    SDLK_ESCAPE,
    SDLK_LEFT,
    SDLK_RIGHT,
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
FRAME_SIZE = 160
IDLE_FRAME_BOTTOM = 160
IDLE_FRAME_LEFTS = (0, 160, 320, 480)
IDLE_FRAME_ANCHOR_XS = (100.5, 97.5, 96.8, 94.9)
IDLE_FRAME_ANCHOR_YS = (134, 134, 135, 135)
IDLE_FRAME_DURATION = 0.18
RUN_FRAME_BOTTOM = 0
RUN_FRAME_LEFTS = (0, 160, 320, 480, 640, 800, 960)
RUN_FRAME_ANCHOR_XS = (96.1, 97.7, 104.2, 97.5, 105.4, 97.6, 103.4)
RUN_FRAME_ANCHOR_YS = (131, 132, 128, 132, 131, 129, 132)
RUN_FRAME_DURATION = 0.1
PLAYER_SIZE = 80
PLAYER_SPEED = 300
PLAYER_MARGIN = PLAYER_SIZE * 0.6
IDLE_REFERENCE_ANCHOR_Y = sum(IDLE_FRAME_ANCHOR_YS) / len(IDLE_FRAME_ANCHOR_YS)


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        sprite_sheet = load_image(
            str(Path(__file__).with_name("robot_animation_sheet.png"))
        )
        player_x = CANVAS_WIDTH // 2
        left_pressed = False
        right_pressed = False
        facing = 1
        was_moving = False
        previous_time = perf_counter()
        idle_animation_start = previous_time
        run_animation_start = previous_time
        game_running = True

        while game_running:
            current_time = perf_counter()
            delta_time = min(current_time - previous_time, 0.1)
            previous_time = current_time

            for event in get_events():
                if event.type == SDL_QUIT:
                    game_running = False
                elif event.type == SDL_KEYDOWN:
                    if event.key == SDLK_ESCAPE:
                        game_running = False
                    elif event.key == SDLK_LEFT:
                        left_pressed = True
                    elif event.key == SDLK_RIGHT:
                        right_pressed = True
                elif event.type == SDL_KEYUP:
                    if event.key == SDLK_LEFT:
                        left_pressed = False
                    elif event.key == SDLK_RIGHT:
                        right_pressed = False

            if not game_running:
                break

            direction = int(right_pressed) - int(left_pressed)
            if direction:
                if not was_moving:
                    run_animation_start = current_time
                facing = direction
                player_x = max(
                    PLAYER_MARGIN,
                    min(
                        CANVAS_WIDTH - PLAYER_MARGIN,
                        player_x + direction * PLAYER_SPEED * delta_time,
                    ),
                )
                frame_index = (
                    int((current_time - run_animation_start) / RUN_FRAME_DURATION)
                    % len(RUN_FRAME_LEFTS)
                )
                frame_left = RUN_FRAME_LEFTS[frame_index]
                frame_bottom = RUN_FRAME_BOTTOM
                frame_anchor_x = RUN_FRAME_ANCHOR_XS[frame_index]
                frame_anchor_y = RUN_FRAME_ANCHOR_YS[frame_index]
            else:
                if was_moving:
                    idle_animation_start = current_time
                frame_index = (
                    int((current_time - idle_animation_start) / IDLE_FRAME_DURATION)
                    % len(IDLE_FRAME_LEFTS)
                )
                frame_left = IDLE_FRAME_LEFTS[frame_index]
                frame_bottom = IDLE_FRAME_BOTTOM
                frame_anchor_x = IDLE_FRAME_ANCHOR_XS[frame_index]
                frame_anchor_y = IDLE_FRAME_ANCHOR_YS[frame_index]

            was_moving = direction != 0
            visual_anchor_x = (
                FRAME_SIZE - frame_anchor_x if facing < 0 else frame_anchor_x
            )
            frame_x = round(
                player_x
                + (FRAME_SIZE / 2 - visual_anchor_x) * PLAYER_SIZE / FRAME_SIZE
            )
            frame_y = round(
                CANVAS_HEIGHT / 2
                + (frame_anchor_y - IDLE_REFERENCE_ANCHOR_Y)
                * PLAYER_SIZE
                / FRAME_SIZE
            )
            flip = "h" if facing < 0 else ""

            clear_canvas()
            sprite_sheet.clip_composite_draw(
                frame_left,
                frame_bottom,
                FRAME_SIZE,
                FRAME_SIZE,
                0,
                flip,
                frame_x,
                frame_y,
                PLAYER_SIZE,
                PLAYER_SIZE,
            )
            update_canvas()

            delay(1 / 60)
    finally:
        close_canvas()


if __name__ == "__main__":
    main()
