import logging
import os

import arcade
from src import GamePanel


def setup_logging():
    """Настройка логирования для всего приложения"""
    # Создаем папку для логов
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    logging.basicConfig(
        level=logging.DEBUG,  # DEBUG для файла, INFO для консоли
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            # В консоль - только INFO и выше
            logging.StreamHandler(),
            # В файл - всё (DEBUG и выше)
            logging.FileHandler(
                os.path.join(log_dir, 'game.log'),
                encoding='utf-8',
                mode='a'  # 'a' для добавления, 'w' для перезаписи
            )
        ]
    )

    # Настройка уровня для консоли отдельно
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.StreamHandler):
            handler.setLevel(logging.INFO)


def main():
    logger = logging.getLogger(__name__)
    logger.info("Запуск игры...")

    try:
        game = GamePanel()
        game.setup()
        arcade.run()
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)
        raise
    finally:
        logger.info("Игра завершена\n")


if __name__ == "__main__":
    setup_logging()
    main()