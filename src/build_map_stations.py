"""지도 표시용 관측소 선별 + 좌표 부여.

sst_stations.json에서 대표성 있는(관측수 충분) 주요 연안 관측소를 선별하고
지역명 기반 근사 좌표를 부여한다. 수온 값은 모두 실측 평균.
출력: data/processed/sst_map_stations.json
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "processed"

# 관측소코드 -> (표시명, 경도, 위도)  ※ 좌표는 지역명 기반 근사값
COORD = {
    # 동해
    "fgbg3": ("고성 봉포", 128.47, 38.28), "byy87": ("양양", 128.66, 38.02),
    "bgna3": ("강릉", 128.95, 37.77), "bsc87": ("삼척", 129.17, 37.44),
    "buhi5": ("울진 후포", 129.45, 36.68), "byd8a": ("영덕", 129.40, 36.42),
    "bpwi5": ("포항 월포", 129.40, 36.28), "bugi5": ("울산 간절곶", 129.36, 35.36),
    "bbji5": ("부산 장안", 129.26, 35.32), "kma13": ("울릉도", 130.90, 37.48),
    "kma15": ("독도", 131.87, 37.24),
    # 서해
    "fbn69": ("백령도", 124.68, 37.96), "biji5": ("인천 장봉도", 126.34, 37.53),
    "biai5": ("인천 자월도", 126.32, 37.26), "ftpk5": ("태안 파도리", 126.14, 36.73),
    "btai5": ("태안 안면도", 126.33, 36.48), "bbsi5": ("보령 삽시도", 126.42, 36.28),
    "bsmi5": ("서천 마량", 126.52, 36.13), "bgbi5": ("군산 비안도", 126.43, 35.78),
    "bbwi5": ("부안 위도", 126.30, 35.62), "byai5": ("영광 안마도", 126.03, 35.36),
    "emp67": ("목포", 126.38, 34.78), "fshj7": ("신안 흑산도", 125.43, 34.68),
    "bjbi5": ("진도 불도", 126.16, 34.42),
    # 남해
    "bjji5": ("진도 조도", 126.10, 34.24), "wc001": ("완도 청산도", 126.85, 34.17),
    "wn087": ("완도 노화도", 126.55, 34.17), "fwdf1": ("완도 동백", 126.75, 34.31),
    "ejhfc": ("장흥 회진", 126.87, 34.42), "fgsj3": ("고흥 소록도", 127.28, 34.52),
    "byki5": ("여수 금오도", 127.78, 34.53), "km001": ("여수 신월", 127.70, 34.73),
    "bnsi5": ("남해 상주", 127.99, 34.70), "bthi5": ("통영 한산도", 128.48, 34.78),
    "gi086": ("거제 일운", 128.70, 34.83), "btei5": ("거제 해금강", 128.65, 34.72),
    "bbdi5": ("부산 다대포", 128.97, 35.05), "bcji5": ("추자도", 126.30, 33.95),
    # 제주
    "bjyi5": ("제주 용담", 126.49, 33.51), "bjii5": ("제주 김녕", 126.75, 33.56),
    "bjui5": ("제주 우도", 126.95, 33.50), "bjsi5": ("제주 신산", 126.81, 33.35),
    "bjni5": ("서귀포 중문", 126.42, 33.24), "bjgi5": ("가파도", 126.27, 33.17),
    "bjhi5": ("제주 협재", 126.24, 33.39), "bjoi5": ("제주 영락", 126.22, 33.30),
}
# 제주는 원자료상 '남해'로 묶여 있어 표시용 해역을 별도 지정
JEJU = {"bjyi5", "bjii5", "bjui5", "bjsi5", "bjni5", "bjgi5", "bjhi5", "bjoi5", "bcji5"}
CODE_RE = re.compile(r"\(([a-z0-9]+)\)\s*$")


def main():
    src = json.load(open(OUT / "sst_stations.json", encoding="utf-8"))
    by_code = {}
    for s in src["stations"]:
        m = CODE_RE.search(s["name"])
        if m:
            by_code[m.group(1)] = s

    out = []
    missing = []
    for code, (label, lon, lat) in COORD.items():
        s = by_code.get(code)
        if s is None:
            missing.append((code, label))
            continue
        sea = "제주" if code in JEJU else s["sea"]
        # 연도별 월배열 + 연평균 (전체 + 각 연도)
        monthly = {"전체": s["monthly"]}
        mean = {"전체": s["mean"]}
        for y, yy in s.get("by_year", {}).items():
            monthly[y] = yy["monthly"]
            mean[y] = yy["mean"]
        out.append({
            "name": label, "lon": lon, "lat": lat, "sea": sea,
            "n": s["n"], "monthly": monthly, "mean": mean,
        })
    out.sort(key=lambda x: x["mean"]["전체"])
    payload = {
        "variable": "표층수온(℃)",
        "note": "국립수산과학원 실시간 연안 관측 실측 평균. 좌표는 지역명 기반 근사값.",
        "years": src.get("years", []),
        "count": len(out),
        "stations": out,
    }
    json.dump(payload, open(OUT / "sst_map_stations.json", "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    print(f"[저장] sst_map_stations.json  ({len(out)}개 관측소)")
    if missing:
        print("경고 - 매칭 실패:", missing)
    print("\n연평균(전체) 최저/최고:")
    print(f"  최저: {out[0]['name']} {out[0]['mean']['전체']}°C")
    print(f"  최고: {out[-1]['name']} {out[-1]['mean']['전체']}°C")
    print(f"관측수 최소: {min(s['n'] for s in out):,} / 최대: {max(s['n'] for s in out):,}")


if __name__ == "__main__":
    main()
