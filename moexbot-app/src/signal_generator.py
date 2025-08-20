"""
Генерация сигналов по консенсусу.
"""
from typing import Dict
import logging

__version__ = "1.0.0"


def generate_signal(analysis: Dict[str, Dict], prices: Dict[str, float]) -> str:
    """
    Генерация сигнала в формате ТЗ.
    """
    logger = logging.getLogger("MOEXbot")
    output = []

    output.append(f"\n{'='*60}")
    output.append("          СТОИМОСТЬ АКТИВОВ")
    output.append("")
    for s, p in prices.items():
        output.append(f"{s}: {p:,.2f} руб.")
    output.append("")
    output.append("="*60)

    output.append("     ПОКАЗАНИЯ ИНДИКАТОРОВ И ИХ АНАЛИЗ")
    output.append("")

    has_signal = False
    for i, (s, data) in enumerate(analysis.items(), 1):
        output.append(f"📊 ТОП-{i}: {s}")
        for tf, (b, s_val, sig) in data.items():
            output.append(f"  • {tf}: {b}/16 BUY, {s_val}/16 SELL → {sig}")
        output.append("  ──────────────────────────────")
        output.append(f"  {sig}")
        output.append("")

        if not has_signal and all(b >= 13 for b, _, _ in data.values()):
            entry = prices[s]
            sl = round(entry * 0.98, 2)
            tp = round(entry * 1.05, 2)
            output.append("="*60)
            output.append("   ИНФОРМАЦИЯ О НАЙДЕННОМ СИГНАЛЕ")
            output.append("")
            output.append(f"✅ СИГНАЛ ПОКУПКИ: {s}")
            output.append(f"Цена входа: {entry:,.2f} руб.")
            output.append(f"Стоп-лосс: {sl:,.2f} руб.")
            output.append(f"Тейк-профит: {tp:,.2f} руб.")
            output.append("="*60)
            has_signal = True

    if not has_signal:
        output.append("="*60)
        output.append("   ИНФОРМАЦИЯ О НАЙДЕННОМ СИГНАЛЕ")
        output.append("")
        output.append("❌ Нет сигналов с уверенностью ≥13/16 на всех таймфреймах.")
        output.append("="*60)

    result = "\n".join(output)
    logger.info("Сигнал сгенерирован.")
    return result
