"""연안 표층수온 집계.

'Sea of korea degree' 폴더의 연도별/해역별 ZIP(월별 CSV, cp949)에서
표층수온(℃)을 추출해 연·월·해역별 평균으로 집계한다.

출력:
  data/processed/sst_monthly_by_sea.csv   (tidy: year, month, sea, mean, n, min, max, std)
  data/processed/sst_dashboard.json        (대시보드 내장용)
"""
from __future__ import annotations

import io
import json
import re
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = Path(r"C:\Users\RYU\Downloads\Sea of korea degree")
OUT_DIR = ROOT / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

SEA = {"es": "동해", "ss": "남해", "ys": "서해"}  # East / South / Yellow(West)
SEA_ORDER = ["동해", "서해", "남해"]
SST_COL = 2  # 표층수온(℃) 컬럼 인덱스
MONTH_RE = re.compile(r"(\d{1,2})\s*월")
YEAR_RE = re.compile(r"(20\d{2})")


def iter_csv_stats():
    """모든 ZIP의 월별 CSV를 순회하며 (year, month, sea, 통계) 산출."""
    zips = sorted(SRC_DIR.rglob("*.zip"))
    print(f"ZIP 파일 {len(zips)}개 발견")
    for zp in zips:
        prefix = zp.stem.split("_")[0].lower()
        sea = SEA.get(prefix)
        ym = YEAR_RE.search(zp.stem)
        year = int(ym.group(1)) if ym else None
        if sea is None or year is None:
            print(f"  건너뜀(형식 불명): {zp.name}")
            continue
        with zipfile.ZipFile(zp) as z:
            for name in z.namelist():
                if not name.lower().endswith(".csv"):
                    continue
                mm = MONTH_RE.search(name)
                if not mm:
                    continue
                month = int(mm.group(1))
                with z.open(name) as fh:
                    raw = fh.read()
                df = pd.read_csv(io.BytesIO(raw), encoding="cp949", usecols=[SST_COL])
                s = pd.to_numeric(df.iloc[:, 0], errors="coerce").dropna()
                # 물리적으로 불가능한 값 제거 (-5 ~ 40℃ 범위)
                s = s[(s >= -5) & (s <= 40)]
                if s.empty:
                    continue
                yield {
                    "year": year, "month": month, "sea": sea,
                    "mean": round(float(s.mean()), 3),
                    "n": int(s.size),
                    "min": round(float(s.min()), 2),
                    "max": round(float(s.max()), 2),
                    "std": round(float(s.std()), 3),
                }
        print(f"  처리 완료: {zp.name}")


def main():
    rows = list(iter_csv_stats())
    df = pd.DataFrame(rows).sort_values(["sea", "year", "month"]).reset_index(drop=True)
    csv_path = OUT_DIR / "sst_monthly_by_sea.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"\n[저장] {csv_path}  ({len(df)} 행)")

    years = sorted(df["year"].unique().tolist())

    def grid(sub):
        """{year: [12개월 평균(없으면 null)]} 형태."""
        out = {}
        for y in years:
            month_vals = [None] * 12
            for _, r in sub[sub["year"] == y].iterrows():
                month_vals[int(r["month"]) - 1] = round(float(r["mean"]), 2)
            out[str(y)] = month_vals
        return out

    data = {sea: grid(df[df["sea"] == sea]) for sea in SEA_ORDER}

    # 전체(해역 통합): 관측수(n) 가중 평균
    overall = {}
    for y in years:
        month_vals = [None] * 12
        for m in range(1, 13):
            sub = df[(df["year"] == y) & (df["month"] == m)]
            if not sub.empty and sub["n"].sum() > 0:
                w = np.average(sub["mean"], weights=sub["n"])
                month_vals[m - 1] = round(float(w), 2)
        overall[str(y)] = month_vals
    data["전체"] = overall

    payload = {
        "source": "국립수산과학원 실시간 연안 해양관측 (Sea of korea degree)",
        "variable": "표층수온(℃)",
        "years": years,
        "seas": SEA_ORDER,
        "data": data,
        "total_obs": int(df["n"].sum()),
    }
    json_path = OUT_DIR / "sst_dashboard.json"
    json.dump(payload, open(json_path, "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    print(f"[저장] {json_path}")

    # 요약 출력
    print("\n=== 연도별 연평균 표층수온 (전체 가중) ===")
    for y in years:
        vals = [v for v in overall[str(y)] if v is not None]
        if vals:
            print(f"  {y}: {np.mean(vals):.2f}°C  (관측월 {len(vals)}/12)")
    print(f"\n총 관측 레코드: {df['n'].sum():,}")


if __name__ == "__main__":
    main()
