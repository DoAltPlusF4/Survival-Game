def spiral(width, height=None):
    if height is None:
        height = width
    x = y = 0
    dx = 0
    dy = -1
    for _ in range((max(width, height)*2+1)**2):
        if (-width < x <= width) and (-height < y <= height):
            yield (x, y)
        if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
            dx, dy = -dy, dx
        x, y = x+dx, y+dy
