# app.py — MAVIPE Landing Page (Hero + Logo Retina + Carrosséis + Newsroom + Setores)
import base64
import time
import re
import json
from pathlib import Path
from urllib.parse import quote
import streamlit as st

# ================== CONFIG GERAL ==================
st.set_page_config(page_title="MAVIPE Space Systems — DAP ATLAS", page_icon=None, layout="wide")

YOUTUBE_ID = "Ulrl6TFaWtA"

LOGO_CANDIDATES = [
    "logo-mavipe@2x.png", "logo-mavipe.png",
    "logo-mavipe@2x.jpg", "logo-mavipe.jpg",
    "logo-mavipe.jpeg", "logo-mavipe@2x.jpeg",
]

LINKEDIN_CANDIDATES = [
    "linkedin@2x.svg","linkedin.svg",
    "linkedin@2x.png","linkedin.png",
    "linkedin@2x.jpg","linkedin.jpg",
    "linkedin_mono.svg","linkedin_mono_green.svg",
]

CAROUSEL_INTERVAL_SEC = 3

EMPRESA_CAPTIONS = [
    "Empresa Certificada do Ministério da Defesa",
    "Plataforma Geoespacial DAP ATLAS — Multipropósito, Proprietária e Certificada como Produto Estratégico de Defesa",
    "Setor de Defesa — Inteligência, Vigilância e Reconhecimento",
]

# Defaults (evita NameError no contato)
MAVIPE_EMAIL = globals().get("MAVIPE_EMAIL") or "contato@dapsat.com"
MAVIPE_ADDRESS = globals().get("MAVIPE_ADDRESS") or "Av. Cassiano Ricardo, 601 / Sala 123, São José dos Campos, SP 12246-870 - Brasil"

# ================== UTILS ==================
def find_first(candidates) -> str | None:
    for name in candidates:
        p = Path(name)
        if p.exists() and p.stat().st_size > 0:
            return str(p)
    return None

def guess_mime(path: Path) -> str:
    ext = path.suffix.lower()
    if ext == ".png": return "image/png"
    if ext in (".jpg", ".jpeg"): return "image/jpeg"
    if ext == ".svg": return "image/svg+xml"
    if ext == ".webp": return "image/webp"
    return "application/octet-stream"

def as_data_uri(path_str: str | Path) -> str:
    p = Path(path_str)
    b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:{guess_mime(p)};base64,{b64}"

def gather_empresa_images(max_n: int = 2) -> list[str]:
    base = [
        "empresa1.jpg", "empresa1.jpeg", "empresa1.png",
        "empresa2.jpg", "empresa2.jpeg", "empresa2.png",
    ]
    found = [p for p in base if Path(p).exists() and Path(p).stat().st_size > 0]
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
        "parceiro*.png", "parceiro*.jpg", "parceiro*.jpeg",
        "certificacao*.png", "certificacao*.jpg", "certificacao*.jpeg",
        "logo*.png", "logo*.jpg", "logo*.jpeg",
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
        return st.query_params.get(name, default)
    except Exception:
        vals = st.experimental_get_query_params().get(name, [default])
        return vals[0] if isinstance(vals, list) else vals

def caption_from_path(path_str: str) -> str:
    name = Path(path_str).stem
    name = re.sub(r"[_\-]+", " ", name).strip()
    return " ".join(w.capitalize() for w in name.split()) or "Imagem"

def empresa_caption(idx: int, path_str: str) -> str:
    if 0 <= idx < len(EMPRESA_CAPTIONS) and (EMPRESA_CAPTIONS[idx] or "").strip():
        return EMPRESA_CAPTIONS[idx].strip()
    return caption_from_path(path_str)

def news_thumbnail_src(path_str: str | None) -> str | None:
    if not path_str:
        return None
    p = Path(path_str)
    return as_data_uri(str(p)) if p.exists() and p.stat().st_size > 0 else None

def render_dots(n: int, active_index: int) -> str:
    parts = []
    for i in range(n):
        cls = "active" if i == active_index else ""
        parts.append(f"<span class='{cls}'></span>")
    return "".join(parts)

