import requests
import time
import json
from config import *

class XRPDCABot:
    def __init__(self):
        self.triggered_levels = set()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def get_xrp_price(self):
        try:
            response = self.session.get(API_URL, timeout=10)
            data = response.json()
            return float(data["ripple"]["usd"])
        except Exception as e:
            print(f"Ошибка получения цены: {e}")
            return None

    def calculate_dca_signal(self, current_price):
        signals = []
        for level in DCA_LEVELS:
            if current_price <= level["price"] and level["price"] not in self.triggered_levels:
                amount_usdt = INITIAL_INVESTMENT * level["allocation"]
                xrp_amount = amount_usdt / current_price
                signals.append({
                    "price": level["price"],
                    "amount_usdt": round(amount_usdt, 2),
                    "xrp_amount": round(xrp_amount, 2)
                })
                self.triggered_levels.add(level["price"])
        return signals

    def print_signal(self, signal):
        print("\n" + "="*50)
        print("🚨 DCA СИГНАЛ ДЛЯ XRP!")
        print(f"Цена: ${signal['price']}")
        print(f"Объем покупки: {signal['xrp_amount']} XRP")
        print(f"Сумма в USDT: ${signal['amount_usdt']}")
        print("="*50 + "\n")

    def run(self):
        print("Запуск DCA бота для XRP...")
        print("Отслеживание ценовых уровней:")
        for level in DCA_LEVELS:
            print(f"- ${level['price']} ({level['allocation']*100}% средств)")
        
        while True:
            price = self.get_xrp_price()
            if price:
                print(f"\rТекущая цена XRP: ${price:.4f}", end="", flush=True)
                signals = self.calculate_dca_signal(price)
                for signal in signals:
                    self.print_signal(signal)
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    bot = XRPDCABot()
    bot.run()
