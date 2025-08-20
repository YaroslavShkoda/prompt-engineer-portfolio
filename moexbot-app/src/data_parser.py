"""
Парсер данных с открытых источников.
Получает динамический ТОП-10 и цены.
"""
import random
from typing import List, Dict

__version__ = "1.0.0"


def fetch_top10_tickers() -> List[str]:
    """
    Имитация получения ТОП-10 тикеров по обороту.
    В реальности — парсинг с moex.com или investing.com.

    Returns:
        Список тикеров.
    """
    all_tickers = [
        "SBER", "GAZP", "LKOH", "MTSS", "NVTK", "ROSN", "TATN", "YNDX",
        "ALRS", "MGNT", "AFKS", "FEES", "PIKK", "MOEX", "CHMF"
    ]
    return random.sample(all_tickers, 10)


def fetch_latest_prices(tickers: List[str]) -> Dict[str, float]:
    """
    Получает текущие цены.

    Args:
        tickers: Список тикеров.

    Returns:
        Словарь: {тикер: цена}
    """
    base_prices = {
        "SBER": 300, "GAZP": 150, "LKOH": 7000, "MTSS": 270,
        "NVTK": 2000, "ROSN": 1200, "TATN": 1400, "YNDX": 5000,
        "ALRS": 20, "MGNT": 300, "AFKS": 60, "FEES": 500,
        "PIKK": 2500, "MOEX": 120, "CHMF": 6000
    }
    prices = {}
    for ticker in tickers:
        base = base_prices.get(ticker, 100)
        noise = random.uniform(0.98, 1.02)
        prices[ticker] = round(base * noise, 2)
    return prices
