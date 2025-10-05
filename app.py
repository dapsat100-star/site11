# app.py — MAVIPE Landing Page (Hero + Logo Base64 + Carrossel com Legenda Manual)
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

# <<< LEGENDA MANUAL DA EMPRESA (ordem dos slides) >>>
EMPRESA_CAPTIONS = [
    "Empresa Estratégica de Defesa  - Certificação do Ministério da Defesa",            # slide 1 (empresa1.*)
    "Plataforma Geoespacial DAP ATLAS - Multipropósito, Proprietária e Certificada como Produto Estratégico de Defesa",   # slide 2 (empresa2.*)
    "GeoINT & InSAR — integridade",       # slide 3 (empresa3.*)
    # adicione mais linhas se tiver mais imagens
]

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

def caption_from_path(path_str: str) -> str:
    """Fallback: legenda do nome do arquivo."""
    name = Path(path_str).stem
    name = re.sub(r"[_\-]+", " ", name).strip()
    caption = " ".join(w.capitalize() for w in name.split())
    return caption if caption else "Imagem"

def empresa_caption(idx: int, path_str: str) -> str:
    """1) Usa EMPRESA_CAPTIONS[idx] se existir; 2) senão, usa caption_from_path."""
    if 0 <= idx < len(EMPRESA_CAPTIONS):
        cap = (EMPRESA_CAPTIONS[idx] or "").strip()
        if cap:
            return cap
    return caption_from_path(path_str)

# ================== CSS ==================
st.markdown('''
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

.thumbs{display:flex; gap:12px; justify-content:center; margin-top:10px; flex-wrap:wrap}
.thumb{
  display:inline-block; width:120px; height:70px; overflow:hidden; border-radius:8px;
  border:2px solid transparent; opacity:.85; transition:all .2s ease-in-out;
}
.thumb img{width:100%; height:100%; object-fit:cover; display:block}
.thumb:hover{opacity:1; transform:translateY(-2px)}
.thumb.active{border-color:#34d399; box-shadow:0 0 0 2px rgba(52,211,153,.35) inset;}
@media (max-width:768px){
  .thumb{width:92px; height:56px;}
}

/* Slide principal com tamanho uniforme */
.carousel-main{
  width:100%;
  height:400px;            /* desktop */
  object-fit:cover;
  border-radius:12px;
  box-shadow:0 8px 28px rgba(0,0,0,.35);
}
@media (max-width:768px){
  .carousel-main{ height:240px; }  /* mobile */
}

/* Legenda abaixo do slide principal */
.carousel-caption{
  text-align:center;
  color:#b9c6e6;
  font-size:0.95rem;
  margin-top:8px;
}
</style>
''', unsafe_allow_html=True)

# ================== NAVBAR ==================
st.markdown('''
<div class="navbar">
  <div class="nav-left"><div class="brand">MAVIPE Space Systems</div></div>
  <div class="nav-right">
    <a href="#empresa">Empresa</a>
    <a href="#solucao">Solução</a>
    <a href="#setores">Setores</a>
    <a class="cta" href="#contato">Agendar demo</a>
  </div>
</div>
''', unsafe_allow_html=True)

# ================== HERO (vídeo + logo Base64) ==================
logo_path = find_first(LOGO_CANDIDATES)
logo_tag = f'<img class="logo" src="{as_data_uri(logo_path)}" alt="MAVIPE logo"/>' if logo_path else ""
if not logo_path:
    st.warning(f"Logo não encontrada. Adicione um dos arquivos: {', '.join(LOGO_CANDIDATES)}")

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

# ================== EMPRESA (texto + CARROSSEL com legenda) ==================
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

    # Estado do carrossel
    if "emp_idx" not in st.session_state:
        st.session_state.emp_idx = 0
    if "emp_last_tick" not in st.session_state:
        st.session_state.emp_last_tick = time.time()

    # Clique via query param (thumbnails)
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

        # imagem principal (tamanho uniforme) + legenda MANUAL (ou fallback)
        uri = as_data_uri(imgs[idx])
        st.markdown(f"<img class='carousel-main' src='{uri}' alt='Empresa {idx+1}/{n}'/>", unsafe_allow_html=True)
        st.markdown(f"<div class='carousel-caption'>{empresa_caption(idx, imgs[idx])}</div>", unsafe_allow_html=True)

        # setas
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
            dots = "".join(
                f"<span class='{'active' if i==idx else ''}'></span>" for i in range(n)
            )
            st.markdown(f"<div class='carousel-dots'>{dots}</div>", unsafe_allow_html=True)

        # thumbnails clicáveis (?thumb=i)
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

        # autoplay
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

# ================== SETORES ==================
st.markdown('<div id="setores"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Setores / Casos de uso")
st.markdown("- Óleo & Gás • Portos & Costas • Mineração • Defesa & Segurança • Monitoramento Ambiental.")
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
    body = f"Nome: {nome}\\nEmail: {email}\\nOrg: {org}\\nTelefone: {phone}\\nMensagem:\\n{msg}"
    st.success("Clique abaixo para abrir seu e-mail:")
    st.markdown(f"[Abrir e-mail](mailto:contato@dapsat.com?subject={quote(subject)}&body={quote(body)})")

st.caption("© MAVIPE Space Systems · DAP ATLAS")


