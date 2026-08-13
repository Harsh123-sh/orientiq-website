"""Safety and validation helpers for the Orientiq AI assistant."""

import re

# Maximum message length (characters)
MAX_MESSAGE_LENGTH = 2000

# Minimum message length (characters)
MIN_MESSAGE_LENGTH = 1

# Simple rate limit: max requests per window (per IP)
RATE_LIMIT_MAX = 20
RATE_LIMIT_WINDOW_SECONDS = 60


def validate_message(message):
    """Validate a visitor message.

    Returns (is_valid, error_message).
    """
    if message is None:
        return False, "Message is required."
    if not isinstance(message, str):
        return False, "Message must be a string."
    message = message.strip()
    if len(message) < MIN_MESSAGE_LENGTH:
        return False, "Message cannot be empty."
    if len(message) > MAX_MESSAGE_LENGTH:
        return False, f"Message is too long (max {MAX_MESSAGE_LENGTH} characters)."
    return True, ""


def sanitize_output(text):
    """Sanitize AI output for safe HTML rendering.

    - Strips any markdown code fences.
    - Removes control characters.
    - Returns plain text (the frontend escapes it).
    """
    if not text:
        return ""
    # Remove markdown code fences
    text = re.sub(r"```[a-zA-Z]*\n?|```", "", text)
    # Remove control characters except newlines/tabs
    text = "".join(ch for ch in text if ch == "\n" or ch == "\t" or ord(ch) >= 32)
    return text.strip()


def is_rate_limited(request, cache):
    """Simple per-IP rate limiting using Django's cache framework.

    Returns True if the request should be rejected.
    """
    ip = request.META.get("REMOTE_ADDR", "unknown")
    key = f"ai_rate_{ip}"
    count = cache.get(key, 0)
    if count >= RATE_LIMIT_MAX:
        return True
    cache.set(key, count + 1, RATE_LIMIT_WINDOW_SECONDS)
    return False