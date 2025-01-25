import logging

# Настройка логирования
def setup_logger(name="bot_logger", level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Форматирование сообщений
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s]: [%(module)s] - %(message)s",  # Новый формат
        datefmt="%Y-%m-%d %H:%M:%S"  # Формат даты
    )
    console_handler.setFormatter(formatter)

    # Добавляем обработчик в логгер
    if not logger.handlers:
        logger.addHandler(console_handler)

    return logger
