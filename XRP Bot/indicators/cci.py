import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from typing import Dict, Any

class CCIIndicator(BaseIndicator):
    """Индикатор Commodity Channel Index (CCI)"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет CCI"""
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
            
        period = self.config.get('period', 20)
        
        high = data['high']
        low = data['low']
        close = data['close']
        
        # Типичная цена
        typical_price = (high + low + close) / 3
        
        # Moving average of typical price
        tp_sma = typical_price.rolling(window=period).mean()
        
        # Mean deviation
        mean_dev = typical_price.rolling(window=period).apply(
            lambda x: np.mean(np.abs(x - np.mean(x)))
        )
        
        # CCI
        cci = (typical_price - tp_sma) / (0.015 * mean_dev)
        
        return {
            'cci': cci.iloc[-1],
            'values': cci.tolist()
        }
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация сигнала на основе CCI"""
        cci_data = self.calculate(data)
        cci_value = cci_data['cci']
        
        overbought = self.config.get('overbought', 100)
        oversold = self.config.get('oversold', -100)
        
        if cci_value > overbought:
            return "SHORT"
        elif cci_value < oversold:
            return "LONG"
        else:
            return "NEUTRAL"
