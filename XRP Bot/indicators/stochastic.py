import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from typing import Dict, Any

class StochasticIndicator(BaseIndicator):
    """Индикатор Stochastic Oscillator"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет Stochastic"""
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
            
        k_period = self.config.get('k_period', 14)
        d_period = self.config.get('d_period', 3)
        smooth_k = self.config.get('smooth_k', 3)
        
        low_min = data['low'].rolling(window=k_period).min()
        high_max = data['high'].rolling(window=k_period).max()
        
        k_percent = 100 * ((data['close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=d_period).mean()
        
        return {
            'k_percent': k_percent.iloc[-1],
            'd_percent': d_percent.iloc[-1],
            'k_values': k_percent.tolist(),
            'd_values': d_percent.tolist()
        }
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация сигнала на основе Stochastic"""
        stoch_data = self.calculate(data)
        k_current = stoch_data['k_percent']
        
        overbought = self.config.get('overbought', 80)
        oversold = self.config.get('oversold', 20)
        
        if k_current > overbought:
            return "SHORT"
        elif k_current < oversold:
            return "LONG"
        else:
            return "NEUTRAL"
