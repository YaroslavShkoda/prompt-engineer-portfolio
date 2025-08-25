import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from typing import Dict, Any

class WilliamsRIndicator(BaseIndicator):
    """Индикатор Williams %R"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет Williams %R"""
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
            
        period = self.config.get('period', 14)
        
        high = data['high']
        low = data['low']
        close = data['close']
        
        highest_high = high.rolling(window=period).max()
        lowest_low = low.rolling(window=period).min()
        
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        
        return {
            'williams_r': williams_r.iloc[-1],
            'values': williams_r.tolist()
        }
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация сигнала на основе Williams %R"""
        wr_data = self.calculate(data)
        wr_value = wr_data['williams_r']
        
        overbought = self.config.get('overbought', -20)
        oversold = self.config.get('oversold', -80)
        
        if wr_value > overbought:
            return "SHORT"
        elif wr_value < oversold:
            return "LONG"
        else:
            return "NEUTRAL"
