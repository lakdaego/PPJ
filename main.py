from pathlib import Path
from time import perf_counter

from pico2d import (
    SDL_KEYDOWN,
    SDL_KEYUP,
    SDL_QUIT,
    SDLK_ESCAPE,
    SDLK_LEFT,
    SDLK_RIGHT,
    SDLK_SPACE,
    SDLK_x,
    SDLK_z,
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
IDLE_FRAME_BOTTOM = 480
IDLE_FRAME_LEFTS = (0, 160, 320, 480)
IDLE_FRAME_ANCHOR_XS = (100.5, 97.5, 96.8, 94.9)
IDLE_FRAME_ANCHOR_YS = (134, 134, 135, 135)
IDLE_FRAME_DURATION = 0.18
RUN_FRAME_BOTTOM = 320
RUN_FRAME_LEFTS = (0, 160, 320, 480, 640, 800, 960)
RUN_FRAME_ANCHOR_XS = (96.1, 97.7, 104.2, 97.5, 105.4, 97.6, 103.4)
RUN_FRAME_ANCHOR_YS = (131, 132, 128, 132, 131, 129, 132)
RUN_FRAME_DURATION = 0.1
JUMP_FRAME_BOTTOM = 160
JUMP_FRAME_LEFTS = (0, 160, 320, 480, 640)
JUMP_FRAME_ANCHOR_XS = (92.1, 94.4, 98.5, 98.3, 95.3)
JUMP_FRAME_ANCHOR_YS = (148, 143, 142, 148, 149)
JUMP_FRAME_DURATION = 0.075
FALL_FRAME_BOTTOM = 0
FALL_FRAME_LEFTS = (0, 160, 320)
FALL_FRAME_ANCHOR_XS = (104.9, 94.9, 89.9)
FALL_FRAME_ANCHOR_YS = (153, 158, 158)
FALL_FRAME_DURATION = 0.12
BOOST_FRAME_HEIGHT = 210
BOOST_FRAME_LEFTS = (0, 160, 320, 480, 640, 800, 960, 1120, 1280)
BOOST_FRAME_ANCHOR_XS = (91, 96, 100, 95.5, 92, 94, 101, 101.5, 97)
BOOST_FRAME_ANCHOR_YS = (144, 150, 143, 139, 135, 141, 143, 152, 163)
BOOST_STARTUP_DURATION = 0.06
BOOST_IGNITION_DURATION = 0.06
BOOST_FRAME_DURATION = 0.09
BOOST_HOVER_FRAME_SEQUENCE = (2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3)
ATTACK_FRAME_WIDTH = 224
ATTACK_FRAME_HEIGHT = 160
ATTACK_FRAME_LEFTS = (0, 224, 448, 672, 896, 1120, 1344, 1568, 1792)
ATTACK_FRAME_ANCHOR_XS = (89.5, 84, 97, 88.5, 85.5, 80.5, 74.5, 69.5, 91.5)
ATTACK_FRAME_ANCHOR_YS = (152, 152, 151, 151, 149, 151, 151, 155, 155)
ATTACK_FRAME_SEQUENCE = (3, 4, 5, 6, 7, 8)
ATTACK_FRAME_DURATIONS = (0.035, 0.035, 0.035, 0.06, 0.035, 0.035)
ATTACK_TOTAL_DURATION = sum(ATTACK_FRAME_DURATIONS)
JUMP_INITIAL_VELOCITY = 464.5
GRAVITY = 1400
JUMP_APEX_TIME = JUMP_INITIAL_VELOCITY / GRAVITY
JETPACK_THRUST = 3200
JETPACK_MAX_RISE_SPEED = 240
MAX_FALL_SPEED = 700
JETPACK_MAX_HEIGHT = CANVAS_HEIGHT / 2 - 60
LANDING_DURATION = 0.1
PLAYER_SIZE = 64
PLAYER_SPEED = 207
PLAYER_MARGIN = PLAYER_SIZE * 0.6
IDLE_REFERENCE_ANCHOR_Y = sum(IDLE_FRAME_ANCHOR_YS) / len(IDLE_FRAME_ANCHOR_YS)


def main():
    open_canvas(CANVAS_WIDTH, CANVAS_HEIGHT)
    try:
        background_image = load_image(
            str(Path(__file__).with_name("back.png"))
        )
        sprite_sheet = load_image(
            str(Path(__file__).with_name("robot_animation_sheet.png"))
        )
        jetpack_sheet = load_image(
            str(Path(__file__).with_name("robot_jetpack_sheet.png"))
        )
        attack_sheet = load_image(
            str(Path(__file__).with_name("robot_attack_sheet.png"))
        )
        player_x = CANVAS_WIDTH // 2
        left_pressed = False
        right_pressed = False
        space_pressed = False
        jetpack_pressed = False
        attack_pressed = False
        is_attacking = False
        attack_started_at = 0.0
        facing = 1
        was_moving = False
        was_falling = False
        is_airborne = False
        player_height = 0.0
        vertical_velocity = 0.0
        jump_started_at = 0.0
        boost_animation_start = 0.0
        fall_animation_start = 0.0
        landing_until = 0.0
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
                    elif event.key == SDLK_SPACE and not space_pressed:
                        space_pressed = True
                        if not is_airborne and current_time >= landing_until:
                            is_airborne = True
                            jump_started_at = current_time
                            player_height = 0.0
                            vertical_velocity = JUMP_INITIAL_VELOCITY
                            landing_until = 0.0
                            was_falling = False
                    elif event.key == SDLK_x and not jetpack_pressed:
                        jetpack_pressed = True
                        boost_animation_start = current_time
                        was_falling = False
                        if not is_airborne and current_time >= landing_until:
                            is_airborne = True
                            player_height = 0.0
                            vertical_velocity = 0.0
                            landing_until = 0.0
                    elif event.key == SDLK_z and not attack_pressed:
                        attack_pressed = True
                        if not is_attacking:
                            is_attacking = True
                            attack_started_at = current_time
                elif event.type == SDL_KEYUP:
                    if event.key == SDLK_LEFT:
                        left_pressed = False
                    elif event.key == SDLK_RIGHT:
                        right_pressed = False
                    elif event.key == SDLK_SPACE:
                        space_pressed = False
                    elif event.key == SDLK_x:
                        jetpack_pressed = False
                        if is_airborne and vertical_velocity > 0:
                            vertical_velocity = 0.0
                    elif event.key == SDLK_z:
                        attack_pressed = False

            if not game_running:
                break

            direction = int(right_pressed) - int(left_pressed)
            if direction:
                facing = direction
                player_x = max(
                    PLAYER_MARGIN,
                    min(
                        CANVAS_WIDTH - PLAYER_MARGIN,
                        player_x + direction * PLAYER_SPEED * delta_time,
                    ),
                )

            if (
                not is_airborne
                and jetpack_pressed
                and current_time >= landing_until
            ):
                is_airborne = True
                player_height = 0.0
                vertical_velocity = 0.0
                landing_until = 0.0
                boost_animation_start = current_time

            if is_airborne:
                previous_velocity = vertical_velocity
                if jetpack_pressed:
                    vertical_velocity = min(
                        vertical_velocity
                        + (JETPACK_THRUST - GRAVITY) * delta_time,
                        JETPACK_MAX_RISE_SPEED,
                    )
                else:
                    vertical_velocity = max(
                        vertical_velocity - GRAVITY * delta_time,
                        -MAX_FALL_SPEED,
                    )
                player_height += (
                    (previous_velocity + vertical_velocity) * 0.5 * delta_time
                )
                if jetpack_pressed and player_height >= JETPACK_MAX_HEIGHT:
                    player_height = JETPACK_MAX_HEIGHT
                    vertical_velocity = 0.0
                elif player_height <= 0 and vertical_velocity < 0:
                    player_height = 0.0
                    vertical_velocity = 0.0
                    is_airborne = False
                    landing_until = current_time + LANDING_DURATION
                    idle_animation_start = current_time
                    was_moving = False
                    was_falling = False

            if not is_airborne and landing_until and current_time >= landing_until:
                landing_until = 0.0

            if (
                is_attacking
                and current_time - attack_started_at >= ATTACK_TOTAL_DURATION
            ):
                is_attacking = False

            frame_width = FRAME_SIZE
            frame_height = FRAME_SIZE
            draw_width = PLAYER_SIZE
            draw_height = PLAYER_SIZE
            frame_image = sprite_sheet

            if is_attacking:
                attack_elapsed = current_time - attack_started_at
                frame_index = 0
                while (
                    frame_index < len(ATTACK_FRAME_DURATIONS) - 1
                    and attack_elapsed >= ATTACK_FRAME_DURATIONS[frame_index]
                ):
                    attack_elapsed -= ATTACK_FRAME_DURATIONS[frame_index]
                    frame_index += 1
                attack_frame_index = ATTACK_FRAME_SEQUENCE[frame_index]
                frame_left = ATTACK_FRAME_LEFTS[attack_frame_index]
                frame_bottom = 0
                frame_anchor_x = ATTACK_FRAME_ANCHOR_XS[attack_frame_index]
                frame_anchor_y = ATTACK_FRAME_ANCHOR_YS[attack_frame_index]
                frame_width = ATTACK_FRAME_WIDTH
                frame_height = ATTACK_FRAME_HEIGHT
                draw_width = round(
                    PLAYER_SIZE * ATTACK_FRAME_WIDTH / FRAME_SIZE
                )
                frame_image = attack_sheet
            elif is_airborne and jetpack_pressed:
                boost_elapsed = current_time - boost_animation_start
                if boost_elapsed < BOOST_STARTUP_DURATION:
                    boost_frame_index = 0
                elif boost_elapsed < (
                    BOOST_STARTUP_DURATION + BOOST_IGNITION_DURATION
                ):
                    boost_frame_index = 1
                else:
                    hover_elapsed = (
                        boost_elapsed
                        - BOOST_STARTUP_DURATION
                        - BOOST_IGNITION_DURATION
                    )
                    cycle_index = int(hover_elapsed / BOOST_FRAME_DURATION) % len(
                        BOOST_HOVER_FRAME_SEQUENCE
                    )
                    boost_frame_index = BOOST_HOVER_FRAME_SEQUENCE[cycle_index]
                frame_left = BOOST_FRAME_LEFTS[boost_frame_index]
                frame_bottom = 0
                frame_anchor_x = BOOST_FRAME_ANCHOR_XS[boost_frame_index]
                frame_anchor_y = BOOST_FRAME_ANCHOR_YS[boost_frame_index]
                frame_height = BOOST_FRAME_HEIGHT
                draw_height = round(
                    PLAYER_SIZE * BOOST_FRAME_HEIGHT / FRAME_SIZE
                )
                frame_image = jetpack_sheet
                was_falling = False
            elif is_airborne and vertical_velocity > 0:
                was_falling = False
                jump_elapsed = current_time - jump_started_at
                if jump_elapsed < JUMP_APEX_TIME:
                    frame_index = min(
                        int(jump_elapsed / JUMP_FRAME_DURATION),
                        len(JUMP_FRAME_LEFTS) - 1,
                    )
                    frame_left = JUMP_FRAME_LEFTS[frame_index]
                    frame_bottom = JUMP_FRAME_BOTTOM
                    frame_anchor_x = JUMP_FRAME_ANCHOR_XS[frame_index]
                    frame_anchor_y = JUMP_FRAME_ANCHOR_YS[frame_index]
                else:
                    frame_index = len(JUMP_FRAME_LEFTS) - 1
                    frame_left = JUMP_FRAME_LEFTS[frame_index]
                    frame_bottom = JUMP_FRAME_BOTTOM
                    frame_anchor_x = JUMP_FRAME_ANCHOR_XS[frame_index]
                    frame_anchor_y = JUMP_FRAME_ANCHOR_YS[frame_index]
            elif is_airborne:
                if not was_falling:
                    fall_animation_start = current_time
                was_falling = True
                fall_elapsed = current_time - fall_animation_start
                frame_index = min(
                    int(fall_elapsed / FALL_FRAME_DURATION),
                    len(FALL_FRAME_LEFTS) - 1,
                )
                frame_left = FALL_FRAME_LEFTS[frame_index]
                frame_bottom = FALL_FRAME_BOTTOM
                frame_anchor_x = FALL_FRAME_ANCHOR_XS[frame_index]
                frame_anchor_y = FALL_FRAME_ANCHOR_YS[frame_index]
            elif current_time < landing_until:
                frame_left = JUMP_FRAME_LEFTS[-1]
                frame_bottom = JUMP_FRAME_BOTTOM
                frame_anchor_x = JUMP_FRAME_ANCHOR_XS[-1]
                frame_anchor_y = JUMP_FRAME_ANCHOR_YS[-1]
            elif direction:
                if not was_moving:
                    run_animation_start = current_time
                frame_index = (
                    int((current_time - run_animation_start) / RUN_FRAME_DURATION)
                    % len(RUN_FRAME_LEFTS)
                )
                frame_left = RUN_FRAME_LEFTS[frame_index]
                frame_bottom = RUN_FRAME_BOTTOM
                frame_anchor_x = RUN_FRAME_ANCHOR_XS[frame_index]
                frame_anchor_y = RUN_FRAME_ANCHOR_YS[frame_index]
                was_moving = True
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
                was_moving = False
            visual_anchor_x = (
                frame_width - frame_anchor_x if facing < 0 else frame_anchor_x
            )
            frame_x = round(
                player_x
                + (frame_width / 2 - visual_anchor_x)
                * PLAYER_SIZE
                / FRAME_SIZE
            )
            frame_y = round(
                CANVAS_HEIGHT / 2
                + (
                    frame_anchor_y
                    - IDLE_REFERENCE_ANCHOR_Y
                    + (FRAME_SIZE - frame_height) / 2
                )
                * PLAYER_SIZE
                / FRAME_SIZE
                + player_height
            )
            flip = "h" if facing < 0 else ""

            clear_canvas()
            background_image.draw(
                CANVAS_WIDTH / 2,
                CANVAS_HEIGHT / 2,
                CANVAS_WIDTH,
                CANVAS_HEIGHT,
            )
            frame_image.clip_composite_draw(
                frame_left,
                frame_bottom,
                frame_width,
                frame_height,
                0,
                flip,
                frame_x,
                frame_y,
                draw_width,
                draw_height,
            )
            update_canvas()

            delay(1 / 60)
    finally:
        close_canvas()


if __name__ == "__main__":
    main()