# ================== CSS (UNIFICADO + HOTFIX) ==================
st.markdown('''
<style>
html, body, [data-testid="stAppViewContainer"]{background:#0b1221; overflow-x:hidden;}
#MainMenu, header, footer {visibility:hidden;}
.block-container{padding:0!important; max-width:100%!important}

/* Navbar */
.navbar{
  position:fixed; top:0; left:0; right:0; z-index:1000;
  display:flex; justify-content:space-between; align-items:center;
  height:64px; padding:8px 8px !important; overflow:visible;
  background:rgba(8,16,33,.35); backdrop-filter:saturate(160%) blur(10px);
  border-bottom:1px solid rgba(255,255,255,.08);
}
.nav-left{ position:relative; height:64px; display:flex; align-items:center; gap:12px; }
.nav-right a{ color:#d6def5; text-decoration:none; margin-left:18px }

/* Logo */
.nav-logo{
  position:relative; height:140px; width:auto; display:block;
  transform:translateY(3px); image-rendering:auto;
  filter:drop-shadow(0 4px 8px rgba(0,0,0,.45));
  z-index:2;
}

/* Hero */
.hero{position:relative; height:100vh; min-height:640px; width:100vw; left:50%; margin-left:-50vw; overflow:hidden}
.hero iframe{position:absolute; top:50%; left:50%; width:177.777vw; height:100vh; transform:translate(-50%,-50%); pointer-events:none}
.hero .overlay{position:absolute; inset:0; background:radial-gradient(85% 60% at 30% 30%, rgba(20,30,55,.0) 0%, rgba(8,16,33,.48) 68%, rgba(8,16,33,.86) 100%); z-index:1}
.hero .content{position:absolute; z-index:2; inset:0; display:flex; align-items:center; padding:0 8vw; color:#e8eefc}
.kicker{color:#cfe7ff; font-weight:600; margin-bottom:10px}
h1.hero-title{font-size:clamp(36px,6vw,64px); line-height:1.05; margin:0 0 12px}
.highlight{color:#34d399}
.hero-sub{font-size:clamp(16px,2.2vw,20px); color:#b9c6e6; max-width:70ch; line-height:1.35; text-wrap:balance;}

.cta, .btn{display:inline-block; padding:12px 18px; border-radius:12px; text-decoration:none; font-weight:700; margin-right:10px}
.cta{background:#34d399; color:#05131a}
.btn{border:1px solid rgba(255,255,255,.18); color:#e6eefc; background:rgba(255,255,255,.06)}
.section{padding:72px 8vw; border-top:1px solid rgba(255,255,255,.07)}
.lead{color:#b9c6e6}

/* Carrossel */
.carousel-dots{display:flex; gap:8px; justify-content:center; margin-top:10px}
.carousel-dots span{width:8px; height:8px; border-radius:50%; background:#5d6a8b; display:inline-block; opacity:.6}
.carousel-dots span.active{background:#e6eefc; opacity:1}
.carousel-main{ width:100%; height:400px; object-fit:cover; border-radius:12px; box-shadow:0 8px 28px rgba(0,0,0,.35); }
.carousel-caption{ text-align:center; color:#b9c6e6; font-size:0.95rem; margin-top:8px; }

/* ===== Cards de Setores (com ícone) ===== */
#setores.section h2{
  color:#0b1221; font-size:2rem; font-weight:800; text-align:center; margin:0 0 .8rem;
}
#setores.section h2::after{
  content:""; display:block; width:68px; height:3px; background:#4EA8DE; margin:.65rem auto 0; border-radius:3px;
}
#setores .subtitle{
  color:#334155; text-align:center; font-size:1.05rem; margin:0 0 2rem 0; opacity:1;
}
.sector-card-grid{ display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:24px; margin-top:1rem; }
.sector-card{
  background:#f8fafc; border:1px solid rgba(0,0,0,.06); border-radius:16px; padding:20px 22px;
  box-shadow:0 10px 24px rgba(0,0,0,.08); transition:transform .2s, box-shadow .2s; color:#0b1221;
}
.sector-card:hover{ transform:translateY(-4px); box-shadow:0 14px 36px rgba(0,0,0,.12); }
.sector-head{ display:flex; align-items:center; gap:12px; margin-bottom:8px; }
.sector-icon{
  flex:0 0 auto; width:56px; height:56px; border-radius:10px; display:flex; align-items:center; justify-content:center;
  background:#fff; border:1px solid rgba(0,0,0,.08); overflow:hidden;
}
.sector-icon img, .sector-icon svg{ width:100% !important; height:100% !important; object-fit:contain; display:block; }
.sector-icon span{ font-size:28px; line-height:1; }
.sector-card h3{ margin:0; font-size:1.3rem; font-weight:800; color:#0b1221; }
.sector-card p{ color:#334155; margin:.3rem 0 .6rem 0; }
.sector-card ul{ margin:0; padding-left:1.2rem; list-style:disc; color:#475569; }
.sector-card li{ margin:.45rem 0; font-size:.97rem; }

/* APLICAÇÕES */
.sol-img{
  width:100%; max-width:520px; height:auto; border-radius:12px;
  box-shadow:0 8px 24px rgba(0,0,0,.10); display:block; margin:0 auto;
  transition: transform 0.45s ease, box-shadow 0.45s ease;
}
.sol-img.sol-left:hover{transform-origin:left center;transform:scale(1.4);z-index:5;position:relative;box-shadow:0 18px 44px rgba(0,0,0,.35);}
.sol-img.sol-right:hover{transform-origin:right center;transform:scale(1.4);z-index:5;position:relative;box-shadow:0 18px 44px rgba(0,0,0,.35);}
.sol-cap{text-align:center;color:#334155;font-size:0.92rem;margin-top:8px;}
.sol-title{font-weight:800;font-size:1.15rem;color:#0b1221;margin:0 0 6px;}
.sol-text{font-size:0.98rem;line-height:1.55;color:#334155;margin:6px 0 0;}
.sol-box{padding:24px 0;border-bottom:1px dashed rgba(0,0,0,.08);}

/* Responsivo */
@media (max-width:980px){
  .sector-card-grid{ grid-template-columns:1fr; }
}
@media (max-width:768px){
  .navbar, .nav-left{ height:56px; }
  .nav-logo{ height:110px; transform:translateY(-10px); }
  .hero iframe{width:177.777vh; height:100vh; max-width:300vw;}
  .section{padding:56px 5vw;}
}
</style>
''', unsafe_allow_html=True)

