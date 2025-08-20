"""
Тесты для technical_analyzer.py
"""
from src.technical_analyzer import analyze_ticker


def test_analyze_ticker():
    result = analyze_ticker("SBER")
    assert isinstance(result, dict)
    assert len(result) == 4  # 15m, 1h, 4h, 1d
    for tf, (buy, sell, signal) in result.items():
        assert isinstance(buy, int)
        assert isinstance(sell, int)
        assert isinstance(signal, str)
        assert 0 <= buy <= 16
        assert 0 <= sell <= 16
