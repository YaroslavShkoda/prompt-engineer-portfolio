import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from typing import Dict, Any

class MACDIndicator(BaseIndicator):
    """Индикатор Moving Average Convergence Divergence (MACD)"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет MACD"""
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
            
        fast_period = self.config.get('fast_period', 12)
        slow_period = self.config.get('slow_period', 26)
        signal_period = self.config.get('signal_period', 9)
        
        close = data['close']
        
        # Расчет EMA
        ema_fast = close.ewm(span=fast_period, adjust=False).mean()
        ema_slow = close.ewm(span=slow_period, adjust=False).mean()
        
        # MACD линия и сигнальная линия
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return {
            'macd_line': macd_line.iloc[-1],
            'signal_line': signal_line.iloc[-1],
            'histogram': histogram.iloc[-1],
            'macd_values': macd_line.tolist(),
            'signal_values': signal_line.tolist(),
            'histogram_values': histogram.tolist()
        }
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация сигнала на основе MACD"""
        macd_data = self.calculate(data)
        
        macd_current = macd_data['macd_line']
        signal_current = macd_data['signal_line']
        
        # Проверка пересечения
        macd_prev = macd_data['macd_values'][-2]
        signal_prev = macd_data['signal_values'][-2]
        
        if macd_current > signal_current and macd_prev <= signal_prev:
            return "LONG"
        elif macd_current < signal_current and macd_prev >= signal_prev:
            return "SHORT"
        else:
            return "NEUTRAL"