# ================== NAVBAR ==================
def pick_logo_path() -> str | None:
    logo_2x = Path("logo-mavipe@2x.png")
    logo_1x = Path("logo-mavipe.png")
    if logo_2x.exists() and logo_2x.stat().st_size > 0: return str(logo_2x)
    if logo_1x.exists() and logo_1x.stat().st_size > 0: return str(logo_1x)
    return find_first(LOGO_CANDIDATES)

logo_path = pick_logo_path()
logo_left_tag = (
    f'<img src="{as_data_uri(logo_path)}" alt="MAVIPE logo" class="nav-logo"/>' if logo_path
    else '<div class="brand" style="color:#e6eefc; font-weight:700">MAVIPE</div>'
)
st.markdown(f'''
<div class="navbar">
  <div class="nav-left">{logo_left_tag}</div>
  <div class="nav-right">
    <a href="#empresa">Empresa</a>
    <a href="#solucao">Solução</a>
    <a href="#setores">Setores & Aplicações</a>
    <a href="#parceiros">Parceiros</a>
    <a href="#newsroom">Imprensa</a>
    <a class="cta" href="#contato" style="background:#34d399; color:#05131a; font-weight:700; padding:10px 14px; border-radius:10px; text-decoration:none">Contato</a>
  </div>
</div>
''', unsafe_allow_html=True)

# ================== HERO ==================
st.markdown(f'''
<div class="hero">
  <iframe src="https://www.youtube.com/embed/{YOUTUBE_ID}?autoplay=1&mute=1&loop=1&controls=0&modestbranding=1&playsinline=1&rel=0&showinfo=0&playlist={YOUTUBE_ID}"
          title="MAVIPE hero" frameborder="0" allow="autoplay; fullscreen; picture-in-picture"></iframe>
  <div class="overlay"></div>
  <div class="content">
    <div>
      <div class="kicker">Monitoramento de Metano • Detecção de Mudanças • Monitoramento Terrestre e Marítimo • Imagens ópticas e SAR de alta resolução</div>
      <h1 class="hero-title">Transformando dados geoespaciais em <span class="highlight">informações acionáveis</span></h1>
      <div class="hero-sub">
        A MAVIPE integra <b>IA</b>, <b>imagens de satélite</b> (ópticas e SAR), <b>dados operacionais de inteligência</b> e <b>dados meteoceanográficos</b> para entregar <b>informações confiáveis</b> de monitoramento por satélite para os setores <b>ambiental</b>, <b>petróleo e gás</b> e <b>defesa e segurança</b>.
      </div>
    </div>
  </div>
</div>
''', unsafe_allow_html=True)

