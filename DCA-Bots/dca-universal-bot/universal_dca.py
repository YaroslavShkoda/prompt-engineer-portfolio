#!/usr/bin/env python3
"""
Universal_DCA_Calculator
Один скрипт для любого тикера.
"""

import requests
from typing import Optional, Tuple, List
from decimal import Decimal, getcontext

DRAWDOWNS: List[int] = [5, 10, 15, 20, 25]
ALLOCATION_PERCENT: List[int] = [20, 25, 30, 35, 40]
getcontext().prec = 18  # высокая точность для Decimal


# ---------- helpers ----------
def search_coingecko_id(ticker: str) -> Optional[Tuple[str, str]]:
    url = "https://api.coingecko.com/api/v3/search"
    params = {"query": ticker}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        coins = r.json().get("coins", [])
        if not coins:
            return None
        needle = ticker.lower()
        for c in coins:
            if c["symbol"].lower() == needle:
                return c["id"], c["name"]
        return coins[0]["id"], coins[0]["name"]
    except Exception:
        return None


def get_price(coin_id: str) -> Optional[Decimal]:
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_id, "vs_currencies": "usd"}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        price = r.json()[coin_id]["usd"]
        return Decimal(str(price))  # Decimal из строки без потери точности
    except Exception as e:
        print(f"Не удалось получить цену: {e}")
        return None


def smart_format(val: Decimal) -> str:
    """Выводим столько знаков, сколько нужно, но не более 8."""
    s = format(val.normalize(), "f")
    if "." in s:
        int_part, frac_part = s.split(".")
        frac_part = frac_part.rstrip("0")[:8]
        return f"{int_part}.{frac_part}" if frac_part else int_part
    return s


# ---------- main ----------
def main() -> None:
    ticker = input("Введите тикер (например, SOL, TON, PEPE): ").strip()
    res = search_coingecko_id(ticker)
    if not res:
        print(f"Тикер {ticker} не найден на CoinGecko.")
        return

    coin_id, coin_name = res
    price = get_price(coin_id)
    if price is None:
        return

    print("=" * 60)
    print(f"Расчет уровней DCA завершен. Текущая цена: ${smart_format(price)}")
    print("=" * 60)
    print(f"📊 DCA УРОВНИ УСРЕДНЕНИЯ {ticker.upper()} ({coin_name})")
    print("=" * 60)
    print(f"💰 Текущая цена: ${smart_format(price)}\n")

    for lvl, (dd, alloc) in enumerate(zip(DRAWDOWNS, ALLOCATION_PERCENT), start=1):
        buy_price = price * (Decimal(100 - dd) / Decimal(100))
        print(f"🔺 УРОВЕНЬ {lvl}:")
        print(f"   📉 Просадка: {dd:.1f}%")
        print(f"   💵 Цена покупки: ${smart_format(buy_price)}")
        print(f"   💳 Докупить: {alloc}% от {ticker.upper()}-портфеля\n")

    print("=" * 60)


if __name__ == "__main__":
    main()
