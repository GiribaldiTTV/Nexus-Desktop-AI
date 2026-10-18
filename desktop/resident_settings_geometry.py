"""Settings-only geometry in Qt logical pixels; rectangles are half-open."""


def _rect(rect):
    x, y, width, height = rect
    if width <= 0 or height <= 0:
        raise ValueError("Rectangle dimensions must be positive")
    return x, y, width, height


def _overlap(first, second):
    x, y, width, height = _rect(first)
    sx, sy, sw, sh = _rect(second)
    return max(0, min(x + width, sx + sw) - max(x, sx)) * max(
        0, min(y + height, sy + sh) - max(y, sy)
    )


def select_work_area(rect, areas, preferred=None):
    """Greatest intersection; ties prefer the current screen, then input order."""
    _rect(rect)
    areas = tuple(_rect(area) for area in areas)
    return max(areas, key=lambda area: (_overlap(rect, area), area == preferred), default=None)


def _limits(minimum, maximum):
    if any(low <= 0 or high < low for low, high in zip(minimum, maximum)):
        raise ValueError("Invalid size limits")
    return tuple(zip(minimum, maximum))


def fit_rect(rect, area, minimum, maximum):
    """Recover placement; an oversized minimum stays intact with its top-left reachable."""
    x, y, width, height = _rect(rect)
    (min_w, max_w), (min_h, max_h) = _limits(minimum, maximum)
    ax, ay, aw, ah = _rect(area)
    width = max(min_w, min(width, max_w, aw))
    height = max(min_h, min(height, max_h, ah))
    return (
        max(ax, min(x, ax + aw - width)),
        max(ay, min(y, ay + ah - height)),
        width,
        height,
    )


def _resize_axis(position, size, delta, leading, trailing, limits, bounds):
    if leading and trailing:
        raise ValueError("Opposite resize edges cannot be active together")
    if not leading and not trailing:
        return position, size
    low, high = limits
    anchor = position + size if leading else position
    if bounds is not None:
        origin, extent = bounds
        span = anchor - origin if leading else origin + extent - anchor
        high = max(low, min(high, span))
    size = max(low, min(size - delta if leading else size + delta, high))
    return (anchor - size if leading else anchor), size


def resize_rect(rect, delta, edges, area, minimum, maximum):
    """Keep the opposite edge fixed; minimum size wins if full fit is impossible."""
    x, y, width, height = _rect(rect)
    dx, dy = delta
    left, right, top, bottom = edges
    horizontal, vertical = _limits(minimum, maximum)
    bounds = _rect(area) if area is not None else None
    x, width = _resize_axis(
        x, width, dx, left, right, horizontal,
        (bounds[0], bounds[2]) if bounds is not None else None,
    )
    y, height = _resize_axis(
        y, height, dy, top, bottom, vertical,
        (bounds[1], bounds[3]) if bounds is not None else None,
    )
    return x, y, width, height
