from consts import *

def generate_brick_coords(level):
    BRICK_DEFAULT_WIDTH = 70
    BRICK_DEFAULT_HEIGHT = 30
    brick_coords = []
    if level == -1:
        # debug level
        brick_coords.append((400, 400, 470, 430, 1))
    if level == 0:
        y_start = 80
        x_start = round((SCREEN_X - 700)/2)
        n_rows = 3
        for y in range(y_start, y_start + BRICK_DEFAULT_HEIGHT*(n_rows), BRICK_DEFAULT_HEIGHT):
            for x in range(x_start, x_start + 700, BRICK_DEFAULT_WIDTH):
                brick_coords.append([x, y, x + BRICK_DEFAULT_WIDTH, y + BRICK_DEFAULT_HEIGHT, 1]) # left, top, right, bottom
    if level == 1:
        y_start = 60
        x_start = round((SCREEN_X - 700)/4)
        x_start_from_right = SCREEN_X - x_start - BRICK_DEFAULT_WIDTH
        n_rows = 10
        for y in range(y_start, y_start + BRICK_DEFAULT_HEIGHT*(n_rows), BRICK_DEFAULT_HEIGHT):
            for i, x in enumerate(range(x_start, x_start + 175, BRICK_DEFAULT_WIDTH)):
                if i == 0:
                    continue
                brick_coords.append([x, y, x + BRICK_DEFAULT_WIDTH, y + BRICK_DEFAULT_HEIGHT]) # left, top, right, bottom
            for i, x in enumerate(range(x_start_from_right, x_start_from_right - 175, -BRICK_DEFAULT_WIDTH)):
                if i == 0:
                    continue
                brick_coords.append([x, y, x + BRICK_DEFAULT_WIDTH, y + BRICK_DEFAULT_HEIGHT]) # left, top, right, bottom
        
        l = [i[0] for i in brick_coords][0:4]
        l.sort()
        
        for coords in brick_coords:
            if coords[0] == l[1] or coords[0] == l[2]:
                coords.append(2)
            else:
                coords.append(1)
        
    if level == 2:
        current_y = 30
        current_x = round((SCREEN_X)/2)
        reflection_offset = 10
        for i in range(6):
            for j in range(i):
                health = 1
                health_reflect = 1
                if i == 5 and j == 2:
                    health = 3
                if i == 5 and j in (1, 3):
                    health = 2
                if i == 4 and j in (1, 2):
                    health, health_reflect = 2, 2
                if i == 3 and j == 1:
                    health, health_reflect = 2, 2
                brick_coords.append(
                    [
                        current_x + j * BRICK_DEFAULT_WIDTH,
                        current_y,
                        current_x + (j + 1) * BRICK_DEFAULT_WIDTH,
                        current_y + BRICK_DEFAULT_HEIGHT,
                        health
                    ]
                )
                # make bricks on under side of longest row too
                if i != 5:
                    brick_coords.append(
                        [
                            current_x + j * BRICK_DEFAULT_WIDTH,
                            current_y + (reflection_offset - i) * BRICK_DEFAULT_HEIGHT,
                            current_x + (j + 1) * BRICK_DEFAULT_WIDTH,
                            current_y + (reflection_offset + 1 - i) * BRICK_DEFAULT_HEIGHT,
                            health_reflect
                        ]
                    )
            reflection_offset -= 1
            current_x -= 0.5 * BRICK_DEFAULT_WIDTH
            current_y += BRICK_DEFAULT_HEIGHT

    max_brick_y = max([i[3] for i in brick_coords])
    return brick_coords, BRICK_DEFAULT_WIDTH, BRICK_DEFAULT_HEIGHT, max_brick_y