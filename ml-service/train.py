"""python train.py — обучение и сохранение моделей."""
from collections import Counter

import pandas as pd

from model import TicketClassifier, DATA_PATH, TARGETS


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    print(f"Загружено {len(df)} примеров")

    # Диагностика: сколько примеров на каждый класс в каждом таргете
    for t in TARGETS:
        print(f"\n[{t}] распределение:")
        for cls, n in sorted(Counter(df[t]).items(), key=lambda x: -x[1]):
            print(f"  {cls:20s}: {n}")

    # Пустые тексты недопустимы
    df = df.dropna(subset=["text"])
    df["text"] = df["text"].astype(str).str.strip()
    df = df[df["text"].str.len() > 0]
    print(f"\nПосле очистки: {len(df)} примеров")

    clf = TicketClassifier()
    metrics = clf.fit(df)
    clf.save()

    print("\n=== Итог ===")
    for k, v in metrics.items():
        print(f"{k:15s}: {v:.3f}")


if __name__ == "__main__":
    main()