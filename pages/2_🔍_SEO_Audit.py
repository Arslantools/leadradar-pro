# 2_SEO_Audit.py
import streamlit as st
import requests
import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import account as acc

st.set_page_config(page_title="SEO Audit — LeadRadar Pro", page_icon="🔍", layout="wide")

# ── Multilingual Localization Selector ────────────────────────
if "language" not in st.session_state:
    st.session_state["language"] = "en"

lang_opts = {"English": "en", "اردو (Urdu)": "ur", "हिन्दी (Hindi)": "hi"}
selected_lang = st.sidebar.selectbox("🌐 Language / زبان / भाषा", list(lang_opts.keys()), index=list(lang_opts.values()).index(st.session_state["language"]))
lang_code = lang_opts[selected_lang]
st.session_state["language"] = lang_code

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}
EMAIL_RE = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
BAD_END = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".js", ".ico", ".woff", ".ttf")
DUMMY = {"youremail", "your-email", "name", "email", "example", "test", "domain",
         "sample", "demo", "user", "johndoe", "noreply", "no-reply", "johnson"}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@400;600;700;800&family=DM+Sans:wght@400;500;600&display=swap');
.stApp{background:radial-gradient(circle at 18% 12%,rgba(0,229,176,0.10) 0%,transparent 40%),radial-gradient(circle at 85% 18%,rgba(56,138,255,0.10) 0%,transparent 45%),linear-gradient(160deg,#0b1120 0%,#070b15 60%,#05070e 100%);background-attachment:fixed;font-family:'DM Sans',sans-serif;color:#dbe5f2;}
[data-testid="stHeader"]{background:transparent;} #MainMenu,footer{visibility:hidden;}
.block-container{padding-top:1.4rem;max-width:1150px;}
.hero{display:flex;align-items:center;gap:26px;padding:26px 34px;margin-bottom:26px;background:linear-gradient(135deg,rgba(255,255,255,0.055),rgba(255,255,255,0.015));border:1px solid rgba(56,160,255,0.22);border-radius:22px;backdrop-filter:blur(14px);}
.hero-title{font-family:'Sora',sans-serif;font-weight:800;font-size:2.1rem;margin:0;background:linear-gradient(92deg,#fff,#38a0ff,#00e5b0);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hero-sub{margin-top:8px;color:#9fb0c8;font-size:0.98rem;max-width:640px;}
.mag{font-size:3rem;animation:float 3s ease-in-out infinite;}@keyframes float{50%{transform:translateY(-8px);}}
.sec{font-family:'Sora',sans-serif;font-weight:600;font-size:0.78rem;letter-spacing:2px;color:#7d90ad;text-transform:uppercase;margin:18px 0 8px;display:flex;align-items:center;gap:10px;}
.sec::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,rgba(56,160,255,0.4),transparent);}
.stTextInput input,.stTextArea textarea{background-color:rgba(255,255,255,0.045)!important;color:#eaf1fb!important;-webkit-text-fill-color:#eaf1fb!important;border:1px solid rgba(255,255,255,0.12)!important;border-radius:12px!important;}
.stTextInput input::placeholder{color:#5e708c!important;}
.stTextInput label,.stTextArea label{color:#aebccd!important;font-weight:500!important;}
.stButton>button{font-family:'Sora',sans-serif;font-weight:700;color:#04140f;border:none;border-radius:14px;padding:13px 28px;width:100%;background:linear-gradient(95deg,#38a0ff,#00e5b0);box-shadow:0 10px 30px rgba(56,160,255,0.38);transition:all .25s ease;}
.stButton>button:hover{transform:translateY(-2px);}
[data-testid="stMetric"]{background:linear-gradient(160deg,rgba(255,255,255,0.055),rgba(255,255,255,0.015));border:1px solid rgba(255,255,255,0.09);border-radius:16px;padding:16px 20px;}
[data-testid="stMetricValue"]{font-family:'Sora',sans-serif;font-weight:700;color:#38a0ff;}
[data-testid="stMetricLabel"]{color:#9fb0c8;}
[data-testid="stExpander"]{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.10);border-radius:14px;}
.card{background:linear-gradient(160deg,rgba(255,255,255,0.05),rgba(255,255,255,0.015));border:1px solid rgba(255,255,255,0.09);border-radius:16px;padding:18px 22px;margin-bottom:12px;}
.ok{color:#00e5b0;}.warn{color:#ffcf5c;}.bad{color:#ff6b7a;}
.chk{padding:7px 0;border-bottom:1px solid rgba(255,255,255,0.06);font-size:0.96rem;}
.score-ring{font-family:'Sora',sans-serif;font-weight:800;font-size:3.4rem;}
.stAlert{border-radius:14px;}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="hero"><div class="mag">🔍</div>
<div><h1 class="hero-title">{acc.t("seo_hero_title", lang_code)}</h1>
<div class="hero-sub">{acc.t("seo_hero_sub", lang_code)}</div></div></div>
""", unsafe_allow_html=True)

# ── Sidebar Multi-API Tab Selector ───────────────────────────
st.sidebar.markdown("### 🛰️ SEO Metric Providers")
api_provider = st.sidebar.selectbox("Select API Provider", ["🔓 Free Crawler Mode", "🚀 RapidAPI (Moz)", "🛡️ Moz V2 Direct", "📊 Semrush API", "🔗 Ahrefs API"])

side_serpapi = st.sidebar.text_input("SerpAPI Key (Optional for index status)", type="password")

provider_keys = {}
if api_provider == "🚀 RapidAPI (Moz)":
    provider_keys["rapid_key"] = st.sidebar.text_input("RapidAPI Key", type="password")
    provider_keys["rapid_host"] = st.sidebar.text_input("RapidAPI Host", value="domain-authority1.p.rapidapi.com")
elif api_provider == "🛡️ Moz V2 Direct":
    provider_keys["moz_id"] = st.sidebar.text_input("Moz Access ID")
    provider_keys["moz_secret"] = st.sidebar.text_input("Moz Secret Key", type="password")
elif api_provider == "📊 Semrush API":
    provider_keys["semrush_key"] = st.sidebar.text_input("Semrush API Key", type="password")
elif api_provider == "🔗 Ahrefs API":
    provider_keys["ahrefs_key"] = st.sidebar.text_input("Ahrefs Bearer Token", type="password")

# ── helpers ────────────────────────────────────────────────────
def good_email(em):
    em = em.lower().strip()
    if "@" not in em or any(em.endswith(x) for x in BAD_END):
        return False
    if em.split("@")[0] in DUMMY or em.startswith("your"):
        return False
    return True


def url_exists(u):
    try:
        return requests.get(u, headers=HEADERS, timeout=8).status_code == 200
    except Exception:
        return False


def find_emails(soup):
    found = set()
    for a in soup.find_all("a", href=True):
        if a["href"].lower().startswith("mailto:"):
            em = a["href"].split("mailto:")[1].split("?")[0].strip()
            if good_email(em):
                found.add(em)
    for em in EMAIL_RE.findall(soup.get_text(" ")):
        if good_email(em):
            found.add(em)
    return sorted(found)


def audit_site(url, serpapi_key=None, provider="🔓 Free Crawler Mode", keys={}):
    if not url.startswith("http"):
        url = "https://" + url
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
    except Exception as e:
        return {"error": f"Website khul nahi rahi: {e}"}
    if r.status_code != 200:
        return {"error": f"Website ne status {r.status_code} diya."}

    soup = BeautifulSoup(r.text, "html.parser")
    parsed = urlparse(url)
    base = parsed.netloc.replace("www.", "")
    scheme = parsed.scheme

    title = (soup.title.string or "").strip() if soup.title and soup.title.string else ""
    md = soup.find("meta", attrs={"name": "description"})
    meta_desc = (md.get("content", "") if md else "").strip()
    h1s = soup.find_all("h1")
    headings = {f"H{i}": len(soup.find_all(f"h{i}")) for i in range(1, 7)}
    imgs = soup.find_all("img")
    imgs_no_alt = sum(1 for i in imgs if not i.get("alt", "").strip())
    words = len(soup.get_text(" ", strip=True).split())
    canonical = bool(soup.find("link", attrs={"rel": "canonical"}))
    viewport = bool(soup.find("meta", attrs={"name": "viewport"}))
    og = bool(soup.find("meta", attrs={"property": re.compile("^og:")}))
    schema = bool(soup.find_all("script", attrs={"type": "application/ld+json"}))
    https = url.startswith("https")

    internal = external = nofollow = dofollow = 0
    for a in soup.find_all("a", href=True):
        netloc = urlparse(urljoin(url, a["href"])).netloc.replace("www.", "")
        rel = " ".join(a.get("rel", [])).lower() if a.get("rel") else ""
        if not netloc or netloc == base:
            internal += 1
        else:
            external += 1
            nofollow += 1 if "nofollow" in rel else 0
            dofollow += 0 if "nofollow" in rel else 1

    emails = find_emails(soup)
    robots = url_exists(f"{scheme}://{base}/robots.txt")
    sitemap = url_exists(f"{scheme}://{base}/sitemap.xml")

    # Fetch Domain Age (Always Free via RDAP)
    age_info = acc.get_domain_age(base)
    domain_age = f"{age_info['years']} years" if age_info else "N/A"
    domain_created = age_info["date"] if age_info else "N/A"

    google_indexed = "N/A (Provide SerpAPI Key)"
    if serpapi_key:
        indexed_pages = acc.get_google_indexed_pages(base, serpapi_key)
        if indexed_pages is not None:
            google_indexed = f"{indexed_pages:,} pages"

    # Multi-API Metrics Checker
    da_metric = "N/A"
    if provider == "🚀 RapidAPI (Moz)" and keys.get("rapid_key"):
        try:
            r_da = requests.get(
                f"https://{keys['rapid_host']}/authority",
                headers={"X-RapidAPI-Key": keys["rapid_key"], "X-RapidAPI-Host": keys["rapid_host"]},
                params={"domain": base},
                timeout=5
            )
            if r_da.status_code == 200:
                da_metric = f"DA: {r_da.json().get('da', 'N/A')}"
        except Exception:
            pass
    elif provider == "🛡️ Moz V2 Direct" and keys.get("moz_id"):
        moz = acc.get_moz_metrics(base, keys["moz_id"], keys["moz_secret"])
        if moz:
            da_metric = f"DA: {moz['da']} | PA: {moz['pa']}"
    elif provider == "📊 Semrush API" and keys.get("semrush_key"):
        sem = acc.get_semrush_metrics(base, keys["semrush_key"])
        if sem:
            da_metric = f"AS Score: {sem['da']} (Traffic: {sem['traffic']})"
    elif provider == "🔗 Ahrefs API" and keys.get("ahrefs_key"):
        ahr = acc.get_ahrefs_metrics(base, keys["ahrefs_key"])
        if ahr:
            da_metric = f"Ahrefs DR: {ahr['da']} (Backlinks: {ahr['backlinks']})"
            
    if da_metric == "N/A":
        da_metric = "N/A (Free Crawl active)"

    checks = []
    def add(label, ok, w, fix_dict, lvl="bad"):
        fix_msg = fix_dict.get(st.session_state.get("language", "en"), fix_dict["en"])
        checks.append({"label": label, "ok": ok, "weight": w, "fix": fix_msg, "level": "ok" if ok else lvl})

    add("HTTPS (secure)", https, 8, {
        "en": "SSL Certificate is missing. Modern browsers mark non-HTTPS sites as 'Not Secure,' which destroys user trust and actively harms Google search rankings.",
        "ur": "ایس ایس ایل سرٹیفکیٹ غائب ہے۔ گوگل غیر محفوظ سائٹس کی رینکنگ دبا دیتا ہے اور براؤزر میں 'غیر محفوظ' کا نشان کسٹمرز کا اعتماد ختم کرتا ہے۔",
        "hi": "एसएसएल प्रमाणपत्र अनुपलब्ध है। ब्राउज़र गैर-सुरक्षित साइटों को ब्लॉक करते हैं, जिससे ग्राहकों का भरोसा टूटता है और रैंकिंग गिरती है।"
    })
    add(f"Title tag ({len(title)} chars)", bool(title) and 25 <= len(title) <= 65, 10, {
        "en": "Title tag is unoptimized. A weak or missing title prevents search crawlers from understanding your page's primary topic and heavily reduces organic Click-Through-Rates (CTR).",
        "ur": "ٹائٹل ٹیگ غیر موزوں ہے۔ گوگل سرچ انجن کو اس صفحہ کا مرکزی موضوع سمجھنے میں مشکل ہوگی، جس سے سرچ رزلٹس میں کلک کرنے والے وزٹرز کم ہو جاتے ہیں۔",
        "hi": "शीर्षक टैग अनुकूलित नहीं है। इससे सर्च इंजन पेज के मुख्य विषय को नहीं समझ पाते और खोज परिणामों में क्लिक कम हो जाते हैं।"
    })
    add(f"Meta description ({len(meta_desc)} chars)", bool(meta_desc) and 60 <= len(meta_desc) <= 170, 10, {
        "en": "Meta description is missing or unoptimized. Without a professional summary snippet, Google auto-generates text which looks broken in search results and costs you premium leads.",
        "ur": "میٹا ڈسکرپشن غائب یا غلط ہے۔ اس کے بغیر گوگل پر آپ کی ویب سائٹ کا تعارف ادھورا یا ٹوٹا ہوا لگتا ہے، جس سے قیمتی کسٹمرز حریفوں کے پاس چلے جاتے ہیں۔",
        "hi": "मेटा विवरण अनुपलब्ध है। इसके बिना खोज परिणामों में आपकी वेबसाइट का परिचय अधूरा लगता है, जिससे ग्राहक प्रतिस्पर्धियों के पास चले जाते हैं।"
    })
    add(f"Single H1 ({len(h1s)} found)", len(h1s) == 1, 8, {
        "en": "Incorrect H1 headings structure. Google requires exactly one clear H1 tag per page to establish the primary topic. Multiple or zero H1 tags severely confuse search bots.",
        "ur": "ایچ ون (H1) ہیڈنگ کا ڈھانچہ غلط ہے۔ گوگل کو ہر صفحے پر صرف ایک ایچ ون ٹیگ چاہیے ہوتا ہے۔ ایک سے زیادہ یا بالکل نہ ہونے سے رینکنگز گر جاتی ہیں۔",
        "hi": "मुख्य हेडिंग (H1) संरचना अमान्य है। प्रत्येक पृष्ठ पर केवल एक ही H1 टैग होना चाहिए। एक से अधिक होने पर गूगल सर्च बॉट्स भ्रमित हो जाते हैं।"
    })
    add("Heading structure (H2/H3)", headings["H2"] + headings["H3"] >= 2, 6, {
        "en": "Missing H2/H3 heading hierarchy. Semantic subheadings are essential to break up page context and rank for secondary high-intent search queries.",
        "ur": "ذیلی سرخیوں (H2/H3) کا ڈھانچہ غائب ہے۔ آرٹیکل میں مناسب ذیلی ہیڈنگز کا ہونا گوگل کی رینکنگ اور ریڈرز کی آسانی کے لیے لازمی ہے۔",
        "hi": "उप-शीर्षक (H2/H3) संरचना अनुपलब्ध है। लेखों में उचित उप-हेडिंग होना गूगल की रैंकिंग और पाठकों की सुविधा के लिए अत्यंत आवश्यक है।"
    })
    add(f"Image ALT tags ({imgs_no_alt}/{len(imgs)} missing)", imgs_no_alt == 0 and len(imgs) > 0, 6, {
        "en": "Missing Image Alt attributes. Search engines cannot 'see' images; they rely on ALT text. Unoptimized images cause you to lose high-value Google Image Search traffic.",
        "ur": "امیج آلٹ ٹیگز (Alt Tags) غائب ہیں۔ گوگل تصاویر کو دیکھ نہیں سکتا، وہ آلٹ ٹیکسٹ پر انحصار کرتا ہے۔ اس کے بغیر آپ گوگل امیج سرچ کی ٹریفک کھو دیتے ہیں۔",
        "hi": "छवि आल्ट टैग अनुपलब्ध हैं। खोज इंजन छवियों को पढ़ नहीं सकते, वे ऑल्ट टेक्स्ट पर निर्भर करते हैं। इसके बिना आप बहुमूल्य ट्रैफ़िक खो देते हैं।"
    }, "warn")
    add(f"Content depth ({words} words)", words >= 300, 10, {
        "en": "Thin content alert. Pages with low word count fail to establish helpfulness or authority in Google's ranking systems. Deep content (300+ words) is required to rank.",
        "ur": "مواد کی مقدار کم ہے۔ گوگل کم مواد والے صفحات کو 'تھن کنٹینٹ' قرار دیتا ہے جو پوری سائٹ کی اتھارٹی کو دبا دیتا ہے۔ مزید معلوماتی مواد شامل کریں۔",
        "hi": "शब्दों की संख्या बहुत कम है। कम सामग्री वाले पृष्ठों को खोज इंजन खराब गुणवत्ता का मानते हैं। अधिक जानकारीपूर्ण सामग्री शामिल करना आवश्यक है।"
    })
    add("Canonical tag", canonical, 5, {
        "en": "Missing Canonical tag. Google may index duplicate URLs of your pages, dividing your search authority and causing duplicate content duplication issues.",
        "ur": "کینو نیکل (Canonical) ٹیگ غائب ہے۔ اس کے بغیر گوگل ایک ہی پیج کے دو لنکس کو نقل سمجھ سکتا ہے اور سرچ اتھارٹی تقسیم ہو جاتی ہے۔",
        "hi": "कैनोनिकल टैग अनुपलब्ध है। इसके बिना खोज इंजनों को दोहराव लगता है, जिससे रैंकिंग प्रभावित होती है।"
    }, "warn")
    add("Mobile viewport", viewport, 6, {
        "en": "Missing Mobile Viewport meta tag. Search engines heavily penalize desktop-only rendering. A mobile-friendly viewport meta tag is critical for Google's mobile-first indexing.",
        "ur": "موبائل ویو پورٹ میٹا ٹیگ غائب ہے۔ گوگل اب 'موبائل فرسٹ انڈیکسنگ' استعمال کرتا ہے؛ اس کے بغیر موبائل رینکنگز کو شدید نقصان پہنچتا ہے۔",
        "hi": "मोबाइल व्यूपोर्ट मेटा टैग अनुपलब्ध है। इसके बिना मोबाइल उपयोगकर्ताओं को असुविधा होती है, जिससे मोबाइल रैंकिंग में भारी गिरावट आती है।"
    })
    add("Open Graph tags", og, 4, {
        "en": "Missing Open Graph meta tags. Without OG tags, social shares on platforms like Facebook, WhatsApp, or LinkedIn will display blank or broken previews.",
        "ur": "اوپن گراف (OG) ٹیگز غائب ہیں۔ اس کے بغیر واٹس ایپ، فیس بک یا لنکڈ ان پر لنک شیئر کرتے وقت آپ کی ویب سائٹ کا لوگو یا ٹائٹل خراب نظر آئے گا۔",
        "hi": "ओपन ग्राफ (OG) टैग अनुपलब्ध हैं। इसके बिना सोशल मीडिया पर लिंक साझा करते समय आपकी वेबसाइट का पूर्वावलोकन खराब दिखता है।"
    }, "warn")
    add("Schema / structured data", schema, 6, {
        "en": "Structured schema markup is missing. JSON-LD schema allows search engines to display rich snippets, reviews, or prices, which boosts CTR by up to 30%.",
        "ur": "اسکیما مارک اپ (Schema Markup) غائب ہے۔ اس کے بغیر گوگل پر آپ کے ریویوز، قیمتیں یا اسٹارز نظر نہیں آئیں گے، جو وزٹرز کو راغب کرنے کے لیے اہم ہیں۔",
        "hi": "स्कीमा मार्कअप अनुपलब्ध है। इसके बिना खोज परिणामों में आपकी रेटिंग या अतिरिक्त विवरण प्रदर्शित नहीं होते, जो ग्राहकों को आकर्षित करते हैं।"
    }, "warn")
    add("robots.txt", robots, 4, {
        "en": "robots.txt is missing. Without explicit crawler instructions, search bots may index private resources or waste crawl budget on irrelevant pages.",
        "ur": "روبوٹس فائل (robots.txt) غائب ہے۔ اس کے بغیر گوگل کے بوٹس کو آپ کی ویب سائٹ کے ضروری اور غیر ضروری صفحات کے درمیان فرق کرنے میں مشکل ہوتی ہے۔",
        "hi": "robots.txt फ़ाइल अनुपलब्ध है। इसके बिना सर्च इंजन के बॉट्स को आपकी वेबसाइट के महत्वपूर्ण पृष्ठों को समझने में कठिनाई होती है।"
    }, "warn")
    add("XML sitemap", sitemap, 5, {
        "en": "XML Sitemap is missing. A sitemap acts as a roadmap for search crawlers. Its absence significantly slows down the indexing of new content.",
        "ur": "سایت میپ فائل غائب ہے۔ سائٹ میپ گوگل کے لیے ویب سائٹ کا روڈ میپ ہوتا ہے، اس کے بغیر نئی صفحات گوگل انڈیکس میں آنے میں ہفتے لگ سکتے ہیں۔",
        "hi": "साइटमैप फ़ाइल अनुपलब्ध है। साइटमैप खोज इंजनों के लिए वेबसाइट का रोडमैप होता है, इसके बिना नए पृष्ठों को इंडेक्स होने में बहुत समय लगता है।"
    }, "warn")
    add(f"Outbound dofollow links ({dofollow})", external == 0 or dofollow > 0, 3, {
        "en": "Unoptimized outbound link signals. Linking to high-authority external resources passes trust signals to Google, proving your content is well-researched.",
        "ur": "آؤٹ باؤنڈ لنکس غیر موزوں ہیں۔ اعلیٰ اتھارٹی والی ویب سائٹس کے لنکس دینا گوگل کو یہ ثبوت دیتا ہے کہ آپ کی معلومات مستند اور ریسرچ شدہ ہیں۔",
        "hi": "आउटबाउंड लिंक अनुकूलित नहीं हैं। उच्च-प्राधिकरण वाली वेबसाइटों के लिंक देने से गूगल को विश्वास होता है कि आपकी सामग्री विश्वसनीय है।"
    }, "warn")

    earned = sum(c["weight"] for c in checks if c["ok"])
    total = sum(c["weight"] for c in checks)
    
    return {
        "url": url, 
        "domain": base, 
        "score": round(earned / total * 100) if total else 0,
        "words": words, 
        "internal": internal,
        "external": external,
        "dofollow": dofollow,
        "nofollow": nofollow,
        "emails": emails,
        "checks": checks,
        "domain_age": domain_age,
        "domain_created": domain_created,
        "google_indexed": google_indexed,
        "da": da_metric,
    }


def build_pitch(a, lang="en"):
    """Generates localized, conversion-optimized personal email pitches designed to land directly in Primary Inbox."""
    if lang == "ur":
        subject = f"آپ کی ویب سائٹ {a['domain']} کے بارے میں ایک چھوٹا سوال"
        body = f"""السلام علیکم،

میں نے حال ہی میں آپ کی ویب سائٹ {a['domain']} کا جائزہ لیا اور وہاں کچھ معمولی تکنیکی مسائل دیکھے (جیسے میٹا تفصیلات اور امیجز کی آلٹ فائلز کا نہ ہونا) جو گوگل رزلٹس میں آپ کی رینکنگ اور ٹریفک کو متاثر کر رہے ہیں۔

آپ کی آسانی کے لیے، میں نے ان تمام مسائل اور ان کے آسان حل کے ساتھ ایک صاف ستھری تشخیصی رپورٹ تیار کر کے نیچے اسی ای میل کے ساتھ منسلک کر دی ہے۔

امید ہے کہ یہ رپورٹ آپ کے کام آئے گی۔ اگر اس حوالے سے کوئی سوال ہو تو بلا جھجھک جواب دیجیے گا۔

نیک تمنائیں،"""
    elif lang == "hi":
        subject = f"आपकी वेबसाइट {a['domain']} के बारे में एक छोटा सा प्रश्न"
        body = f"""नमस्ते,

हाल ही में मैंने आपकी वेबसाइट {a['domain']} का अवलोकन किया और वहाँ कुछ छोटी तकनीकी कमियाँ पाईं (जैसे इमेज आल्ट टैग और मेटा विवरण की अनुपलब्धता) जो गूगल खोज में आपकी रैंकिंग को प्रभावित कर सकती हैं।

आपकी सुविधा के लिए, मैंने इन सभी कमियों और उनके आसान सुधारों के साथ एक साफ़-सुथरी नैदानिक रिपोर्ट तैयार कर नीचे इसी ईमेल के साथ संलग्न कर दी है।

आशा है कि यह रिपोर्ट आपके काम आएगी। यदि आपके पास कोई प्रश्न है, तो कृपया बेझिझक उत्तर दें।

शुभकामनाएं,"""
    else:
        subject = f"quick question about {a['domain']}"
        body = f"""Hi there,

I was looking at your website, {a['domain']}, and noticed a couple of minor errors (specifically regarding missing meta descriptions and unoptimized header tags) that are likely affecting how you show up on Google.

I put together a clean, colored status sheet of the specific parameters and exact fixes so you can resolve them easily. I've attached it directly below in this email for your convenience.

Let me know if you find it helpful, or if you have any questions.

Best,"""
        
    return subject, body


# ══════════════════════════════════════════════════════════════
#  UI RENDER
# ══════════════════════════════════════════════════════════════
st.markdown(f'<div class="sec">🌐 {acc.t("web_to_audit", lang_code)}</div>', unsafe_allow_html=True)
url_in = st.text_input("Website URL", placeholder="e.g., https://example.com")

if st.button(acc.t("run_audit", lang_code)):
    if not url_in:
        st.warning("⚠️ Please paste a website URL.")
    else:
        with st.spinner(acc.t("audit_spinner", lang_code)):
            a = audit_site(url_in, side_serpapi, api_provider, provider_keys)
        if a.get("error"):
            st.error(a["error"])
            st.session_state.pop("audit", None)
        else:
            subj, body = build_pitch(a, lang_code)
            st.session_state["audit"] = a
            st.session_state["pitch_subject"] = subj
            st.session_state["pitch_body"] = body

# ── Render results ────────────────────────────────────────────
if st.session_state.get("audit"):
    a = st.session_state["audit"]
    color = "#00e5b0" if a["score"] >= 70 else ("#ffcf5c" if a["score"] >= 45 else "#ff6b7a")
    grade = "Strong" if a["score"] >= 70 else ("Needs work" if a["score"] >= 45 else "Weak")
    
    col_score, col_metrics = st.columns([1, 1.8])
    with col_score:
        st.markdown(f"""<div class="card" style="text-align:center; height:240px; display:flex; flex-direction:column; justify-content:center;">
            <div style="color:#9fb0c8;font-size:0.8rem;letter-spacing:2px;">{acc.t("onpage_title", lang_code)}</div>
            <div class="score-ring" style="color:{color};">{a['score']}<span style="font-size:1.4rem;color:#9fb0c8;">/100</span></div>
            <div style="color:{color};font-weight:600;font-size:1.2rem;margin-top:2px;">{grade}</div>
            <div style="color:#7d90ad;font-size:0.85rem;margin-top:5px;">{a['domain']}</div></div>""", unsafe_allow_html=True)
            
    with col_metrics:
        st.markdown('<div class="card" style="height:240px;">'
                    f'<div style="font-size:0.8rem; letter-spacing:2px; color:#9fb0c8; font-weight:600; border-bottom:1px solid rgba(255,255,255,0.06); padding-bottom:6px; margin-bottom:12px;">{acc.t("crawl_metrics", lang_code)}</div>'
                    f'<div style="font-size:0.95rem; line-height:1.8;">'
                    f'⏳ <b>Domain Age:</b> <span class="ok">{a["domain_age"]}</span> (Created {a["domain_created"]})<br>'
                    f'📄 <b>Google Indexed Pages:</b> <span class="ok">{a["google_indexed"]}</span><br>'
                    f'🛡️ <b>SEO Authority Check:</b> <span class="ok">{a["da"]}</span><br>'
                    f'👥 <b>Estimated Traffic:</b> <span class="ok">' + ("Low" if a["google_indexed"] == "N/A" or "0" in a["google_indexed"] else "High (Indexed Pages active)") + '</span><br>'
                    f'</div></div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📝 Words Count", a["words"])
    c2.metric("🔗 Internal Links", a["internal"])
    c3.metric("↗️ Outbound Dofollow", a["dofollow"])
    c4.metric("🚫 Outbound Nofollow", a["nofollow"])

    st.markdown(f'<div class="sec">✅ {acc.t("chk_title", lang_code)}</div>', unsafe_allow_html=True)
    rows = ""
    for c in a["checks"]:
        icon = "✅" if c["ok"] else ("⚠️" if c["level"] == "warn" else "❌")
        rows += f'<div class="chk"><span class="{("ok" if c["ok"] else c["level"])}">{icon}</span> &nbsp;{c["label"]}</div>'
    st.markdown(f'<div class="card">{rows}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="sec">💼 {acc.t("pitch_title", lang_code)}</div>', unsafe_allow_html=True)
    fixes = [c for c in a["checks"] if not c["ok"]]
    if fixes:
        win_sub = {
            "en": "**By resolving these specific technical issues, you can demonstrate your expertise and win them as a client:**\n\n",
            "ur": "**ان مخصوص تکنیکی مسائل کو حل کر کے آپ اپنی مہارت ثابت کر سکتے ہیں اور انہیں اپنا کلائنٹ بنا سکتے ہیں:**\n\n",
            "hi": "**इन विशिष्ट तकनीकी समस्याओं को हल करके आप अपनी विशेषज्ञता साबित कर सकते हैं और उन्हें अपना ग्राहक बना सकते हैं:**\n\n"
        }.get(lang_code, "**By resolving these specific technical issues, you can win them as a client:**\n\n")
        
        rec = win_sub
        for c in fixes:
            rec += f"- **{c['label']}** → {c['fix']}\n"
        st.markdown(rec)
    else:
        strong_msg = {
            "en": "The website's on-page SEO is highly optimized. We recommend offering premium off-page backlinks and high-quality guest posting campaigns to build their organic authority.",
            "ur": "سائٹ کا آن پیج ایس ای او بہترین ہے۔ انہیں آرگینک اتھارٹی بڑھانے کے لیے آف پیج بیک لنکس اور گیسٹ پوسٹنگ کی خدمات پیش کریں۔",
            "hi": "साइट का ऑन-पेज एसईओ बहुत अच्छा है। उनकी ऑर्गेनिक अथॉरिटी बढ़ाने के लिए ऑफ-पेज बैकलिंक्स और गेस्ट पोस्टिंग की पेशकश करें।"
        }.get(lang_code, "The website's on-page SEO is highly optimized...")
        st.success(strong_msg)

    # ── SEND PITCH ─────────────────────────────────────────────
    st.markdown(f'<div class="sec">✉️ {acc.t("pitch_sec", lang_code)}</div>', unsafe_allow_html=True)
    user = st.session_state.get("user")
    if not user:
        st.info("📌 Email yahin se bhejne ke liye pehle **🔐 Account** page par login/signup karein. "
                "Aapke naam, phone, email & logo se professional signature lag jayegi.")
        st.markdown("**Preview pitch (copy & send manually):**")
        st.text_area("Pitch", f"Subject: {st.session_state['pitch_subject']}\n\n{st.session_state['pitch_body']}", height=340)
    else:
        auto_email = a["emails"][0] if a["emails"] else ""
        if a["emails"]:
            st.caption(f"🔎 Auto-found on website: {', '.join(a['emails'])}")
        to = st.text_input("To (auto-found, editable)", value=auto_email)
        subj = st.text_input("Subject", value=st.session_state["pitch_subject"])
        body = st.text_area("Message (signature & colorful HTML audit table auto-added)", value=st.session_state["pitch_body"], height=300)

        with st.expander("⚙️ Sending settings (Gmail App Password chahiye)"):
            from_email = st.text_input("Send from (your email)", value=user["email"])
            app_pw = st.text_input("Email App Password", type="password",
                                   help="Gmail: myaccount.google.com/apppasswords (2FA on hona zaroori).")
            host = st.text_input("SMTP host", value="smtp.gmail.com")

        cols = st.columns([1, 3])
        with cols[0]:
            if user.get("logo_b64"):
                st.image(acc.b64_to_bytes(user["logo_b64"]), width=70)
        with cols[1]:
            st.caption(f"✍️ Signature Preview: **{user['name']}** · {user['company']} · 📞 {user['phone']} · ✉️ {user['email']}")

        if st.button(acc.t("send_button", lang_code)):
            if not (to and app_pw):
                st.warning("Recipient email aur App Password zaroori hain.")
            else:
                with st.spinner("Sending..."):
                    # Pass audit results for the colorful HTML audit sheet!
                    ok, msg = acc.send_email(from_email, app_pw, to, subj, body, user, audit_results=a, lang=lang_code, smtp_host=host)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
