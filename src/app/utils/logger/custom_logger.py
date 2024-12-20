import functools

from fastapi import Request

from src.app.utils.context import get_user_from_context
from src.app.utils.logger.logger import Logger


def custom_logger(logger: Logger):
    def logger_wrapper(func):
        @functools.wraps(func)
        async def wrapped_func(*args, **kwargs):
            # Initialize variables with default values
            user_id = 'Unknown'
            role = 'Unknown'
            sanitized_body = {}
            request = None

            try:
                # Get the Request object from args or kwargs
                request = next((arg for arg in args if isinstance(arg, Request)), kwargs.get('request'))

                if request:
                    # Extract user context from request state
                    user = get_user_from_context(request) or {}
                    user_id = user.get('user_id', 'Unknown')
                    role = user.get('role', 'Unknown')

                    # Extract and sanitize request details
                    sanitized_body = logger.sanitize_body(await request.json() if await request.body() else {})

                    # Log the entry with structured details
                    logger.debug(
                        f"Entering {func.__name__}\n"
                        f"User Context:\n"
                        f"  - user_id: {user_id}\n"
                        f"  - role: {role}\n"
                        f"Request Context:\n"
                        f"  - method: {request.method}\n"
                        f"  - path: {request.url.path}\n"
                        f"  - client_ip: {request.client.host}\n"
                        f"  - headers: {dict(request.headers)}\n"
                        f"  - body: {sanitized_body}\n"
                    )

                # Execute the function
                result = func(*args, **kwargs)

                # Log successful execution
                logger.info(f"{func.__name__} executed successfully.")
                return result

            except Exception as e:
                # Handle and log exceptions with request details
                error_msg = (
                    f"Error occurred in {func.__name__}: {str(e)}\n"
                    f"User Context:\n"
                    f"  - user_id: {user_id}\n"
                    f"  - role: {role}\n"
                )

                if request:
                    error_msg += (
                        f"Request Context:\n"
                        f"  - method: {request.method}\n"
                        f"  - path: {request.url.path}\n"
                        f"  - body: {sanitized_body}"
                    )

                logger.error(error_msg)
                raise

            finally:
                # Log exit from the function
                logger.debug(f"Exiting {func.__name__}")

        return wrapped_func

    return logger_wrapper