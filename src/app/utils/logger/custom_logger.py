import functools


def custom_logger(logger):
    def logger_wrapper(func):

        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            logger.info(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"{func.__name__} executed successfully.")
                return result
            except Exception as e:
                logger.error(f"Error occurred in {func.__name__} with args: {args}, kwargs: {kwargs}, error: {str(e)}")
                raise

        return wrapped_func

    return logger_wrapper