from consts import SCREEN_X, BRICK_DEFAULT_WIDTH, BRICK_DEFAULT_HEIGHT

def generate_brick_coords(level):
    level_dict = {
        -1: debuglevel,
        0:  level0,
        1:  level1,
        2:  level2,
        3:  level3
    }
    brick_coords = level_dict[level]()
    max_brick_y = 0
    for i in brick_coords:
        # Add 5 to account for ceiling thickness
        y_height = (i[1] + 1) * BRICK_DEFAULT_HEIGHT + 5
        if y_height > max_brick_y:
            max_brick_y = y_height
    
    return brick_coords, max_brick_y
    

def debuglevel() -> list:
    return [(0, 1, 1)]


def level0() -> list:
    brick_coords = []
    y_start = 2 # Two grid spaces above first row
    x_start = 1 # One grid space left and right of rows
    n_rows = 3
    n_cols = 11
    for y in range(y_start, n_rows + y_start):
        for x in range(x_start, n_cols + x_start):
            brick_coords.append([x, y, 1]) # Top left corner (x, y) and health (1)
    return brick_coords


def level1() -> list:
    brick_coords = []
    y_start = 2
    n_rows = 11
    n_cols = 13
    for y in range(y_start, n_rows + y_start):
        for x in range(n_cols):
            if x in [2, 3, 9, 10]:
                brick_coords.append([x, y])
    l = [i[0] for i in brick_coords][0:4]
    l.sort()
    
    for coords in brick_coords:
        if coords[0] == l[1] or coords[0] == l[2]:
            coords.append(2)
        else:
            coords.append(1)

    for coords in [(6, 6, 1), (5, 7, 1), (7, 7, 1), (6, 7, 2), (6, 8, 1)]:
        brick_coords.append(coords)
        
    return brick_coords
        

def level2() -> list:
    brick_coords = []
    y_offset1 = 7
    coords = [
        (2, 1, 1), (1, 2, 1), (2, 2, 2), (2, 3, 1), (3, 2, 1),
        (6, 1, 1), (5, 2, 1), (6, 2, 2), (6, 3, 1), (7, 2, 1),
        (10, 1, 1), (9, 2, 1), (10, 2, 2), (10, 3, 1), (11, 2, 1)
    ]
    for c in coords:
        brick_coords.append(c)
        brick_coords.append(
            (c[0], c[1] + y_offset1, c[2])
        )

    for i in range(13):
        brick_coords.append((i, 6, 2))

    for i in range(13):
        if i % 2 == 1:
            brick_coords.append((i, 13, 1))

    return brick_coords

    
def level3() -> list:
    brick_coords = []
    current_y = 1
    current_x = 6.5
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
                    current_x + j,
                    current_y,
                    health
                ]
            )
            # make bricks on under side of longest row too
            if i != 5:
                brick_coords.append(
                    [
                        current_x + j,
                        current_y + (reflection_offset - i),
                        health_reflect
                    ]
                )
        reflection_offset -= 1
        current_x -= 0.5
        current_y += 1

    return brick_coords
