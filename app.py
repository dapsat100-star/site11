# app.py — MAVIPE Landing Page Completa
import streamlit as st
from urllib.parse import quote
from pathlib import Path
import base64

st.set_page_config(page_title="MAVIPE Space Systems — DAP ATLAS", page_icon=None, layout="wide")

# ===== CONFIG =====
YOUTUBE_ID = "Ulrl6TFaWtA"
LOGO_FILE  = "logo-mavipe.jpeg"   # se for .png, mude para "logo-mavipe.png"

def as_data_uri(path: Path) -> str:
    """Converte a imagem do logo para data URI (Base64) com o MIME correto."""
    mime = "image/png" if path.suffix.lower()==".png" else "image/jpeg"
    b64  = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

# ===== CSS (desktop + mobile) =====
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"]{background:#0b1221; overflow-x:hidden;}
#MainMenu, header, footer {visibility:hidden;}
.block-container{padding:0!important; max-width:100%!important}

.navbar{position:fixed; top:0; left:0; right:0; z-index:1000; display:flex; justify-content:space-between;
  padding:14px 36px; background:rgba(8,16,33,.35); backdrop-filter:saturate(160%) blur(10px);
  border-bottom:1px solid rgba(255,255,255,.08)}
.nav-left .brand{color:#e6eefc; font-weight:700}
.nav-right a{color:#d6def5; text-decoration:none; margin-left:22px}

/* HERO */
.hero{position:relative; height:100vh; min-height:640px; width:100vw; left:50%; margin-left:-50vw; overflow:hidden}
.hero iframe{position:absolute; top:50%; left:50%; width:177.777vw; height:100vh; transform:translate(-50%,-50%); pointer-events:none}
.hero .overlay{position:absolute; inset:0; background:radial-gradient(85% 60% at 30% 30%, rgba(20,30,55,.0) 0%, rgba(8,16,33,.48) 68%, rgba(8,16,33,.86) 100%); z-index:1}
.hero .logo{
  position:absolute; z-index:3; top:18px; right:28px;
  width: clamp(110px, 12vw, 200px); height:auto;
  opacity:.98; filter:drop-shadow(0 6px 14px rgba(0,0,0,.45));
  pointer-events:none;
}
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

/* MOBILE OPTIMIZATION */
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
</style>
""", unsafe_allow_html=True)

# ===== NAVBAR =====
st.markdown("""
<div class="navbar">
  <div class="nav-left"><div class="brand">MAVIPE Space Systems</div></div>
  <div class="nav-right">
    <a href="#empresa">Empresa</a>
    <a href="#solucao">Solução</a>
    <a href="#setores">Setores</a>
    <a class="cta" href="#contato">Agendar demo</a>
  </div>
</div>
""", unsafe_allow_html=True)

# ===== HERO (vídeo + logo Base64) =====
logo_tag = ""
p = Path(LOGO_FILE)
if p.exists() and p.stat().st_size > 0:
    try:
        logo_tag = f'<img class="logo" src="{as_data_uri(p)}" alt="MAVIPE logo"/>'
    except Exception as e:
        st.error(f"Falha ao embutir o logo em Base64: {e}")
else:
    st.warning(f"Logo não encontrada: {LOGO_FILE}. Coloque o arquivo na raiz.")

st.markdown(f"""
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
""", unsafe_allow_html=True)

# ===== EMPRESA =====
st.markdown('<div id="empresa"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="section" style="display:flex; flex-wrap:wrap; align-items:center; gap:48px;">
  <div style="flex:1 1 360px; min-width:280px;">
    <h1 style="font-size:2.2rem; font-weight:700; color:#e6eefc; margin-bottom:12px;">DAP Space Systems</h1>
    <p style="color:#b9c6e6; line-height:1.6; font-size:1rem;">
      We are a startup company that develops cutting-edge technological solutions for the automated analysis of satellite images
      with optical and SAR-type sensors through its <b>DAP Ocean Framework™</b>. Our company is capable of performing automated
      analytics from any supplier of satellite images on the market for the provision of <b>Maritime Domain Awareness (MDA)</b> and
      <b>Ground Domain Awareness (GDA)</b>, either on the defense or private markets.
    </p>
    <a href="#contato" style="display:inline-block; margin-top:18px; background:#34d399; color:#05131a; font-weight:600;
       padding:12px 20px; border-radius:10px; text-decoration:none;">Know more</a>
  </div>
  <div style="flex:1 1 420px; min-width:300px; display:grid; grid-template-columns:1fr 1fr; grid-gap:12px;">
    <img src="empresa1.jpg" style="width:100%; border-radius:10px; object-fit:cover;" alt="Satellite analytics 1"/>
    <img src="empresa2.jpg" style="width:100%; border-radius:10px; object-fit:cover;" alt="Satellite analytics 2"/>
    <img src="empresa3.jpg" style="grid-column:1/3; width:100%; border-radius:10px; object-fit:cover;" alt="Earth from space"/>
  </div>
</div>
""", unsafe_allow_html=True)

# ===== SOLUÇÃO =====
st.markdown('<div id="solucao"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Solução — DAP ATLAS")
st.markdown("- Metano (OGMP 2.0 L5): detecção por fonte, fluxo (kg/h), incerteza e Q/C; relatórios georreferenciados.")
st.markdown("- InSAR: deformação (mm/mês), mapas de risco e recomendações para integridade de ativos.")
st.markdown("- GeoINT: camadas contextuais, alertas e dashboards; exportações e integrações por API/CSV.")
st.markdown("</div>", unsafe_allow_html=True)

# ===== SETORES =====
st.markdown('<div id="setores"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Setores / Casos de uso")
st.markdown("- Óleo & Gás • Portos & Costas • Mineração • Defesa & Segurança • Monitoramento Ambiental.")
st.markdown("</div>", unsafe_allow_html=True)

# ===== CONTATO =====
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

