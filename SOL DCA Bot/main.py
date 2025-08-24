#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SOL DCA Bot – аналитический калькулятор усреднения позиции SOL
"""

import requests
import json
from datetime import datetime

# Параметры стратегии
SOLANA_SYMBOL = 'solana'
VS_CURRENCY = 'usd'

# Уровни просадок и распределение капитала
DRAWDOWN_LEVELS = [5, 10, 15, 20, 25]  # %
PORTFOLIO_ALLOCATION = [20, 25, 30, 35, 40]  # % от всего SOL-портфеля


def fetch_sol_price() -> float:
    """Получить текущую цену SOL через CoinGecko API."""
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": SOLANA_SYMBOL,
        "vs_currencies": VS_CURRENCY
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()[SOLANA_SYMBOL][VS_CURRENCY]


def calculate_dca_levels(current_price: float) -> list[dict]:
    """Рассчитать 5 уровней DCA."""
    levels = []
    for idx, drawdown in enumerate(DRAWDOWN_LEVELS):
        target_price = current_price * (1 - drawdown / 100)
        allocation = PORTFOLIO_ALLOCATION[idx]
        levels.append({
            "drawdown_percent": drawdown,
            "target_price": round(target_price, 2),
            "portfolio_allocation": allocation
        })
    return levels


def format_output(current_price: float, levels: list[dict]) -> str:
    """Форматировать итоговый вывод."""
    lines = [
        f"SOL DCA Bot – аналитический расчёт ({datetime.now().strftime('%d.%m.%Y %H:%M')})",
        "=" * 60,
        f"Текущая цена SOL: ${current_price:,.2f}",
        "",
        "5 уровней усреднения:",
    ]
    for lvl in levels:
        lines.append(
            f"• Просадка {lvl['drawdown_percent']}% "
            f"→ докупка по ${lvl['target_price']:,.2f} "
            f"({lvl['portfolio_allocation']}% от SOL-портфеля)"
        )
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    """Основной цикл работы бота."""
    try:
        price = fetch_sol_price()
        levels = calculate_dca_levels(price)
        output = format_output(price, levels)
        print(output)
    except Exception as e:
        print(f"Ошибка при получении данных: {e}")


if __name__ == "__main__":
    main()

