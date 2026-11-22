import logging

# Expected 403/404/405 responses in the tests would otherwise spam the console.
logging.disable(logging.CRITICAL)
