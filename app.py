# app.py — MAVIPE Landing Page (Hero + Logo Retina + Carrosséis + Newsroom + Setores)
import base64
import time
import re
from pathlib import Path
from urllib.parse import quote
import streamlit as st

st.set_page_config(page_title="MAVIPE Space Systems — DAP ATLAS", page_icon=None, layout="wide")

# ================== CONFIG ==================
YOUTUBE_ID = "Ulrl6TFaWtA"
# Preferimos o @2x para ficar nítido em telas retina; depois 1x; por fim nomes antigos.
LOGO_CANDIDATES = [
    "logo-mavipe@2x.png",
    "logo-mavipe.png",
    "logo-mavipe@2x.jpg",
    "logo-mavipe.jpg",
    "logo-mavipe.jpeg",
    "logo-mavipe@2x.jpeg",
    "logo-mavipe.png",  # repetido por compatibilidade, não atrapalha
]
CAROUSEL_INTERVAL_SEC = 3      # autoplay Empresa
PARTNER_INTERVAL_SEC  = 3      # autoplay Parceiros

# <<< LEGENDA MANUAL DA EMPRESA (ordem dos slides) >>>
EMPRESA_CAPTIONS = [
    "Empresa Estratégica de Defesa  - Certificação do Ministério da Defesa",
    "Plataforma Geoespacial DAP ATLAS - Multipropósito, Proprietária e Certificada como Produto Estratégico de Defesa",
    "GeoINT & InSAR — integridade",
]

# <<< NEWSROOM: edite aqui as suas notícias >>>
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

# ================== UTILS ==================
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
  height:140px;         /* ajuste aqui para maior/menor */
  width:auto; display:block;
  transform:translateY(-14px);
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
  .nav-logo{ height:110px; transform:translateY(-16px); }
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
@media (max-width:768px){ .thumb{width:92px; height:56px;} }

/* Slide principal com tamanho uniforme */
.carousel-main{ width:100%; height:400px; object-fit:cover; border-radius:12px; box-shadow:0 8px 28px rgba(0,0,0,.35); }
@media (max-width:768px){ .carousel-main{ height:240px; } }

