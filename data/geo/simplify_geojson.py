"""GeoJSON 폴리곤을 Douglas-Peucker로 단순화 (외부 의존성 없음).
사용: python simplify_geojson.py <입력> <출력> <epsilon_deg>
"""
import json
import sys


def perp_dist(p, a, b):
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0, min(1, t))
    cx, cy = ax + t * dx, ay + t * dy
    return ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5


def dp(pts, eps):
    if len(pts) < 3:
        return pts
    dmax, idx = 0.0, 0
    for i in range(1, len(pts) - 1):
        d = perp_dist(pts[i], pts[0], pts[-1])
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        left = dp(pts[:idx + 1], eps)
        right = dp(pts[idx:], eps)
        return left[:-1] + right
    return [pts[0], pts[-1]]


def simplify_ring(ring, eps, ndigits=4):
    closed = ring[0] == ring[-1]
    pts = ring[:-1] if closed else ring[:]
    s = dp(pts, eps)
    if closed:
        s = s + [s[0]]
    return [[round(x, ndigits), round(y, ndigits)] for x, y in s]


def simplify_geom(geom, eps):
    t = geom["type"]
    c = geom["coordinates"]
    if t == "Polygon":
        rings = [simplify_ring(r, eps) for r in c]
        geom["coordinates"] = [r for r in rings if len(r) >= 4]
    elif t == "MultiPolygon":
        polys = []
        for poly in c:
            rings = [simplify_ring(r, eps) for r in poly]
            rings = [r for r in rings if len(r) >= 4]
            if rings:
                polys.append(rings)
        geom["coordinates"] = polys
    return geom


def count(geom):
    def walk(x):
        return 1 if isinstance(x[0], (int, float)) else sum(walk(i) for i in x)
    return walk(geom["coordinates"])


if __name__ == "__main__":
    src, dst, eps = sys.argv[1], sys.argv[2], float(sys.argv[3])
    d = json.load(open(src, encoding="utf-8"))
    before = sum(count(f["geometry"]) for f in d["features"])
    for f in d["features"]:
        # 필요한 속성만 유지
        p = f["properties"]
        f["properties"] = {
            "name": p.get("name"),
            "name_eng": p.get("name_eng"),
            "code": p.get("code"),
        }
        simplify_geom(f["geometry"], eps)
    after = sum(count(f["geometry"]) for f in d["features"])
    json.dump(d, open(dst, "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    print(f"points: {before} -> {after}  (eps={eps})")
