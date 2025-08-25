import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from typing import Dict, Any

class ParabolicSARIndicator(BaseIndicator):
    """Индикатор Parabolic SAR"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет Parabolic SAR"""
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
            
        start = self.config.get('start', 0.02)
        increment = self.config.get('increment', 0.02)
        max_acc = self.config.get('max', 0.2)
        
        high = data['high']
        low = data['low']
        close = data['close']
        
        # Инициализация
        sar = pd.Series(index=data.index)
        ep = pd.Series(index=data.index)
        acc = pd.Series(index=data.index)
        
        # Первые значения
        sar.iloc[0] = low.iloc[0]
        ep.iloc[0] = high.iloc[0]
        acc.iloc[0] = start
        
        # Расчет Parabolic SAR
        for i in range(1, len(data)):
            if i == 1:
                sar.iloc[i] = sar.iloc[0]
                ep.iloc[i] = high.iloc[i] if close.iloc[i] > close.iloc[i-1] else low.iloc[i]
                acc.iloc[i] = start
            else:
                prev_sar = sar.iloc[i-1]
                prev_ep = ep.iloc[i-1]
                prev_acc = acc.iloc[i-1]
                
                # Обновление SAR
                sar.iloc[i] = prev_sar + prev_acc * (prev_ep - prev_sar)
                
                # Определение направления тренда
                uptrend = close.iloc[i] > close.iloc[i-1]
                
                if uptrend:
                    ep.iloc[i] = max(prev_ep, high.iloc[i])
                    if ep.iloc[i] > prev_ep:
                        acc.iloc[i] = min(prev_acc + increment, max_acc)
                    else:
                        acc.iloc[i] = prev_acc
                else:
                    ep.iloc[i] = min(prev_ep, low.iloc[i])
                    if ep.iloc[i] < prev_ep:
                        acc.iloc[i] = min(prev_acc + increment, max_acc)
                    else:
                        acc.iloc[i] = prev_acc
        
        return {
            'sar': sar.iloc[-1],
            'values': sar.tolist()
        }
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация сигнала на основе Parabolic SAR"""
        sar_data = self.calculate(data)
        sar_value = sar_data['sar']
        current_price = data['close'].iloc[-1]
        
        if current_price > sar_value:
            return "LONG"
        elif current_price < sar_value:
            return "SHORT"
        else:
            return "NEUTRAL"
