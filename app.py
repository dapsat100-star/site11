# app.py — MAVIPE Carrossel Lite (sem editor, sem upload, sem JSON)
import time, base64, re
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="MAVIPE — Carrosséis", layout="wide")

# ===== CONFIG =====
LOGO_CANDIDATES = ["logo-mavipe.png", "logo-mavipe.jpeg", "logo-mavipe.jpg"]
EMP_AUTOPLAY_SEC   = 3   # intervalo do carrossel Empresa
PART_AUTOPLAY_SEC  = 3   # intervalo do carrossel Parceiros

# ===== UTILS =====
def find_first(cands):
    for n in cands:
        p = Path(n)
        if p.exists() and p.stat().st_size > 0:
            return str(p)
    return None

def guess_mime(p: Path) -> str:
    return "image/png" if p.suffix.lower()==".png" else "image/jpeg"

def as_data_uri(path_str: str) -> str:
    p = Path(path_str)
    b64 = base64.b64encode(p.read_bytes()).decode("utf-8")
    return f"data:{guess_mime(p)};base64,{b64}"

def caption_from_path(path_str: str) -> str:
    name = Path(path_str).stem
    name = re.sub(r"[_\\-]+", " ", name).strip()
    return " ".join(w.capitalize() for w in name.split()) or "Imagem"

def gather_empresa_images(max_n=12):
    results = []
    # prioridade para empresa1/2/3…
    prim = [f"empresa{i}{ext}" for i in range(1, 100) for ext in (".png",".jpg",".jpeg")]
    for n in prim:
        p = Path(n)
        if p.exists() and p.stat().st_size>0:
            results.append(str(p))
    # extras com padrão empresa*.*
    for pat in ("empresa*.png","empresa*.jpg","empresa*.jpeg"):
        for p in sorted(Path(".").glob(pat)):
            s = str(p)
            if s not in results and p.stat().st_size>0:
                results.append(s)
    return results[:max_n]

def gather_partner_images(max_n=24):
    pats = [
        "parceiro*.png","parceiro*.jpg","parceiro*.jpeg",
        "certificacao*.png","certificacao*.jpg","certificacao*.jpeg",
        "logo*.png","logo*.jpg","logo*.jpeg",
    ]
    results = []
    for pat in pats:
        for p in sorted(Path(".").glob(pat)):
            if p.is_file() and p.stat().st_size>0:
                s = str(p)
                if s not in results:
                    results.append(s)
    return results[:max_n]

# ===== CSS =====
st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"]{background:#0b1221; color:#e6eefc}
#MainMenu, header, footer {visibility:hidden;}
.block-container{padding-top:12px; max-width:1100px}

.topbar{display:flex; align-items:center; justify-content:space-between; gap:16px; margin:8px 0 16px 0}
.brand{font-weight:800; letter-spacing:.3px}

.logo{height:40px; width:auto; display:block; filter:drop-shadow(0 3px 10px rgba(0,0,0,.4))}

.section{padding:28px 0; border-top:1px solid rgba(255,255,255,.07)}
h2{margin:0 0 14px 0}

.carousel-main{
  width:100%; height:400px; object-fit:cover;
  border-radius:12px; box-shadow:0 8px 28px rgba(0,0,0,.35);
}
@media (max-width:768px){ .carousel-main{ height:240px; } }

.carousel-main.partner{ object-fit:contain; background:rgba(255,255,255,.03); }

