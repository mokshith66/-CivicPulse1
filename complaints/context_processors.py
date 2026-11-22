from .constants import CATEGORIES, PRIORITIES, STATUSES


def civic_constants(request):
    """Make dropdown lists available to every template."""
    return {"categories": CATEGORIES, "statuses": STATUSES, "priorities": PRIORITIES}
