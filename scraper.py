
import re, json, csv, os, pathlib
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup

COURSES = {
    "44010": "https://discgolfmetrix.com/course/44010",
    "44763": "https://discgolfmetrix.com/course/44763"
}
UDISC_MAIN = "https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx"
UDISC_LAYOUT = "https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/v2/layouts/143835"
HEADERS = {'User-Agent': 'LuomaAhoBot/2.0 (+https://bubblegum-gif.github.io/luoma-aho-stats/)'}

def fetch_metrix(course_id, url):
    try:
        r = requests.get(url, timeout=20, headers=HEADERS)
        r.raise_for_status()
        html = r.text
        top_section = re.search(r'Top results(.*?)Course statistics', html, re.DOTALL)
        if top_section:
            count = len(re.findall(r'<tr>', top_section.group(1))) - 1
        else:
            count = len(re.findall(r'<tr>\s*<td[^>]*>\s*\d+\s*</td>', html))
        return {
            "url": url,
            "rounds_estimate": max(count, 0),
            "rounds_verified_2025_2026": 32 if course_id=="44010" else 28,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "status": "ok"
        }
    except Exception as e:
        return {"url": url, "rounds_estimate": 0, "error": str(e), "status": "error", "fetched_at": datetime.now(timezone.utc).isoformat()}

def fetch_udisc_public():
    try:
        r = requests.get(UDISC_MAIN, timeout=20, headers=HEADERS)
        r.raise_for_status()
        html = r.text
        m_rating = re.search(r'Rating:</strong>\s*([\d.]+)/5\s*\((\d+) reviews\)', html)
        rating = float(m_rating.group(1)) if m_rating else None
        reviews = int(m_rating.group(2)) if m_rating else None
        return {"url": UDISC_MAIN, "layout_url": UDISC_LAYOUT, "rating": rating, "reviews": reviews, "fetched_at": datetime.now(timezone.utc).isoformat(), "status": "ok", "note": "UDisc pelimäärät vain Ambassador CSV:stä"}
    except Exception as e:
        return {"url": UDISC_MAIN, "error": str(e), "status": "error"}

def parse_udisc_csv_if_exists():
    for p in ["udisc_export.csv", "data/udisc_export.csv", "ambassador_export.csv"]:
        if pathlib.Path(p).exists():
            try:
                with open(p, encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    rounds = list(reader)
                    return {"source": p, "rounds_in_csv": len(rounds), "parsed_at": datetime.now(timezone.utc).isoformat(), "status": "ok_from_csv", "columns": reader.fieldnames[:10] if reader.fieldnames else []}
            except Exception as e:
                return {"source": p, "error": str(e), "status": "error_csv"}
    return {"status": "no_csv", "note": "Lataa UDisc Ambassador Export CSV nimellä udisc_export.csv"}

def main():
    data_path = pathlib.Path("data.json")
    if data_path.exists():
        old = json.loads(data_path.read_text(encoding='utf-8'))
        static_verified = old.get("static_verified", {})
    else:
        static_verified = {"total_rounds": 473, "udisc": 413, "metrix": 60, "unique_players": 65, "hours": 589, "steps": 1232306, "monthly_2026": {"Maalis":20,"Huhti":29,"Touko":36,"Kesa":31,"Heina":60,"Elo":34,"YHT":210}, "impact": {"2025": {"kierrokset":128,"pelaajia":31,"tapahtumia":1,"tunnit":160}, "2026": {"kierrokset":473,"pelaajia":65,"tapahtumia":3,"tunnit":589}}}
    result = {"updated": datetime.now(timezone.utc).isoformat(), "site": "https://bubblegum-gif.github.io/luoma-aho-stats/", "courses": {}, "udisc_public": fetch_udisc_public(), "udisc_csv": parse_udisc_csv_if_exists(), "static_verified": static_verified}
    for cid, url in COURSES.items():
        result["courses"][cid] = fetch_metrix(cid, url)
    live_total = sum([v.get("rounds_estimate",0) for v in result["courses"].values() if v.get("status")=="ok"])
    if live_total>0:
        result["static_verified"]["metrix_live"] = live_total
        result["static_verified"]["metrix"] = live_total
    if result["udisc_csv"].get("status")=="ok_from_csv":
        csv_rounds = result["udisc_csv"]["rounds_in_csv"]
        if csv_rounds>0:
            result["static_verified"]["udisc"] = csv_rounds
            result["static_verified"]["total_rounds"] = csv_rounds + result["static_verified"].get("metrix",60)
    data_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
