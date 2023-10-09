from variables import *

def generate_brick_coords(level):
    brick_default_width = 70
    brick_default_height = 30
    if level == -1:
        # debug level
        brick_coords = []
        brick_coords.append((400, 400, 470, 430, 3))
    if level == 0:
        brick_coords = []
        y_start = 80
        x_start = round((screen_x - 700)/2)
        n_rows = 3
        for y in range(y_start, y_start + brick_default_height*(n_rows), brick_default_height):
            for x in range(x_start, x_start + 700, brick_default_width):
                brick_coords.append([x, y, x + brick_default_width, y + brick_default_height, 1]) # left, top, right, bottom
    if level == 1:
        brick_coords = []
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

    max_brick_y = max([i[3] for i in brick_coords])
    return brick_coords, brick_default_width, brick_default_height, max_brick_y