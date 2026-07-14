"""관측소별 표층수온 집계 (연도 차원 포함).

각 관측소별로 (전체 + 연도별) × (연평균 + 월별) 표층수온을 산출.
출력: data/processed/sst_stations.json
"""
from __future__ import annotations

import io
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = Path(r"C:\Users\RYU\Downloads\Sea of korea degree")
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)

SEA = {"es": "동해", "ss": "남해", "ys": "서해"}
MONTH_RE = re.compile(r"(\d{1,2})\s*월")
YEAR_RE = re.compile(r"(20\d{2})")


def blank():
    return {"msum": [0.0] * 12, "mn": [0] * 12}


def main():
    # station -> {sea, years: {year: {msum[12], mn[12]}}}
    st = defaultdict(lambda: {"sea": None, "years": defaultdict(blank)})
    years = set()
    for zp in sorted(SRC_DIR.rglob("*.zip")):
        prefix = zp.stem.split("_")[0].lower()
        sea = SEA.get(prefix)
        ym = YEAR_RE.search(zp.stem)
        if sea is None or not ym:
            continue
        year = int(ym.group(1))
        years.add(year)
        with zipfile.ZipFile(zp) as z:
            for name in z.namelist():
                if not name.lower().endswith(".csv"):
                    continue
                mm = MONTH_RE.search(name)
                if not mm:
                    continue
                month = int(mm.group(1)) - 1
                df = pd.read_csv(io.BytesIO(z.read(name)), encoding="cp949", usecols=[0, 2])
                df.columns = ["station", "sst"]
                df["sst"] = pd.to_numeric(df["sst"], errors="coerce")
                df = df[(df["sst"] >= -5) & (df["sst"] <= 40)]
                for station, s in df.groupby("station")["sst"]:
                    rec = st[station]
                    rec["sea"] = sea
                    yr = rec["years"][year]
                    yr["msum"][month] += float(s.sum())
                    yr["mn"][month] += int(s.size)
        print(f"  처리: {zp.name}")

    years = sorted(years)

    def monthly_and_mean(msum, mn):
        monthly = [round(msum[i] / mn[i], 2) if mn[i] else None for i in range(12)]
        tot_s = sum(msum)
        tot_n = sum(mn)
        mean = round(tot_s / tot_n, 2) if tot_n else None
        return monthly, mean, tot_n

    stations = []
    for name, r in sorted(st.items()):
        # 연도별
        by_year = {}
        all_msum = [0.0] * 12
        all_mn = [0] * 12
        for y in years:
            if y not in r["years"]:
                continue
            yy = r["years"][y]
            monthly, mean, n = monthly_and_mean(yy["msum"], yy["mn"])
            by_year[str(y)] = {"monthly": monthly, "mean": mean, "n": n}
            for i in range(12):
                all_msum[i] += yy["msum"][i]
                all_mn[i] += yy["mn"][i]
        monthly, mean, n = monthly_and_mean(all_msum, all_mn)
        stations.append({
            "name": name, "sea": r["sea"],
            "mean": mean, "n": n, "monthly": monthly,   # 전체(모든 연도)
            "by_year": by_year,
        })

    payload = {"variable": "표층수온(℃)", "years": years,
               "count": len(stations), "stations": stations}
    json.dump(payload, open(OUT / "sst_stations.json", "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    print(f"\n[저장] sst_stations.json  ({len(stations)} 관측소, 연도 {years})")


if __name__ == "__main__":
    main()
