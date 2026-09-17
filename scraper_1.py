
import re, json, requests
from datetime import datetime
from bs4 import BeautifulSoup

COURSES = {
    "44010": "https://discgolfmetrix.com/course/44010",
    "44763": "https://discgolfmetrix.com/course/44763"
}
UDISC_URL = "https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/v2/layouts/143835"

def fetch_metrix(course_id, url):
    try:
        r = requests.get(url, timeout=15, headers={'User-Agent':'LuomaAhoBot/1.0'})
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        # Count top results rows
        # Metrix table has tr with class maybe, simple count of result rows after Par row
        text = r.text
        # Count occurrences of rating pattern in Top results
        # crude: count <tr> in Top results section
        matches = re.findall(r'<tr>\s*<td[^>]*>\d+</td>', text)
        count = len(matches)
        # Try to find rating table lines
        # Also extract last events
        return {"url": url, "rounds_estimate": count, "fetched_at": datetime.utcnow().isoformat(), "status": "ok"}
    except Exception as e:
        return {"url": url, "rounds_estimate": 0, "error": str(e), "status": "error"}

def fetch_udisc(url):
    try:
        r = requests.get(url, timeout=15, headers={'User-Agent':'LuomaAhoBot/1.0'})
        # UDisc public page is JS heavy, we try to find json ld or play count
        m = re.search(r'"plays"\s*:\s*(\d+)', r.text)
        plays = int(m.group(1)) if m else None
        return {"url": url, "plays": plays, "fetched_at": datetime.utcnow().isoformat(), "status": "ok" if plays else "no_count_found"}
    except Exception as e:
        return {"url": url, "error": str(e), "status": "error"}

def main():
    data = {
        "updated": datetime.utcnow().isoformat(),
        "courses": {},
        "udisc": {},
        "static_verified": {
            "total_rounds": 473,
            "udisc": 413,
            "metrix": 60,
            "unique_players": 65,
            "hours": 589,
            "steps": 1232306,
            "monthly_2026": {"Maalis":20,"Huhti":29,"Touko":36,"Kesa":31,"Heina":60,"Elo":34,"YHT":210},
            "impact": {
                "2025": {"kierrokset":128,"pelaajia":31,"tapahtumia":1,"tunnit":160},
                "2026": {"kierrokset":473,"pelaajia":65,"tapahtumia":3,"tunnit":589}
            }
        }
    }
    for cid, url in COURSES.items():
        data["courses"][cid] = fetch_metrix(cid, url)
    data["udisc"] = fetch_udisc(UDISC_URL)
    # Merge live metrix counts if found
    metrix_total = sum([v.get("rounds_estimate",0) for v in data["courses"].values() if v.get("status")=="ok"])
    if metrix_total>0:
        data["static_verified"]["metrix_live"] = metrix_total
    with open("data.json","w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
    print(json.dumps(data,ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()
