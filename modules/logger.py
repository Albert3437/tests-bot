from loguru import logger



logger.add("debug.log")


def logging(func):
    # И да, в логуру есть свой декоратор, но он совершенно не подходит для моих задач, 
    # так как возвращает огромный трейсбек который мне не нужен, и не удобен для вывода 
    # в веб приложение, а отключить простым способом его нельзя
    def wrapper(*args, **kwargs):
        try:
            return_value = func(*args, **kwargs)
            return return_value
        except Exception as e:
            function_name = func.__name__
            logger.error((function_name, e))
    return wrapper
