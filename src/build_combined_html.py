"""여러 대시보드 HTML을 '단일 공유용 HTML' 하나로 합친다.

각 대시보드는 iframe(srcdoc)으로 격리 삽입해 CSS/JS 충돌을 방지한다.
외부 의존성 없이 파일 하나만 공유하면 오프라인에서 전부 열람 가능.
출력: docs/korea_sst_dashboards.html
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

# (탭 이름, 파일명, 이모지)
PAGES = [
    ("연도별 비교 지도", "korea_sst_yearly_maps.html", "🗓️"),
    ("관측소 실측 지도", "korea_sst_station_map.html", "📍"),
    ("연·월 시계열", "korea_sst_timeseries.html", "🌡️"),
    ("연안 수온 보드", "korea_sst_board.html", "🗺️"),
    ("연안 수온 지도", "korea_coastal_sst.html", "🌊"),
]

blocks, tabs = [], []
for i, (label, fname, emo) in enumerate(PAGES):
    html = (DOCS / fname).read_text(encoding="utf-8")
    # 외부 script 파서가 조기 종료되지 않도록 </script> 이스케이프
    html = html.replace("</script>", "<\\/script>").replace("</SCRIPT>", "<\\/script>")
    blocks.append(f'<script type="text/plain" id="d{i}">{html}</script>')
    tabs.append(f'<button class="navbtn" role="tab" data-i="{i}">'
                f'<span class="e">{emo}</span>{label}</button>')

wrapper = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>대한민국 연안 표층수온 대시보드 모음</title>
<style>
  :root{{--bg:#0e2732;--bar:#0f2b39;--ink:#eaf3f7;--muted:#93b0bc;--hair:#20404d;--accent:#39b6d8}}
  *{{box-sizing:border-box}}
  html,body{{margin:0;height:100%}}
  body{{display:flex;flex-direction:column;background:var(--bg);
    font-family:"Malgun Gothic","맑은 고딕","Apple SD Gothic Neo",system-ui,sans-serif;color:var(--ink)}}
  header{{background:var(--bar);border-bottom:1px solid var(--hair);padding:10px 16px;
    display:flex;align-items:center;gap:16px;flex-wrap:wrap}}
  .brand{{font-weight:800;font-size:15px;letter-spacing:-.01em;white-space:nowrap}}
  .brand small{{display:block;font-weight:600;font-size:11px;color:var(--muted);letter-spacing:0}}
  nav{{display:flex;gap:6px;flex-wrap:wrap}}
  .navbtn{{font-family:inherit;font-size:13px;font-weight:700;color:var(--muted);cursor:pointer;
    background:transparent;border:1px solid var(--hair);border-radius:999px;padding:7px 14px;
    display:inline-flex;align-items:center;gap:6px;transition:all .12s}}
  .navbtn .e{{font-size:14px}}
  .navbtn:hover{{color:var(--ink)}}
  .navbtn[aria-selected="true"]{{background:var(--accent);color:#04222b;border-color:var(--accent)}}
  main{{flex:1;min-height:0}}
  iframe{{width:100%;height:100%;border:0;display:block;background:#eaf1f5}}
  @media (prefers-reduced-motion:reduce){{.navbtn{{transition:none}}}}
</style>
</head>
<body>
  <header>
    <div class="brand">🌊 연안 표층수온 대시보드<small>국립수산과학원 실측 · 2021–2025</small></div>
    <nav role="tablist">{"".join(tabs)}</nav>
  </header>
  <main><iframe id="frame" title="대시보드"></iframe></main>

  {"".join(blocks)}

  <script>
    var tabs=[].slice.call(document.querySelectorAll(".navbtn"));
    var frame=document.getElementById("frame");
    function show(i){{
      var raw=document.getElementById("d"+i).textContent;
      frame.srcdoc=raw.split("<\\\\/script>").join("<\\/script>");
      tabs.forEach(function(t){{t.setAttribute("aria-selected", +t.dataset.i===i);}});
    }}
    tabs.forEach(function(t){{t.addEventListener("click",function(){{show(+t.dataset.i);}});}});
    show(0);
  </script>
</body>
</html>'''

out = DOCS / "korea_sst_dashboards.html"
out.write_text(wrapper, encoding="utf-8")
kb = out.stat().st_size / 1024
print(f"[저장] {out}  ({kb:.1f} KB)")
print(f"포함 대시보드 {len(PAGES)}개: " + ", ".join(p[0] for p in PAGES))
