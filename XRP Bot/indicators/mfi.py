import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from typing import Dict, Any

class MFIIndicator(BaseIndicator):
    """Индикатор Money Flow Index (MFI)"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет MFI"""
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
            
        period = self.config.get('period', 14)
        
        high = data['high']
        low = data['low']
        close = data['close']
        volume = data['volume']
        
        # Типичная цена
        typical_price = (high + low + close) / 3
        
        # Money Flow
        money_flow = typical_price * volume
        
        # Positive и Negative Money Flow
        positive_flow = pd.Series(0, index=data.index)
        negative_flow = pd.Series(0, index=data.index)
        
        for i in range(1, len(typical_price)):
            if typical_price.iloc[i] > typical_price.iloc[i-1]:
                positive_flow.iloc[i] = money_flow.iloc[i]
            elif typical_price.iloc[i] < typical_price.iloc[i-1]:
                negative_flow.iloc[i] = money_flow.iloc[i]
        
        # Money Flow Ratio
        positive_mf = positive_flow.rolling(window=period).sum()
        negative_mf = negative_flow.rolling(window=period).sum()
        
        money_ratio = positive_mf / negative_mf
        mfi = 100 - (100 / (1 + money_ratio))
        
        return {
            'mfi': mfi.iloc[-1],
            'values': mfi.tolist()
        }
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация сигнала на основе MFI"""
        mfi_data = self.calculate(data)
        mfi_value = mfi_data['mfi']
        
        overbought = self.config.get('overbought', 80)
        oversold = self.config.get('oversold', 20)
        
        if mfi_value > overbought:
            return "SHORT"
        elif mfi_value < oversold:
            return "LONG"
        else:
            return "NEUTRAL"