/* Legenda abaixo do slide principal */
.carousel-caption{ text-align:center; color:#b9c6e6; font-size:0.95rem; margin-top:8px; }

/* Parceiros: preservar proporção dos logos */
.carousel-main.partner{ object-fit:contain; background:rgba(255,255,255,.03); }
.thumbs.partner .thumb{ background:rgba(255,255,255,.02); }
.thumbs.partner .thumb img{ object-fit:contain; background:transparent; }

/* === Setores: cards com âncoras === */
.sectors-grid{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; margin-top:18px }
.sector-card{ background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.08); border-radius:16px; padding:16px 18px; }
.sector-card h3{margin:0 0 8px 0; color:#e6eefc}
.sector-card p{margin:0 0 8px 0; color:#b9c6e6}
.sector-card ul{margin:8px 0 0 18px; color:#c7d3f0}
.sector-card li{margin:4px 0}
@media (max-width:980px){ .sectors-grid{grid-template-columns:1fr} }

/* === Newsroom === */
.news-grid{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; margin-top:18px; }
.news-card{ background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.08); border-radius:16px; overflow:hidden; display:flex; flex-direction:column; }
.news-thumb{width:100%; height:160px; object-fit:cover; background:rgba(255,255,255,.02)}
.news-body{padding:14px 16px}
.news-title{color:#e6eefc; font-weight:700; margin:0 0 6px 0}
.news-meta{color:#9fb0d4; font-size:.85rem; margin-bottom:6px}
.news-summary{color:#cbd6f2; font-size:.95rem; margin-bottom:10px}
.news-actions{padding:0 16px 14px 16px}
.news-actions a{display:inline-block; padding:10px 14px; border-radius:10px; text-decoration:none; background:#34d399; color:#05131a; font-weight:700}
@media (max-width:980px){ .news-grid{grid-template-columns:1fr} }
</style>
''', unsafe_allow_html=True)

# ================== NAVBAR (com LOGO à esquerda) ==================
# Retina de verdade: se existir @2x usamos ele (embutido em base64), o CSS mantém altura/posicionamento.
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
    <a class="cta" href="#contato" style="background:#34d399; color:#05131a; font-weight:700; padding:10px 14px; border-radius:10px; text-decoration:none">Agendar demo</a>
  </div>
</div>
''', unsafe_allow_html=True)

# ================== HERO (vídeo sem logo duplicado) ==================
# Removemos o logo do topo direito para evitar duplicação.
logo_tag = ""  # sem logo no hero
if not logo_path:
    st.warning(
        f"Logo não encontrada. Adicione um dos arquivos: logo-mavipe@2x.png, logo-mavipe.png"
    )

st.markdown(f'''
<div class="hero">
  <iframe src="https://www.youtube.com/embed/{YOUTUBE_ID}?autoplay=1&mute=1&loop=1&controls=0&modestbranding=1&playsinline=1&rel=0&showinfo=0&playlist={YOUTUBE_ID}"
          title="MAVIPE hero" frameborder="0" allow="autoplay; fullscreen; picture-in-picture"></iframe>
  <div class="overlay"></div>
  {logo_tag}
  <div class="content">
    <div>
      <div class="kicker">GeoINT • InSAR • Metano (OGMP 2.0 L5)</div>
      <h1 class="hero-title">Transformando dados geoespaciais em <span class="highlight">informações acionáveis</span></h1>
      <div class="hero-sub">A MAVIPE integra <b>IA</b>, <b>imagens de satélite</b> (ópticas e SAR) e dados operacionais para entregar
        <b>insights confiáveis</b> em monitoramento ambiental, emissões de metano e integridade de ativos — no ritmo da sua operação.</div>
      <div style="margin-top:22px">
        <a class="cta" href="#contato">Agendar demo</a>
        <a class="btn" href="#solucao">Explorar solução</a>
        <a class="btn" href="#setores">Casos de uso</a>
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
        "<h1 style='font-size:2.2rem; font-weight:700; color:#e6eefc; margin-bottom:12px;'>DAP Space Systems</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <p style="color:#b9c6e6; line-height:1.6; font-size:1rem;">
        We are a startup company that develops cutting-edge technological solutions for the automated analysis of satellite images
        with optical and SAR-type sensors through its <b>DAP Ocean Framework™</b>. Our company is capable of performing automated
        analytics from any supplier of satellite images on the market for the provision of <b>Maritime Domain Awareness (MDA)</b> and
        <b>Ground Domain Awareness (GDA)</b>, either on the defense or private markets.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        "<a href='#contato' style='display:inline-block; margin-top:18px; background:#34d399; color:#05131a; font-weight:600; padding:12px 20px; border-radius:10px; text-decoration:none;'>Know more</a>",
        unsafe_allow_html=True,
    )

with col_img:
    imgs = gather_empresa_images(max_n=3)
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
            dots = "".join(f"<span class='{'active' if i==idx else ''}'></span>" for i in range(n))
            st.markdown(f"<div class='carousel-dots'>{dots}</div>", unsafe_allow_html=True)

        thumbs_html = "<div class='thumbs'>"
        for i, pth in enumerate(imgs):
            t_uri = as_data_uri(pth)
            active_cls = "active" if i == idx else ""
            thumbs_html += (
                f"<a class='thumb {active_cls}' href='?thumb={i}' title='{caption_from_path(pth)}'>"
                f"<img src='{t_uri}' alt='thumb {i+1}' /></a>"
            )
        thumbs_html += "</div>"
        st.markdown(thumbs_html, unsafe_allow_html=True)

        now = time.time()
        if now - st.session_state.emp_last_tick >= CAROUSEL_INTERVAL_SEC:
            st.session_state.emp_idx = (idx + 1) % n
            st.session_state.emp_last_tick = now
            time.sleep(0.05)
            st.rerun()
    else:
        st.info("Coloque 3 imagens com nomes começando por 'empresa' (ex.: empresa1.jpg, empresa2.png, empresa3.jpeg).")

st.markdown('</div>', unsafe_allow_html=True)

# ================== SOLUÇÃO ==================
st.markdown('<div id="solucao"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Solução — DAP ATLAS")
st.markdown("- Metano (OGMP 2.0 L5): detecção por fonte, fluxo (kg/h), incerteza e Q/C; relatórios georreferenciados.")
st.markdown("- InSAR: deformação (mm/mês), mapas de risco e recomendações para integridade de ativos.")
st.markdown("- GeoINT: camadas contextuais, alertas e dashboards; exportações e integrações por API/CSV.")
st.markdown("</div>", unsafe_allow_html=True)

# ================== PARCEIROS ==================
st.markdown('<div id="parceiros"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Parceiros")

logos = gather_partner_images(max_n=24)
if "part_idx" not in st.session_state: st.session_state.part_idx = 0
if "part_last_tick" not in st.session_state: st.session_state.part_last_tick = time.time()

pthumb_param = get_query_param("pthumb", None)
if pthumb_param is not None and logos:
    try:
        st.session_state.part_idx = int(pthumb_param) % len(logos)
        st.session_state.part_last_tick = time.time()
    except Exception:
        pass

if logos:
    n2 = len(logos)
    j = st.session_state.part_idx % n2
    p_uri = as_data_uri(logos[j])

    st.markdown(f"<img class='carousel-main partner' src='{p_uri}' alt='Parceiro {j+1}/{n2}'/>", unsafe_allow_html=True)
    st.markdown(f"<div class='carousel-caption'>{caption_from_path(logos[j])}</div>", unsafe_allow_html=True)

    d1, d2, d3 = st.columns([1, 6, 1])
    with d1:
        if st.button("◀", key="part_prev"):
            st.session_state.part_idx = (j - 1) % n2
            st.session_state.part_last_tick = time.time()
            st.rerun()
    with d3:
        if st.button("▶", key="part_next"):
            st.session_state.part_idx = (j + 1) % n2
            st.session_state.part_last_tick = time.time()
            st.rerun()
    with d2:
        dots2 = "".join(f"<span class='{'active' if k==j else ''}'></span>" for k in range(n2))
        st.markdown(f"<div class='carousel-dots'>{dots2}</div>", unsafe_allow_html=True)

    pthumbs = "<div class='thumbs partner'>"
    for k, p in enumerate(logos):
        t_uri = as_data_uri(p)
        active = "active" if k == j else ""
        pthumbs += f"<a class='thumb {active}' href='?pthumb={k}' title='{caption_from_path(p)}'><img src='{t_uri}' alt='logo {k+1}'/></a>"
    pthumbs += "</div>"
    st.markdown(pthumbs, unsafe_allow_html=True)

    now = time.time()
    if now - st.session_state.part_last_tick >= PARTNER_INTERVAL_SEC:
        st.session_state.part_idx = (j + 1) % n2
        st.session_state.part_last_tick = now
        time.sleep(0.05)
        st.rerun()
else:
    st.info("Adicione logos na pasta: parceiro*.png/jpg/jpeg, certificacao*.png/jpg/jpeg ou logo*.png/jpg/jpeg.")

st.markdown("</div>", unsafe_allow_html=True)

# ================== NEWSROOM ==================
st.markdown('<div id="newsroom"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Newsroom")

if not NEWS_ITEMS:
    st.info("Adicione notícias em NEWS_ITEMS no topo do arquivo.")
else:
    def sort_key(item): return item.get("date", ""), item.get("title","")
    items = sorted(NEWS_ITEMS, key=sort_key, reverse=True)

    html = '<div class="news-grid">'
    for it in items:
        title   = it.get("title","")
        date    = it.get("date","")
        summary = it.get("summary","")
        link    = it.get("link","#")
        img_src = news_thumbnail_src(it.get("image"))
        thumb   = f"<img class='news-thumb' src='{img_src}' alt='thumb'/>" if img_src else "<div class='news-thumb'></div>"
        html += f"""
        <div class="news-card">
          {thumb}
          <div class="news-body">
            <div class="news-title">{title}</div>
            <div class="news-meta">{date}</div>
            <div class="news-summary">{summary}</div>
          </div>
          <div class="news-actions">
            <a href="{link}" target="_blank" rel="noopener">Ler mais</a>
          </div>
        </div>
        """
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ================== SETORES ==================
st.markdown('<div id="setores"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Setores / Casos de uso")
st.markdown("- Óleo & Gás • Portos & Costas • Mineração • Defesa & Segurança • Monitoramento Ambiental.")

st.markdown('''
<div class="sectors-grid">
  <div id="defesa" class="sector-card">
    <h3>Defense & Security</h3>
    <p>Maritime & Ground Domain Awareness com alertas e análise assistida por IA.</p>
    <ul>
      <li>Contagem de aeronaves/veículos e novas estruturas em instalações</li>
      <li>Vigilância de Área Econômica Exclusiva, combate à pesca ilegal e contrabando</li>
      <li>Detecção de mudanças em fronteiras e áreas sensíveis</li>
    </ul>
  </div>

  <div id="ambiental" class="sector-card">
    <h3>Environmental</h3>
    <p>Monitoramento de emissões e riscos ambientais, baseado em observação da Terra.</p>
    <ul>
      <li>Metano (OGMP 2.0 L5): quantificação por fonte e incerteza</li>
      <li>Cobertura do solo, queimadas e portos &amp; costas</li>
      <li>Dashboards e relatórios georreferenciados</li>
    </ul>
  </div>

  <div id="oleoegas" class="sector-card">
    <h3>Oil &amp; Gas</h3>
    <p>Integridade de ativos e segurança operacional com imagens SAR e ópticas.</p>
    <ul>
      <li>Monitoramento de Emissão de Metano - Dashboards para OGMP 2.0 Nível 5</li>
      <li>Deformação/subsidência em dutos, tanques (fundação), well pads, taludes, pilhas</li>
      <li>Derrames/manchas de óleos</li>
    </ul>
  </div>
</div>
''', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ================== CONTATO ==================
st.markdown('<div id="contato"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Agendar demo")

c1, c2 = st.columns(2)
with c1:
    nome = st.text_input("Seu nome")
    email = st.text_input("E-mail corporativo")
with c2:
    org = st.text_input("Organização")
    phone = st.text_input("WhatsApp/Telefone (opcional)")
msg = st.text_area("Qual desafio você quer resolver?")

if st.button("Enviar e-mail"):
    subject = "MAVIPE — Agendar demo"
    body = f"Nome: {nome}\nEmail: {email}\nOrg: {org}\nTelefone: {phone}\nMensagem:\n{msg}"
    st.success("Clique abaixo para abrir seu e-mail:")
    st.markdown(f"[Abrir e-mail](mailto:contato@dapsat.com?subject={quote(subject)}&body={quote(body)})")

st.caption("© MAVIPE Space Systems · DAP ATLAS")