.carousel-caption{ text-align:center; color:#b9c6e6; font-size:.98rem; margin-top:8px; }

.controls{display:flex; align-items:center; justify-content:center; gap:8px; margin:6px 0 4px}
.ctrl-btn{padding:6px 10px; border-radius:10px; border:1px solid rgba(255,255,255,.12); background:rgba(255,255,255,.05); color:#e6eefc}
.ctrl-btn:hover{background:rgba(255,255,255,.09)}

.carousel-dots{display:flex; gap:8px; justify-content:center; margin:8px 0}
.carousel-dots span{width:8px; height:8px; border-radius:50%; background:#5d6a8b; opacity:.6; display:inline-block}
.carousel-dots span.active{background:#e6eefc; opacity:1}

.thumbs{display:flex; gap:12px; justify-content:center; margin-top:8px; flex-wrap:wrap}
.thumb{display:inline-block; width:120px; height:70px; overflow:hidden; border-radius:8px; border:2px solid transparent; opacity:.85}
.thumb img{width:100%; height:100%; object-fit:cover; display:block}
.thumb.active{border-color:#34d399; box-shadow:0 0 0 2px rgba(52,211,153,.35) inset;}
@media (max-width:768px){ .thumb{width:92px; height:56px;} }

/* thumbs de parceiros com fundo leve e contain */
.thumbs.partner .thumb{ background:rgba(255,255,255,.02); }
.thumbs.partner .thumb img{ object-fit:contain; background:transparent; }
</style>
""", unsafe_allow_html=True)

# ===== TOP BAR =====
logo_path = find_first(LOGO_CANDIDATES)
left, right = st.columns([1,1])
with left:
    st.markdown("<div class='topbar'><div class='brand'>MAVIPE Space Systems</div></div>", unsafe_allow_html=True)
with right:
    if logo_path:
        st.markdown(f"<div style='display:flex; justify-content:flex-end'><img class='logo' src='{as_data_uri(logo_path)}' alt='logo'/></div>", unsafe_allow_html=True)

# ===== CARROSSEL EMPRESA =====
st.markdown("<div class='section'></div>", unsafe_allow_html=True)
st.subheader("Sobre a Empresa")

emp_imgs = gather_empresa_images()
if "emp_idx" not in st.session_state: st.session_state.emp_idx = 0
if "emp_last" not in st.session_state: st.session_state.emp_last = time.time()

if emp_imgs:
    n = len(emp_imgs)
    i = st.session_state.emp_idx % n
    st.markdown(f"<img class='carousel-main' src='{as_data_uri(emp_imgs[i])}' alt='Empresa {i+1}/{n}'/>", unsafe_allow_html=True)
    st.markdown(f"<div class='carousel-caption'>{caption_from_path(emp_imgs[i])}</div>", unsafe_allow_html=True)

    c1,c2,c3 = st.columns([1,6,1])
    with c1:
        if st.button("◀", key="emp_prev"): st.session_state.emp_idx = (i-1)%n; st.session_state.emp_last=time.time(); st.rerun()
    with c3:
        if st.button("▶", key="emp_next"): st.session_state.emp_idx = (i+1)%n; st.session_state.emp_last=time.time(); st.rerun()
    with c2:
        dots = "".join(f"<span class='{'active' if k==i else ''}'></span>" for k in range(n))
        st.markdown(f"<div class='carousel-dots'>{dots}</div>", unsafe_allow_html=True)

    thumbs = "<div class='thumbs'>"
    for k,p in enumerate(emp_imgs):
        active = "active" if k==i else ""
        thumbs += f"<a class='thumb {active}' href='?emp={k}'><img src='{as_data_uri(p)}' alt='thumb {k+1}'/></a>"
    thumbs += "</div>"
    st.markdown(thumbs, unsafe_allow_html=True)

    # autoplay simples
    now = time.time()
    if now - st.session_state.emp_last >= EMP_AUTOPLAY_SEC:
        st.session_state.emp_idx = (i+1)%n; st.session_state.emp_last = now; time.sleep(0.05); st.rerun()
else:
    st.info("Coloque imagens nomeadas como: empresa1.jpg, empresa2.png, empresa3.jpeg…")

# ===== CARROSSEL PARCEIROS =====
st.markdown("<div class='section'></div>", unsafe_allow_html=True)
st.subheader("Parceiros e Certificações")

part_imgs = gather_partner_images()
if "part_idx" not in st.session_state: st.session_state.part_idx = 0
if "part_last" not in st.session_state: st.session_state.part_last = time.time()

if part_imgs:
    n2 = len(part_imgs)
    j = st.session_state.part_idx % n2
    st.markdown(f"<img class='carousel-main partner' src='{as_data_uri(part_imgs[j])}' alt='Parceiro {j+1}/{n2}'/>", unsafe_allow_html=True)
    st.markdown(f"<div class='carousel-caption'>{caption_from_path(part_imgs[j])}</div>", unsafe_allow_html=True)

    d1,d2,d3 = st.columns([1,6,1])
    with d1:
        if st.button("◀", key="part_prev"): st.session_state.part_idx=(j-1)%n2; st.session_state.part_last=time.time(); st.rerun()
    with d3:
        if st.button("▶", key="part_next"): st.session_state.part_idx=(j+1)%n2; st.session_state.part_last=time.time(); st.rerun()
    with d2:
        dots2 = "".join(f"<span class='{'active' if k==j else ''}'></span>" for k in range(n2))
        st.markdown(f"<div class='carousel-dots'>{dots2}</div>", unsafe_allow_html=True)

    t2 = "<div class='thumbs partner'>"
    for k,p in enumerate(part_imgs):
        active = "active" if k==j else ""
        t2 += f"<a class='thumb {active}' href='?part={k}'><img src='{as_data_uri(p)}' alt='logo {k+1}'/></a>"
    t2 += "</div>"
    st.markdown(t2, unsafe_allow_html=True)

    now = time.time()
    if now - st.session_state.part_last >= PART_AUTOPLAY_SEC:
        st.session_state.part_idx = (j+1)%n2; st.session_state.part_last = now; time.sleep(0.05); st.rerun()
else:
    st.info("Coloque logos: parceiro*.png/jpg, certificacao*.png/jpg, logo*.png/jpg")

# ===== Query params (navegação por thumbnail) =====
# (Funciona sem precisar de uploads/edição)
try:
    params = st.query_params
    emp_q = params.get("emp", None); part_q = params.get("part", None)
except Exception:
    params = st.experimental_get_query_params()
    emp_q = params.get("emp", [None])[0]; part_q = params.get("part", [None])[0]

if emp_q is not None and emp_imgs:
    try:
        st.session_state.emp_idx = int(emp_q) % len(emp_imgs)
        st.session_state.emp_last = time.time()
        st.rerun()
    except: pass

if part_q is not None and part_imgs:
    try:
        st.session_state.part_idx = int(part_q) % len(part_imgs)
        st.session_state.part_last = time.time()
        st.rerun()
    except: pass
