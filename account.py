# account.py
import json
import os
import io
import hashlib
import base64
import smtplib
import re
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import requests
from PIL import Image, ImageDraw, ImageFont

USERS_FILE = "users.json"

# ── Translations Database (English, Urdu, Hindi) ──────────────
TRANSLATIONS = {
    "en": {
        "title": "LeadRadar Pro",
        "sub": "Live business intelligence engine — scan any niche & location, extract verified contacts, emails & social profiles in seconds.",
        "badge_maps": "●  Live Google Maps Tracking",
        "niche": "Niche",
        "niche_holder": "e.g., Travel Agency, Cafe, Dentist",
        "location": "Location",
        "location_holder": "e.g., London, Lahore, Manchester",
        "max_leads": "Number of leads (max)",
        "cost_note": "⚡ Up to {leads} leads · uses ~{pages} SerpAPI search(es). Actual count depends on Maps availability.",
        "keys_title": "🔑 Keys",
        "serp_label": "SerpAPI Key (required)",
        "serp_holder": "Paste your SerpAPI key",
        "adv_metrics": "⚙️ Advanced — Domain metrics (optional)",
        "adv_sub": "Add your RapidAPI key to fetch Domain Authority. Otherwise, free estimates & domain age are automatically calculated.",
        "rapid_key": "RapidAPI Key",
        "rapid_host": "RapidAPI Host",
        "scan_button": "🛰️  SCAN FOR LEADS",
        "scanning_status": "🛰️ Connecting live to SerpAPI tracking engines...",
        "maps_crawling": "🔍 Crawling page {page} from Google Maps (start offset {start})...",
        "maps_done": "✓ Maps engine generated {count} leads. Deep scraping starting...",
        "scraping_parallel": "📧 Scrapers executing in parallel (BeautifulSoup parallel workers running)...",
        "leads_found": "🎉 {count} leads found in {loc}!",
        "leads_limited": "🎉 {count} leads found in {loc} — that's all the businesses available for this niche here.",
        "results_header": "📈 Scan Results",
        "download_button": "📥  Download Leads (CSV)",
        "fill_warning": "⚠️ SerpAPI Key, Niche and Location filling are mandatory.",
        "acc_title": "🔐 Account",
        "acc_sub": "Login or create an account. Your credentials and details generate highly professional email signatures.",
        "logged_in_as": "✅ Logged in as **{name}** ({email})",
        "profile_title": "👤 Update Profile & Signatures",
        "full_name": "Full Name",
        "company": "Company / Brand",
        "phone_num": "Phone Number",
        "social_links_title": "Social Links (HTML Signatures dynamically updated):",
        "logo_preview": "**Logo preview:**",
        "sig_preview": "**Signature Preview (HTML format):**",
        "save_profile": "💾 Save profile",
        "profile_saved": "Profile and social signatures saved successfully!",
        "logout": "🚪 Logout",
        "login_tab": "🔑 Login",
        "signup_tab": "✨ Sign Up",
        "email": "Email",
        "password": "Password",
        "create_acc": "Create Account",
        "warning_fields": "Email, password aur name zaroori hain.",
        "website_url": "Website URL",
        "social_telegram": "Telegram URL",
        "social_whatsapp": "WhatsApp URL",
        "social_linkedin": "LinkedIn URL",
        "social_facebook": "Facebook URL",
        "social_instagram": "Instagram URL",
        "social_twitter": "Twitter URL",
        "seo_hero_title": "SEO Audit & Pitch Sender",
        "seo_hero_sub": "Audit a prospect's site, crawl domain authority & Google indexes for free, and send a professional email pitch right from here.",
        "web_to_audit": "🌐 Website to audit",
        "run_audit": "🔍  RUN SEO AUDIT",
        "audit_spinner": "🔍 Auditing — on-page SEO, links, emails, domain age...",
        "onpage_title": "ON-PAGE SEO SCORE",
        "crawl_metrics": "🛰️ DOMAIN AUTHORITY & CRAWL METRICS",
        "chk_title": "✅ On-page checklist",
        "pitch_title": "💼 How to win this client",
        "pitch_sec": "✉️ Send pitch to prospect",
        "send_button": "📤  SEND EMAIL NOW",
        "free_metrics_lbl": "⏳ Domain Age: {age} | 📄 Indexed Pages: {idx} | 🛡️ Domain Authority: {da}"
    },
    "ur": {
        "title": "لیڈ ریڈار پرو",
        "sub": "لائیو بزنس انٹیلی جنس انجن — سیکنڈوں میں کسی بھی نیچ اور لوکیشن کو اسکین کریں، تصدیق شدہ رابطے، ای میلز اور سوشل پروفائلز نکالیں۔",
        "badge_maps": "● لائیو گوگل میپس ٹریکنگ",
        "niche": "کاروبار کی قسم (نیچ)",
        "niche_holder": "مثال کے طور پر: کیفے، ٹریول ایجنسی، ڈینٹسٹ",
        "location": "شہر / لوکیشن",
        "location_holder": "مثال کے طور پر: لاہور، کراچی، اسلام آباد",
        "max_leads": "لیڈز کی کل تعداد (زیادہ سے زیادہ)",
        "cost_note": "⚡ {leads} لیڈز تک · تقریباً {pages} SerpAPI سرچز استعمال ہوں گی۔ اصل تعداد گوگل میپس کی دستیابی پر منحصر ہے۔",
        "keys_title": "🔑 اے پی آئی کیز (Keys)",
        "serp_label": "SerpAPI Key (لازمی ہے)",
        "serp_holder": "اپنی SerpAPI Key یہاں پیسٹ کریں",
        "adv_metrics": "⚙️ ایڈوانسڈ — ڈومین میٹرکس (اختیاری)",
        "adv_sub": "ڈومین اتھارٹی (DA) حاصل کرنے کے لیے اپنی RapidAPI کی داخل کریں۔ ورنہ مفت تخمینہ اور ڈومین کی عمر خود بخود حاصل کر لی جائے گی۔",
        "rapid_key": "RapidAPI Key",
        "rapid_host": "RapidAPI Host",
        "scan_button": "🛰️ لیڈز کے لیے اسکین کریں",
        "scanning_status": "🛰️ SerpAPI ٹریکنگ انجن سے لائیو کنیکٹ ہو رہا ہے...",
        "maps_crawling": "🔍 گوگل میپس سے پیج {page} حاصل کیا جا رہا ہے (شروع کا ہدف {start})...",
        "maps_done": "✓ گوگل میپس نے {count} لیڈز بنا دیں۔ تفصیلی اسکریپنگ شروع ہو رہی ہے...",
        "scraping_parallel": "📧 متوازی اسکریپرز چل رہے ہیں (BeautifulSoup کے ورکرز متحرک ہیں)...",
        "leads_found": "🎉 {loc} میں {count} لیڈز مل گئیں!",
        "leads_limited": "🎉 {loc} میں {count} لیڈز ملیں — اس جگہ پر اس کام کی اتنی ہی کل لیڈز دستیاب تھیں۔",
        "results_header": "📈 اسکین کے نتائج",
        "download_button": "📥 لیڈز ڈاؤن لوڈ کریں (CSV)",
        "fill_warning": "⚠️ SerpAPI Key، نیچ اور لوکیشن لکھنا لازمی ہے۔",
        "acc_title": "🔐 اکاؤنٹ مینیجر",
        "acc_sub": "لاگ ان کریں یا نیا اکاؤنٹ بنائیں۔ آپ کی تفصیلات سے انتہائی پروفیشنل ای میل دستخط (Signatures) تیار ہوں گے۔",
        "logged_in_as": "✅ لاگ ان کے طور پر: **{name}** ({email})",
        "profile_title": "👤 پروفائل اور سگنیچر اپ ڈیٹ کریں",
        "full_name": "پورا نام",
        "company": "کمپنی / برانڈ",
        "phone_num": "فون نمبر",
        "social_links_title": "سوشل لنکس (ای میل دستخطوں میں خود بخود شامل ہو جائیں گے):",
        "logo_preview": "**لوگو کا پیش نظارہ:**",
        "sig_preview": "**دستخط کا نمونہ (HTML فارمیٹ):**",
        "save_profile": "💾 پروفائل محفوظ کریں",
        "profile_saved": "پروفائل اور سوشل سگنیچرز کامیابی سے محفوظ ہو گئے!",
        "logout": "🚪 لاگ آؤٹ",
        "login_tab": "🔑 لاگ ان",
        "signup_tab": "✨ سائن اپ",
        "email": "ای میل ایڈریس",
        "password": "پاس ورڈ",
        "create_acc": "اکاؤنٹ بنائیں",
        "warning_fields": "ای میل، پاس ورڈ اور نام لکھنا لازمی ہے۔",
        "website_url": "ویب سائٹ لنک",
        "social_telegram": "ٹیلی گرام لنک",
        "social_whatsapp": "واٹس ایپ لنک",
        "social_linkedin": "لنکڈ ان لنک",
        "social_facebook": "فیس بک لنک",
        "social_instagram": "انسٹاگرام لنک",
        "social_twitter": "ٹویٹر لنک",
        "seo_hero_title": "SEO آڈٹ اور پچ سینڈر",
        "seo_hero_sub": "کلائنٹ کی سائٹ کا آڈٹ کریں، مفت ڈومین ایج اور گوگل انڈیکس معلوم کریں، اور یہیں سے پروفیشنل پچ ای میل بھیجیں۔",
        "web_to_audit": "🌐 جس ویب سائٹ کا آڈٹ کرنا ہے",
        "run_audit": "🔍 ایس ای او آڈٹ شروع کریں",
        "audit_spinner": "🔍 آڈٹ جاری ہے — اون پیج، لنکس، ای میلز اور ڈومین ایج چیک ہو رہی ہے...",
        "onpage_title": "آن پیج ایس ای او اسکور",
        "crawl_metrics": "🛰️ ڈومین اتھارٹی اور کرال میٹرکس",
        "chk_title": "✅ آن پیج چیک لسٹ",
        "pitch_title": "💼 کلائنٹ کو راضی کرنے کا طریقہ",
        "pitch_sec": "✉️ کلائنٹ کو پچ ای میل بھیجیں",
        "send_button": "📤 ای میل ابھی بھیجیں",
        "free_metrics_lbl": "⏳ ڈومین کی عمر: {age} | 📄 انڈیکس صفحات: {idx} | 🛡️ ڈومین اتھارٹی: {da}"
    },
    "hi": {
        "title": "लीडरेडार प्रो",
        "sub": "लाइव बिजनेस इंटेलिजेंस इंजन — सेकंड में किसी भी नीच और लोकेशन को स्कैन करें, सत्यापित ईमेल और सोशल प्रोफाइल निकालें।",
        "badge_maps": "● लाइव गूगल मैप्स ट्रैकिंग",
        "niche": "कारोबार का प्रकार (नीच)",
        "niche_holder": "उदा. कैफ़े, ट्रेवल एजेंसी, दंत चिकित्सक",
        "location": "शहर / स्थान",
        "location_holder": "उदा. दिल्ली, मुंबई, बैंगलोर",
        "max_leads": "लीड की कुल संख्या (अधिकतम)",
        "cost_note": "⚡ {leads} लीड तक · लगभग {pages} SerpAPI खोजों का उपयोग होगा। वास्तविक संख्या मैप्स पर निर्भर करती है।",
        "keys_title": "🔑 एपीआई कीज (Keys)",
        "serp_label": "SerpAPI Key (अनिवार्य है)",
        "serp_holder": "अपनी SerpAPI Key यहाँ पेस्ट करें",
        "adv_metrics": "⚙️ उन्नत — डोमेन मेट्रिक्स (वैकल्पिक)",
        "adv_sub": "डोमेन अथॉरिटी (DA) प्राप्त करने के लिए अपनी RapidAPI कुंजी डालें। अन्यथा, मुक्त अनुमान और डोमेन की आयु स्वचालित रूप से प्राप्त की जाएगी।",
        "rapid_key": "RapidAPI Key",
        "rapid_host": "RapidAPI Host",
        "scan_button": "🛰️ लीड्स के लिए स्कैन करें",
        "scanning_status": "🛰️ SerpAPI ट्रैकिंग इंजन से लाइव कनेक्ट हो रहा है...",
        "maps_crawling": "🔍 गूगल मैप्स से पेज {page} प्राप्त किया जा रहा है (शुरुआती ऑफसेट {start})...",
        "maps_done": "✓ गूगल मैप्स ने {count} लीड्स उत्पन्न की। विस्तृत स्क्रैपिंग शुरू हो रही है...",
        "scraping_parallel": "📧 समानांतर स्क्रैपर चल रहे हैं (BeautifulSoup के वर्कर्स सक्रिय हैं)...",
        "leads_found": "🎉 {loc} में {count} लीड्स मिलीं!",
        "leads_limited": "🎉 {loc} में {count} लीड्स मिलीं — इस स्थान पर इस काम की इतनी ही कुल लीड्स उपलब्ध थीं।",
        "results_header": "📈 स्कैन के परिणाम",
        "download_button": "📥 लीड्स डाउनलोड करें (CSV)",
        "fill_warning": "⚠️ SerpAPI Key, नीच और स्थान लिखना अनिवार्य है।",
        "acc_title": "🔐 खाता प्रबंधक",
        "acc_sub": "लॉग इन करें या नया खाता बनाएं। आपके विवरण से अत्यंत पेशेवर ईमेल हस्ताक्षर (Signatures) तैयार होंगे।",
        "logged_in_as": "✅ लॉगिन के रूप में: **{name}** ({email})",
        "profile_title": "👤 प्रोफ़ाइल और हस्ताक्षर अपडेट करें",
        "full_name": "पूरा नाम",
        "company": "कंपनी / ब्रांड",
        "phone_num": "फ़ोन नंबर",
        "social_links_title": "सोशल लिंक्स (ईमेल हस्ताक्षरों में गतिशील रूप से जोड़े जाएंगे):",
        "logo_preview": "**लोगो का पूर्वावलोकन:**",
        "sig_preview": "**हस्ताक्षर का नमूना (HTML प्रारूप):**",
        "save_profile": "💾 प्रोफ़ाइल सहेजें",
        "profile_saved": "प्रोफ़ाइल और सोशल सिग्नेचर सफलतापूर्वक सुरक्षित हो गए!",
        "logout": "🚪 लॉग आउट",
        "login_tab": "🔑 लॉग इन",
        "signup_tab": "✨ साइन अप",
        "email": "ईमेल पता",
        "password": "पासवर्ड",
        "create_acc": "खाता बनाएँ",
        "warning_fields": "ईमेल, पासवर्ड और नाम लिखना अनिवार्य है।",
        "website_url": "वेबसाइट लिंक",
        "social_telegram": "टेलीग्राम लिंक",
        "social_whatsapp": "व्हाट्सएप लिंक",
        "social_linkedin": "लिंक्डइन लिंक",
        "social_facebook": "फेसबुक लिंक",
        "social_instagram": "इंस्टाग्राम लिंक",
        "social_twitter": "ट्विटर लिंक",
        "seo_hero_title": "SEO ऑडिट और पिच सेंडर",
        "seo_hero_sub": "ग्राहक की साइट का ऑडिट करें, डोमेन आयु और गूगल इंडेक्स मुफ्त में जांचें, और यहीं से पेशेवर पिच ईमेल भेजें।",
        "web_to_audit": "🌐 जिस वेबसाइट का ऑडिट करना है",
        "run_audit": "🔍 एसईओ ऑडिट शुरू करें",
        "audit_spinner": "🔍 ऑडिट जारी है — ऑन-पेज, लिंक्स, ईमेल और डोमेन आयु की जांच हो रही है...",
        "onpage_title": "ऑन-पेज एसईओ स्कोर",
        "crawl_metrics": "🛰️ डोमेन अथॉरिटी और क्रॉल मेट्रिक्स",
        "chk_title": "✅ ऑन-पेज चेकलिस्ट",
        "pitch_title": "💼 ग्राहक को समझाने का तरीका",
        "pitch_sec": "✉️ ग्राहक को पिच ईमेल भेजें",
        "send_button": "📤 ईमेल अभी भेजें",
        "free_metrics_lbl": "⏳ डोमेन की आयु: {age} | 📄 अनुक्रमित पृष्ठ: {idx} | 🛡️ डोमेन अथॉरिटी: {da}"
    }
}

