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
IDLE_FRAME_SIZE = 160
IDLE_FRAME_BOTTOM = 816
IDLE_FRAME_LEFTS = (50, 200, 360, 515)
IDLE_FOOT_ANCHORS = (79.5, 79.5, 80.5, 80)
IDLE_FOOT_ANCHOR_Y = 129.5
IDLE_FRAME_DURATION = 0.18
RUN_FRAME_WIDTH = 160
RUN_FRAME_HEIGHT = 140
RUN_FRAME_LEFTS = (52, 196, 378, 560, 749, 945, 1174)
RUN_FRAME_BOTTOMS = (647, 639, 638, 637, 634, 634, 630)
RUN_FOOT_ANCHORS = (79.5, 68.5, 65.5, 66, 66, 66.5, 84.5)
RUN_FOOT_ANCHOR_Y = 120
RUN_FRAME_DURATION = 0.1
PLAYER_SIZE = 80
PLAYER_SPEED = 300
PLAYER_MARGIN = PLAYER_SIZE * 0.6
PLAYER_FOOT_Y = CANVAS_HEIGHT // 2 - (
    IDLE_FOOT_ANCHOR_Y - IDLE_FRAME_SIZE / 2
) * PLAYER_SIZE / IDLE_FRAME_SIZE


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        sprite_sheet = load_image(
            str(Path(__file__).with_name("robot_sheet_transparent.png"))
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
                frame_bottom = RUN_FRAME_BOTTOMS[frame_index]
                frame_width = RUN_FRAME_WIDTH
                frame_height = RUN_FRAME_HEIGHT
                foot_anchor_x = RUN_FOOT_ANCHORS[frame_index]
                foot_anchor_y = RUN_FOOT_ANCHOR_Y
            else:
                if was_moving:
                    idle_animation_start = current_time
                frame_index = (
                    int((current_time - idle_animation_start) / IDLE_FRAME_DURATION)
                    % len(IDLE_FRAME_LEFTS)
                )
                frame_left = IDLE_FRAME_LEFTS[frame_index]
                frame_bottom = IDLE_FRAME_BOTTOM
                frame_width = IDLE_FRAME_SIZE
                frame_height = IDLE_FRAME_SIZE
                foot_anchor_x = IDLE_FOOT_ANCHORS[frame_index]
                foot_anchor_y = IDLE_FOOT_ANCHOR_Y

            was_moving = direction != 0
            visual_anchor_x = (
                frame_width - foot_anchor_x if facing < 0 else foot_anchor_x
            )
            frame_x = round(
                player_x
                + (frame_width / 2 - visual_anchor_x)
                * PLAYER_SIZE
                / frame_width
            )
            frame_y = round(
                PLAYER_FOOT_Y
                + (foot_anchor_y - frame_height / 2)
                * PLAYER_SIZE
                / frame_width
            )
            frame_draw_height = round(PLAYER_SIZE * frame_height / frame_width)
            flip = "h" if facing < 0 else ""

            clear_canvas()
            sprite_sheet.clip_composite_draw(
                frame_left,
                frame_bottom,
                frame_width,
                frame_height,
                0,
                flip,
                frame_x,
                frame_y,
                PLAYER_SIZE,
                frame_draw_height,
            )
            update_canvas()

            delay(1 / 60)
    finally:
        close_canvas()


if __name__ == "__main__":
    main()
