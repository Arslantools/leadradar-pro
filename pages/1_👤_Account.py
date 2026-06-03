# 1_Account.py
import streamlit as st
import account as acc

st.set_page_config(page_title="Account — LeadRadar Pro", page_icon="🔐", layout="wide")

# ── Multilingual Localization Selector ────────────────────────
if "language" not in st.session_state:
    st.session_state["language"] = "en"

lang_opts = {"English": "en", "اردو (Urdu)": "ur", "हिन्दी (Hindi)": "hi"}
selected_lang = st.sidebar.selectbox("🌐 Language / زبان / भाषा", list(lang_opts.keys()), index=list(lang_opts.values()).index(st.session_state["language"]))
lang_code = lang_opts[selected_lang]
st.session_state["language"] = lang_code

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');
.stApp{background:radial-gradient(circle at 18% 12%,rgba(0,229,176,0.10) 0%,transparent 40%),radial-gradient(circle at 85% 18%,rgba(56,138,255,0.10) 0%,transparent 45%),linear-gradient(160deg,#0b1120 0%,#070b15 60%,#05070e 100%);background-attachment:fixed;font-family:'DM Sans',sans-serif;color:#dbe5f2;}
[data-testid="stHeader"]{background:transparent;} #MainMenu,footer{visibility:hidden;}
.block-container{padding-top:1.4rem;max-width:1000px;}
.hero-title{font-family:'Sora',sans-serif;font-weight:800;font-size:2.1rem;background:linear-gradient(92deg,#fff,#00e5b0,#38a0ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.stTextInput input{background-color:rgba(255,255,255,0.045)!important;color:#eaf1fb!important;-webkit-text-fill-color:#eaf1fb!important;border:1px solid rgba(255,255,255,0.12)!important;border-radius:12px!important;padding:11px 14px!important;}
.stTextInput input::placeholder{color:#5e708c!important;}
.stTextInput input:focus{border-color:rgba(0,229,176,0.6)!important;box-shadow:0 0 0 3px rgba(0,229,176,0.14)!important;}
.stTextInput label{color:#aebccd!important;font-weight:500!important;}
.stButton>button{font-family:'Sora',sans-serif;font-weight:700;color:#04140f;border:none;border-radius:12px;padding:12px 26px;width:100%;background:linear-gradient(95deg,#00e5b0,#25d0ff);box-shadow:0 8px 24px rgba(0,229,176,0.35);transition:all .25s ease;}
.stButton>button:hover{transform:translateY(-2px);filter:brightness(1.06);}
.stTabs [data-baseweb="tab-list"]{gap:8px;}
.stTabs [data-baseweb="tab"]{color:#9fb0c8;}
.card{background:linear-gradient(160deg,rgba(255,255,255,0.05),rgba(255,255,255,0.015));border:1px solid rgba(255,255,255,0.09);border-radius:16px;padding:20px 24px;}
.stAlert{border-radius:12px;}
</style>
""", unsafe_allow_html=True)

st.markdown(f'<h1 class="hero-title">{acc.t("acc_title", lang_code)}</h1>', unsafe_allow_html=True)
st.write(acc.t("acc_sub", lang_code))

# Already logged in?
if st.session_state.get("user"):
    u = st.session_state["user"]
    st.success(acc.t("logged_in_as", lang_code).format(name=u["name"], email=u["email"]))

    st.markdown(f"### {acc.t('profile_title', lang_code)}")
    col1, col2 = st.columns([1.3, 1])
    with col1:
        name = st.text_input(acc.t("full_name", lang_code), value=u.get("name", ""))
        company = st.text_input(acc.t("company", lang_code), value=u.get("company", ""))
        phone = st.text_input(acc.t("phone_num", lang_code), value=u.get("phone", ""))
        
        st.write("---")
        st.markdown(f"**{acc.t('social_links_title', lang_code)}**")
        linkedin = st.text_input(acc.t("social_linkedin", lang_code), value=u.get("linkedin", ""), placeholder="https://linkedin.com/in/username")
        facebook = st.text_input(acc.t("social_facebook", lang_code), value=u.get("facebook", ""), placeholder="https://facebook.com/username")
        instagram = st.text_input(acc.t("social_instagram", lang_code), value=u.get("instagram", ""), placeholder="https://instagram.com/username")
        twitter = st.text_input(acc.t("social_twitter", lang_code), value=u.get("twitter", ""), placeholder="https://x.com/username")
        telegram = st.text_input(acc.t("social_telegram", lang_code), value=u.get("telegram", ""), placeholder="https://t.me/username")
        whatsapp = st.text_input(acc.t("social_whatsapp", lang_code), value=u.get("whatsapp", ""), placeholder="e.g. +923001234567")
        website = st.text_input(acc.t("website_url", lang_code), value=u.get("website", ""), placeholder="https://yourwebsite.com")
        st.write("---")

        st.markdown("**Logo for signature:**")
        mode = st.radio("Logo type", ["Auto (name se monogram)", "Upload my picture/logo"],
                        horizontal=True, label_visibility="collapsed")
        logo_bytes = None
        if mode == "Auto (name se monogram)":
            logo_bytes = acc.make_monogram(company or name or "Lead")
        else:
            up = st.file_uploader("Apni pic ya logo upload karein (PNG/JPG)", type=["png", "jpg", "jpeg"])
            if up:
                logo_bytes = acc.process_upload(up.read())
            elif u.get("logo_b64"):
                logo_bytes = acc.b64_to_bytes(u["logo_b64"])

        if st.button(acc.t("save_profile", lang_code)):
            logo_b64 = acc.bytes_to_b64(logo_bytes) if logo_bytes else u.get("logo_b64", "")
            acc.update_profile(u["email"], name, phone, company, logo_b64, linkedin, facebook, instagram, twitter, website, telegram, whatsapp)
            st.session_state["user"].update({
                "name": name, 
                "phone": phone,
                "company": company, 
                "logo_b64": logo_b64,
                "linkedin": linkedin,
                "facebook": facebook,
                "instagram": instagram,
                "twitter": twitter,
                "telegram": telegram,
                "whatsapp": whatsapp,
                "website": website
            })
            st.success(acc.t("profile_saved", lang_code))
            st.rerun()

    with col2:
        st.markdown(acc.t("logo_preview", lang_code))
        prev = logo_bytes or acc.b64_to_bytes(u.get("logo_b64", ""))
        if prev:
            st.image(prev, width=150)
        else:
            st.caption("Koi logo nahi.")
            
        st.markdown(acc.t("sig_preview", lang_code))
        st.markdown('<div style="background: white; padding: 15px; border-radius: 12px;">', unsafe_allow_html=True)
        st.html(acc.signature_html(u))
        st.markdown('</div>', unsafe_allow_html=True)

    st.write("")
    if st.button(acc.t("logout", lang_code)):
        del st.session_state["user"]
        st.rerun()

else:
    tab1, tab2 = st.tabs([acc.t("login_tab", lang_code), acc.t("signup_tab", lang_code)])

    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        le = st.text_input(acc.t("email", lang_code), key="login_email")
        lp = st.text_input(acc.t("password", lang_code), type="password", key="login_pw")
        if st.button(acc.t("login_tab", lang_code)):
            ok, prof = acc.login(le, lp)
            if ok:
                st.session_state["user"] = prof
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Email ya password galat hai.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("Account banayein — yeh details aapki email signatures aur social icons mein enrich hongi.")
        se = st.text_input(acc.t("email", lang_code) + " *", key="su_email")
        sp = st.text_input(acc.t("password", lang_code) + " * (min 6 chars)", type="password", key="su_pw")
        sn = st.text_input(acc.t("full_name", lang_code) + " *", key="su_name")
        sc = st.text_input(acc.t("company", lang_code), key="su_company")
        sph = st.text_input(acc.t("phone_num", lang_code), key="su_phone")
        
        st.write("---")
        st.markdown("**Social Links (Optional):**")
        s_li = st.text_input(acc.t("social_linkedin", lang_code), key="su_li", placeholder="https://linkedin.com/in/username")
        s_fb = st.text_input(acc.t("social_facebook", lang_code), key="su_fb", placeholder="https://facebook.com/username")
        s_ig = st.text_input(acc.t("social_instagram", lang_code), key="su_ig", placeholder="https://instagram.com/username")
        s_tw = st.text_input(acc.t("social_twitter", lang_code), key="su_tw", placeholder="https://x.com/username")
        s_tel = st.text_input(acc.t("social_telegram", lang_code), key="su_tel", placeholder="https://t.me/username")
        s_wa = st.text_input(acc.t("social_whatsapp", lang_code), key="su_wa", placeholder="e.g. +923001234567")
        s_web = st.text_input(acc.t("website_url", lang_code), key="su_web", placeholder="https://yourwebsite.com")
        st.write("---")
        
        if st.button(acc.t("create_acc", lang_code)):
            if not (se and sp and sn):
                st.warning(acc.t("warning_fields", lang_code))
            else:
                logo_b64 = acc.bytes_to_b64(acc.make_monogram(sc or sn))
                ok, msg = acc.signup(se, sp, sn, sph, sc, logo_b64, s_li, s_fb, s_ig, s_tw, s_web, s_tel, s_wa)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
        st.markdown('</div>', unsafe_allow_html=True)
