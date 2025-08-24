{
  "bot_name": "ETH_DCA_Calculator",
  "role": "Сигнальный бот для DCA/усреднения",
  "description": "Бот, который вычисляет уровни для усреднения позиции на основе заданной стратегии (Dollar-Cost Averaging) и показывает, сколько процентов от портфеля докупать на каждом уровне.",
  "implementation": "Локальный Python-скрипт, который запрашивает текущую цену ETH через CoinGecko API и выводит в консоль 5 уровней усреднения с просадками 5%, 10%, 15%, 20%, 25%.",
  "stage_one": {
    "exchange_api": false,
    "telegram_notifications": false,
    "price_source": "CoinGecko API (открытые данные)"
  },
  "strategy": {
    "asset": "ETH",
    "levels": 5,
    "drawdowns": [5, 10, 15, 20, 25],
    "allocation_percent": [20, 25, 30, 35, 40],
    "calculation_type": "процент от портфеля"
  },
  "output_format": {
    "header": "Расчет уровней DCA завершен",
    "current_price": "Текущая цена: $X.XXXX",
    "levels": [
      {
        "level": 1,
        "drawdown": "5.0%",
        "buy_price": "$X.XXXX",
        "allocation": "20% от ETH-портфеля"
      },
      {
        "level": 2,
        "drawdown": "10.0%",
        "buy_price": "$X.XXXX",
        "allocation": "25% от ETH-портфеля"
      },
      {
        "level": 3,
        "drawdown": "15.0%",
        "buy_price": "$X.XXXX",
        "allocation": "30% от ETH-портфеля"
      },
      {
        "level": 4,
        "drawdown": "20.0%",
        "buy_price": "$X.XXXX",
        "allocation": "35% от ETH-портфеля"
      },
      {
        "level": 5,
        "drawdown": "25.0%",
        "buy_price": "$X.XXXX",
        "allocation": "40% от ETH-портфеля"
      }
    ]
  },
  "coding_rules": {
    "always_full_files": true,
    "no_code_snippets": true,
    "editor": "nano",
    "command_format": "nano filename.py → полный код файла"
  }
}
