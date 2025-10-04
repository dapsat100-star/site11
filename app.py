# -*- coding: utf-8 -*-
# app.py — MAVIPE Space Systems · HERO YouTube + logo no canto superior direito

import streamlit as st
from urllib.parse import quote
from pathlib import Path

# ================== CONFIG ==================
st.set_page_config(
    page_title="MAVIPE Space Systems — DAP ATLAS",
    page_icon=None,                 # sem favicon
    layout="wide",
    initial_sidebar_state="collapsed",
)

YOUTUBE_ID = "Ulrl6TFaWtA"         # https://youtu.be/Ulrl6TFaWtA
LOGO_FILE  = "logo-mavipe.jpeg"     # troque para "logo-mavipe.png" se for PNG

# ================== CSS ==================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] { height:100%; background:#0b1221; overflow-x:hidden; }
#MainMenu, header, footer {visibility:hidden;}
.block-container { padding:0 !important; max-width:100% !important; }

/* Navbar (simples, sem logo) */
.navbar { position: fixed; top:0; left:0; right:0; z-index:1000; display:flex; align-items:center; justify-content:space-between;
          padding:14px 36px; background: rgba(8,16,33,.35); backdrop-filter: saturate(160%) blur(10px);
          border-bottom:1px solid rgba(255,255,255,.08); }
