# app.py — MAVIPE Landing Page com botão LinkedIn no lugar de “Know more”
import base64
import time
import re
from pathlib import Path
from urllib.parse import quote
import streamlit as st

st.set_page_config(page_title="MAVIPE Space Systems — DAP ATLAS", page_icon=None, layout="wide")

# ================== CONFIG ==================
YOUTUBE_ID = "Ulrl6TFaWtA"
LOGO_CANDIDATES = [
    "logo-mavipe@2x.png",
    "logo-mavipe.png",
    "logo-mavipe@2x.jpg",
    "logo-mavipe.jpg",
    "logo-mavipe.jpeg",
    "logo-mavipe@2x.jpeg",
    "logo-mavipe.png",
]
CAROUSEL_INTERVAL_SEC = 3
PARTNER_INTERVAL_SEC = 3

EMPRESA_CAPTIONS = [
    "Empresa Estratégica de Defesa  - Certificação do Ministério da Defesa",
    "Plataforma Geoespacial DAP ATLAS - Multipropósito, Proprietária e Certificada como Produto Estratégico de Defesa",
    "GeoINT & InSAR — integridade",
]

NEWS_ITEMS = [
    {
        "title": "MAVIPE lança módulo OGMP 2.0 Nível 5",
        "date": "2025-09-15",
        "summary": "Quantificação por fonte, incerteza e Q/C com dashboards e API.",
        "link": "https://example.com/noticia1",
        "image": "news1.jpg",
    },
    {
        "title": "Parceria para InSAR de alta cadência",
        "date": "2025-08-22",
        "summary": "Monitoramento de deformação em dutos, tanques e taludes.",
        "link": "https://example.com/noticia2",
        "image": "news2.jpg",
    },
    {
        "title": "DAP ATLAS integra alertas marítimos",
        "date": "2025-07-02",
        "summary": "Detecção de navios não colaborativos, spoofing e rendezvous.",
        "link": "https://example.com/noticia3",
        "image": "news3.png",
    },
]

def find_first(candidates) -> str | None:
    for name in candidates:
        p = Path(name)
        if p.exists() and p.stat().st_size > 0:
            return str(p)
    return None

