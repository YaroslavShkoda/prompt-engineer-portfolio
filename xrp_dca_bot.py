#!/usr/bin/env python3"""XRP DCA Signal Bot
Локальный скрипт для расчета уровней усреднения позиции XRP
"""

import requests
import json
import datetime
from typing import Dict, List, Tuple

class XRPDcaBot:
    def __init__(self):
        self.coin_id = "ripple"
        self.currency = "usd"
        self.api_url = f"https://api.coingecko.com/api/v3/simple/price"
        
        # Параметры стратегии DCA
        self.dca_levels = [
            {"drop": -0.05, "allocation": 0.10},   # -5%  → 10% бюджета
            {"drop": -0.10, "allocation": 0.20},   # -10% → 20% бюджета
            {"drop": -0.15, "allocation": 0.30},   # -15% → 30% бюджета
            {"drop": -0.25, "allocation": 0.25},   # -25% → 25% бюджета
            {"drop": -0.35, "allocation": 0.15},   # -35% → 15% бюджета
        ]
        
    def get_current_price(self) -> float:
        """Получение текущей цены XRP"""
        try:
            response = requests.get(
                self.api_url,
                params={"ids": self.coin_id, "vs_currencies": self.currency},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data["ripple"]["usd"]
        except Exception as e:
            print(f"Ошибка при получении цены: {e}")
            return None
    
    def calculate_dca_levels(self, entry_price: float, total_budget: float) -> List[Dict]:
        """Расчет уровней DCA на основе входной цены"""
        levels = []
        
        for level in self.dca_levels:
            drop_price = entry_price * (1 + level["drop"])
            allocation_amount = total_budget * level["allocation"]
            coins_to_buy = allocation_amount / drop_price
            
            levels.append({
                "drop_percentage": level["drop"] * 100,
                "target_price": round(drop_price, 4),
                "allocation_usd": round(allocation_amount, 2),
                "coins_to_buy": round(coins_to_buy, 2),
                "total_invested": 0,
                "avg_price": 0
            })
        
        return levels
    
    def calculate_portfolio_metrics(self, levels: List[Dict], entry_price: float) -> Dict:
        """Расчет метрик портфеля"""
        total_invested = 0
        total_coins = 0
        
        # Начальная покупка (20% бюджета)
        initial_investment = 0.2 * sum(level["allocation_usd"] for level in levels) / 0.8
        initial_coins = initial_investment / entry_price
        
        total_invested += initial_investment
        total_coins += initial_coins
        
        # Учет DCA покупок
        for level in levels:
            total_invested += level["allocation_usd"]
            total_coins += level["coins_to_buy"]
            level["total_invested"] = round(total_invested, 2)
            level["avg_price"] = round(total_invested / total_coins, 4)
        
        return {
            "total_investment": round(total_invested, 2),
            "total_coins": round(total_coins, 2),
            "average_price": round(total_invested / total_coins, 4),
            "break_even_price": round(total_invested / total_coins, 4)
        }
    
    def generate_signal_report(self, entry_price: float, total_budget: float) -> str:
        """Генерация отчета с сигналами для DCA"""
        current_price = self.get_current_price()
        if not current_price:
            return "Не удалось получить текущую цену XRP"
        
        levels = self.calculate_dca_levels(entry_price, total_budget)
        metrics = self.calculate_portfolio_metrics(levels, entry_price)
        
        report = f"""
XRP DCA СТРАТЕГИЯ УСРЕДНЕНИЯ
============================

ТЕКУЩАЯ СИТУАЦИЯ:
   Текущая цена XRP: ${current_price:.4f}
   Ваша входная цена: ${entry_price:.4f}
   Текущая просадка: {((current_price - entry_price) / entry_price * 100):.2f}%

СТРАТЕГИЯ DCA (Бюджет: ${total_budget:.2f}):

УРОВНИ ДОКУПКИ:
"""
        
        for i, level in enumerate(levels, 1):
            status = "🔴 АКТИВЕН" if current_price <= level["target_price"] else "⚪ ОЖИДАНИЕ"
            report += f"""
{i}. {status}
   Цена докупки: ${level['target_price']:.4f} 
   Просадка: {level['drop_percentage']:.1f}%
   Сумма: ${level['allocation_usd']:.2f}
   Кол-во XRP: {level['coins_to_buy']:.2f}
   Средняя цена после: ${level['avg_price']:.4f}
"""
        
        report += f"""
ИТОГОВЫЕ МЕТРИКИ:
   Общая инвестиция: ${metrics['total_investment']:.2f}
   Всего XRP: {metrics['total_coins']:.2f}
   Средняя цена позиции: ${metrics['average_price']:.4f}
   Цена безубытка: ${metrics['break_even_price']:.4f}

РЕКОМЕНДАЦИИ:
   • Используйте 20% бюджета для начальной покупки по ${entry_price:.4f}
   • Следите за уровнями просадки для докупок
   • Установите стоп-лосс ниже последнего уровня (${levels[-1]['target_price'] * 0.95:.4f})
   • Цель продажи: 2x от средней цены (${metrics['break_even_price'] * 2:.4f})

ДЕЙСТВИЯ СЕГОДНЯ:
"""
        
        # Проверка активных уровней
        active_levels = [l for l in levels if current_price <= l["target_price"]]
        if active_levels:
            for level in active_levels:
                report += f"   🔥 Докупайте {level['coins_to_buy']:.2f} XRP по ${level['target_price']:.4f}\n"
        else:
            closest_level = min(levels, key=lambda x: abs(x['target_price'] - current_price))
            drop_needed = ((closest_level['target_price'] - current_price) / current_price * 100)
            report += f"   ⏳ Дождитесь просадки на {drop_needed:.1f}% для докупки на уровне ${closest_level['target_price']:.4f}\n"
        
        return report

    def save_strategy_to_file(self, report: str, filename: str = "xrp_dca_strategy.txt"):
        """Сохранение стратегии в файл"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"Стратегия сохранена в файл: {filename}")

def main():
    """Основная функция запуска бота"""
    print("Запуск XRP DCA Бота...")
    
    bot = XRPDcaBot()
    
    # Ввод параметров
    try:
        entry_price = float(input("Введите вашу входную цену XRP: ") or "3.02")
        total_budget = float(input("Введите общий бюджет для DCA ($): ") or "1000")
    except ValueError:
        print("Ошибка ввода, используются значения по умолчанию")
        entry_price = 3.02
        total_budget = 1000
    
    # Генерация отчета
    report = bot.generate_signal_report(entry_price, total_budget)
    print(report)
    
    # Сохранение в файл
    bot.save_strategy_to_file(report)
    
    # Дополнительная информация
    print("\nДЛЯ АВТОМАТИЧЕСКОГО ОБНОВЛЕНИЯ:")
    print("   Запустите: python3 xrp_dca_bot.py")
    print("   Для автоматического режима каждые 30 минут:")
    print("   */30 * * * * /usr/bin/python3 /path/to/xrp_dca_bot.py >> /path/to/dca_log.txt")

if __name__ == "__main__":
    main()
EOF