.nav-left .brand {line-height:1; color:#e6eefc; font-weight:700; letter-spacing:.5px;}
.nav-right {display:flex; align-items:center; gap:28px;}
.nav-link {color:#d6def5; text-decoration:none; font-weight:500;}
.nav-link:hover{opacity:.92}
.cta { background:#34d399; color:#05131a; font-weight:700; padding:10px 16px; border-radius:12px; text-decoration:none; }
.cta:hover { filter:brightness(1.05); }

/* HERO YouTube */
.hero-wrapper { position:relative; height:100vh; min-height:640px; width:100vw; left:50%; right:50%;
                margin-left:-50vw; margin-right:-50vw; overflow:hidden; }
#yt-hero { position:absolute; top:50%; left:50%; width:177.777vw; height:100vh; transform:translate(-50%,-50%); pointer-events:none; }
.hero-overlay { position:absolute; inset:0; background: radial-gradient(85% 60% at 30% 30%, rgba(20,30,55,.0) 0%, rgba(8,16,33,.48) 68%, rgba(8,16,33,.86) 100%); z-index:1; }
.hero-content { position:absolute; inset:0; z-index:2; display:flex; align-items:center; padding:0 8vw; color:#e8eefc; }

/* Título/Sub */
.kicker{ color:#cfe7ff; opacity:.92; font-weight:600; margin-bottom:10px; }
h1.hero-title{ font-size: clamp(36px, 6vw, 64px); line-height:1.05; margin:0 0 12px 0; }
.highlight{ color:#34d399; }
.hero-sub{ font-size: clamp(16px, 2.2vw, 20px); color:#b9c6e6; max-width: 70ch; }
.hero-actions{ margin-top:22px; display:flex; gap:14px; flex-wrap:wrap; }
.btn{ display:inline-block; padding:12px 18px; border-radius:12px; text-decoration:none; font-weight:700;
      border:1px solid rgba(255,255,255,.18); color:#e6eefc; background: rgba(255,255,255,.06); }
.btn:hover{ background: rgba(255,255,255,.12); }

/* === LOGO no canto superior direito do HERO === */
.hero-logo {
  position:absolute; z-index:3;           /* acima do overlay e do vídeo */
  top:16px; right:24px;                    /* canto superior direito */
  width: clamp(110px, 12vw, 200px);        /* responsivo: 110–200px */
  height:auto;
  opacity: .95;
  filter: drop-shadow(0 6px 14px rgba(0,0,0,.45));
  pointer-events:none;                     /* não bloqueia cliques nos botões */
}

/* Seções */
.section { padding:72px 8vw; border-top:1px solid rgba(255,255,255,.07); }
.lead { color:#b9c6e6; }
.card {border:1px solid rgba(255,255,255,.12); border-radius:18px; padding:18px; background:#0f1830;}
.grid3 { display:grid; grid-template-columns: repeat(3, 1fr); gap:18px; }

@media (max-width:980px){
  .grid3{ grid-template-columns:1fr; }
  .navbar{padding:12px 18px}
  .nav-right{gap:16px}
}
</style>
""", unsafe_allow_html=True)

# ================== NAVBAR ==================
st.markdown("""
<div class="navbar">
  <div class="nav-left"><div class="brand">MAVIPE Space Systems</div></div>
  <div class="nav-right">
    <a class="nav-link" href="#empresa">Empresa</a>
    <a class="nav-link" href="#solucao">Solução</a>
    <a class="nav-link" href="#setores">Setores</a>
    <a class="cta" href="#contato">Agendar demo</a>
  </div>
</div>
""", unsafe_allow_html=True)

# ================== HERO (YouTube) ==================
# Se a logo existir, injetamos a <img> posicionada no topo direito
logo_exists = Path(LOGO_FILE).exists()
logo_tag = f'<img class="hero-logo" src="{LOGO_FILE}" alt="MAVIPE logo"/>' if logo_exists else ""

st.markdown(f"""
<div class="hero-wrapper">
  <iframe id="yt-hero"
      src="https://www.youtube.com/embed/{YOUTUBE_ID}?autoplay=1&mute=1&loop=1&controls=0&modestbranding=1&playsinline=1&rel=0&showinfo=0&playlist={YOUTUBE_ID}"
      title="MAVIPE hero" frameborder="0" allow="autoplay; fullscreen; picture-in-picture">
  </iframe>

  <div class="hero-overlay"></div>

  {logo_tag}  <!-- LOGO no canto superior direito -->

  <div class="hero-content">
    <div>
      <div class="kicker">GeoINT • InSAR • Metano (OGMP 2.0 L5)</div>
      <h1 class="hero-title">Transformando dados geoespaciais em <span class="highlight">informações acionáveis</span></h1>
      <div class="hero-sub">
        A MAVIPE integra <b>IA</b>, <b>imagens de satélite</b> (ópticas e SAR) e dados operacionais para entregar
        <b>insights confiáveis</b> em monitoramento ambiental, emissões de metano e integridade de ativos — no ritmo da sua operação.
      </div>
      <div class="hero-actions">
        <a class="cta" href="#contato">Agendar demo</a>
        <a class="btn" href="#solucao">Explorar solução</a>
        <a class="btn" href="#setores">Casos de uso</a>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ================== SEÇÃO EMPRESA ==================
st.markdown('<div id="empresa"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Empresa")
st.markdown("<p class='lead'>Unimos experiência em operações de satélites, GeoINT e análise avançada para transformar dados em resultados práticos.</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ================== SOLUÇÃO ==================
st.markdown('<div id="solucao"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Solução — DAP ATLAS")
st.markdown("""
<div class="grid3">
  <div class="card"><h4>Metano (CH₄)</h4><p>Monitoramento OGMP 2.0 L5: detecção por fonte, fluxo (kg/h), incerteza, Q/C e relatórios georreferenciados.</p></div>
  <div class="card"><h4>InSAR</h4><p>Deformação do terreno e estruturas (mm/mês), mapas de risco e recomendações para integridade de ativos.</p></div>
  <div class="card"><h4>GeoINT</h4><p>Camadas contextuais, detecção, alertas e dashboards — exportações em PDF e integrações via API/CSV.</p></div>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# ================== SETORES ==================
st.markdown('<div id="setores"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Setores / Casos de uso")
st.markdown("- Óleo & Gás • Portos e Costas • Mineração • Defesa & Segurança • Monitoramento Ambiental.")
st.markdown("</div>", unsafe_allow_html=True)

# ================== CONTATO ==================
st.markdown('<div id="contato"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Agendar demo")
col1, col2 = st.columns(2)
with col1:
    nome = st.text_input("Seu nome")
    email = st.text_input("E-mail corporativo")
with col2:
    org = st.text_input("Organização")
    phone = st.text_input("WhatsApp/Telefone (opcional)")
msg = st.text_area("Qual desafio você quer resolver?")
if st.button("Enviar e-mail"):
    subject = "MAVIPE — Agendar demo"
    body = f"Nome: {nome}\\nEmail: {email}\\nOrg: {org}\\nTelefone: {phone}\\nMensagem:\\n{msg}"
    st.success("Clique abaixo para abrir seu e-mail:")
    st.markdown(f"[Abrir e-mail](mailto:contato@dapsat.com?subject={quote(subject)}&body={quote(body)})")
st.caption("© MAVIPE Space Systems · DAP ATLAS")