def guess_mime(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".png":
        return "image/png"
    if ext in (".jpg", ".jpeg"):
        return "image/jpeg"
    return "application/octet-stream"

def as_data_uri(path_str: str) -> str:
    p = Path(path_str)
    b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:{guess_mime(p)};base64,{b64}"

def gather_empresa_images(max_n: int = 3) -> list[str]:
    base_candidates = [
        "empresa1.jpg","empresa1.jpeg","empresa1.png",
        "empresa2.jpg","empresa2.jpeg","empresa2.png",
        "empresa3.jpg","empresa3.jpeg","empresa3.png",
    ]
    found = [p for p in base_candidates if Path(p).exists() and Path(p).stat().st_size > 0]
    extras = []
    for pat in ("empresa*.jpg", "empresa*.jpeg", "empresa*.png"):
        for p in sorted(Path(".").glob(pat)):
            if p.is_file() and p.stat().st_size > 0:
                extras.append(str(p))
    seen, ordered = set(), []
    for p in found + extras:
        if p not in seen:
            ordered.append(p); seen.add(p)
        if len(ordered) >= max_n:
            break
    return ordered

def gather_partner_images(max_n: int = 24) -> list[str]:
    patterns = [
        "parceiro*.png","parceiro*.jpg","parceiro*.jpeg",
        "certificacao*.png","certificacao*.jpg","certificacao*.jpeg",
        "logo*.png","logo*.jpg","logo*.jpeg",
    ]
    results = []
    for pat in patterns:
        for p in sorted(Path(".").glob(pat)):
            if p.is_file() and p.stat().st_size > 0:
                s = str(p)
                if s not in results:
                    results.append(s)
    return results[:max_n]

def get_query_param(name: str, default=None):
    try:
        params = st.query_params
        val = params.get(name, default)
        return val
    except Exception:
        params = st.experimental_get_query_params()
        vals = params.get(name, [default])
        return vals[0] if isinstance(vals, list) else vals

def caption_from_path(path_str: str) -> str:
    name = Path(path_str).stem
    name = re.sub(r"[_\-]+", " ", name).strip()
    caption = " ".join(w.capitalize() for w in name.split())
    return caption if caption else "Imagem"

def empresa_caption(idx: int, path_str: str) -> str:
    if 0 <= idx < len(EMPRESA_CAPTIONS):
        cap = (EMPRESA_CAPTIONS[idx] or "").strip()
        if cap:
            return cap
    return caption_from_path(path_str)

def news_thumbnail_src(path_str: str | None) -> str | None:
    if not path_str:
        return None
    p = Path(path_str)
    if p.exists() and p.stat().st_size > 0:
        return as_data_uri(str(p))
    return None

# ================== CSS ==================
st.markdown('''
<style>
html, body, [data-testid="stAppViewContainer"]{background:#0b1221; overflow-x:hidden;}
#MainMenu, header, footer {visibility:hidden;}
.block-container{padding:0!important; max-width:100%!important}

/* Navbar compacta e estável */
.navbar{
  position:fixed; top:0; left:0; right:0; z-index:1000;
  display:flex; justify-content:space-between; align-items:center;
  height:64px; padding:8px 8px !important; overflow:visible;
  background:rgba(8,16,33,.35); backdrop-filter:saturate(160%) blur(10px);
  border-bottom:1px solid rgba(255,255,255,.08);
}
.nav-left{ position:relative; height:64px; display:flex; align-items:center; gap:12px; }
.nav-right a{ color:#d6def5; text-decoration:none; margin-left:18px }

/* Logo grande e “saltando” acima da barra */
.nav-logo{
  position:relative;
  height:140px;
  width:auto; display:block;
  transform:translateY(-12px);  /* menos salto para ficar melhor */
  image-rendering:auto;
  filter:drop-shadow(0 4px 8px rgba(0,0,0,.45));
  z-index:2;
}

/* Hero YouTube */
.hero{position:relative; height:100vh; min-height:640px; width:100vw; left:50%; margin-left:-50vw; overflow:hidden}
.hero iframe{position:absolute; top:50%; left:50%; width:177.777vw; height:100vh; transform:translate(-50%,-50%); pointer-events:none}
.hero .overlay{position:absolute; inset:0; background:radial-gradient(85% 60% at 30% 30%, rgba(20,30,55,.0) 0%, rgba(8,16,33,.48) 68%, rgba(8,16,33,.86) 100%); z-index:1}

/* Garantir que nenhum logo extra apareça no hero */
.hero .logo{ display:none }

/* Conteúdo Hero */
.hero .content{position:absolute; z-index:2; inset:0; display:flex; align-items:center; padding:0 8vw; color:#e8eefc}
.kicker{color:#cfe7ff; font-weight:600; margin-bottom:10px}
h1.hero-title{font-size:clamp(36px,6vw,64px); line-height:1.05; margin:0 0 12px}
.highlight{color:#34d399}
.hero-sub{font-size:clamp(16px,2.2vw,20px); color:#b9c6e6; max-width:70ch}
.cta, .btn{display:inline-block; padding:12px 18px; border-radius:12px; text-decoration:none; font-weight:700; margin-right:10px}
.cta{background:#34d399; color:#05131a}
.btn{border:1px solid rgba(255,255,255,.18); color:#e6eefc; background:rgba(255,255,255,.06)}
.section{padding:72px 8vw; border-top:1px solid rgba(255,255,255,.07)}
.lead{color:#b9c6e6}

/* MOBILE */
:root{ --safe-top: env(safe-area-inset-top, 0px); --safe-right: env(safe-area-inset-right, 0px); --safe-bottom: env(safe-area-inset-bottom, 0px); --safe-left: env(safe-area-inset-left, 0px); }
.navbar{ padding: max(8px, calc(8px + var(--safe-top))) max(8px, calc(8px + var(--safe-right))) 8px max(8px, calc(8px + var(--safe-left))) !important; }
@media (max-width:768px){
  .navbar, .nav-left{ height:56px; }
  .nav-logo{ height:110px; transform:translateY(-10px); }
  .hero iframe{width:177.777vh; height:100vh; max-width:300vw;}
  .kicker{font-size:14px;}
  h1.hero-title{font-size:clamp(28px,8vw,36px);}
  .hero-sub{font-size:15px; max-width:100%;}
  .section{padding:56px 5vw;}
  .nav-right a{margin-left:12px;}
}

/* Dots e thumbnails */
.carousel-dots{display:flex; gap:8px; justify-content:center; margin-top:10px}
.carousel-dots span{width:8px; height:8px; border-radius:50%; background:#5d6a8b; display:inline-block; opacity:.6}
.carousel-dots span.active{background:#e6eefc; opacity:1}

.thumbs{display:flex; gap:12px; justify-content:center; margin-top:10px; flex-wrap:wrap}
.thumb{ display:inline-block; width:120px; height:70px; overflow:hidden; border-radius:8px; border:2px solid transparent; opacity:.85; transition:all .2s ease-in-out; }
.thumb img{width:100%; height:100%; object-fit:cover; display:block}
.thumb:hover{opacity:1; transform:translateY(-2px)}
.thumb.active{border-color:#34d399; box-shadow:0 0 0 2px rgba(52,211,153,.35) inset;}
@media (max-width:768px){ .thumb{width=92px; height=56px;} }

.carousel-main{ width:100%; height:400px; object-fit:cover; border-radius:12px; box-shadow:0 8px 28px rgba(0,0,0,.35); }
@media (max-width:768px){ .carousel-main{ height:240px; } }
.carousel-caption{ text-align:center; color:#b9c6e6; font-size:0.95rem; margin-top:8px; }
.carousel-main.partner{ object-fit:contain; background:rgba(255,255,255,.03); }
.thumbs.partner .thumb{ background:rgba(255,255,255,.02); }
.thumbs.partner .thumb img{ object-fit:contain; background:transparent; }

.sectors-grid{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; margin-top:18px }
.sector-card{ background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.08); border-radius:16px; padding:16px 18px; }
.sector-card h3{margin:0 0 8px 0; color:#e6eefc}
.sector-card p{margin:0 0 8px 0; color:#b9c6e6}
.sector-card ul{margin:8px 0 0 18px; color:#c7d3f0}
.sector-card li{margin:4px 0}
@media (max-width:980px){ .sectors-grid{grid-template-columns:1fr} }

.news-grid{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; margin-top:18px; }
.news-card{ background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.08); border-radius:16px; overflow:hidden; display:flex; flex-direction:column; }
.news-thumb{width:100%; height:160px; object-fit:cover; background:rgba(255,255,255,.02)}
.news-body{padding:14px 16px}
.news-title{color:#e6eefc; font-weight:700; margin:0 0 6px 0}
.news-meta{color:#9fb0d4; font-size:.85rem; margin-bottom:6px}
.news-summary{color:#cbd6f2; font-size:.95rem; margin-bottom:10px}
.news-actions{padding:0 16px 14px 16px}
.news-actions a{display:inline-block; padding=10px 14px; border-radius:10px; text-decoration:none; background:#34d399; color:#05131a; font-weight:700}
@media (max-width:980px){ .news-grid{grid-template-columns:1fr} }
</style>
''', unsafe_allow_html=True)

# ================== NAVBAR (com LOGO à esquerda) ==================
logo_2x = Path("logo-mavipe@2x.png")
logo_1x = Path("logo-mavipe.png")
fallback = find_first(LOGO_CANDIDATES)

def pick_logo_path() -> str | None:
    if logo_2x.exists() and logo_2x.stat().st_size > 0:
        return str(logo_2x)
    if logo_1x.exists() and logo_1x.stat().st_size > 0:
        return str(logo_1x)
    return fallback

logo_path = pick_logo_path()
logo_left_tag = (
    f'<img src="{as_data_uri(logo_path)}" alt="MAVIPE logo" class="nav-logo"/>'
    if logo_path else
    '<div class="brand" style="color:#e6eefc; font-weight:700">MAVIPE</div>'
)

st.markdown(f'''
<div class="navbar">
  <div class="nav-left">{logo_left_tag}</div>
  <div class="nav-right">
    <a href="#empresa">Empresa</a>
    <a href="#solucao">Solução</a>
    <a href="#parceiros">Parceiros</a>
    <a href="#newsroom">Newsroom</a>
    <a href="#setores">Setores</a>
    <a class="cta" href="https://www.linkedin.com/company/mavipe" target="_blank" style="background:#34d399; color:#05131a; font-weight:700; padding:10px 14px; border-radius:10px; text-decoration:none">
      <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="#0A66C2">
        <path d="M4.98 3.5C4.98 4.88 3.88 6 2.5 6S0 4.88 0 3.5 1.12 1 2.5 1 4.98 2.12 4.98 3.5zM.5 8.5h4V24h-4V8.5zM8.5 8.5h3.8v2.1h.05c.53-1 1.8-2.1 3.7-2.1 4 0 4.75 2.6 4.75 6v9.5h-4v-8.5c0-2-.04-4.5-2.75-4.5-2.75 0-3.17 2.15-3.17 4.35V24h-4V8.5z"/>
      </svg>
    </a>
  </div>
</div>
''', unsafe_allow_html=True)

# ... (restante do app como antes: hero, empresa, solução, parceiros, newsroom, setores, contato)

