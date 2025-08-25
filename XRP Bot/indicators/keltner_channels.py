import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from typing import Dict, Any

class KeltnerChannelsIndicator(BaseIndicator):
    """Индикатор Keltner Channels"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет Keltner Channels"""
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
            
        ema_period = self.config.get('ema_period', 20)
        atr_period = self.config.get('atr_period', 10)
        multiplier = self.config.get('multiplier', 2)
        
        high = data['high']
        low = data['low']
        close = data['close']
        
        # EMA
        ema = close.ewm(span=ema_period, adjust=False).mean()
        
        # ATR для Keltner Channels
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = true_range.rolling(window=atr_period).mean()
        
        # Keltner Channels
        upper_band = ema + (multiplier * atr)
        lower_band = ema - (multiplier * atr)
        
        return {
            'upper_band': upper_band.iloc[-1],
            'lower_band': lower_band.iloc[-1],
            'middle_line': ema.iloc[-1],
            'upper_values': upper_band.tolist(),
            'lower_values': lower_band.tolist(),
            'middle_values': ema.tolist()
        }
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация сигнала на основе Keltner Channels"""
        kc_data = self.calculate(data)
        current_price = data['close'].iloc[-1]
        
        upper_band = kc_data['upper_band']
        lower_band = kc_data['lower_band']
        
        if current_price > upper_band:
            return "SHORT"
        elif current_price < lower_band:
            return "LONG"
        else:
            return "NEUTRAL"
