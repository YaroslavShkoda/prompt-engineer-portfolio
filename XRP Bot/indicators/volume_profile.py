import pandas as pd
import numpy as np
from .base_indicator import BaseIndicator
from typing import Dict, Any, List, Tuple

class VolumeProfileIndicator(BaseIndicator):
    """Индикатор Volume Profile"""
    
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет Volume Profile"""
        if not self.validate_data(data):
            raise ValueError("Invalid data format")
            
        num_bins = self.config.get('num_bins', 20)
        
        close = data['close']
        volume = data['volume']
        
        # Создание bins для цен
        price_min = close.min()
        price_max = close.max()
        price_range = price_max - price_min
        
        bins = np.linspace(price_min, price_max, num_bins + 1)
        
        # Распределение объема по bins
        volume_profile = np.zeros(num_bins)
        
        for i in range(len(close)):
            price = close.iloc[i]
            vol = volume.iloc[i]
            
            # Определение bin для текущей цены
            bin_idx = np.digitize(price, bins) - 1
            bin_idx = max(0, min(bin_idx, num_bins - 1))
            
            volume_profile[bin_idx] += vol
        
        # Нахождение контрольной точки (Point of Control)
        poc_index = np.argmax(volume_profile)
        poc_price = bins[poc_index] + (bins[poc_index + 1] - bins[poc_index]) / 2
        
        # Нахождение зон поддержки и сопротивления
        high_volume_nodes = []
        for i, vol in enumerate(volume_profile):
            if vol > np.mean(volume_profile):
                node_price = bins[i] + (bins[i + 1] - bins[i]) / 2
                high_volume_nodes.append((node_price, vol))
        
        high_volume_nodes.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'poc': poc_price,
            'volume_profile': volume_profile.tolist(),
            'bins': bins.tolist(),
            'high_volume_nodes': high_volume_nodes[:5]  # Топ-5 узлов
        }
    
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация сигнала на основе Volume Profile"""
        vp_data = self.calculate(data)
        current_price = data['close'].iloc[-1]
        poc = vp_data['poc']
        
        # Определение зон поддержки и сопротивления
        high_volume_nodes = vp_data['high_volume_nodes']
        
        if not high_volume_nodes:
            return "NEUTRAL"
        
        # Проверка, находится ли цена выше или ниже POC
        if current_price > poc * 1.01:
            return "LONG"
        elif current_price < poc * 0.99:
            return "SHORT"
        else:
            return "NEUTRAL"
