import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from typing import Dict, Any

class OBVIndicator(BaseIndicator):
    """Индикатор On-Balance Volume (OBV)"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет OBV"""
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
        
        close = data['close']
        volume = data['volume']
        
        # Расчет OBV
        price_change = close.diff()
        volume_direction = np.where(price_change > 0, volume,
                                   np.where(price_change < 0, -volume, 0))
        
        obv = pd.Series(volume_direction).cumsum()
        
        return {
            'obv': obv.iloc[-1],
            'values': obv.tolist()
        }
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация сигнала на основе OBV"""
        obv_data = self.calculate(data)
        obv_values = obv_data['values']
        
        # Проверка дивергенции между ценой и OBV
        close = data['close']
        obv_trend = obv_values[-1] - obv_values[-10]  # Тренд за последние 10 периодов
        price_trend = close.iloc[-1] - close.iloc[-10]
        
        if obv_trend > 0 and price_trend <= 0:
            return "LONG"  # Бычья дивергенция
        elif obv_trend < 0 and price_trend >= 0:
            return "SHORT"  # Медвежья дивергенция
        else:
            return "NEUTRAL"
