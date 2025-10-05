# ================== EMPRESA (texto + CARROSSEL com legenda editável) ==================
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
    # ---- init estado/legendas ----
    if "emp_captions" not in st.session_state:
        st.session_state.emp_captions = load_emp_captions()

    imgs = gather_empresa_images(max_n=3)
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

        # imagem principal + legenda (usa overrides se houver)
        uri = as_data_uri(imgs[idx])
        st.markdown(f"<img class='carousel-main' src='{uri}' alt='Empresa {idx+1}/{n}'/>", unsafe_allow_html=True)
        st.markdown(f"<div class='carousel-caption'>{caption_for(imgs[idx])}</div>", unsafe_allow_html=True)

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

        # thumbnails (?thumb=i)
        thumbs_html = "<div class='thumbs'>"
        for i, pth in enumerate(imgs):
            t_uri = as_data_uri(pth)
            active_cls = "active" if i == idx else ""
            title_txt = caption_for(pth)
            thumbs_html += (
                f"<a class='thumb {active_cls}' href='?thumb={i}' title='{title_txt}'>"
                f"<img src='{t_uri}' alt='thumb {i+1}' /></a>"
            )
        thumbs_html += "</div>"
        st.markdown(thumbs_html, unsafe_allow_html=True)

        # ====== EDITOR DE LEGENDAS (UI) ======
        with st.expander("✎ Editar legendas do carrossel (Empresa)"):
            new_caps = {}
            for i, pth in enumerate(imgs):
                key = Path(pth).stem
                cur = st.session_state.emp_captions.get(key, caption_from_path(pth))
                val = st.text_input(f"Legenda da imagem {i+1} — {key}", value=cur, key=f"cap_in_{i}")
                new_caps[key] = val.strip()

            c1, c2, c3 = st.columns([1,1,2])
            with c1:
                if st.button("Salvar legendas"):
                    # atualiza memória
                    st.session_state.emp_captions.update(new_caps)
                    # tenta salvar no disco para persistir
                    try:
                        Path(CAPTIONS_FILE).write_text(
                            json.dumps(st.session_state.emp_captions, ensure_ascii=False, indent=2),
                            encoding="utf-8"
                        )
                        st.success(f"Legendas salvas em {CAPTIONS_FILE}")
                    except Exception:
                        st.info("Ambiente sem permissão para escrever arquivo. Use o botão ao lado para baixar o JSON.")
                    st.rerun()
            with c2:
                st.download_button(
                    "Baixar JSON de legendas",
                    data=json.dumps(st.session_state.emp_captions, ensure_ascii=False, indent=2),
                    file_name=CAPTIONS_FILE,
                    mime="application/json",
                )

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
