# app.py — MAVIPE Landing Page (Hero + Logo Base64 + Carrossel com Legenda Automática/Manual)
import base64
import time
import re
from pathlib import Path
from urllib.parse import quote

import streamlit as st

st.set_page_config(page_title="MAVIPE Space Systems — DAP ATLAS", page_icon=None, layout="wide")

# ================== CONFIG ==================
YOUTUBE_ID = "Ulrl6TFaWtA"
LOGO_CANDIDATES = ["logo-mavipe.png", "logo-mavipe.jpeg", "logo-mavipe.jpg"]
CAROUSEL_INTERVAL_SEC = 3  # autoplay

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# LEGENDA MANUAL (Empresa) — defina aqui, sem depender dos nomes de arquivo
EMPRESA_CAPTIONS = [
    "DAP ATLAS — visão geral",            # slide 1
    "Detecção de metano (OGMP 2.0 L5)",   # slide 2
    "GeoINT & InSAR — integridade",       # slide 3
    # adicione mais linhas se tiver mais imagens
]
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# ================== UTILS ==================
def find_first(candidates) -> str | None:
    for name in candidates:
        p = Path(name)
        if p.exists() and p.stat().st_size > 0:
            return str(p)
    return None

def guess_mime(path: Path) -> str:
    return "image/png" if path.suffix.lower() == ".png" else "image/jpeg"

def as_data_uri(path_str: str) -> str:
    p = Path(path_str)
    b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:{guess_mime(p)};base64,{b64}"

def gather_empresa_images(max_n: int = 3) -> list[str]:
    """Coleta até max_n imagens p/ o carrossel (empresa1/2/3 prioritárias, depois empresa*)."""
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

def get_query_param(name: str, default=None):
    try:
        params = st.query_params
        val = params.get(name, default)
        return val
    except Exception:
        params = st.experimental_get_query_params()
        vals = params.get(name, [default])
        return vals[0] if isinstance(vals, list) else vals

def set_query_param(**kwargs):
    try:
        st.query_params.update(kwargs)
    except Exception:
        st.experimental_set_query_params(**kwargs)

def caption_from_path(path_str: str) -> str:
    """Gera legenda amigável do nome do arquivo: remove extensão, substitui _ e - por espaço, capitaliza."""
    name = Path(path_str).stem
    name = re.sub(r"[_\-]+", " ", name).strip()
    caption = " ".join(w.capitalize() for w in name.split())
    return caption if caption else "Imagem"

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def empresa_caption(idx: int, path_str: str) -> str:
    """
    Legenda final da Empresa:
      1) usa EMPRESA_CAPTIONS[idx], se existir e não for vazio
      2) senão, fallback para legenda automática pelo nome do arquivo
    """
    if 0 <= idx < len(EMPRESA_CAPTIONS):
        cap = (EMPRESA_CAPTIONS[idx] or "").strip()
        if cap:
            return cap
    return caption_from_path(path_str)
# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

# ================== CSS ==================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"]{background:#0b1221; overflow-x:hidden;}
#MainMenu, header, footer {visibility:hidden;}
.block-container{padding:0!important; max-width:100%!important}

/* Navbar fixa */
.navbar{position:fixed; top:0; left:0; right:0; z-index:1000; display:flex; justify-content:space-between;
  padding:14px 36px; background:rgba(8,16,33,.35); backdrop-filter:saturate(160%) blur(10px);
  border-bottom:1px solid rgba(255,255,255,.08)}
.nav-left .brand{color:#e6eefc; font-weight:700}
.nav-right a{color:#d6def5; text-decoration:none; margin-left:22px}

/* Hero YouTube */
.hero{position:relative; height:100vh; min-height:640px; width:100vw; left:50%; margin-left:-50vw; overflow:hidden}
.hero iframe{position:absolute; top:50%; left:50%; width:177.777vw; height:100vh; transform:translate(-50%,-50%); pointer-events:none}
.hero .overlay{position:absolute; inset:0; background:radial-gradient(85% 60% at 30% 30%, rgba(20,30,55,.0) 0%, rgba(8,16,33,.48) 68%, rgba(8,16,33,.86) 100%); z-index:1}

/* LOGO topo direito */
.hero .logo{
  position:absolute; z-index:3; top:18px; right:28px;
  width: clamp(110px, 12vw, 200px); height:auto;
  opacity:.98; filter:drop-shadow(0 6px 14px rgba(0,0,0,.45));
  pointer-events:none;
}

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
:root{
  --safe-top: env(safe-area-inset-top, 0px);
  --safe-right: env(safe-area-inset-right, 0px);
  --safe-bottom: env(safe-area-inset-bottom, 0px);
  --safe-left: env(safe-area-inset-left, 0px);
}
.navbar{
  padding: max(12px, calc(12px + var(--safe-top))) max(24px, calc(24px + var(--safe-right))) 12px max(24px, calc(24px + var(--safe-left)));
}
.cta, .btn{min-height:44px; line-height:1.15; margin-bottom:10px;}
.hero{height:100svh;}
@supports (height:100dvh){.hero{height:100dvh;}}
@media (max-width:768px){
  .hero .logo{top:calc(12px + var(--safe-top)); right:calc(16px + var(--safe-right)); width:clamp(96px,28vw,160px);}
  .hero iframe{width:177.777vh; height:100vh; max-width:300vw;}
  .kicker{font-size:14px;}
  h1.hero-title{font-size:clamp(28px,8vw,36px);}
  .hero-sub{font-size:15px; max-width:100%;}
  [data-testid="column"]{width:100%!important; flex:0 0 100%!important;}
  .section{padding:56px 5vw;}
  .nav-right a{margin-left:14px;}
}

/* Dots e thumbnails */
.carousel-dots{display:flex; gap:8px; justify-content:center; margin-top:10px}
.carousel-dots span{width:8px; height:8px; border-radius:50%; background:#5d6a8b; display:inline-block; opacity:.6}
.carousel-dots span.active{background:#e6eefc; opacity:1}


