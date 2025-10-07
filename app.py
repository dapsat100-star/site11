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
PARTNER_INTERVAL_SEC  = 3

EMPRESA_CAPTIONS = [
    "Empresa Certificada do Ministério da Defesa",
    "Plataforma Geoespacial DAP ATLAS — Multipropósito, Proprietária e Certificada como Produto Estratégico de Defesa",
    "GeoINT & InSAR — Integridade",
]

NEWS_ITEMS = [
    {"title":"MAVIPE lança módulo OGMP 2.0 Nível 5","date":"2025-09-15",
     "summary":"Quantificação por fonte, incerteza e Q/C com dashboards e API.",
     "link":"https://example.com/noticia1","image":"news1.jpg"},
    {"title":"Parceria para InSAR de alta cadência","date":"2025-08-22",
     "summary":"Monitoramento de deformação em dutos, tanques e taludes.",
     "link":"https://example.com/noticia2","image":"news2.jpg"},
    {"title":"DAP ATLAS integra alertas marítimos","date":"2025-07-02",
     "summary":"Detecção de navios não colaborativos, spoofing e rendezvous.",
     "link":"https://example.com/noticia3","image":"news3.png"},
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
    if ext == ".png": return "image/png"
    if ext in (".jpg",".jpeg"): return "image/jpeg"
    if ext == ".svg": return "image/svg+xml"
    return "application/octet-stream"

def as_data_uri(path_str: str) -> str:
    p = Path(path_str)
    b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:{guess_mime(p)};base64,{b64}"

def gather_empresa_images(max_n: int = 3) -> list[str]:
    base = ["empresa1.jpg","empresa1.jpeg","empresa1.png",
            "empresa2.jpg","empresa2.jpeg","empresa2.png",
            "empresa3.jpg","empresa3.jpeg","empresa3.png"]
    found = [p for p in base if Path(p).exists() and Path(p).stat().st_size > 0]
    extras = []
    for pat in ("empresa*.jpg","empresa*.jpeg","empresa*.png"):
        for p in sorted(Path(".").glob(pat)):
            if p.is_file() and p.stat().st_size > 0:
                extras.append(str(p))
    seen, ordered = set(), []
    for p in found + extras:
        if p not in seen:
            ordered.append(p); seen.add(p)
        if len(ordered) >= max_n: break
    return ordered

def gather_partner_images(max_n: int = 24) -> list[str]:
    patterns = ["parceiro*.png","parceiro*.jpg","parceiro*.jpeg",
                "certificacao*.png","certificacao*.jpg","certificacao*.jpeg",
                "logo*.png","logo*.jpg","logo*.jpeg"]
    results = []
    for pat in patterns:
        for p in sorted(Path(".").glob(pat)):
            if p.is_file() and p.stat().st_size > 0:
                s = str(p)
                if s not in results: results.append(s)
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
    if not path_str: return None
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
.thumbs{display:flex; gap:12px; justify-content:center; margin-top:10px; flex-wrap:wrap}
.thumb{ display:inline-block; width:120px; height:70px; overflow:hidden; border-radius:8px; border:2px solid transparent; opacity:.85; transition:all .2s ease-in-out; }
.thumb img{width:100%; height:100%; object-fit:cover; display:block}
.thumb:hover{opacity:1; transform:translateY(-2px)}
.thumb.active{border-color:#34d399; box-shadow:0 0 0 2px rgba(52,211,153,.35) inset;}
.carousel-main{ width:100%; height:400px; object-fit:cover; border-radius:12px; box-shadow:0 8px 28px rgba(0,0,0,.35); }
.carousel-caption{ text-align:center; color:#b9c6e6; font-size:0.95rem; margin-top:8px; }

/* Parceiros */
.carousel-main.partner{ object-fit:contain; background:rgba(255,255,255,.03); }
.thumbs.partner .thumb{ background:rgba(255,255,255,.02); }
.thumbs.partner .thumb img{ object-fit:contain; background:transparent; }

/* ===== HOTFIX: Setores ===== */
#setores{ position:relative; isolation:isolate; }
#setores, #setores * { opacity:1 !important; } /* elimina heranças opacas */

/* Newsroom */
.news-grid{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; margin-top:18px; }
.news-card{ background:rgba(255,255,255,.03); border:1px solid rgba(255,255,255,.08); border-radius:16px; overflow:hidden; display:flex; flex-direction:column; }
.news-thumb{width:100%; height:160px; object-fit:cover; background:rgba(255,255,255,.02)}
.news-body{padding:14px 16px}
.news-title{color:#e6eefc; font-weight:700; margin:0 0 6px 0}
.news-meta{color:#9fb0d4; font-size:.85rem; margin-bottom:6px}
.news-summary{color:#cbd6f2; font-size:.95rem; margin-bottom:10px}
.news-actions{padding:0 16px 14px 16px}
.news-actions a{display:inline-block; padding:10px 14px; border-radius:10px; text-decoration:none; background:#34d399; color:#05131a; font-weight:700}

/* Social (LinkedIn) — ícone menor */
.social{ display:flex; justify-content:center; margin-top:24px; }
.social a{
  display:inline-flex; align-items:center; justify-content:center;
  width:44px; height:44px; border-radius:12px;
  background:rgba(255,255,255,.06); border:1px solid rgba(255,255,255,.18);
  backdrop-filter:saturate(140%) blur(6px);
  text-decoration:none; transition:transform .15s ease, box-shadow .15s ease, border-color .15s ease;
}
.social a:hover{ transform:translateY(-2px); border-color:rgba(52,211,153,.65);
  box-shadow:0 8px 18px rgba(0,0,0,.35), 0 0 0 4px rgba(52,211,153,.15) inset; }
.social img{ width:22px; height:22px; display:block; }

/* ===== Cards de Setores (com ícone) ===== */
.sector-card-grid {
  display:grid;
  grid-template-columns:repeat(auto-fit,minmax(300px,1fr));
  gap:20px;
  margin-top:24px;
}
.sector-card{
  background:rgba(255,255,255,.06);
  border:1px solid rgba(255,255,255,.18);
  border-radius:16px;
  padding:18px 20px;
  box-shadow:0 10px 28px rgba(0,0,0,.45);
  transition: transform .2s ease, box-shadow .2s ease;
  color:#e6eefc;
}
.sector-card:hover{ transform:translateY(-4px); box-shadow:0 16px 36px rgba(0,0,0,.55); }
.sector-head{ display:flex; align-items:center; gap:12px; margin-bottom:8px; }
.sector-icon{
  flex:0 0 auto;
  width:42px; height:42px;
  border-radius:10px;
  display:flex; align-items:center; justify-content:center;
  background:rgba(255,255,255,.08);
  border:1px solid rgba(255,255,255,.18);
  overflow:hidden;
}
.sector-icon img{ width:100%; height:100%; object-fit:contain; display:block; }
.sector-icon span{ font-size:22px; line-height:1; }
.sector-card h3{ margin:0; font-size:1.2rem; font-weight:800; color:#fff; }
.sector-card p{ color:#cbd6f2; margin:.3rem 0 .6rem 0; }
.sector-card ul{ margin:0; padding-left:1.2rem; list-style:disc; color:#d5def6; }
.sector-card li{ margin:.45rem 0; font-size:.97rem; }
.sector-card li strong{ color:#fff; }

@media (max-width:980px){
  .news-grid{ grid-template-columns:1fr; }
  .sector-card-grid{ grid-template-columns:1fr; }
}
@media (max-width:768px){
  .navbar, .nav-left{ height:56px; }
  .nav-logo{ height:110px; transform:translateY(-10px); }
  .hero iframe{width:177.777vh; height:100vh; max-width:300vw;}
  .kicker{font-size:14px;} h1.hero-title{font-size:clamp(28px,8vw,36px);}
  .hero-sub{font-size:15px; max-width:100%;}
  .section{padding:56px 5vw;}
  .nav-right a{margin-left:12px;}
  .carousel-main{ height:240px; }
  .social a{ width:40px; height:40px; border-radius:10px; }
  .social img{ width:20px; height:20px; }
}
</style>
''', unsafe_allow_html=True)

# ================== NAVBAR ==================
logo_2x = Path("logo-mavipe@2x.png")
logo_1x = Path("logo-mavipe.png")
def pick_logo_path() -> str | None:
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
    <a href="#parceiros">Parceiros & Casos de Sucesso</a>
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
        "<h1 style='font-size:2.2rem; font-weight:700; color:#e6eefc; margin-bottom:12px;'>MAVIPE Sistemas Espaciais</h1>",
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

    linkedin_path = find_first(LINKEDIN_CANDIDATES)
    if linkedin_path:
        st.markdown(
            f"""
            <div class="social">
              <a href="https://www.linkedin.com/company/mavipe"
                 target="_blank" rel="noopener" aria-label="LinkedIn da MAVIPE">
                <img src="{as_data_uri(linkedin_path)}" alt="LinkedIn"/>
              </a>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="social">
              <a href="https://www.linkedin.com/company/mavipe" target="_blank" rel="noopener"
                 style="color:#9fc6ff; text-decoration:underline; width:auto; height:auto; background:transparent; border:none;">
                 LinkedIn
              </a>
            </div>
            """,
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
            st.markdown(f"<div class='carousel-dots'>{render_dots(n, idx)}</div>", unsafe_allow_html=True)

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

# ================== PARCEIROS & CASOS DE SUCESSO (LADO A LADO — STREAMLIT COLUMNS) ==================
st.markdown('<div id="parceiros"></div>', unsafe_allow_html=True)

# Fundo branco só nesta seção usando uma <div> wrapper
st.markdown("""
<div class="section partners-cases-section" style="background:#ffffff; color:#0b1221; border-top:1px solid rgba(0,0,0,.06); padding:72px 8vw;">
<h2 style="margin-top:0; margin-bottom:8px;">Parceiros & Casos de Sucesso</h2>
<p style="margin:0 0 16px 0; color:#334155; font-size:0.95rem;">Alianças estratégicas e resultados comprovados em campo.</p>
</div>
""", unsafe_allow_html=True)

# CSS local para imagens e legendas
st.markdown("""
<style>
.parcases-img{
  width:100%;
  max-width:520px;
  height:auto;
  border-radius:12px;
  box-shadow:0 8px 24px rgba(0,0,0,.12);
  display:block;
  margin:0 auto;
}
.parcapes-caption{
  text-align:center;
  color:#4b5a7a;
  font-size:0.95rem;
  margin-top:10px;
  line-height:1.4;
}
</style>
""", unsafe_allow_html=True)

# Container visual da seção (fundo branco já foi aplicado no wrapper acima)
with st.container():
    col1, col2 = st.columns([1,1], gap="large")

    partners_img = "partners.png"
    success_img  = "case_petrobras.png"

    # Coluna 1 — Parceiros
    with col1:
        if Path(partners_img).exists() and Path(partners_img).stat().st_size > 0:
            st.markdown(
                f"<img class='parcases-img' src='{as_data_uri(partners_img)}' alt='Parceiros — BlackSky &amp; GHGSat'/>",
                unsafe_allow_html=True
            )
            st.markdown(
                "<div class='parcapes-caption'>Parceiros estratégicos — BlackSky &amp; GHGSat</div>",
                unsafe_allow_html=True
            )
        else:
            st.info("Imagem de parceiros não encontrada (partners.png).")

    # Coluna 2 — Caso de Sucesso
    with col2:
        if Path(success_img).exists() and Path(success_img).stat().st_size > 0:
            st.markdown(
                f"<img class='parcases-img' src='{as_data_uri(success_img)}' alt='Caso de Sucesso — Petrobras OGMP 2.0'/>",
                unsafe_allow_html=True
            )
            st.markdown(
                """<div class='parcapes-caption'>
                Caso de Sucesso — <b>Monitoramento OGMP 2.0 Nível 5 com Petrobras</b><br>
                Detecção e quantificação de emissões de metano (onshore &amp; offshore), com IA, dados satelitais e dashboards georreferenciados.
                </div>""",
                unsafe_allow_html=True
            )
        else:
            st.info("Imagem do caso de sucesso não encontrada (case_petrobras.png).")



# ================== NEWSROOM ==================
st.markdown('<div id="newsroom"></div>', unsafe_allow_html=True)
st.markdown('<div class="section">', unsafe_allow_html=True)
st.header("Newsroom")

if not NEWS_ITEMS:
    st.info("Adicione notícias em NEWS_ITEMS no topo do arquivo.")
else:
    items = sorted(NEWS_ITEMS, key=lambda it: (it.get("date",""), it.get("title","")), reverse=True)
    html = '<div class="news-grid">'
    for it in items:
        title = it.get("title",""); date = it.get("date","")
        summary = it.get("summary",""); link = it.get("link","#")
        img_src = news_thumbnail_src(it.get("image"))
        thumb = f"<img class='news-thumb' src='{img_src}' alt='thumb'/>" if img_src else "<div class='news-thumb'></div>"
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
        </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ================== SETORES & APLICAÇÕES ==================
import textwrap

# ================== SETORES & APLICAÇÕES ==================
st.markdown("""
<style>
#setores.section h2{color:#fff!important;opacity:1!important;font-size:2rem!important;font-weight:800!important;text-align:center!important;margin:0 0 .8rem}
#setores.section h2::after{content:"";display:block;width:68px;height:3px;background:#4EA8DE;margin:.65rem auto 0;border-radius:3px}
#setores .subtitle{color:#f5f7ff!important;text-align:center!important;font-size:1.05rem!important;margin:0 0 1.6rem 0!important;opacity:1!important}

.sector-card-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px}
.sector-card{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.18);border-radius:16px;padding:18px 20px;box-shadow:0 10px 28px rgba(0,0,0,.45);transition:transform .2s, box-shadow .2s}
.sector-card:hover{transform:translateY(-4px);box-shadow:0 16px 36px rgba(0,0,0,.55)}
.sector-head{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.sector-icon img{width:24px;height:24px;display:block}
.sector-icon span{font-size:20px;display:inline-block;line-height:1}
.sector-card h3{margin:0;color:#fff;font-size:1.25rem;font-weight:600}
.sector-card p{color:#e9eefc;margin:.4rem 0 .6rem;line-height:1.5}
.sector-card ul{color:#d5def6;margin:.5rem 0 0 1.1rem}
.sector-card li{margin:.35rem 0;font-size:.96rem;line-height:1.4}
</style>
""", unsafe_allow_html=True)

def sector_icon_data_uri(slug: str) -> str | None:
    candidates=[]
    for ext in ("svg","png","jpg","jpeg"):
        candidates += [
            f"icons/{slug}.{ext}", f"icons/{slug}_icon.{ext}", f"icons/icon-{slug}.{ext}",
            f"{slug}.{ext}", f"{slug}_icon.{ext}", f"icon-{slug}.{ext}",
        ]
    path = find_first(candidates)
    return as_data_uri(path) if path else None

SECTORS = [
    {"slug":"oleogas","title":"Óleo & Gás",
     "desc":"Monitoramento de Emissão de Metano e Monitoramento de Ativos Críticos ",
     "bullets":[
        "Monitoramento de Emissão de Metano — OGMP 2.0 Nível 5",
        "Detecção & Monitoramento de Ativos Críticos: Supervisão contínua de dutos, instalações industriais e outras infraestruturas estratégicas, com detecção de anomalias",
        "Detecção de Derramamento de Petróleo: Identificação rápida de manchas e derrames de óleo no mar com alertas operacionais e suporte à resposta ambiental.",
     ],
     "fallback_emoji":"🛢️"}, 
    
    {"slug":"defesa","title":"Defesa & Segurança",
     "desc":"Maritime & Ground Domain Awareness com alertas e análise assistida por IA.",
     "bullets":[
        "Monitoramento de embarcações não-colaborativas (dark ships)",
        "Monitoramento de fronteiras terrestres e marítimas",        
        "Monitoramento de instalações civis e militares (edificações, portos, aeroportos,etc.) ",
     ],
     "fallback_emoji":"🛡️"},
    {"slug":"ambiental","title":"Ambiental",
     "desc":"Monitoramento de emissões e riscos ambientais.",
     "bullets":[
        "Emissões em Resíduos: Detecção de metano em aterros sanitários e áreas de manejo de resíduos.",
        "Cobertura do solo: Acompanhamento de desmatamento, mudanças no uso do solo e focos de incêndio.",
        "Desastres Ambientais: Monitoramento de eventos extremos,como enchentes e derramamentos de óleo no mar",
     ],
     "fallback_emoji":"🌎"},
]    
st.markdown('<div id="setores" class="section">', unsafe_allow_html=True)
st.header("Setores & Aplicações")
st.markdown(
    '<p class="subtitle">Óleo &amp; Gás • Defesa &amp; Segurança • Monitoramento Ambiental</p>',
    unsafe_allow_html=True
)

# Monta HTML sem indentação que crie bloco de código
cards = ['<div class="sector-card-grid">']
for s in SECTORS:
    data_uri = sector_icon_data_uri(s["slug"])
    icon_html = (f'<div class="sector-icon"><img src="{data_uri}" alt="{s["slug"]}"/></div>'
                 if data_uri else
                 f'<div class="sector-icon"><span>{s["fallback_emoji"]}</span></div>')
    bullets = "".join(f"<li>{b}</li>" for b in s["bullets"])
    tpl = f"""
<div id="{s["slug"]}" class="sector-card">
  <div class="sector-head">
    {icon_html}
    <h3>{s["title"]}</h3>
  </div>
  <p>{s["desc"]}</p>
  <ul>{bullets}</ul>
</div>
"""
    cards.append(textwrap.dedent(tpl).strip())
cards.append("</div>")
html = "\n".join(cards)

# IMPORTANTE: unsafe_allow_html e sem indentação no início das linhas
st.markdown(html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

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
