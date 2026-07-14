"""관측소별 표층수온 집계.

각 관측소(강릉(bgna3) 등)별로 표층수온 전체 평균 + 월별 평균을 산출.
출력: data/processed/sst_stations.json  (지도 표시용, 좌표는 별도 매핑 필요)
"""
from __future__ import annotations

import io
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = Path(r"C:\Users\RYU\Downloads\Sea of korea degree")
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

SEA = {"es": "동해", "ss": "남해", "ys": "서해"}
MONTH_RE = re.compile(r"(\d{1,2})\s*월")


def main():
    # station -> {sea, sum, n, month_sum[12], month_n[12]}
    st = defaultdict(lambda: {"sea": None, "sum": 0.0, "n": 0,
                              "msum": [0.0] * 12, "mn": [0] * 12})
    for zp in sorted(SRC_DIR.rglob("*.zip")):
        prefix = zp.stem.split("_")[0].lower()
        sea = SEA.get(prefix)
        if sea is None:
            continue
        with zipfile.ZipFile(zp) as z:
            for name in z.namelist():
                if not name.lower().endswith(".csv"):
                    continue
                mm = MONTH_RE.search(name)
                if not mm:
                    continue
                month = int(mm.group(1)) - 1
                df = pd.read_csv(io.BytesIO(z.read(name)), encoding="cp949",
                                 usecols=[0, 2])
                df.columns = ["station", "sst"]
                df["sst"] = pd.to_numeric(df["sst"], errors="coerce")
                df = df[(df["sst"] >= -5) & (df["sst"] <= 40)]
                grp = df.groupby("station")["sst"]
                for station, s in grp:
                    rec = st[station]
                    rec["sea"] = sea
                    rec["sum"] += float(s.sum())
                    rec["n"] += int(s.size)
                    rec["msum"][month] += float(s.sum())
                    rec["mn"][month] += int(s.size)
        print(f"  처리: {zp.name}")

    stations = []
    for name, r in sorted(st.items()):
        monthly = [round(r["msum"][i] / r["mn"][i], 2) if r["mn"][i] else None
                   for i in range(12)]
        stations.append({
            "name": name,
            "sea": r["sea"],
            "mean": round(r["sum"] / r["n"], 2),
            "n": r["n"],
            "monthly": monthly,
        })
    payload = {"variable": "표층수온(℃)", "count": len(stations), "stations": stations}
    p = OUT / "sst_stations.json"
    json.dump(payload, open(p, "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    print(f"\n[저장] {p}  ({len(stations)} 관측소)")
    print("\n=== 해역별 관측소 수 ===")
    from collections import Counter
    c = Counter(s["sea"] for s in stations)
    for k, v in c.items():
        print(f"  {k}: {v}")
    print("\n=== 관측소 목록 (이름 | 해역 | 평균℃ | 관측수) ===")
    for s in stations:
        print(f"  {s['name']} | {s['sea']} | {s['mean']} | {s['n']:,}")


if __name__ == "__main__":
    main()
