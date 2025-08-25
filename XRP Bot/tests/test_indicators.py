import pytest
import pandas as pd
import numpy as np
import sys
import os

# Добавление пути для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from indicators.rsi import RSIIndicator
from indicators.macd import MACDIndicator
from indicators.ema import EMAIndicator
from indicators.bollinger_bands import BollingerBandsIndicator
from indicators.stochastic import StochasticIndicator

class TestIndicators:
    """Тесты для индикаторов"""
    
    @pytest.fixture
    def sample_data(self):
        """Создание тестовых данных"""
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=100, freq='1H')
        
        # Генерация данных с трендом
        trend = np.linspace(100, 110, 100)
        noise = np.random.normal(0, 2, 100)
        close = trend + noise
        
        data = pd.DataFrame({
            'timestamp': dates,
            'open': close - np.random.uniform(0.5, 2, 100),
            'high': close + np.random.uniform(0.5, 2, 100),
            'low': close - np.random.uniform(0.5, 2, 100),
            'close': close,
            'volume': np.random.uniform(1000, 5000, 100)
        })
        
        data.set_index('timestamp', inplace=True)
        return data
    
    def test_rsi_calculation(self, sample_data):
        """Тест расчета RSI"""
        config = {'period': 14, 'overbought': 70, 'oversold': 30}
        rsi_indicator = RSIIndicator(config, '1H')
        
        result = rsi_indicator.calculate(sample_data)
        
        assert 'rsi' in result
        assert 0 <= result['rsi'] <= 100
        assert isinstance(result['values'], list)
        assert len(result['values']) == len(sample_data)
    
    def test_macd_calculation(self, sample_data):
        """Тест расчета MACD"""
        config = {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        }
        macd_indicator = MACDIndicator(config, '1H')
        
        result = macd_indicator.calculate(sample_data)
        
        assert 'macd_line' in result
        assert 'signal_line' in result
        assert 'histogram' in result
        assert isinstance(result['macd_values'], list)
    
    def test_ema_calculation(self, sample_data):
        """Тест расчета EMA"""
        config = {'period': 20}
        ema_indicator = EMAIndicator(config, '1H', 20)
        
        result = ema_indicator.calculate(sample_data)
        
        assert 'ema' in result
        assert isinstance(result['ema'], (int, float))
        assert len(result['values']) == len(sample_data)
    
    def test_bollinger_bands(self, sample_data):
        """Тест Bollinger Bands"""
        config = {'period': 20, 'std_dev': 2}
        bb_indicator = BollingerBandsIndicator(config, '1H')
        
        result = bb_indicator.calculate(sample_data)
        
        assert 'upper_band' in result
        assert 'middle_band' in result
        assert 'lower_band' in result
        assert result['upper_band'] > result['middle_band'] > result['lower_band']
    
    def test_stochastic_calculation(self, sample_data):
        """Тест Stochastic Oscillator"""
        config = {
            'k_period': 14,
            'd_period': 3,
            'smooth_k': 3,
            'overbought': 80,
            'oversold': 20
        }
        stoch_indicator = StochasticIndicator(config, '1H')
        
        result = stoch_indicator.calculate(sample_data)
        
        assert 'k_percent' in result
        assert 'd_percent' in result
        assert 0 <= result['k_percent'] <= 100
        assert 0 <= result['d_percent'] <= 100
    
    def test_signal_generation(self, sample_data):
        """Тест генерации сигналов"""
        config = {'period': 14, 'overbought': 70, 'oversold': 30}
        rsi_indicator = RSIIndicator(config, '1H')
        
        signal = rsi_indicator.generate_signal(sample_data)
        
        assert signal in ['LONG', 'SHORT', 'NEUTRAL']
    
    def test_data_validation(self, sample_data):
        """Тест валидации данных"""
        config = {'period': 14}
        rsi_indicator = RSIIndicator(config, '1H')
        
        # Правильные данные
        assert rsi_indicator.validate_data(sample_data) == True
        
        # Неправильные данные
        invalid_data = pd.DataFrame({'price': [1, 2, 3]})
        assert rsi_indicator.validate_data(invalid_data) == False

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
