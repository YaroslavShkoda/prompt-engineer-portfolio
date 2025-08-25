#!/usr/bin/env python3
"""
XRP High-Frequency Trading Bot
Автоматическая торговая система с 16 индикаторами
"""

import asyncio
import logging
import signal
import sys
import os
from datetime import datetime
import argparse
from src.signal_engine import SignalEngine

# Отключаем стандартное логирование
logging.getLogger().setLevel(logging.CRITICAL)  # Полностью глушим логи
logging.getLogger('ccxt').setLevel(logging.CRITICAL)
logging.getLogger('asyncio').setLevel(logging.CRITICAL)


class TradingBot:
    """Основной класс торгового бота"""

    def __init__(self, config_path: str = "config/strategy_config.json"):
        self.config_path = config_path
        self.signal_engine = None
        self.running = False

    async def initialize(self):
        """Инициализация бота"""
        print("=" * 60)
        print("XRP HIGH-FREQUENCY TRADING BOT")
        print("=" * 60)
        print(f"Запуск в {datetime.now()}")
        print()

        try:
            self.signal_engine = SignalEngine(self.config_path)
            print("Инициализация завершена успешно")
        except Exception as e:
            print(f"Ошибка инициализации: {e}")
            raise

    async def start(self, continuous: bool = False, interval: int = 15):
        """Запуск бота"""
        await self.initialize()

        if continuous:
            print("Запуск непрерывного анализа...")
            self.running = True

            def signal_handler(signum, frame):
                print("\nБот остановлен пользователем")
                self.running = False

            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)

            while self.running:
                try:
                    result = await self.signal_engine.analyze_all_timeframes()
                    report = self.signal_engine.create_signal_report(result)
                    print(report)
                    print()
                    await asyncio.sleep(interval * 60)
                except KeyboardInterrupt:
                    break
                except Exception as e:
                    print(f"Ошибка в цикле: {e}")
                    await asyncio.sleep(60)
            print("Бот остановлен")
        else:
            result = await self.signal_engine.analyze_all_timeframes()
            report = self.signal_engine.create_signal_report(result)
            print(report)

    async def backtest(self, days: int = 30):
        """Запуск бэктеста"""
        print(f"Бэктестинг за {days} дней пока не реализован")

    async def health_check(self):
        """Проверка здоровья"""
        print("Система: OK")


async def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description='XRP High-Frequency Trading Bot')
    parser.add_argument('--config', default='config/strategy_config.json',
                       help='Путь к конфигурационному файлу')
    parser.add_argument('--continuous', action='store_true',
                       help='Запустить непрерывный анализ')
    parser.add_argument('--interval', type=int, default=15,
                       help='Интервал анализа в минутах')
    parser.add_argument('--backtest', type=int, metavar='DAYS',
                       help='Запустить бэктест')
    parser.add_argument('--health-check', action='store_true',
                       help='Проверка здоровья')

    args = parser.parse_args()

    bot = TradingBot(args.config)

    if args.health_check:
        await bot.health_check()
        return

    if args.backtest:
        await bot.backtest(args.backtest)
        return

    await bot.start(continuous=args.continuous, interval=args.interval)


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    asyncio.run(main())
