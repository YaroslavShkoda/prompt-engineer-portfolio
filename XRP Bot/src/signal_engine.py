import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import asyncio
import os
import sys

# Добавление путей для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indicators.rsi import RSIIndicator
from indicators.macd import MACDIndicator
from indicators.ema import EMAIndicator
from indicators.bollinger_bands import BollingerBandsIndicator
from indicators.stochastic import StochasticIndicator
from indicators.adx import ADXIndicator
from indicators.ichimoku import IchimokuIndicator
from indicators.atr import ATRIndicator
from indicators.vwap import VWAPIndicator
from indicators.obv import OBVIndicator
from indicators.mfi import MFIIndicator
from indicators.williams_r import WilliamsRIndicator
from indicators.parabolic_sar import ParabolicSARIndicator
from indicators.cci import CCIIndicator
from indicators.keltner_channels import KeltnerChannelsIndicator
from indicators.volume_profile import VolumeProfileIndicator
from src.timeframe_analyzer import TimeframeAnalyzer

class SignalEngine:
    """Движок генерации торговых сигналов"""

    def __init__(self, config_path: str = "config/strategy_config.json"):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config(config_path)
        self.timeframe_analyzer = TimeframeAnalyzer(self.config)

        # Инициализация индикаторов
        self.indicators = {}
        self._initialize_indicators()

        # Параметры стратегии
        self.signal_threshold = self.config['signal_threshold']
        self.symbol = self.config['bot']['symbol']

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Загрузка конфигурации"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Конфигурационный файл не найден: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Ошибка парсинга JSON: {e}")

    def _initialize_indicators(self):
        """Инициализация всех индикаторов"""
        indicators_config = self.config['indicators']
        timeframes = self.config['timeframes']

        indicator_classes = {
            'rsi': RSIIndicator,
            'macd': MACDIndicator,
            'ema_20': lambda config, tf: EMAIndicator(config, tf, 20),
            'ema_50': lambda config, tf: EMAIndicator(config, tf, 50),
            'ema_200': lambda config, tf: EMAIndicator(config, tf, 200),
            'bollinger_bands': BollingerBandsIndicator,
            'stochastic': StochasticIndicator,
            'adx': ADXIndicator,
            'ichimoku': IchimokuIndicator,
            'atr': ATRIndicator,
            'vwap': VWAPIndicator,
            'obv': OBVIndicator,
            'mfi': MFIIndicator,
            'williams_r': WilliamsRIndicator,
            'parabolic_sar': ParabolicSARIndicator,
            'cci': CCIIndicator,
            'keltner_channels': KeltnerChannelsIndicator,
            'volume_profile': VolumeProfileIndicator
        }

        for timeframe in timeframes:
            self.indicators[timeframe] = {}
            for indicator_name, indicator_class in indicator_classes.items():
                if indicator_name in indicators_config and indicators_config[indicator_name]['enabled']:
                    if timeframe in indicators_config[indicator_name]['timeframes']:
                        self.indicators[timeframe][indicator_name] = indicator_class(
                            indicators_config[indicator_name],
                            timeframe
                        )

    async def analyze_all_timeframes(self) -> Dict[str, Any]:
        """Анализ всех таймфреймов и генерация сигналов"""
        self.logger.info("Начало иерархического анализа таймфреймов")

        # Получение данных для всех таймфреймов
        timeframe_data = await self.timeframe_analyzer.analyze_timeframes(self.symbol)

        # Анализ индикаторов для каждого таймфрейма
        timeframe_signals = {}

        for timeframe, tf_data in timeframe_data.items():
            if tf_data is None:
                continue

            self.logger.info(f"Анализ индикаторов для таймфрейма {timeframe}")
            # Получение сигналов от индикаторов
            indicator_signals = await self._get_indicator_signals(
                timeframe,
                tf_data['data']
            )

            # Взвешенный анализ сигналов
            weighted_signal = self._calculate_weighted_signal(
                indicator_signals,
                timeframe
            )

            timeframe_signals[timeframe] = {
                'weight': tf_data['weight'],
                'trend': tf_data['trend'],
                'structure': tf_data['structure'],
                'levels': tf_data['levels'],
                'volume': tf_data['volume'],
                'indicator_signals': indicator_signals,
                'weighted_signal': weighted_signal,
                'current_price': float(tf_data['data']['close'].iloc[-1])
            }

        # Объединение сигналов с учетом иерархии
        final_signal = self._generate_final_signal(timeframe_signals)

        return {
            'timestamp': datetime.now().isoformat(),
            'symbol': self.symbol,
            'current_price': timeframe_signals.get('15m', {}).get('current_price') or
                           timeframe_signals.get('1H', {}).get('current_price') or
                           timeframe_signals.get('4H', {}).get('current_price') or
                           timeframe_signals.get('1D', {}).get('current_price'),
            'timeframe_signals': timeframe_signals,
            'final_signal': final_signal
        }

    async def _get_indicator_signals(self, timeframe: str, data: pd.DataFrame) -> Dict[str, str]:
        """Получение сигналов от всех индикаторов для таймфрейма"""
        signals = {}

        if timeframe not in self.indicators:
            return signals

        for indicator_name, indicator in self.indicators[timeframe].items():
            try:
                signal = indicator.generate_signal(data)
                signals[indicator_name] = signal
                self.logger.debug(f"{timeframe} - {indicator_name}: {signal}")
            except Exception as e:
                self.logger.error(f"Ошибка в {indicator_name} для {timeframe}: {e}")
                signals[indicator_name] = "NEUTRAL"

        return signals

    def _calculate_weighted_signal(self, indicator_signals: Dict[str, str], timeframe: str) -> Dict[str, Any]:
        """Расчет взвешенного сигнала для таймфрейма"""
        long_count = sum(1 for signal in indicator_signals.values() if signal == "LONG")
        short_count = sum(1 for signal in indicator_signals.values() if signal == "SHORT")
        total_indicators = len(indicator_signals)
        long_percentage = (long_count / total_indicators) * 100
        short_percentage = (short_count / total_indicators) * 100

        # Определение преобладающего направления
        if long_percentage > 60:
            direction = "LONG"
            confidence = long_percentage
        elif short_percentage > 60:
            direction = "SHORT"
            confidence = short_percentage
        else:
            direction = "NEUTRAL"
            confidence = max(long_percentage, short_percentage)

        return {
            'direction': direction,
            'confidence': confidence,
            'long_count': long_count,
            'short_count': short_count,
            'total_indicators': total_indicators
        }

    def _generate_final_signal(self, timeframe_signals: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация финального сигнала на основе иерархического анализа"""
        total_weight = 0
        weighted_long_score = 0
        weighted_short_score = 0

        # Проход по таймфреймам в порядке приоритета
        for timeframe, signals in timeframe_signals.items():
            if signals is None:
                continue

            weight = signals['weight']
            weighted_signal = signals['weighted_signal']

            if weighted_signal['direction'] == "LONG":
                weighted_long_score += weight * weighted_signal['long_count']
            elif weighted_signal['direction'] == "SHORT":
                weighted_short_score += weight * weighted_signal['short_count']

            total_weight += weight

        # Подсчет взвешенного количества сигналов
        total_signals = weighted_long_score + weighted_short_score
        threshold = self.signal_threshold

        # Определение финального направления
        if total_signals >= threshold:
            if weighted_long_score > weighted_short_score * 1.2:
                final_direction = "LONG"
                confidence = (weighted_long_score / total_signals) * 100
            elif weighted_short_score > weighted_long_score * 1.2:
                final_direction = "SHORT"
                confidence = (weighted_short_score / total_signals) * 100
            else:
                final_direction = "NEUTRAL"
                confidence = 0
        else:
            final_direction = "NEUTRAL"
            confidence = 0

        return {
            'direction': final_direction,
            'confidence': confidence,
            'total_long_signals': weighted_long_score,
            'total_short_signals': weighted_short_score,
            'total_signals': total_signals,
            'threshold': threshold,
            'long_percentage': (weighted_long_score / total_signals) * 100 if total_signals > 0 else 0,
            'short_percentage': (weighted_short_score / total_signals) * 100 if total_signals > 0 else 0
        }

    def create_signal_report(self, analysis_result: Dict[str, Any]) -> str:
        """Создание подробного отчета о сигнале в стиле пользователя"""
        report = []
        report.append("=" * 60)
        report.append("          СТОИМОСТЬ МОНЕТ")
        report.append("")

        # Текущая цена
        current_price = analysis_result.get('current_price', 0)
        symbol = analysis_result['symbol'].replace('USDT', '')

        report.append(f"{symbol}: ${current_price:,.4f}")
        report.append("")
        report.append("=" * 60)

        # Показания индикаторов
        report.append("     ПОКАЗАНИЯ ИНДИКАТОРОВ И ИХ АНАЛИЗ")
        report.append("")

        # Единый блок по XRP
        report.append(f"📊 {symbol}:")
        
        # Сортировка таймфреймов: 1D, 4H, 1H, 15m
        ordered_timeframes = ['1D', '4H', '1H', '15m']
        
        for timeframe in ordered_timeframes:
            tf_data = analysis_result['timeframe_signals'].get(timeframe)
            if not tf_data:
                continue

            long = tf_data['weighted_signal']['long_count']
            short = tf_data['weighted_signal']['short_count']
            total = tf_data['weighted_signal']['total_indicators']

            # Определяем иконку и вывод
            if long > short and long >= 10:
                conclusion = "🟢 Вывод: Чёткий рост. Сигнал к покупке."
            elif short > long and short >= 10:
                conclusion = "🔴 Вывод: Чёткое падение. Сигнал к продаже."
            elif abs(long - short) < 3:
                conclusion = "⚪️ Вывод: Нет чёткого направления."
            else:
                conclusion = "🟡 Вывод: Слабый сигнал. Осторожно."

            report.append(f"  • {timeframe}: {long}/{total} BUY, {short}/{total} SELL")

        report.append("  ──────────────────────────────")
        report.append(f"  {conclusion}")
        report.append("")

        report.append("=" * 60)
        report.append("   ИНФОРМАЦИЯ О НАЙДЕННОМ СИГНАЛЕ")
        report.append("")

        final_signal = analysis_result['final_signal']
        if final_signal['confidence'] > 90:
            report.append(f"✅ Сигнал: {final_signal['direction']} с уверенностью {final_signal['confidence']:.1f}%")
        else:
            report.append("❌ Нет сигналов с уверенностью > 90%.")

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)

    async def run_continuous_analysis(self, interval_minutes: int = 15):
        """Запуск непрерывного анализа"""
        self.logger.info("Запуск непрерывного анализа сигналов")

        while True:
            try:
                # Анализ и генерация сигнала
                result = await self.analyze_all_timeframes()

                # Логирование результатов
                report = self.create_signal_report(result)
                self.logger.info(report)

                # Сохранение в файл
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"logs/signal_report_{timestamp}.json"

                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, 'w') as f:
                    json.dump(result, f, indent=2, default=str)

                # Ожидание следующего цикла
                await asyncio.sleep(interval_minutes * 60)

            except Exception as e:
                self.logger.error(f"Ошибка в цикле анализа: {e}")
                await asyncio.sleep(60)  # Пауза при ошибке
