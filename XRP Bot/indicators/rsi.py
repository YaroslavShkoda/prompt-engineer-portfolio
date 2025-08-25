import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from typing import Dict, Any

class RSIIndicator(BaseIndicator):
    """Индикатор Relative Strength Index (RSI)"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет RSI"""
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
            
        period = self.config.get('period', 14)
        close = data['close']
        
        # Расчет RSI
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return {
            'rsi': rsi.iloc[-1],
            'values': rsi.tolist()
        }
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация сигнала на основе RSI"""
        rsi_data = self.calculate(data)
        rsi_value = rsi_data['rsi']
        
        overbought = self.config.get('overbought', 70)
        oversold = self.config.get('oversold', 30)
        
        if rsi_value > overbought:
            return "SHORT"
        elif rsi_value < oversold:
            return "LONG"
        else:
            return "NEUTRAL"
