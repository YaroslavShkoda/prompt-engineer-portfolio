"""
MOEXbot — бот-аналитик ТОП-10 Московской биржи.
"""
import time
import logging
from src.logger import setup_logger
from src.data_parser import fetch_top10_tickers, fetch_latest_prices
from src.technical_analyzer import analyze_ticker
from src.signal_generator import generate_signal

__version__ = "1.0.0"


def main():
    logger = setup_logger()
    logger.info("Бот запущен. Начинаем цикл анализа каждые 15 минут.")

    while True:
        try:
            logger.info("=== Начинаем новый цикл анализа ===")

            tickers = fetch_top10_tickers()
            logger.info(f"Получен динамический ТОП-10: {tickers}")

            prices = fetch_latest_prices(tickers)
            logger.info(f"Получены цены: {prices}")

            analysis = {}
            for s in tickers:
                analysis[s] = analyze_ticker(s)
            logger.info("Технический анализ завершён.")

            signal = generate_signal(analysis, prices)
            print(signal)

            logger.info("=== Цикл завершён. Ожидание 15 минут... ===")
            time.sleep(15 * 60)

        except KeyboardInterrupt:
            logger.info("Работа бота остановлена пользователем.")
            break
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
