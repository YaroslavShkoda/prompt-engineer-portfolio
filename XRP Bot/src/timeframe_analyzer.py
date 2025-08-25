import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
import ccxt
import asyncio
from concurrent.futures import ThreadPoolExecutor

class TimeframeAnalyzer:
    """Анализатор для иерархического анализа таймфреймов"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'sandbox': config['api']['testnet']
        })

        # Сопоставление таймфреймов с корректными значениями для Binance API
        self.timeframe_mapping = {
            '1D': '1d',
            '4H': '4h',
            '1H': '1h',
            '15m': '15m'
        }

    async def fetch_data(self, symbol: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
        """Получение исторических данных для таймфрейма"""
        try:
            # Преобразование таймфрейма в формат Binance
            binance_timeframe = self.timeframe_mapping.get(timeframe)
            if not binance_timeframe:
                raise ValueError(f"Неизвестный таймфрейм: {timeframe}")

            ohlcv = await asyncio.get_event_loop().run_in_executor(
                None,
                self.exchange.fetch_ohlcv,
                symbol,
                binance_timeframe,
                None,
                limit
            )

            df = pd.DataFrame(ohlcv, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume'
            ])

            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)

            # Переименование колонок для соответствия формату
            df.columns = ['open', 'high', 'low', 'close', 'volume']

            return df

        except Exception as e:
            self.logger.error(f"Ошибка при получении данных для {timeframe}: {e}")
            raise

    async def analyze_timeframes(self, symbol: str) -> Dict[str, Any]:
        """Иерархический анализ всех таймфреймов"""
        timeframes = self.config['timeframes']
        results = {}

        # Сортировка таймфреймов по приоритету (от высшего к низшему)
        sorted_timeframes = sorted(
            timeframes.items(),
            key=lambda x: x[1]['priority']
        )

        for timeframe, tf_config in sorted_timeframes:
            try:
                self.logger.info(f"Анализ таймфрейма {timeframe}")

                # Получение данных
                data = await self.fetch_data(symbol, timeframe)

                # Анализ структуры рынка
                structure = self._analyze_market_structure(data)

                # Определение тренда
                trend = self._determine_trend(data)

                # Расчет ключевых уровней
                levels = self._calculate_key_levels(data)

                # Анализ объема
                volume_analysis = self._analyze_volume(data)

                results[timeframe] = {
                    'weight': tf_config['weight'],
                    'trend': trend,
                    'structure': structure,
                    'levels': levels,
                    'volume': volume_analysis,
                    'data': data
                }

            except Exception as e:
                self.logger.error(f"Ошибка анализа таймфрейма {timeframe}: {e}")
                results[timeframe] = None

        return results

    def _analyze_market_structure(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Анализ структуры рынка"""
        close = data['close']

        # Определение структуры через swing highs/lows
        period = 5
        highs = []
        lows = []

        for i in range(period, len(close) - period):
            if all(close.iloc[i] >= close.iloc[i-j] for j in range(1, period+1)) and \
               all(close.iloc[i] >= close.iloc[i+j] for j in range(1, period+1)):
                highs.append((i, close.iloc[i]))

            if all(close.iloc[i] <= close.iloc[i-j] for j in range(1, period+1)) and \
               all(close.iloc[i] <= close.iloc[i+j] for j in range(1, period+1)):
                lows.append((i, close.iloc[i]))

        # Определение структуры
        structure = "ranging"  # По умолчанию
        if len(highs) >= 2 and len(lows) >= 2:
            # Проверка на восходящий тренд
            if all(highs[i][1] > highs[i-1][1] for i in range(1, len(highs))) and \
               all(lows[i][1] > lows[i-1][1] for i in range(1, len(lows))):
                structure = "uptrend"
            # Проверка на нисходящий тренд
            elif all(highs[i][1] < highs[i-1][1] for i in range(1, len(highs))) and \
                 all(lows[i][1] < lows[i-1][1] for i in range(1, len(lows))):
                structure = "downtrend"

        return {
            'type': structure,
            'swing_highs': highs,
            'swing_lows': lows
        }

    def _determine_trend(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Определение направления тренда"""
        close = data['close']

        # Использование нескольких методов для определения тренда
        ema_20 = close.ewm(span=20, adjust=False).mean()
        ema_50 = close.ewm(span=50, adjust=False).mean()

        # Тренд на основе EMA
        if ema_20.iloc[-1] > ema_50.iloc[-1] and close.iloc[-1] > ema_20.iloc[-1]:
            ema_trend = "bullish"
        elif ema_20.iloc[-1] < ema_50.iloc[-1] and close.iloc[-1] < ema_20.iloc[-1]:
            ema_trend = "bearish"
        else:
            ema_trend = "neutral"

        # Тренд на основе наклона
        slope_20 = (ema_20.iloc[-1] - ema_20.iloc[-10]) / 10
        slope_50 = (ema_50.iloc[-1] - ema_50.iloc[-10]) / 10

        trend_strength = abs(slope_20) + abs(slope_50)

        return {
            'direction': ema_trend,
            'strength': trend_strength,
            'slope_20': slope_20,
            'slope_50': slope_50
        }

    def _calculate_key_levels(self, data: pd.DataFrame) -> Dict[str, List[float]]:
        """Расчет ключевых уровней поддержки и сопротивления"""
        high = data['high']
        low = data['low']
        close = data['close']

        # Уровни сопротивления (предыдущие максимумы)
        resistance_levels = []
        for i in range(1, len(high) - 1):
            if high.iloc[i] > high.iloc[i-1] and high.iloc[i] > high.iloc[i+1]:
                resistance_levels.append(high.iloc[i])

        # Уровни поддержки (предыдущие минимумы)
        support_levels = []
        for i in range(1, len(low) - 1):
            if low.iloc[i] < low.iloc[i-1] and low.iloc[i] < low.iloc[i+1]:
                support_levels.append(low.iloc[i])

        # Фибоначчи уровни
        recent_high = high.tail(50).max()
        recent_low = low.tail(50).min()
        fib_levels = [
            recent_high,
            recent_high - 0.236 * (recent_high - recent_low),
            recent_high - 0.382 * (recent_high - recent_low),
            recent_high - 0.5 * (recent_high - recent_low),
            recent_high - 0.618 * (recent_high - recent_low),
            recent_high - 0.786 * (recent_high - recent_low),
            recent_low
        ]

        return {
            'support': support_levels[-5:],  # Последние 5 уровней
            'resistance': resistance_levels[-5:],
            'fibonacci': fib_levels
        }

    def _analyze_volume(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Анализ объема торгов"""
        volume = data['volume']
        close = data['close']

        # Скользящая средняя объема
        volume_ma = volume.rolling(window=20).mean()

        # Относительный объем
        relative_volume = volume.iloc[-1] / volume_ma.iloc[-1]

        # Анализ объема при движении цены
        price_change = close.pct_change()
        volume_price_trend = (price_change * volume).rolling(window=5).sum()

        return {
            'current_volume': volume.iloc[-1],
            'volume_ma': volume_ma.iloc[-1],
            'relative_volume': relative_volume,
            'volume_price_trend': volume_price_trend.iloc[-1],
            'volume_spike': relative_volume > 1.5
        }
