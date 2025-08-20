"""
Тесты для data_parser.py
"""
import pytest
from src.data_parser import fetch_top10_tickers, fetch_latest_prices


def test_fetch_top10_tickers():
    tickers = fetch_top10_tickers()
    assert isinstance(tickers, list)
    assert len(tickers) == 10
    assert all(isinstance(t, str) for t in tickers)


def test_fetch_latest_prices():
    tickers = ["SBER", "GAZP"]
    prices = fetch_latest_prices(tickers)
    assert isinstance(prices, dict)
    assert len(prices) == 2
    assert "SBER" in prices
    assert isinstance(prices["SBER"], float)
