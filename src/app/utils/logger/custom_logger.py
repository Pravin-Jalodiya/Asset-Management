import functools
from flask import request, g
from src.app.utils.logger.logger import Logger


def custom_logger(logger: Logger):
    def logger_wrapper(func):

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            try:
                # Extract and sanitize request details
                sanitized_body = logger.sanitize_body(request.get_json(silent=True) or {})
                user_id = getattr(g, 'user_id', 'Unknown')
                role = getattr(g, 'role', 'Unknown')

                # Log the entry with structured details
                logger.debug(
                    f"Entering {func.__name__}\n"
                    f"User Context:\n"
                    f"  - user_id: {user_id}\n"
                    f"  - role: {role}\n"
                    f"Request Context:\n"
                    f"  - method: {request.method}\n"
                    f"  - path: {request.path}\n"
                    f"  - client_ip: {request.remote_addr}\n"
                    f"  - headers: {dict(request.headers)}\n"
                    f"  - body: {sanitized_body}\n"
                    f"Function Context:\n"
                    f"  - handler: {type(args[0]).__name__ if args else 'Unknown'}\n"
                )

                # Execute the function
                result = func(*args, **kwargs)

                # Log successful execution
                logger.info(f"{func.__name__} executed successfully.")
                return result
            except Exception as e:
                # Handle and log exceptions with request details
                logger.error(
                    f"Error occurred in {func.__name__}: {str(e)}\n"
                    f"User Context:\n"
                    f"  - user_id: {user_id}\n"
                    f"  - role: {role}\n"
                    f"Request Context:\n"
                    f"  - method: {request.method}\n"
                    f"  - path: {request.path}\n"
                    f"  - client_ip: {request.remote_addr}\n"
                    f"  - body: {sanitized_body}"
                )
                raise
            finally:
                # Log exit from the function
                logger.debug(f"Exiting {func.__name__}")

        return wrapped_func

    return logger_wrapper
