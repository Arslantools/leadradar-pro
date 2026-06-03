# main.py - LeadRadar Pro Entry Point
from fastapi import FastAPI, HTTPException
from serpapi import GoogleSearch
import pandas as pd
import re

app = FastAPI()

def clean_domain(url):
    if not url or url == "N/A" or "javascript:" in url:
        return "N/A"
    domain = url.replace("https://", "").replace("http://", "").replace("www.", "")
    return domain.split("/")[0].strip().lower()

def extract_real_email(text):
    if not text:
        return "N/A"
    emails = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    for em in emails:
        em_lower = em.lower()
        if not any(x in em_lower for x in ["facebook.com", "linkedin.com", "instagram.com", "twitter.com", "wix.com", "sentry.io"]):
            return em
    return "N/A"

@app.get("/scrape")
def scrape_leads(niche: str, location: str, api_key: str):
    try:
        search_query = f"{niche} in {location}"
        all_raw_leads = []

        # 1. GOOGLE MAPS ENGINE
        try:
            maps_search = GoogleSearch({"engine": "google_maps", "q": search_query, "api_key": api_key})
            maps_data = maps_search.get_dict()
            for place in maps_data.get("local_results", []):
                all_raw_leads.append({
                    "Business Name": place.get("title", "N/A"),
                    "Website": place.get("website", "N/A"),
                    "Source": "Google Maps",
                    "Phone Number": place.get("phone", "N/A")
                })
        except Exception:
            pass

        # 2. GOOGLE ORGANIC ENGINE
        try:
            google_search = GoogleSearch({"engine": "google", "q": search_query, "num": 30, "api_key": api_key})
            google_data = google_search.get_dict()
            for res in google_data.get("organic_results", []):
                all_raw_leads.append({
                    "Business Name": res.get("title", "N/A"),
                    "Website": res.get("link", "N/A"),
                    "Source": "Google Search",
                    "Phone Number": "N/A"
                })
        except Exception:
            pass

        if not all_raw_leads:
            return {"status": "Success", "leads_found": 0, "data": []}

        df = pd.DataFrame(all_raw_leads)
        df_clean = df.drop_duplicates(subset=["Business Name"], keep="first").copy()
        
        final_leads = []
        
        for index, row in df_clean.iterrows():
            web = row["Website"]
            domain = clean_domain(web)
            email = "N/A"
            
            if domain != "N/A" and not any(x in domain for x in ["facebook.com", "linkedin.com"]):
                try:
                    lookup = GoogleSearch({
                        "engine": "google",
                        "q": f'"{domain}" site:facebook.com OR site:linkedin.com OR "email"',
                        "api_key": api_key
                    })
                    lookup_data = lookup.get_dict()
                    for l_res in lookup_data.get("organic_results", []):
                        l_snippet = l_res.get("snippet", "")
                        found_email = extract_real_email(l_snippet)
                        if found_email != "N/A":
                            email = found_email
                except Exception:
                    pass
            
            final_leads.append({
                "Business Name": row["Business Name"],
                "Website": web,
                "Source": row["Source"],
                "Phone Number": row["Phone Number"],
                "Email Address": email
            })
            
        return {"status": "Success", "leads_found": len(final_leads), "data": final_leads}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
