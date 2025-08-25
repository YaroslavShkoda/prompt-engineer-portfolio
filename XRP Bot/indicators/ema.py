import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from typing import Dict, Any

class EMAIndicator(BaseIndicator):
    """Индикатор Exponential Moving Average (EMA)"""
    
    def __init__(self, config: Dict[str, Any], timeframe: str, period: int = 20):
        super().__init__(config, timeframe)
        self.period = period
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет EMA"""
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
            
        close = data['close']
        ema = close.ewm(span=self.period, adjust=False).mean()
        
        return {
            'ema': ema.iloc[-1],
            'values': ema.tolist()
        }
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация сигнала на основе EMA"""
        ema_data = self.calculate(data)
        ema_value = ema_data['ema']
        current_price = data['close'].iloc[-1]
        
        if current_price > ema_value:
            return "LONG"
        elif current_price < ema_value:
            return "SHORT"
        else:
            return "NEUTRAL"