def t(key, lang="en"):
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


# ── User store ────────────────────────────────────────────────
def _load():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ── Password hashing (PBKDF2-SHA256) ──────────────────────────
def _hash(pw, salt=None):
    if salt is None:
        salt = os.urandom(16)
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 100000)
    return base64.b64encode(salt).decode(), base64.b64encode(dk).decode()


def _verify(pw, salt_b64, hash_b64):
    dk = hashlib.pbkdf2_hmac("sha256", pw.encode(), base64.b64decode(salt_b64), 100000)
    return base64.b64encode(dk).decode() == hash_b64


# ── Auth API ──────────────────────────────────────────────────
def signup(email, password, name, phone, company, logo_b64="", linkedin="", facebook="", instagram="", twitter="", website="", telegram="", whatsapp="", lang="en"):
    email = email.lower().strip()
    users = _load()
    if email in users:
        msg = {
            "en": "This email is already registered. Please login.",
            "ur": "یہ ای میل پہلے سے رجسٹرڈ ہے۔ لاگ ان کریں۔",
            "hi": "यह ईमेल पहले से पंजीकृत है। कृपया लॉग इन करें।"
        }.get(lang, "This email is already registered. Please login.")
        return False, msg
    if len(password) < 6:
        msg = {
            "en": "Password must be at least 6 characters.",
            "ur": "پاس ورڈ کم از کم 6 حروف کا ہونا چاہیے۔",
            "hi": "पासवर्ड कम से कम 6 अक्षरों का होना चाहिए।"
        }.get(lang, "Password must be at least 6 characters.")
        return False, msg
    salt, h = _hash(password)
    users[email] = {
        "name": name, 
        "phone": phone, 
        "company": company,
        "salt": salt, 
        "hash": h, 
        "logo_b64": logo_b64,
        "linkedin": linkedin,
        "facebook": facebook,
        "instagram": instagram,
        "twitter": twitter,
        "website": website,
        "telegram": telegram,
        "whatsapp": whatsapp
    }
    _save(users)
    success_msg = {
        "en": "Account created successfully! Please login.",
        "ur": "اکاؤنٹ کامیابی سے بن گیا! اب لاگ ان کریں۔",
        "hi": "खाता सफलतापूर्वक बन गया! कृपया लॉग इन करें।"
    }.get(lang, "Account created successfully! Please login.")
    return True, success_msg


