from variables import *

def generate_brick_coords(level):
    brick_default_width = 70
    brick_default_height = 30
    brick_coords = []
    if level == -1:
        # debug level
        brick_coords.append((400, 400, 470, 430, 1))
    if level == 0:
        y_start = 80
        x_start = round((screen_x - 700)/2)
        n_rows = 3
        for y in range(y_start, y_start + brick_default_height*(n_rows), brick_default_height):
            for x in range(x_start, x_start + 700, brick_default_width):
                brick_coords.append([x, y, x + brick_default_width, y + brick_default_height, 1]) # left, top, right, bottom
    if level == 1:
        y_start = 60
        x_start = round((screen_x - 700)/4)
        x_start_from_right = screen_x - x_start - brick_default_width
        n_rows = 10
        for y in range(y_start, y_start + brick_default_height*(n_rows), brick_default_height):
            for i, x in enumerate(range(x_start, x_start + 175, brick_default_width)):
                if i == 0:
                    continue
                brick_coords.append([x, y, x + brick_default_width, y + brick_default_height]) # left, top, right, bottom
            for i, x in enumerate(range(x_start_from_right, x_start_from_right - 175, -brick_default_width)):
                if i == 0:
                    continue
                brick_coords.append([x, y, x + brick_default_width, y + brick_default_height]) # left, top, right, bottom
        
        l = [i[0] for i in brick_coords][0:4]
        l.sort()
        
        for coords in brick_coords:
            if coords[0] == l[1] or coords[0] == l[2]:
                coords.append(2)
            else:
                coords.append(1)
        
    if level == 2:
        current_y = 30
        current_x = round((screen_x)/2)
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
                        current_x + j * brick_default_width,
                        current_y,
                        current_x + (j + 1) * brick_default_width,
                        current_y + brick_default_height,
                        health
                    ]
                )
                # make bricks on under side of longest row too
                if i != 5:
                    brick_coords.append(
                        [
                            current_x + j * brick_default_width,
                            current_y + (reflection_offset - i) * brick_default_height,
                            current_x + (j + 1) * brick_default_width,
                            current_y + (reflection_offset + 1 - i) * brick_default_height,
                            health_reflect
                        ]
                    )
            reflection_offset -= 1
            current_x -= 0.5 * brick_default_width
            current_y += brick_default_height

    max_brick_y = max([i[3] for i in brick_coords])
    return brick_coords, brick_default_width, brick_default_height, max_brick_y