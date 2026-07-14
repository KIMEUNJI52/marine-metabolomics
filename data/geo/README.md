# 지도 데이터 (GeoJSON)

대한민국 시도 경계 지도. 대시보드(`docs/korea_sst_board.html`)에 내장해 사용.

## 출처
- **southkorea/southkorea-maps** — GitHub에서 가장 널리 쓰이는 한국 행정경계 GeoJSON
- 원본(시도, 2018): https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2018/json/skorea-provinces-2018-geo.json

## 파일
| 파일 | 설명 | git |
|------|------|-----|
| `skorea-provinces-2018-geo.json` | 원본 (약 7.3MB, 18.4만 좌표) | 제외(.gitignore) |
| `skorea-prov-0.006.json` | 단순화본 (약 84KB, 4.4천 좌표) — 대시보드에 내장 | 포함 |
| `simplify_geojson.py` | Douglas-Peucker 단순화 스크립트 (의존성 없음) | 포함 |

## 재현
```powershell
# 1) 원본 내려받기
Invoke-WebRequest "https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2018/json/skorea-provinces-2018-geo.json" -OutFile skorea-provinces-2018-geo.json
# 2) 단순화 (epsilon=0.006도 ≈ 600m)
python simplify_geojson.py skorea-provinces-2018-geo.json skorea-prov-0.006.json 0.006
```