def login(email, password):
    email = email.lower().strip()
    users = _load()
    u = users.get(email)
    if not u or not _verify(password, u["salt"], u["hash"]):
        return False, None
    return True, {
        "email": email, 
        "name": u["name"], 
        "phone": u["phone"],
        "company": u["company"], 
        "logo_b64": u.get("logo_b64", ""),
        "linkedin": u.get("linkedin", ""),
        "facebook": u.get("facebook", ""),
        "instagram": u.get("instagram", ""),
        "twitter": u.get("twitter", ""),
        "website": u.get("website", ""),
        "telegram": u.get("telegram", ""),
        "whatsapp": u.get("whatsapp", "")
    }


def update_profile(email, name, phone, company, logo_b64=None, linkedin="", facebook="", instagram="", twitter="", website="", telegram="", whatsapp=""):
    users = _load()
    if email not in users:
        return False
    users[email]["name"] = name
    users[email]["phone"] = phone
    users[email]["company"] = company
    users[email]["linkedin"] = linkedin
    users[email]["facebook"] = facebook
    users[email]["instagram"] = instagram
    users[email]["twitter"] = twitter
    users[email]["website"] = website
    users[email]["telegram"] = telegram
    users[email]["whatsapp"] = whatsapp
    if logo_b64 is not None:
        users[email]["logo_b64"] = logo_b64
    _save(users)
    return True


