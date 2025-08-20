"""
Centralized error handling for SIA Dashboard UI.
"""

from functools import wraps

def handle_errors(user_message="An error occurred."):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Optionally log error here
                return f"{user_message} Details: {e}"
        return wrapper
    return decorator

def format_error_message(e, user_message="An error occurred."):
    return f"{user_message} Details: {e}"