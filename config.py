# Параметры DCA стратегии для XRP
INITIAL_INVESTMENT = 1000.0  # Начальная инвестиция в USDT

# Уровни DCA на основе текущей цены ~$3.02
DCA_LEVELS = [
    {"price": 2.85, "allocation": 0.15},   # -5.6% от текущей цены
    {"price": 2.70, "allocation": 0.20},   # -10.6% от текущей цены
    {"price": 2.55, "allocation": 0.25},   # -15.6% от текущей цены
    {"price": 2.40, "allocation": 0.20},   # -20.5% от текущей цены
    {"price": 2.25, "allocation": 0.20}    # -25.5% от текущей цены
]

# Настройки API
API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=ripple&vs_currencies=usd"
CHECK_INTERVAL = 60  # Проверка цены каждые 60 секунд
