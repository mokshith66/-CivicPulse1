CATEGORIES = [
    "Potholes and damaged roads",
    "Garbage and waste management",
    "Broken streetlights",
    "Water leakage",
    "Blocked drainage",
    "Damaged public infrastructure",
    "Other civic issues",
]
STATUSES = ["Submitted", "Acknowledged", "In Progress", "Resolved", "Rejected"]
PRIORITIES = ["Low", "Normal", "High", "Urgent"]
ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "webp"]

ROLE_CITIZEN = "citizen"
ROLE_ADMIN = "admin"
ROLE_CHOICES = [(ROLE_CITIZEN, "Citizen"), (ROLE_ADMIN, "Administrator")]


def as_choices(values):
    return [(v, v) for v in values]
