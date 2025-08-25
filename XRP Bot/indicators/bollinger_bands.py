import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from typing import Dict, Any

class BollingerBandsIndicator(BaseIndicator):
    """Индикатор Bollinger Bands"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет Bollinger Bands"""
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
            
        period = self.config.get('period', 20)
        std_dev = self.config.get('std_dev', 2)
        
        close = data['close']
        sma = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        middle_band = sma
        
        return {
            'upper_band': upper_band.iloc[-1],
            'middle_band': middle_band.iloc[-1],
            'lower_band': lower_band.iloc[-1],
            'upper_values': upper_band.tolist(),
            'middle_values': middle_band.tolist(),
            'lower_values': lower_band.tolist()
        }
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация сигнала на основе Bollinger Bands"""
        bb_data = self.calculate(data)
        current_price = data['close'].iloc[-1]
        
        upper_band = bb_data['upper_band']
        lower_band = bb_data['lower_band']
        
        if current_price > upper_band:
            return "SHORT"
        elif current_price < lower_band:
            return "LONG"
        else:
            return "NEUTRAL"
