# Параметры DCA стратегии для XRP
INITIAL_INVESTMENT = 1000.0  # Начальная инвестиция в USDT

# Уровни DCA на основе процентного отклонения от текущей цены
# (рассчитано для текущей цены ~$3.02)
DCA_LEVELS = [
    {"price": 2.71, "allocation": 0.10},   # -10% от текущей цены
    {"price": 2.42, "allocation": 0.15},   # -20% от текущей цены
    {"price": 2.11, "allocation": 0.20},   # -30% от текущей цены
    {"price": 1.81, "allocation": 0.25},   # -40% от текущей цены
    {"price": 1.51, "allocation": 0.30}    # -50% от текущей цены
]

# Настройки API (используем CoinGecko)
API_URL = "https://api.coingecko.com/api/v3/simple/price?ids=ripple&vs_currencies=usd"
CHECK_INTERVAL = 60  # Проверка цены каждые 60 секунд