# ================== EMPRESA ==================
st.markdown('<div id="empresa"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)

col_text, col_img = st.columns([1, 1])

with col_text:
    st.markdown(
        "<h1 style='font-size:2.2rem; font-weight:700; color:#00E3A5; margin-bottom:12px;'>MAVIPE Sistemas Espaciais</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <p style="color:#b9c6e6; line-height:1.6; font-size:1rem; text-align:justify;">
        A <b>MAVIPE Sistemas Espaciais</b> é uma empresa de base tecnológica que emprega soluções próprias, no <b>estado-da-arte</b>, baseadas em <b>IA</b>, <b>aprendizado de máquinas</b> e <b>dados operacionais de inteligência</b> para a realização de <b>monitoramentos por satélite</b> em ambientes terrestre e marítimo.
        </p>
        <p style="color:#b9c6e6; line-height:1.6; font-size:1rem; text-align:justify;">
        Seus profissionais possuem anos de experiência em <b>centros de operações espaciais</b>, P&D e gestão de ativos. Expertise em <b>meio ambiente</b>, <b>petróleo e gás</b> e <b>defesa e segurança</b>.
        </p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
    '<p style="text-align:center; margin:16px 0;">'
    '<a href="https://www.linkedin.com/company/mavipe" target="_blank" rel="noopener" '
    'style="color:#9fc6ff; text-decoration:underline; font-weight:600;">'
    'LinkedIn da MAVIPE</a></p>',
    unsafe_allow_html=True
)


with col_img:
    imgs = gather_empresa_images(max_n=2)
    if "emp_idx" not in st.session_state: st.session_state.emp_idx = 0
    if "emp_last_tick" not in st.session_state: st.session_state.emp_last_tick = time.time()

    thumb_param = get_query_param("thumb", None)
    if thumb_param is not None:
        try:
            new_idx = int(thumb_param)
            if imgs:
                st.session_state.emp_idx = new_idx % len(imgs)
                st.session_state.emp_last_tick = time.time()
        except Exception:
            pass

    if imgs:
        n = len(imgs)
        idx = st.session_state.emp_idx % n
        uri = as_data_uri(imgs[idx])
        st.markdown(f"<img class='carousel-main' src='{uri}' alt='Empresa {idx+1}/{n}'/>", unsafe_allow_html=True)
        st.markdown(f"<div class='carousel-caption'>{empresa_caption(idx, imgs[idx])}</div>", unsafe_allow_html=True)

        bcol1, bcol2, bcol3 = st.columns([1, 6, 1])
        with bcol1:
            if st.button("◀", key="emp_prev"):
                st.session_state.emp_idx = (idx - 1) % n
                st.session_state.emp_last_tick = time.time()
                st.rerun()
        with bcol3:
            if st.button("▶", key="emp_next"):
                st.session_state.emp_idx = (idx + 1) % n
                st.session_state.emp_last_tick = time.time()
                st.rerun()
        with bcol2:
            st.markdown(f"<div class='carousel-dots'>{render_dots(n, idx)}</div>", unsafe_allow_html=True)

        now = time.time()
        if now - st.session_state.emp_last_tick >= CAROUSEL_INTERVAL_SEC:
            st.session_state.emp_idx = (idx + 1) % n
            st.session_state.emp_last_tick = now
            time.sleep(0.05)
            st.rerun()
    else:
        st.info("Coloque 1–2 imagens começando por 'empresa' (ex.: empresa1.jpg, empresa2.png).")

st.markdown('</div>', unsafe_allow_html=True)

# ================== SOLUÇÃO ==================
st.markdown('<div id="solucao"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="section" style="background:#ffffff; color:#0b1221; border-top:1px solid rgba(0,0,0,.06); padding:24px 8vw;">
  <h2 style="margin:0 0 8px;">Solução</h2>
</div>
""", unsafe_allow_html=True)
st.markdown("""
<div class="section" style="padding:56px 8vw;">
  <h2 style="margin:0 0 10px; color:#00E3A5; font-weight:800;">Plataforma DAP ATLAS</h2>
  <p class="lead" style="margin:0 0 14px;">
    A Plataforma DAP ATLAS é uma solução georreferenciada de última geração desenvolvida pela MAVIPE Sistemas Espaciais, projetada para o monitoramento remoto terrestre e marítimo em larga escala.
  </p>
  <ul style="color:#cbd6f2; margin:0 0 0 1.1rem; line-height:1.5">
    <li><b>Tecnologias empregadas:</b> IA, aprendizado de máquina e métodos estatísticos tradicionais.</li>
    <li><b>Origem e propósito:</b> concebida originalmente como uma <b>plataforma ISR (Intelligence, Surveillance and Reconnaissance)</b> de apoio a <b>C2</b>, voltada a centros de operações espaciais e ao segmento de <b>Defesa &amp; Segurança</b>.</li>
    <li><b>Aplicações:</b> expandida para monitoramento ambiental, infraestruturas críticas, energia, logística e petróleo & gás.</li>
    <li><b>Entregáveis:</b> análises, dados e insights acionáveis para apoiar decisões de gestores e autoridades.</li>
  </ul>
</div>
""", unsafe_allow_html=True)

# ================== SETORES & APLICAÇÕES (SEÇÃO ÚNICA) ==================
# cria ícone padrão de óleo&gás (caso não exista)
icons_dir = Path("icons"); icons_dir.mkdir(exist_ok=True)
oleogas_path = icons_dir / "oleogas.svg"
if not oleogas_path.exists():
    oleogas_path.write_text("""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" fill="none">
  <rect width="64" height="64" rx="12" fill="#0b1221"/>
  <path d="M14 48h36v2H14v-2Zm12-14h4v14h-4V34Zm18 0h4v14h-4V34ZM20 22h24l-2 12H22l-2-12Zm3 0 2 10h14l2-10H23Zm6-8h6v6h-6v-6Zm-2 6h10v2h-10v-2Z" fill="#4EA8DE"/>
</svg>
""".strip(), encoding="utf-8")

def sector_icon_data_uri(slug: str) -> str | None:
    candidates=[]
    for ext in ("svg","png","jpg","jpeg","webp"):
        candidates += [
            f"icons/{slug}.{ext}", f"icons/{slug}_icon.{ext}", f"icons/icon-{slug}.{ext}",
            f"{slug}.{ext}", f"{slug}_icon.{ext}", f"icon-{slug}.{ext}",
        ]
    for c in candidates:
        p = Path(c)
        if p.exists() and p.stat().st_size > 0:
            return as_data_uri(p)
    return None

SECTORS = [
    {"slug":"oleogas","title":"Óleo & Gás",
     "desc":"Monitoramento de Emissão de Metano e Monitoramento de Ativos Críticos.",
     "bullets":[
        "Monitoramento de Emissão de Metano — OGMP 2.0 Nível 5.",
        "Supervisão contínua de dutos e instalações estratégicas com IA e análise temporal.",
        "Detecção de Derramamento de Petróleo e suporte à resposta ambiental."
     ]},
    {"slug":"defesa","title":"Defesa & Segurança",
     "desc":"Maritime & Ground Domain Awareness com alertas e análise assistida por IA.",
     "bullets":[
        "Monitoramento de embarcações não-colaborativas (dark ships).",
        "Monitoramento de fronteiras terrestres e marítimas.",
        "Acompanhamento de instalações civis e militares críticas."
     ]},
    {"slug":"ambiental","title":"Ambiental",
     "desc":"Monitoramento de emissões e riscos ambientais.",
     "bullets":[
        "Detecção de metano em aterros sanitários e áreas de resíduos.",
        "Acompanhamento de desmatamento e mudanças no uso do solo.",
        "Monitoramento de desastres ambientais como enchentes e derramamentos."
     ]},
]

SOLUTIONS = [
    {
        "title": "Monitoramento de Metano — OGMP 2.0 (Nível 5)",
        "desc": (
            "<ul style='margin:.4rem 0 0 1.1rem'>"
            "<li>Parceria com a canadense GHGSat, líder mundial em satélites SWIR.</li>"
            "<li>Detecção e medição de plumas de metano em ambientes onshore e offshore.</li>"
            "<li>Dashboards, APIs e relatórios compatíveis com OGMP 2.0 (ONU).</li>"
            "<li>Permite o reporte em nível L5 (site level).</li>"
            "<li>Apoia empresas na conquista do Selo Gold Standard em gestão de metano.</li>"
            "</ul>"
        ),
        "img": "solucao1.png",
        "caption": "Exemplo de Relatório de Metano (OGMP 2.0)",
        "reverse": False,
    },
    {
        "title": "Derramamento de Óleo no Mar",
        "desc": (
            "<ul style='margin:.4rem 0 0 1.1rem'>"
            "<li>Emprego de imagens de satélites do tipo radar (SAR), combinadas à IA.</li>"
            "<li>Detecção de derramamentos de óleo no mar, dia e noite (24/7).</li>"
            "<li>Inclusão de metadados, nível de confiança e recomendações operacionais.</li>"
            "<li>Exibição da imagem da Área de Interesse (AOI) com características detectadas e sobrepostas.</li>"
            "<li>Dados apresentados em tabela e resumo conciso para apoiar a resposta ambiental e identificar a fonte causadora.</li>"
            "</ul>"
        ),
        "img": "solucao2.png",
        "caption": "Tela da plataforma DAP ATLAS",
        "reverse": True,
    },
    {
        "title": "Detecção de Mudanças",
        "desc": "Detecção automática de mudanças utilizando imagens ópticas de altíssima resolução.",
        "img": "solucao3.png",
        "caption": "Fluxo de quantificação e evidências",
        "reverse": False,
    },
    {
        "title": "Inteligência, Vigilância e Reconhecimento (ISR)",
        "desc": (
             "<ul style='margin:.4rem 0 0 1.1rem'>"
             "<li>Inteligência para Comando e Controle (C2).</li>"
             "<li>Monitoramento remoto por satélite em ambientes terrestres e marítimos.</li>"
             "<li>Fusão de imagens ópticas e SAR com dados AIS, RF e meteoceanográficos.</li>"
             "<li>Detecção de navios não colaborativos (dark ships), fronteiras e instalações sensíveis.</li>"
             "<li>Operação contínua dia e noite, 24/7.</li>"
             "<li>Relatório Situacional (SITREP) com alvos e eventos sobrepostos.</li>"
             "<li>Suporte imediato à decisão e acionamento de vetores de defesa e segurança.</li>"
             "</ul>"
),
        "img": "solucao4.png",
        "caption": "Mudanças e alertas priorizados",
        "reverse": True,
    },
]

st.markdown('<div id="setores" class="section" style="background:#ffffff; color:#0b1221; border-top:1px solid rgba(0,0,0,.06); padding:48px 8vw;">', unsafe_allow_html=True)
st.markdown('<h2>Setores & Aplicações</h2>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Óleo &amp; Gás • Defesa &amp; Segurança • Monitoramento Ambiental</p>', unsafe_allow_html=True)

# ---- Grid dos Setores (sem indentação para não virar code-block) ----
fallback_by_slug = {"oleogas":"🛢️","defesa":"🛡️","ambiental":"🌎"}
cards_html = ['<div class="sector-card-grid">']
for s in SECTORS:
    data_uri = sector_icon_data_uri(s["slug"])
    icon_html = (
        f'<div class="sector-icon"><img src="{data_uri}" alt="{s["slug"]}"/></div>'
        if data_uri else
        f'<div class="sector-icon"><span>{fallback_by_slug.get(s["slug"], "📡")}</span></div>'
    )
    bullets = "".join(f"<li>{b}</li>" for b in s["bullets"])
    cards_html.append(
        f'<div id="{s["slug"]}" class="sector-card">'
        f'<div class="sector-head">{icon_html}<h3>{s["title"]}</h3></div>'
        f'<p>{s["desc"]}</p>'
        f'<ul>{bullets}</ul>'
        f'</div>'
    )
cards_html.append('</div>')
st.markdown("".join(cards_html), unsafe_allow_html=True)

# ---- Aplicações ----
st.markdown("<hr style='margin:3rem 0; border:0; border-top:1px solid rgba(0,0,0,.08);'/>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center; font-weight:700; color:#0b1221;'>Aplicações</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#334155;'>Quatro ofertas principais — cada uma com resultados e entregáveis claros, prontos para operação.</p>", unsafe_allow_html=True)

for s in SOLUTIONS:
    st.markdown('<div class="sol-box">', unsafe_allow_html=True)
    if s["reverse"]:
        col_text, col_img = st.columns([1.2, 1], gap="large")
    else:
        col_img, col_text = st.columns([1, 1.2], gap="large")

    with col_img:
        p = Path(s["img"])
        if p.exists() and p.stat().st_size > 0:
            img_dir_class = "sol-left" if not s["reverse"] else "sol-right"
            st.markdown(f"<img class='sol-img {img_dir_class}' src='{as_data_uri(p)}' alt='{s['title']}'/>", unsafe_allow_html=True)
            st.markdown(f"<div class='sol-cap'>{s['caption']}</div>", unsafe_allow_html=True)
        else:
            st.info(f"Imagem não encontrada ({s['img']}).")

    with col_text:
        st.markdown(f"<div class='sol-title'>{s['title']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sol-text'>{s['desc']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ================== PARCEIROS ==================
st.markdown('<div id="parceiros"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="section partners-cases-section" style="background:#ffffff; color:#0b1221; border-top:1px solid rgba(0,0,0,.06); padding:16px 8vw;">
<h2 style="margin-top:0; margin-bottom:8px;">Parceiros</h2>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.parcases-img{
  width:50%; max-width:520px; height:auto; border-radius:12px;
  box-shadow:0 8px 24px rgba(0,0,0,.12); display:block; margin:0 auto;
}
.parcapes-caption{ text-align:center; color:#0b1221; font-size:0.95rem; margin-top:10px; line-height:1.4; }
</style>
""", unsafe_allow_html=True)

with st.container():
    partners_img = "partners.png"
    if Path(partners_img).exists() and Path(partners_img).stat().st_size > 0:
        st.markdown(
            f"<img class='parcases-img' src='{as_data_uri(partners_img)}' alt='Parceiros — BlackSky &amp; GHGSat'/>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='parcapes-caption'>Provedores de Dados Espaciais</div>", unsafe_allow_html=True)
    else:
        st.info("Imagem de parceiros não encontrada (partners.png).")

# ================== 📰 NEWSROOM ==================
st.markdown('<div id="newsroom"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Newsroom")

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")

NEWS_ITEMS = [
    {
        "title": "MAVIPE Assina Contrato com a PETROBRAS para Monitoramento de Metano por Satélite",
        "date": "2025-08-26",
        "summary": (
            "Em 26 de agosto de 2025, a MAVIPE Sistemas Espaciais assinou contrato com a PETROBRAS "
            "para realizar o monitoramento de metano por satélite aplicado aos ambientes onshore e offshore, "
            "em conformidade com o nível L5 (site level) da OGMP 2.0."
        ),
        "link": "",
        "image": "news1.png",
    },
    {
        "title": "A MAVIPE é Certificada pelo Ministério da Defesa como Empresa Estratégica de Defesa (EED)",
        "date": "2024-12-20",
        "summary": (
            "A certificação do Ministério da Defesa reforça o caráter estratégico das soluções da MAVIPE "
            "e consolida sua atuação no ecossistema espacial e de defesa."
        ),
        "link": "",
        "image": "news2.png",
    },
]

for it in NEWS_ITEMS:
    it["slug"] = slugify(it["title"])

ARTICLE_BODY = {}
json_path = Path("news_articles.json")
if json_path.exists():
    with open(json_path, "r", encoding="utf-8") as f:
        ARTICLE_BODY = json.load(f)

st.markdown("""
<style>
.news-grid { display:grid; grid-template-columns:repeat(auto-fit, minmax(360px,1fr)); gap:20px; margin-top:18px; }
.news-card { background:rgba(255,255,255,.02); border:1px solid rgba(255,255,255,.08);
  border-radius:14px; overflow:hidden; display:flex; flex-direction:column;
  box-shadow:0 6px 18px rgba(0,0,0,.25); transition:transform .2s ease; }
.news-card:hover { transform:translateY(-3px); }
.news-thumb { width:100%; height:180px; background:#ffffff; overflow:hidden; }
.news-thumb img { width:100%; height:100%; object-fit:contain; display:block; }
.news-body { padding:14px 16px; flex-grow:1; }
.news-title { color:#e6eefc; font-weight:700; margin:0 0 6px; font-size:1rem; }
.news-meta { color:#9fb0d4; font-size:.85rem; margin-bottom:8px; }
.news-summary { color:#cbd6f2; font-size:.94rem; margin-bottom:14px; line-height:1.4; }
.news-actions { padding:0 16px 14px 16px; display:flex; gap:10px; flex-wrap:wrap; }
.button-primary { display:inline-block; padding:10px 14px; border-radius:10px;
  text-decoration:none; background:#34d399; color:#05131a; font-weight:700; }
.article-wrap { max-width:1000px; margin:8px auto 24px auto; background:rgba(255,255,255,.02);
  border:1px solid rgba(255,255,255,.08); border-radius:14px; box-shadow:0 6px 18px rgba(0,0,0,.25); }
.article-hero { width:100%; height:320px; background:#fff; overflow:hidden;
  border-top-left-radius:14px; border-top-right-radius:14px; }
.article-hero img { width:100%; height:100%; object-fit:contain; }
.article-body { padding:22px 26px 26px 26px; }
.article-title { margin:0; color:#e6eefc; font-size:1.6rem; font-weight:800; }
.article-meta { color:#9fb0d4; margin:6px 0 16px 0; }
.article-text { color:#cbd6f2; font-size:1.05rem; line-height:1.6; }
.backlink { text-decoration:none; color:#9fb0d4; }
</style>
""", unsafe_allow_html=True)

qp = st.query_params
open_slug = qp.get("news", None)

if open_slug:
    item = next((x for x in NEWS_ITEMS if x["slug"] == open_slug), None)
    if item:
        st.markdown(f'<p><a class="backlink" href="./#newsroom">← Voltar para a Newsroom</a></p>', unsafe_allow_html=True)
        img_path = Path(item["image"])
        hero = ""
        if img_path.exists() and img_path.stat().st_size > 0:
            hero = f"<div class='article-hero'><img src='{as_data_uri(img_path)}' alt='hero'/></div>"
        body = ARTICLE_BODY.get(item["slug"], {}).get("body", item["summary"])
        article_html = f"""
        <div class="article-wrap">
          {hero}
          <div class="article-body">
            <h2 class="article-title">{item['title']}</h2>
            <div class="article-meta">{item['date']}</div>
            <div class="article-text">{body}</div>
            <div class="article-actions">
              <a class="button-primary" href="./#newsroom">Voltar</a>
            </div>
          </div>
        </div>
        """
        st.markdown(article_html, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()

# Grade principal da Newsroom
cards = ['<div class="news-grid">']
for item in NEWS_ITEMS:
    img_path = Path(item["image"])
    if img_path.exists() and img_path.stat().st_size > 0:
        thumb = f"<div class='news-thumb'><img src='{as_data_uri(img_path)}' alt='thumb'/></div>"
    else:
        thumb = "<div class='news-thumb' style='background:#ffffff'></div>"
    internal_href = f"?news={item['slug']}#newsroom"
    card_html = f"""
    <div class="news-card">
      <a href="{internal_href}" style="text-decoration:none;color:inherit">
        {thumb}
        <div class="news-body">
          <div class="news-title">{item['title']}</div>
          <div class="news-meta">{item['date']}</div>
          <div class="news-summary">{item['summary']}</div>
        </div>
      </a>
      <div class="news-actions">
        <a class="button-primary" href="{internal_href}">Ler mais</a>
      </div>
    </div>
    """.strip()
    cards.append(card_html)
cards.append("</div>")
st.markdown("\n".join(cards), unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ================== CONTATO ==================
st.markdown('<div id="contato"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Contato")

c1, c2 = st.columns(2)
with c1:
    nome = st.text_input("Seu nome")
    email = st.text_input("E-mail corporativo")
with c2:
    org = st.text_input("Organização")
    phone = st.text_input("WhatsApp/Telefone (opcional)")
msg = st.text_area("Qual desafio você quer resolver?")

if st.button("Enviar e-mail"):
    subject = "MAVIPE — Contato"
    body = f"Nome: {nome}\\nEmail: {email}\\nOrg: {org}\\nTelefone: {phone}\\nMensagem:\\n{msg}"
    st.success("Clique abaixo para abrir seu e-mail:")
    st.markdown(f"[Abrir e-mail](mailto:{MAVIPE_EMAIL}?subject={quote(subject)}&body={quote(body)})")

st.markdown(f"""
<style>
.contact-card{{ margin-top:18px; padding:16px 18px; border-radius:12px;
  background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.18);
  box-shadow:0 8px 24px rgba(0,0,0,.35); color:#e6eefc; }}
.contact-card h4{{ margin:0 0 8px 0; font-size:1.05rem; font-weight:800; color:#fff; }}
.contact-item{{ margin:.25rem 0; color:#cbd6f2; }}
.contact-item a{{ color:#9fd8c8; text-decoration:none; }}
.contact-item a:hover{{ text-decoration:underline; }}
</style>
<div class="contact-card">
  <h4>Informações de contato</h4>
  <div class="contact-item"><strong>Endereço:</strong> {MAVIPE_ADDRESS}</div>
  <div class="contact-item"><strong>E-mail:</strong> <a href="mailto:{MAVIPE_EMAIL}">{MAVIPE_EMAIL}</a></div>
</div>
""", unsafe_allow_html=True)

st.caption("© MAVIPE Space Systems · DAP ATLAS")



