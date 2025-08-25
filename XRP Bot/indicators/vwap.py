import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from typing import Dict, Any

class VWAPIndicator(BaseIndicator):
    """Индикатор Volume Weighted Average Price (VWAP)"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет VWAP"""
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
        
        # Проверяем, есть ли столбец объема
        if 'volume' not in data.columns:
            raise ValueError("Volume data required for VWAP calculation")
            
        high = data['high']
        low = data['low']
        close = data['close']
        volume = data['volume']
        
        # Типичная цена
        typical_price = (high + low + close) / 3
        
        # VWAP
        cumulative_tp_vol = (typical_price * volume).cumsum()
        cumulative_vol = volume.cumsum()
        vwap = cumulative_tp_vol / cumulative_vol
        
        return {
            'vwap': vwap.iloc[-1],
            'values': vwap.tolist()
        }
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация сигнала на основе VWAP"""
        vwap_data = self.calculate(data)
        vwap_value = vwap_data['vwap']
        current_price = data['close'].iloc[-1]
        
        if current_price > vwap_value * 1.01:  # 1% выше VWAP
            return "LONG"
        elif current_price < vwap_value * 0.99:  # 1% ниже VWAP
            return "SHORT"
        else:
            return "NEUTRAL"
