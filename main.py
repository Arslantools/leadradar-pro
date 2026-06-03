# main.py - LeadRadar Pro Entry Point
import streamlit as st
import requests
import pandas as pd
import re
import math
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import account as acc

st.set_page_config(page_title="LeadRadar Pro", page_icon="🛰️", layout="wide")

# ── Multilingual Localization Selector ────────────────────────
if "language" not in st.session_state:
    st.session_state["language"] = "en"

lang_opts = {"English": "en", "اردو (Urdu)": "ur", "हिन्दी (Hindi)": "hi"}
selected_lang = st.sidebar.selectbox("🌐 Language / زبان / भाषा", list(lang_opts.keys()), index=list(lang_opts.values()).index(st.session_state["language"]))
lang_code = lang_opts[selected_lang]
st.session_state["language"] = lang_code

# ── Styling (Premium Dark Mode + Radar) ───────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');

.stApp {
    background:
        radial-gradient(circle at 18% 12%, rgba(0,229,176,0.10) 0%, transparent 40%),
        radial-gradient(circle at 85% 18%, rgba(56,138,255,0.10) 0%, transparent 45%),
        linear-gradient(160deg, #0b1120 0%, #070b15 60%, #05070e 100%);
    background-attachment: fixed;
    font-family: 'DM Sans', sans-serif;
    color: #dbe5f2;
}
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.4rem; max-width: 1200px; }

