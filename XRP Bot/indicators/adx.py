import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from typing import Dict, Any

class ADXIndicator(BaseIndicator):
    """Индикатор Average Directional Index (ADX)"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет ADX"""
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
            
        period = self.config.get('period', 14)
        
        high = data['high']
        low = data['low']
        close = data['close']
        
        # Расчет True Range
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Расчет Directional Movement
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
        
        # Сглаживание
        atr = true_range.rolling(window=period).mean()
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # Расчет ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return {
            'adx': adx.iloc[-1],
            'plus_di': plus_di.iloc[-1],
            'minus_di': minus_di.iloc[-1],
            'adx_values': adx.tolist(),
            'plus_di_values': plus_di.tolist(),
            'minus_di_values': minus_di.tolist()
        }
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация сигнала на основе ADX"""
        adx_data = self.calculate(data)
        adx_value = adx_data['adx']
        plus_di = adx_data['plus_di']
        minus_di = adx_data['minus_di']
        
        threshold = self.config.get('threshold', 25)
        
        if adx_value > threshold:
            if plus_di > minus_di:
                return "LONG"
            else:
                return "SHORT"
        else:
            return "NEUTRAL"
