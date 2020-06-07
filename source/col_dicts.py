import pymunk

RECT = {
    "type": "rect",
    "x": float, "y": float,
    "width": float, "height": float,
    "radius": float,
    "collision_type": int
}

POLY = {
    "type": "poly",
    "vertices": [
        (float, float)
    ],
    "radius": float,
    "collision_type": int
}

CIRCLE = {
    "type": "circle",
    "offset": (float, float),
    "radius": float,
    "collision_type": int
}

SEGMENT = {
    "type": "segment",
    "a": (float, float),
    "b": (float, float),
    "radius": float,
    "collision_type": int
}


def rect(data):
    transform = pymunk.Transform(
        tx=-data["width"]/2,
        ty=-data["height"]/2
    )
    collider = pymunk.Poly(
        None,
        vertices=[
            (data["x"], data["y"]),
            (data["x"]+data["width"], data["y"]),
            (data["x"]+data["width"], data["y"]+data["width"]),
            (data["x"], data["y"]+data["width"])
        ],
        transform=transform,
        radius=data["radius"]
    )
    collider.collision_type = data["collision_type"]
    return collider


def poly(data):
    collider = pymunk.Poly(
        None,
        vertices=data["vertices"],
        radius=data["radius"]
    )
    collider.collision_type = data["collision_type"]
    return collider


def circle(data):
    collider = pymunk.Circle(
        None,
        radius=data["radius"],
        offset=data["offset"]
    )
    collider.collision_type = data["collision_type"]
    return collider


def segment(data):
    collider = pymunk.Segment(
        None,
        a=data["a"],
        b=data["b"],
        radius=data["radius"]
    )
    collider.collision_type = data["collision_type"]
    return collider


def dict_to_collider(collider):
    cols = {
        "poly": poly,
        "rect": rect,
        "circle": circle,
        "segment": segment
    }

    return cols[collider["type"]](collider)
