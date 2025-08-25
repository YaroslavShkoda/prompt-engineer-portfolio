import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
import logging

class BaseIndicator(ABC):
    """Базовый абстрактный класс для всех технических индикаторов"""
    
    def __init__(self, config: Dict[str, Any], timeframe: str):
        self.config = config
        self.timeframe = timeframe
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Расчет значения индикатора"""
        pass
    
    @abstractmethod
    def generate_signal(self, data: pd.DataFrame) -> str:
        """Генерация торгового сигнала на основе индикатора"""
        pass
    
    def validate_data(self, data: pd.DataFrame) -> bool:
        """Проверка корректности данных"""
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        return all(col in data.columns for col in required_columns)
    
    def get_name(self) -> str:
        """Возвращает название индикатора"""
        return self.__class__.__name__.lower().replace('indicator', '')