# ── Logo generation ───────────────────────────────────────────
def _font(size):
    for path in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/arial.ttf",
                 "/Library/Fonts/Arial Bold.ttf"]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def make_monogram(name, size=240):
    initials = "".join(w[0] for w in name.split()[:2]).upper() or "L"
    S = size * 3  # supersample for smooth edges

    c1, c2 = (0, 224, 178), (40, 132, 255)
    g = Image.new("RGB", (24, 24))
    gp = g.load()
    for y in range(24):
        for x in range(24):
            t = (x + y) / 46
            gp[x, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    grad = g.resize((S, S), Image.BILINEAR)

    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.24), fill=255)
    badge = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    badge.paste(grad, (0, 0), mask)

    d = ImageDraw.Draw(badge)
    d.ellipse([S * 0.13, S * 0.13, S * 0.87, S * 0.87], outline=(255, 255, 255, 60),
              width=max(2, S // 90))

    font = _font(int(S * 0.40))
    bbox = d.textbbox((0, 0), initials, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    d.text(((S - w) / 2 - bbox[0], (S - h) / 2 - bbox[1]), initials,
           fill=(255, 255, 255, 255), font=font)

    badge = badge.resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    badge.save(buf, "PNG")
    return buf.getvalue()


def process_upload(image_bytes, size=240):
    S = size * 3
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB").resize((S, S))
    mask = Image.new("L", (S, S), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.24), fill=255)
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    out.paste(img, (0, 0), mask)
    out = out.resize((size, size), Image.LANCZOS)
    buf = io.BytesIO()
    out.save(buf, "PNG")
    return buf.getvalue()


def b64_to_bytes(b64):
    try:
        return base64.b64decode(b64)
    except Exception:
        return b""


def bytes_to_b64(b):
    return base64.b64encode(b).decode()


# ── Free SEO Metrics API (Keyless RDAP & SerpAPI Indexed) ─────
def get_domain_age(domain):
    try:
        domain = domain.strip().lower()
        if domain.startswith("www."):
            domain = domain[4:]
        url = f"https://rdap.org/domain/{domain}"
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            data = r.json()
            events = data.get("events", [])
            for event in events:
                if event.get("eventAction") == "registration":
                    date_str = event.get("eventDate")
                    date_part = date_str[:10]
                    reg_date = datetime.strptime(date_part, "%Y-%m-%d")
                    age_days = (datetime.now() - reg_date).days
                    age_years = round(age_days / 365.25, 1)
                    return {"date": date_part, "years": age_years}
    except Exception:
        pass
    return None


def get_google_indexed_pages(domain, serpapi_key):
    try:
        if not serpapi_key:
            return None
        domain = domain.strip().lower()
        if domain.startswith("www."):
            domain = domain[4:]
        params = {
            "engine": "google",
            "q": f"site:{domain}",
            "api_key": serpapi_key
        }
        r = requests.get("https://serpapi.com/search", params=params, timeout=8)
        if r.status_code == 200:
            res = r.json()
            total_results = res.get("search_information", {}).get("total_results", 0)
            return total_results
    except Exception:
        pass
    return None


# ── Multi-API Integrations ────────────────────────────────────
def get_moz_metrics(domain, access_id, secret_key):
    """Direct Moz V2 API link metrics check."""
    try:
        url = "https://lsapi.seomoz.com/v2/link_metrics"
        auth_str = base64.b64encode(f"{access_id}:{secret_key}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_str}",
            "Content-Type": "application/json"
        }
        payload = {"targets": [domain], "columns": ["domain_authority", "page_authority", "links_to_domain"]}
        r = requests.post(url, headers=headers, json=payload, timeout=6)
        if r.status_code == 200:
            res = r.json()
            results = res.get("results", [])
            if results:
                return {
                    "da": round(results[0].get("domain_authority", 0)),
                    "pa": round(results[0].get("page_authority", 0)),
                    "links": results[0].get("links_to_domain", 0)
                }
    except Exception:
        pass
    return None


def get_semrush_metrics(domain, api_key):
    """Direct Semrush domain ranking metrics."""
    try:
        # AS (Authority Score) is retrieved via domain_ranks
        url = "https://api.semrush.com/"
        params = {
            "type": "domain_ranks",
            "key": api_key,
            "domain": domain,
            "export_columns": "as,OrTraffic"
        }
        r = requests.get(url, params=params, timeout=6)
        if r.status_code == 200 and "as;" in r.text:
            lines = r.text.strip().split("\n")
            if len(lines) > 1:
                vals = lines[1].split(";")
                return {
                    "da": vals[0],
                    "traffic": vals[1] if len(vals) > 1 else "N/A"
                }
    except Exception:
        pass
    return None


def get_ahrefs_metrics(domain, api_key):
    """Direct Ahrefs V3 API metrics check."""
    try:
        url = "https://api.ahrefs.com/v3/public/domain-rating"
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        payload = {"target": domain}
        r = requests.post(url, headers=headers, json=payload, timeout=6)
        if r.status_code == 200:
            res = r.json()
            return {
                "da": round(res.get("domainRating", 0)),
                "backlinks": res.get("backlinks", 0)
            }
    except Exception:
        pass
    return None


# ── Dynamic HTML Email Signature ──────────────────────────────
def signature_html(profile):
    name = profile.get("name", "")
    company = profile.get("company", "")
    phone = profile.get("phone", "")
    email = profile.get("email", "")
    logo_block = '<img src="cid:logo" width="60" height="60" style="border-radius:50%; margin-right:12px; border:2px solid #00b894;">' if profile.get("logo_b64") else ""
    
    socials = []
    if profile.get("linkedin"):
        socials.append(f'<a href="{profile["linkedin"]}" style="color:#00a8cc; text-decoration:none; font-weight:bold; margin-right:10px; font-size:12px;">🔗 LinkedIn</a>')
    if profile.get("facebook"):
        socials.append(f'<a href="{profile["facebook"]}" style="color:#3b5998; text-decoration:none; font-weight:bold; margin-right:10px; font-size:12px;">🔗 Facebook</a>')
    if profile.get("instagram"):
        socials.append(f'<a href="{profile["instagram"]}" style="color:#e1306c; text-decoration:none; font-weight:bold; margin-right:10px; font-size:12px;">🔗 Instagram</a>')
    if profile.get("twitter"):
        socials.append(f'<a href="{profile["twitter"]}" style="color:#1da1f2; text-decoration:none; font-weight:bold; margin-right:10px; font-size:12px;">🔗 Twitter</a>')
    if profile.get("telegram"):
        socials.append(f'<a href="{profile["telegram"]}" style="color:#0088cc; text-decoration:none; font-weight:bold; margin-right:10px; font-size:12px;">✈️ Telegram</a>')
    if profile.get("whatsapp"):
        # standard WhatsApp wa.me parse
        wa_url = profile["whatsapp"]
        if not wa_url.startswith("http"):
            wa_clean = re.sub(r'\D', '', wa_url)
            wa_url = f"https://wa.me/{wa_clean}"
        socials.append(f'<a href="{wa_url}" style="color:#25d366; text-decoration:none; font-weight:bold; margin-right:10px; font-size:12px;">💬 WhatsApp</a>')
    if profile.get("website"):
        socials.append(f'<a href="{profile["website"]}" style="color:#00e5b0; text-decoration:none; font-weight:bold; margin-right:10px; font-size:12px;">🌐 Website</a>')
    
    socials_block = ""
    if socials:
        socials_block = f'<div style="margin-top:8px; padding-top:6px; border-top:1px solid #eee; font-size:12px;">{" ".join(socials)}</div>'

    return f"""
    <table style="font-family:Arial,sans-serif; border-top:2px solid #00b894; padding-top:12px; margin-top:18px; line-height:1.4;">
      <tr>
        <td style="padding-right:14px; vertical-align:middle;">{logo_block}</td>
        <td style="vertical-align:middle;">
          <div style="font-size:16px; font-weight:bold; color:#1a1a1a;">{name}</div>
          <div style="font-size:13px; color:#00897b; font-weight:bold;">{company}</div>
          <div style="font-size:12px; color:#555; margin-top:3px;">
            📞 {phone} &nbsp;|&nbsp; ✉️ {email}
          </div>
          {socials_block}
        </td>
      </tr>
    </table>"""


# ── Colorful HTML Diagnostic Table Compiler ──────────────────
def compile_diagnostic_table_html(audit_results, lang="en"):
    """Generates an extremely professional, colorful HTML status sheet for the email body."""
    headers_lang = {
        "en": ("Audit Parameter", "Status", "Action / Win Recommendation"),
        "ur": ("ایس ای او میٹرک", "حالت", "حل / تجویز کردہ ایکشن"),
        "hi": ("एसईओ पैरामीटर", "स्थिति", "सुझाव / आवश्यक सुधार")
    }
    hd = headers_lang.get(lang, headers_lang["en"])
    
    title_text = {
        "en": "🛠️ Personalized Website SEO Diagnostic Audit Sheet",
        "ur": "🛠️ ویب سائٹ ایس ای او آڈٹ تشخیصی شیٹ (رپورٹ)",
        "hi": "🛠️ वैयक्तिकृत वेबसाइट एसईओ ऑडिट नैदानिक रिपोर्ट"
    }.get(lang, "Website SEO Audit Report")

    rows_html = ""
    for c in audit_results["checks"]:
        # Select style tokens based on status
        if c["ok"]:
            status_lbl = "Pass" if lang == "en" else ("ٹھیک ہے" if lang == "ur" else "उत्तीर्ण")
            status_col = "#00e5b0"
            status_bg = "rgba(0,229,176,0.1)"
            icon = "✅"
            action_text = "Perfect! Excellent optimization." if lang == "en" else ("زبردست! کوئی ایکشن درکار نہیں ہے۔" if lang == "ur" else "उत्कृष्ट! किसी सुधार की आवश्यकता नहीं है।")
        else:
            status_col = "#ffcf5c" if c["level"] == "warn" else "#ff6b7a"
            status_bg = "rgba(255,207,92,0.1)" if c["level"] == "warn" else "rgba(255,107,122,0.1)"
            status_lbl = ("Warning" if c["level"] == "warn" else "Critical") if lang == "en" else (("انتباہ" if c["level"] == "warn" else "فوری توجہ") if lang == "ur" else ("चेतावनी" if c["level"] == "warn" else "गंभीर"))
            icon = "⚠️" if c["level"] == "warn" else "❌"
            action_text = c["fix"]

        rows_html += f"""
        <tr style="border-bottom: 1px solid #e1e7f0; font-size:13.5px;">
          <td style="padding:10px 12px; color:#2d3748; font-weight:bold;">{icon} &nbsp; {c['label']}</td>
          <td style="padding:10px 12px; text-align:center;">
             <span style="background-color:{status_bg}; color:{status_col}; border:1px solid {status_col}; padding:3px 8px; border-radius:12px; font-size:11px; font-weight:bold; text-transform:uppercase;">
               {status_lbl}
             </span>
          </td>
          <td style="padding:10px 12px; color:#4a5568;">{action_text}</td>
        </tr>"""

    # Extra meta metrics block in table footer
    footer_text = {
        "en": f"📊 Page Size: <b>{audit_results['words']} words</b> | ⏳ Domain Age: <b>{audit_results['domain_age']}</b> | 📄 Google Indexed: <b>{audit_results['google_indexed']}</b>",
        "ur": f"📊 صفحہ کے الفاظ: <b>{audit_results['words']} الفاظ</b> | ⏳ ڈومین کی عمر: <b>{audit_results['domain_age']}</b> | 📄 گوگل انڈیکس: <b>{audit_results['google_indexed']}</b>",
        "hi": f"📊 पृष्ठ के शब्द: <b>{audit_results['words']} शब्द</b> | ⏳ डोमेन की आयु: <b>{audit_results['domain_age']}</b> | 📄 गूगल अनुक्रमित: <b>{audit_results['google_indexed']}</b>"
    }.get(lang, "")

    # Website ka apna logo (favicon) — "professional research on YOUR site" feel
    domain = audit_results.get("domain", "")
    score = audit_results.get("score", 0)
    site_logo = f"https://www.google.com/s2/favicons?domain={domain}&sz=128"
    score_col = "#16a34a" if score >= 70 else ("#f59e0b" if score >= 45 else "#dc2626")

    header_html = f"""
      <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;border-radius:12px 12px 0 0;overflow:hidden;">
        <tr style="background-color:#0ea5a4;background:linear-gradient(95deg,#0ea5a4,#2563eb);">
          <td width="62" style="padding:14px 0 14px 18px;vertical-align:middle;">
            <img src="{site_logo}" width="46" height="46" alt="" style="border-radius:10px;background:#ffffff;padding:4px;display:block;">
          </td>
          <td style="padding:14px 12px;vertical-align:middle;">
            <div style="color:#ffffff;font-size:18px;font-weight:bold;">{domain}</div>
            <div style="color:#d1fae5;font-size:12px;">Personalized SEO Health Report</div>
          </td>
          <td style="padding:14px 18px;text-align:right;vertical-align:middle;">
            <div style="color:#ffffff;font-size:26px;font-weight:bold;line-height:1;">{score}<span style="font-size:13px;opacity:.85;">/100</span></div>
            <div style="color:#d1fae5;font-size:10px;letter-spacing:1px;">HEALTH SCORE</div>
          </td>
        </tr>
      </table>"""

    return f"""
    <div style="margin: 20px 0; max-width:600px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
      {header_html}
      <table style="width:100%; border-collapse:collapse; border:1px solid #e2e8f0; overflow:hidden; box-shadow:0 4px 12px rgba(0,0,0,0.05);">
        <thead>
          <tr style="background-color:#0f172a; color:#ffffff; font-size:13px; text-align:left;">
            <th style="padding:12px; border:1px solid #e2e8f0;">{hd[0]}</th>
            <th style="padding:12px; border:1px solid #e2e8f0; width:120px; text-align:center;">{hd[1]}</th>
            <th style="padding:12px; border:1px solid #e2e8f0;">{hd[2]}</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
      <div style="background-color:#f7fafc; padding:10px 14px; border:1px solid #e2e8f0; border-top:none; border-radius: 0 0 12px 12px; font-size:12px; color:#718096; text-align:center;">
        {footer_text}
      </div>
    </div>"""


# ── Full SMTP Send with signature & inline attachments ────────
def send_email(from_email, app_password, to_email, subject, body_text, profile,
               audit_results=None, lang="en", smtp_host="smtp.gmail.com", smtp_port=465):
    try:
        body_html = body_text.replace("\n", "<br>")
        
        # Append beautiful diagnostic table if results are supplied!
        table_html = ""
        if audit_results:
            table_html = compile_diagnostic_table_html(audit_results, lang)

        html = f"""<html><body style="font-family:Arial,sans-serif; color:#222; line-height:1.5;">
        {body_html}
        {table_html}
        {signature_html(profile)}</body></html>"""

        msg = MIMEMultipart("related")
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email
        alt = MIMEMultipart("alternative")
        alt.attach(MIMEText(body_text, "plain"))
        alt.attach(MIMEText(html, "html"))
        msg.attach(alt)

        if profile.get("logo_b64"):
            img = MIMEImage(b64_to_bytes(profile["logo_b64"]))
            img.add_header("Content-ID", "<logo>")
            img.add_header("Content-Disposition", "inline")
            msg.attach(img)

        with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=20) as s:
            s.login(from_email, app_password)
            s.send_message(msg)
        return True, "Email bhej diya gaya! Reply aapke inbox mein aayega."
    except smtplib.SMTPAuthenticationError:
        return False, "Login fail. Gmail ke liye normal password nahi — App Password use karein (2FA on hona chahiye)."
    except Exception as e:
        return False, f"Send fail: {type(e).__name__}: {e}"
