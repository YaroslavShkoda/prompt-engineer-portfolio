import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from typing import Dict, Any

class ATRIndicator(BaseIndicator):
    """Индикатор Average True Range (ATR)"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет ATR"""
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
            
        period = self.config.get('period', 14)
        
        high = data['high']
        low = data['low']
        close = data['close']
        
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # ATR
        atr = true_range.rolling(window=period).mean()
        
        return {
            'atr': atr.iloc[-1],
            'values': atr.tolist()
        }
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация сигнала на основе ATR"""
        atr_data = self.calculate(data)
        atr_value = atr_data['atr']
        current_price = data['close'].iloc[-1]
        
        # ATR используется для определения волатильности
        # Более высокий ATR означает больше волатильности
        atr_ratio = atr_value / current_price
        
        if atr_ratio > 0.02:  # Высокая волатильность
            return "LONG"  # Возможность для трендовой торговли
        elif atr_ratio < 0.005:  # Низкая волатильность
            return "SHORT"  # Возможный выход из позиции
        else:
            return "NEUTRAL"