/* ── HERO ─────────────────────────────────────────────── */
.hero {
    display: flex; align-items: center; gap: 34px;
    padding: 30px 38px; margin-bottom: 30px;
    background: linear-gradient(135deg, rgba(255,255,255,0.055), rgba(255,255,255,0.015));
    border: 1px solid rgba(0,229,176,0.20);
    border-radius: 24px; backdrop-filter: blur(14px);
    box-shadow: 0 24px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.07);
    position: relative; overflow: hidden;
}
.hero::before {
    content:''; position:absolute; top:-50%; left:-10%; width:60%; height:200%;
    background: radial-gradient(circle, rgba(0,229,176,0.10), transparent 70%);
    animation: drift 9s ease-in-out infinite;
}
@keyframes drift { 0%,100%{transform:translateX(0);} 50%{transform:translateX(40%);} }
.hero-title {
    font-family:'Sora',sans-serif; font-weight:800; font-size:2.6rem; line-height:1.05;
    letter-spacing:-1px; margin:0; position:relative;
    background: linear-gradient(92deg, #ffffff 8%, #00e5b0 52%, #38a0ff 96%);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
    background-size:200% auto; animation: shine 6s linear infinite;
}
@keyframes shine { to { background-position:200% center; } }
.hero-sub { margin-top:10px; color:#9fb0c8; font-size:1.02rem; max-width:560px; position:relative; }
.badge {
    display:inline-block; margin-top:15px; padding:6px 15px;
    font-family:'Sora',sans-serif; font-size:0.72rem; font-weight:600; letter-spacing:1.5px;
    color:#00e5b0; text-transform:uppercase; position:relative;
    background:rgba(0,229,176,0.10); border:1px solid rgba(0,229,176,0.32); border-radius:30px;
}
.badge .dot { animation: blink 1.4s ease-in-out infinite; }
@keyframes blink { 50% { opacity:.25; } }

/* ── RADAR ─────────────────────────────────────────────── */
.radar { position:relative; width:136px; height:136px; flex:0 0 auto; }
.radar .ring { position:absolute; inset:0; border-radius:50%; border:1px solid rgba(0,229,176,0.25); }
.radar .ring.r2 { inset:23px; } .radar .ring.r3 { inset:46px; }
.radar .sweep {
    position:absolute; inset:0; border-radius:50%;
    background: conic-gradient(from 0deg, rgba(0,229,176,0.5), transparent 38%);
    animation: spin 2.6s linear infinite;
}
.radar .core { position:absolute; top:50%; left:50%; width:12px; height:12px; margin:-6px;
    background:#00e5b0; border-radius:50%; box-shadow:0 0 16px 4px rgba(0,229,176,0.75); }
.radar .blip { position:absolute; width:8px; height:8px; border-radius:50%; background:#38a0ff;
    box-shadow:0 0 10px 2px rgba(56,160,255,0.85); animation: ping 2.6s ease-out infinite; }
.radar .b1 { top:28px; left:90px; animation-delay:.2s; }
.radar .b2 { top:86px; left:36px; animation-delay:1.1s; }
.radar .b3 { top:98px; left:94px; animation-delay:1.8s; }
@keyframes spin { to { transform:rotate(360deg); } }
@keyframes ping { 0%{transform:scale(.4);opacity:0;} 30%{opacity:1;} 100%{transform:scale(1.7);opacity:0;} }

/* ── Section label with accent line ───────────────────── */
.sec {
    font-family:'Sora',sans-serif; font-weight:600; font-size:0.78rem; letter-spacing:2px;
    color:#7d90ad; text-transform:uppercase; margin:6px 0 10px;
    display:flex; align-items:center; gap:10px;
}
.sec::after { content:''; flex:1; height:1px; background:linear-gradient(90deg, rgba(0,229,176,0.4), transparent); }

/* ── Inputs — FORCE dark + visible text ───────────────── */
.stTextInput input {
    background-color: rgba(255,255,255,0.045) !important;
    color: #eaf1fb !important; -webkit-text-fill-color:#eaf1fb !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important; padding: 12px 14px !important; font-size:0.98rem !important;
}
.stTextInput input::placeholder { color:#5e708c !important; -webkit-text-fill-color:#5e708c !important; }
.stTextInput input:focus {
    border-color: rgba(0,229,176,0.6) !important;
    box-shadow: 0 0 0 3px rgba(0,229,176,0.14) !important;
}
.stTextInput div[data-baseweb="input"] { background:transparent !important; border:none !important; }
.stTextInput label { color:#aebccd !important; font-weight:500 !important; }
.stSlider label { color:#aebccd !important; font-weight:500 !important; }

/* ── Button ───────────────────────────────────────────── */
.stButton > button {
    font-family:'Sora',sans-serif; font-weight:700; font-size:1.05rem; letter-spacing:.4px;
    color:#04140f; border:none; border-radius:14px; padding:15px 30px; width:100%;
    background: linear-gradient(95deg, #00e5b0, #25d0ff);
    box-shadow: 0 10px 30px rgba(0,229,176,0.38); transition: all .25s ease;
}
.stButton > button:hover { transform:translateY(-2px); box-shadow:0 18px 44px rgba(0,229,176,0.58); filter:brightness(1.07); }
.stButton > button:active { transform:translateY(0); }

/* ── Metrics ──────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: linear-gradient(160deg, rgba(255,255,255,0.055), rgba(255,255,255,0.015));
    border:1px solid rgba(255,255,255,0.09); border-radius:18px; padding:18px 22px;
    box-shadow: 0 12px 32px rgba(0,0,0,0.32); transition: all .25s ease;
}
[data-testid="stMetric"]:hover { transform:translateY(-3px); border-color:rgba(0,229,176,0.35); }
[data-testid="stMetricValue"] { font-family:'Sora',sans-serif; font-weight:700; color:#00e5b0; }
[data-testid="stMetricLabel"] { color:#9fb0c8; }

/* ── Dataframe / expander / download ──────────────────── */
[data-testid="stDataFrame"] { border:1px solid rgba(255,255,255,0.09); border-radius:14px; overflow:hidden; }
[data-testid="stExpander"] { background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.10); border-radius:14px; }
.stDownloadButton > button {
    background: rgba(0,229,176,0.12); color:#00e5b0; border:1px solid rgba(0,229,176,0.38);
    border-radius:12px; font-family:'Sora',sans-serif; font-weight:600; padding:12px 24px;
}
.stDownloadButton > button:hover { background:rgba(0,229,176,0.2); }
.stAlert { border-radius:14px; }
</style>
""", unsafe_allow_html=True)

# ── HERO PANEL ────────────────────────────────────────────────
st.markdown(f"""
<div class="hero">
  <div class="radar">
    <div class="ring"></div><div class="ring r2"></div><div class="ring r3"></div>
    <div class="sweep"></div><div class="core"></div>
    <div class="blip b1"></div><div class="blip b2"></div><div class="blip b3"></div>
  </div>
  <div>
    <h1 class="hero-title">{acc.t("title", lang_code)}</h1>
    <div class="hero-sub">{acc.t("sub", lang_code)}</div>
    <span class="badge"><span class="dot">●</span>&nbsp; {acc.t("badge_maps", lang_code)}</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Already logged in indicator
if st.session_state.get("user"):
    u = st.session_state["user"]
    st.caption(f"🔐 Logged in as **{u['name']}** ({u['email']}) · Custom signatures active!")
else:
    st.info("💡 **Pro Tip**: Send emails directly from LeadRadar with your own signature and logo! Set up your credentials in **🔐 Account** in the sidebar.")

# ── INPUT PANEL ────────────────────────────────────────────────
left, right = st.columns([1.15, 1], gap="large")

with left:
    st.markdown(f'<div class="sec">🎯 {acc.t("niche", lang_code)} & {acc.t("location", lang_code)}</div>', unsafe_allow_html=True)
    niche_val = st.text_input(acc.t("niche", lang_code), placeholder=acc.t("niche_holder", lang_code))
    location_val = st.text_input(acc.t("location", lang_code), placeholder=acc.t("location_holder", lang_code))
    max_leads = st.select_slider(acc.t("max_leads", lang_code), options=[20, 40, 60, 80, 100], value=40)
    st.caption(acc.t("cost_note", lang_code).format(leads=max_leads, pages=max_leads // 20))

with right:
    st.markdown(f'<div class="sec">🔑 {acc.t("keys_title", lang_code)}</div>', unsafe_allow_html=True)
    user_api_key = st.text_input(acc.t("serp_label", lang_code), type="password",
                                 placeholder=acc.t("serp_holder", lang_code))
    with st.expander(acc.t("adv_metrics", lang_code)):
        st.write(acc.t("adv_sub", lang_code))
        rapidapi_key = st.text_input(acc.t("rapid_key", lang_code), type="password")
        rapidapi_host = st.text_input(acc.t("rapid_host", lang_code), value="domain-authority1.p.rapidapi.com")

st.write("")
go = st.button(acc.t("scan_button", lang_code))

# ── SCRAPING WORKERS & PIPELINES ──────────────────────────────
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}
EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
PHONE_RE = re.compile(r'\+?\d{1,4}[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}')
BAD_END = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".js", ".ico", ".woff", ".ttf")

DUMMY_LOCAL_PARTS = {"youremail", "your-email", "name", "email", "example", "test", "domain",
                     "sample", "demo", "user", "johndoe", "noreply", "no-reply", "johnson"}
DUMMY_DOMAINS = {"example.com", "yourdomain.com", "template.com"}
PROVIDER_DOMAINS = {"wix.com", "squarespace.com", "wordpress.org", "sentry.io"}

def clean_email(em):
    em = em.lower().strip()
    if "@" not in em or any(em.endswith(x) for x in BAD_END):
        return None
    local_part, domain = em.split("@", 1)
    if local_part in DUMMY_LOCAL_PARTS or local_part.startswith("your"):
        return None
    if domain in DUMMY_DOMAINS or any(prov in domain for prov in PROVIDER_DOMAINS):
        return None
    return em

def clean_phone(ph):
    ph = ph.strip()
    if len(re.sub(r'\D', '', ph)) < 8:
        return None
    return ph

def scrape_website_worker(web_url, serpapi_key, rapid_key=None, rapid_host=None):
    res = {
        "email": "N/A", 
        "phone": "N/A", 
        "facebook": "N/A", 
        "linkedin": "N/A", 
        "instagram": "N/A",
        "da": "N/A", 
        "domain_age": "N/A", 
        "google_indexed": "N/A"
    }
    
    if not web_url or web_url == "N/A":
        return res
        
    if not web_url.startswith("http"):
        web_url = "https://" + web_url

    parsed = urlparse(web_url)
    domain = parsed.netloc.replace("www.", "")

    # 1. Fetch free domain metrics
    age_info = acc.get_domain_age(domain)
    if age_info:
        res["domain_age"] = f"{age_info['years']} years"
        
    indexed = acc.get_google_indexed_pages(domain, serpapi_key)
    if indexed is not None:
        res["google_indexed"] = f"{indexed:,}"

    # 2. Fetch Domain Authority (if key provided)
    if rapid_key:
        try:
            r_da = requests.get(
                f"https://{rapid_host}/authority", 
                headers={"X-RapidAPI-Key": rapid_key, "X-RapidAPI-Host": rapid_host},
                params={"domain": domain}, 
                timeout=5
            )
            if r_da.status_code == 200:
                res["da"] = r_da.json().get("da", "N/A")
        except Exception:
            pass

    # 3. Crawler for contacts
    try:
        r = requests.get(web_url, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            
            emails = set()
            phones = set()
            fb = insta = ln = "N/A"

            for em in EMAIL_RE.findall(r.text):
                cleaned = clean_email(em)
                if cleaned:
                    emails.add(cleaned)
                    
            for p in PHONE_RE.findall(r.text):
                cleaned = clean_phone(p)
                if cleaned:
                    phones.add(cleaned)

            for a in soup.find_all("a", href=True):
                href = a["href"].lower()
                if "facebook.com" in href and "sharer" not in href:
                    fb = a["href"]
                elif "linkedin.com" in href and "share" not in href:
                    ln = a["href"]
                elif "instagram.com" in href:
                    insta = a["href"]
                elif href.startswith("mailto:"):
                    em = href.split("mailto:")[1].split("?")[0].strip()
                    cleaned = clean_email(em)
                    if cleaned:
                        emails.add(cleaned)

            if not emails:
                contact_links = []
                for a in soup.find_all("a", href=True):
                    txt = a.get_text().lower()
                    href = a["href"].lower()
                    if any(x in txt or x in href for x in ["contact", "about", "reach", "touch", "support"]):
                        full_c_url = urljoin(web_url, a["href"])
                        if full_c_url not in contact_links:
                            contact_links.append(full_c_url)
                
                for c_url in contact_links[:2]:
                    try:
                        cr = requests.get(c_url, headers=HEADERS, timeout=5)
                        if cr.status_code == 200:
                            for em in EMAIL_RE.findall(cr.text):
                                cleaned = clean_email(em)
                                if cleaned:
                                    emails.add(cleaned)
                            
                            c_soup = BeautifulSoup(cr.text, "html.parser")
                            for ca in c_soup.find_all("a", href=True):
                                chref = ca["href"].lower()
                                if "facebook.com" in chref and fb == "N/A":
                                    fb = ca["href"]
                                elif "linkedin.com" in chref and ln == "N/A":
                                    ln = ca["href"]
                                elif "instagram.com" in chref and insta == "N/A":
                                    insta = ca["href"]
                    except Exception:
                        pass

            res["email"] = ", ".join(sorted(emails)) if emails else "N/A"
            res["phone"] = list(phones)[0] if phones else "N/A"
            res["facebook"] = fb
            res["linkedin"] = ln
            res["instagram"] = insta
    except Exception:
        pass

    return res

# ── ENGINE EXECUTION ──────────────────────────────────────────
if go:
    if niche_val and location_val and user_api_key:
        with st.spinner(acc.t("scanning_status", lang_code)):
            leads_collected = []
            pages_needed = math.ceil(max_leads / 20)
            
            for page in range(pages_needed):
                start = page * 20
                st.caption(acc.t("maps_crawling", lang_code).format(page=page+1, start=start))
                params = {
                    "engine": "google_maps",
                    "q": f"{niche_val} {location_val}",
                    "api_key": user_api_key,
                    "start": start
                }
                try:
                    r = requests.get("https://serpapi.com/search", params=params, timeout=20)
                    if r.status_code == 200:
                        res = r.json()
                        local_results = res.get("local_results", [])
                        if not local_results:
                            break
                        for item in local_results:
                            leads_collected.append({
                                "Business Name": item.get("title", "N/A"),
                                "Website": item.get("website", "N/A"),
                                "Phone Number": item.get("phone", "N/A"),
                                "Address": item.get("address", "N/A"),
                                "Location": location_val,
                                "Rating": item.get("rating", "N/A"),
                                "Reviews": item.get("reviews", "N/A"),
                            })
                            if len(leads_collected) >= max_leads:
                                break
                    else:
                        st.error(f"SerpAPI Error: {r.text}")
                        break
                except Exception as e:
                    st.error(f"SerpAPI connection error: {e}")
                    break
                
                if len(leads_collected) >= max_leads:
                    break

            if not leads_collected:
                st.warning("❌ Data not found.")
            else:
                st.success(acc.t("maps_done", lang_code).format(count=len(leads_collected)))
                
                enriched_leads = []
                with st.spinner(acc.t("scraping_parallel", lang_code)):
                    with ThreadPoolExecutor(max_workers=8) as executer:
                        futures = {
                            executer.submit(
                                scrape_website_worker, 
                                lead["Website"], 
                                user_api_key,
                                rapidapi_key, 
                                rapidapi_host
                            ): lead for lead in leads_collected
                        }
                        
                        for fut in as_completed(futures):
                            lead = futures[fut]
                            try:
                                scrape_res = fut.result()
                                lead["Email Address"] = scrape_res["email"]
                                if lead["Phone Number"] == "N/A" or not lead["Phone Number"]:
                                    lead["Phone Number"] = scrape_res["phone"]
                                lead["Facebook Profile"] = scrape_res["facebook"]
                                lead["LinkedIn Profile"] = scrape_res["linkedin"]
                                lead["Instagram Profile"] = scrape_res["instagram"]
                                lead["Domain Authority"] = scrape_res["da"]
                                lead["Domain Age"] = scrape_res["domain_age"]
                                lead["Google Indexed Pages"] = scrape_res["google_indexed"]
                            except Exception:
                                lead["Email Address"] = "N/A"
                                lead["Facebook Profile"] = "N/A"
                                lead["LinkedIn Profile"] = "N/A"
                                lead["Instagram Profile"] = "N/A"
                                lead["Domain Authority"] = "N/A"
                                lead["Domain Age"] = "N/A"
                                lead["Google Indexed Pages"] = "N/A"
                            
                            enriched_leads.append(lead)

                df = pd.DataFrame(enriched_leads)
                cols_order = [
                    "Business Name", "Email Address", "Phone Number", "Website", 
                    "Domain Authority", "Domain Age", "Google Indexed Pages",
                    "LinkedIn Profile", "Facebook Profile", "Instagram Profile", 
                    "Address", "Location", "Rating", "Reviews"
                ]
                cols_order = [c for c in cols_order if c in df.columns]
                df = df[cols_order]

                total = len(df)
                with_email = int((df["Email Address"] != "N/A").sum())
                with_phone = int((df["Phone Number"] != "N/A").sum())
                with_web = int((df["Website"] != "N/A").sum())

                st.balloons()
                
                st.markdown(f'<div class="sec">📈 {acc.t("results_header", lang_code)}</div>', unsafe_allow_html=True)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Total Leads", total)
                m2.metric("📧 Emails Found", with_email)
                m3.metric("📞 Phones", with_phone)
                m4.metric("🌐 Websites", with_web)

                st.dataframe(df, use_container_width=True, height=480)

                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button(acc.t("download_button", lang_code), csv,
                                   file_name=f"{niche_val}_{location_val}_leads.csv",
                                   mime="text/csv")
    else:
        st.warning(acc.t("fill_warning", lang_code))

