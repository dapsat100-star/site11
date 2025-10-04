# app.py — Landing DAP Ocean Framework™ com HERO em vídeo (flat)
# Coloque no MESMO diretório: app.py, hero.mp4, logo-mavipe.png
import streamlit as st
from urllib.parse import quote
from pathlib import Path

st.set_page_config(page_title="DAP Ocean Framework™", page_icon="logo-mavipe.png", layout="wide")

# ---------- Diagnóstico rápido (remova se quiser) ----------
p = Path("hero.mp4")
with st.sidebar:
    st.write("🎬 hero.mp4 existe?", p.exists())
    if p.exists():
        st.write("Tamanho (MB):", round(p.stat().st_size / (1024*1024), 2))
        with st.expander("Ver player (teste)"):
            st.video("hero.mp4")

# ================== CSS ==================
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] { height:100%; background:#0b1221; }
#MainMenu, header, footer {visibility:hidden;}
.block-container { padding:0 !important; max-width:100% !important; }

/* Navbar */
.navbar {
  position: fixed; top:0; left:0; right:0; z-index:1000;
  display:flex; align-items:center; justify-content:space-between;
  padding:14px 36px;
  background: rgba(8,16,33,.35);
  backdrop-filter: saturate(160%) blur(10px);
  border-bottom:1px solid rgba(255,255,255,.08);
}
.nav-left {display:flex; align-items:center; gap:14px;}
.nav-left img {height: 44px; width:auto;}
.nav-left .brand {line-height:1; color:#e6eefc; font-weight:700; letter-spacing:.5px;}
.nav-right {display:flex; align-items:center; gap:28px;}
.nav-link {color:#d6def5; text-decoration:none; font-weight:500;}
.nav-link:hover{opacity:.92}
.cta {
  background:#34d399; color:#05131a; font-weight:700;
  padding:10px 16px; border-radius:12px; text-decoration:none;
}
.cta:hover{ filter:brightness(1.05); }

/* HERO com vídeo */
.hero { position:relative; height:100vh; min-height:640px; overflow:hidden; }
.hero video {
  position:absolute; top:50%; left:50%;
  min-width:100%; min-height:100%; width:auto; height:auto;
  transform:translate(-50%, -50%); object-fit:cover;
  filter:brightness(.58);
}
.hero-overlay {
  position:absolute; inset:0;
  background: radial-gradient(85% 60% at 30% 30%, rgba(20,30,55,.0) 0%, rgba(8,16,33,.48) 68%, rgba(8,16,33,.86) 100%);
  z-index:1;
}
.hero-content {
  position:absolute; z-index:2; inset:0;
  display:flex; align-items:center;
  padding:0 8vw; color:#e8eefc;
}
.kicker{ color:#cfe7ff; opacity:.92; font-weight:600; margin-bottom:10px; }
h1.hero-title{ font-size: clamp(36px, 6vw, 64px); line-height:1.05; margin:0 0 12px 0; }
.highlight{ color:#34d399; }
.hero-sub{ font-size: clamp(16px, 2.2vw, 20px); color:#b9c6e6; max-width: 70ch; }
.hero-actions{ margin-top:22px; display:flex; gap:14px; flex-wrap:wrap; }
.btn {
  display:inline-block; padding:12px 18px; border-radius:12px; text-decoration:none; font-weight:700;
  border:1px solid rgba(255,255,255,.18); color:#e6eefc; background: rgba(255,255,255,.06);
}
.btn:hover{ background: rgba(255,255,255,.12); }

/* Seções */
.section { padding:72px 8vw; border-top:1px solid rgba(255,255,255,.07); }
.lead { color:#b9c6e6; }
.card {border:1px solid rgba(255,255,255,.12); border-radius:18px; padding:18px; background:#0f1830;}
.grid3 { display:grid; grid-template-columns: repeat(3, 1fr); gap:18px; }
@media (max-width: 980px){ .grid3{ grid-template-columns:1fr; } .navbar{padding:12px 18px} .nav-right{gap:16px} }
</style>
""", unsafe_allow_html=True)

# ================== NAVBAR ==================
st.markdown("""
<div class="navbar">
  <div class="nav-left">
    <img src="logo-mavipe.png" alt="logo"/>
    <div class="brand">DAP SPACE SYSTEMS</div>
  </div>
  <div class="nav-right">
    <a class="nav-link" href="#company">Company</a>
    <a class="nav-link" href="#solution">Solution</a>
    <a class="nav-link" href="#industries">Industries</a>
    <a class="cta" href="#contact">Contact Sales</a>
  </div>
</div>
""", unsafe_allow_html=True)

# ================== HERO (vídeo) ==================
# Dica: se quiser usar um link público em vez de arquivo local, troque src="hero.mp4" por src="https://SEU_CDN/hero.mp4"
st.markdown("""
<div class="hero">
  <video autoplay loop muted playsinline preload="auto">
    <source src="hero.mp4" type="video/mp4">
  </video>
  <div class="hero-overlay"></div>
  <div class="hero-content">
    <div>
      <div class="kicker">Maritime & Ground Domain Awareness</div>
      <h1 class="hero-title">Maritime Domain Awareness<br>Made Accessible by<br>
        <span class="highlight">DAP Ocean Framework™</span>
      </h1>
      <div class="hero-sub">
        Multi-sensor data fusion (SAR, optical, AIS, RF, weather) into one actionable framework.
        DAP Ocean Framework™ delivers detections, tracks and alerts you can trust.
      </div>
      <div class="hero-actions">
        <a class="cta" href="#contact">Contact Sales</a>
        <a class="btn" href="#solution">Explore Solution</a>
        <a class="btn" href="#industries">Use Cases</a>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ================== SEÇÕES ==================
st.markdown('<div id="company"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Company")
st.markdown("<p class='lead'>Brief institutional overview, mission, team, certifications…</p>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div id="solution"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Solution — DAP Ocean Framework™")
st.markdown("""
<div class="grid3">
  <div class="card"><h4>Ingestion</h4><p>AIS, SAR/optical imagery, RF, metocean.</p></div>
  <div class="card"><h4>Analytics</h4><p>Vessel detection/tracking, anomaly routes, risk scoring.</p></div>
  <div class="card"><h4>Delivery</h4><p>APIs, dashboards, alerts and reports.</p></div>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div id="industries"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Industries / Use Cases")
st.markdown("- Port security • Oil & Gas offshore • IUU fishing • SAR operations • Border/coast guard.")
st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div id="contact"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Contact Sales")
col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Name")
    email = st.text_input("Work email")
with col2:
    org = st.text_input("Organization")
    phone = st.text_input("Phone/WhatsApp (optional)")
msg = st.text_area("What challenge are you trying to solve?")
if st.button("Send email"):
    subject = "DAP Ocean Framework — Contact"
    body = f"Name: {name}\\nEmail: {email}\\nOrg: {org}\\nPhone: {phone}\\nMessage:\\n{msg}"
    st.success("Click the link below to open your email client:")
    st.markdown(f"[Compose email](mailto:contato@dapsat.com?subject={quote(subject)}&body={quote(body)})")
st.caption("© DAP Space Systems · DAP Ocean Framework™")
