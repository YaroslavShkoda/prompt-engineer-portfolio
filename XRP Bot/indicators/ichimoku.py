import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from typing import Dict, Any

class IchimokuIndicator(BaseIndicator):
    """Индикатор Ichimoku Cloud"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет Ichimoku"""
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
            
        tenkan_period = self.config.get('tenkan_period', 9)
        kijun_period = self.config.get('kijun_period', 26)
        senkou_b_period = self.config.get('senkou_b_period', 52)
        
        high = data['high']
        low = data['low']
        close = data['close']
        
        # Tenkan-sen (Conversion Line)
        tenkan_sen = (high.rolling(window=tenkan_period).max() + 
                      low.rolling(window=tenkan_period).min()) / 2
        
        # Kijun-sen (Base Line)
        kijun_sen = (high.rolling(window=kijun_period).max() + 
                     low.rolling(window=kijun_period).min()) / 2
        
        # Senkou Span A (Leading Span A)
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(kijun_period)
        
        # Senkou Span B (Leading Span B)
        senkou_span_b = ((high.rolling(window=senkou_b_period).max() + 
                          low.rolling(window=senkou_b_period).min()) / 2).shift(kijun_period)
        
        # Chikou Span (Lagging Span)
        chikou_span = close.shift(-kijun_period)
        
        return {
            'tenkan_sen': tenkan_sen.iloc[-1],
            'kijun_sen': kijun_sen.iloc[-1],
            'senkou_span_a': senkou_span_a.iloc[-1],
            'senkou_span_b': senkou_span_b.iloc[-1],
            'chikou_span': chikou_span.iloc[-1] if not pd.isna(chikou_span.iloc[-1]) else close.iloc[-1],
            'tenkan_values': tenkan_sen.tolist(),
            'kijun_values': kijun_sen.tolist(),
            'senkou_a_values': senkou_span_a.tolist(),
            'senkou_b_values': senkou_span_b.tolist()
        }
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация сигнала на основе Ichimoku"""
        ichimoku_data = self.calculate(data)
        current_price = data['close'].iloc[-1]
        
        tenkan = ichimoku_data['tenkan_sen']
        kijun = ichimoku_data['kijun_sen']
        senkou_a = ichimoku_data['senkou_span_a']
        senkou_b = ichimoku_data['senkou_span_b']
        
        # Сигналы на основе положения цены относительно облака
        if current_price > senkou_a and current_price > senkou_b:
            if tenkan > kijun:
                return "LONG"
        elif current_price < senkou_a and current_price < senkou_b:
            if tenkan < kijun:
                return "SHORT"
        
        return "NEUTRAL"
