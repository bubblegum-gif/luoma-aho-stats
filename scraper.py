
"""
Luoma-aho Frisbeegolfrata - Tilasto-skraperi
Hakee kierrokset 4 Metrix-radalta + UDiscista ja summaa yhteen.
Päivitetään GitHub Actionsissa 1h välein.

Metrix IDs:
- 43119
- 48112
- 44763
- 44010

UDisc:
- https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx
- layout 143835
- /manage/stats (vaatii kirjautumisen, tuki manuaaliselle yliajolle)

Jos UDisc-skrapaus epäonnistuu (Pro-vaatimus), käyttää UDISC_MANUAL_COUNT env muuttujaa
tai data/udisc_override.json tiedostoa.
"""

import re
import json
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import time

METRIX_IDS = ["43119", "48112", "44763", "44010"]
UDISC_URLS = [
    "https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx",
    "https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/v2/layouts/143835",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Luoma-aho Stats Bot; +https://luoma-aho.fi) AppleWebKit/537.36",
    "Accept-Language": "fi-FI,fi;q=0.9,en;q=0.8"
}

def fetch_metrix_rounds(course_id):
    url = f"https://discgolfmetrix.com/course/{course_id}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        html = r.text
        
        # Yritä useita patterneja - Metrix näyttää kierrokset eri paikoissa riippuen layoutista
        # Pattern 1: "Rounds played: 1234" tai "Pelattuja kierroksia"
        patterns = [
            r'(?:Rounds played|Pelattuja kierroksia|Kierroksia yhteensä)[^\d]*(\d[\d\s]*)',
            r'course-statistics.*?([\d\s]+)\s*rounds',
            r'"totalRounds"\s*:\s*(\d+)',
            r'data-total-rounds="(\d+)"',
        ]
        
        # Hae myös taulukosta - laske rivejä jos tarpeen
        soup = BeautifulSoup(html, 'html.parser')
        
        # Etsi lukuja jotka näyttävät kierrosmääriltä
        text = soup.get_text(" ", strip=True)
        
        # Viimeinen fallback: etsi suuri luku joka on todennäköisesti kierrosmäärä
        # Metrix-sivuilla on usein elementti jossa lukee esim "1234 rounds"
        for pat in patterns:
            m = re.search(pat, text, re.I)
            if m:
                num = re.sub(r'\D', '', m.group(1))
                if num and int(num) > 0:
                    print(f"Metrix {course_id}: löytyi pattern {pat} -> {num}")
                    return int(num)
        
        # Jos ei löydy suoraa lukua, yritä laskea tulosriveistä (top results määrä ei ole oikea, mutta käyttötilasto voi olla)
        # Tässä vaiheessa palauta 0 ja logita - oikea scraper tarvitsee Playwrightin heatmap-datalle
        # Väliaikainen: yritä etsiä JSON dataa sivun script tagista
        scripts = soup.find_all("script")
        for sc in scripts:
            if sc.string and "courseUsage" in sc.string or "rounds" in sc.string.lower():
                nums = re.findall(r'(\d{2,5})', sc.string)
                if nums:
                    # ota suurin järkevä
                    candidates = [int(n) for n in nums if 10 < int(n) < 100000]
                    if candidates:
                        est = max(candidates)
                        print(f"Metrix {course_id}: arvio scriptista {est}")
                        # Älä palauta tätä vielä varmana, vaan logita
        
        print(f"Metrix {course_id}: EI löytynyt suoraa kierrosmäärää - tarvitsee Playwright-skrapauksen")
        return None
        
    except Exception as e:
        print(f"Metrix {course_id} virhe: {e}")
        return None

def fetch_metrix_with_playwright():
    """Vaihtoehtoinen tarkempi haku Playwrightilla - hakee Course statistics taulukon"""
    try:
        from playwright.sync_api import sync_playwright
        results = {}
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            for cid in METRIX_IDS:
                try:
                    page.goto(f"https://discgolfmetrix.com/course/{cid}", wait_until="networkidle", timeout=30000)
                    # Odota statistics osio
                    page.wait_for_timeout(3000)
                    content = page.content()
                    # Etsi "Course statistics" -taulukko
                    # Oikea tapa: lue monthly usage ja summaa
                    # Tässä yksinkertaistettu
                    soup = BeautifulSoup(content, 'html.parser')
                    # Etsi kaikki numerot jotka voivat olla kierroksia
                    text = soup.get_text(" ", strip=True)
                    # Metrix näyttää usein "Total: X"
                    m = re.search(r'Total[^\d]*(\d+)', text)
                    if m:
                        results[cid] = int(m.group(1))
                    else:
                        results[cid] = None
                except Exception as e:
                    print(f"Playwright Metrix {cid} virhe: {e}")
                    results[cid] = None
            browser.close()
        return results
    except ImportError:
        print("Playwright ei asennettu - käytetään requests fallback")
        return {}

def fetch_udisc_plays():
    """Yrittää hakea UDisc pelimäärän - vaatii yleensä Pron"""
    # Tarkista manuaalinen override ensin
    override_path = Path("data/udisc_override.json")
    if override_path.exists():
        try:
            data = json.loads(override_path.read_text())
            if "plays" in data and data["plays"] > 0:
                print(f"UDisc: käytetään override {data['plays']}")
                return data["plays"]
        except:
            pass
    
    # Env muuttuja
    import os
    manual = os.getenv("UDISC_MANUAL_COUNT")
    if manual and manual.isdigit():
        print(f"UDisc: käytetään ENV {manual}")
        return int(manual)
    
    # Yritä scrape public sivulta - UDisc näyttää joskus "X plays in last 30 days" vain jos on Pro data
    for url in UDISC_URLS:
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code == 200:
                # Etsi "Play count" tai "X plays"
                m = re.search(r'(\d+)\s*plays', r.text, re.I)
                if m:
                    print(f"UDisc {url}: {m.group(1)} plays (30d)")
                    # Tämä on vain 30 päivän, ei total - tarvitsee /manage/stats joka vaatii loginin
        except Exception as e:
            print(f"UDisc {url} virhe: {e}")
    
    # Jos ei onnistu, palauta None - käyttäjä päivittää manuaalisesti kuvan perusteella
    print("UDisc: automaattinen haku epäonnistui (vaatii Pro-kirjautumisen). Käytä manuaalista overridea.")
    return None

def main():
    print("=== Luoma-aho Tilasto Skraperi ===")
    metrix_totals = {}
    metrix_sum = 0
    metrix_missing = []
    
    # Yritä Playwrightilla ensin jos saatavilla
    pw_results = fetch_metrix_with_playwright()
    
    for cid in METRIX_IDS:
        count = pw_results.get(cid) if pw_results else None
        if count is None:
            count = fetch_metrix_rounds(cid)
        
        if count is not None:
            metrix_totals[cid] = count
            metrix_sum += count
        else:
            # Fallback: lue edellinen data jos on, jotta summa ei nollaannu
            prev_path = Path("data/stats.json")
            if prev_path.exists():
                try:
                    prev = json.loads(prev_path.read_text())
                    old = prev.get("metrix", {}).get(cid)
                    if old:
                        metrix_totals[cid] = old
                        metrix_sum += old
                        print(f"Metrix {cid}: käytetään edellistä arvoa {old}")
                        continue
                except:
                    pass
            metrix_totals[cid] = 0
            metrix_missing.append(cid)
    
    udisc_plays = fetch_udisc_plays()
    
    # Lue edellinen kokonaistilasto
    prev_total = 0
    prev_path = Path("data/stats.json")
    if prev_path.exists():
        try:
            prev = json.loads(prev_path.read_text())
            prev_total = prev.get("total", {}).get("rounds", 0)
        except:
            pass
    
    # Jos UDisc puuttuu, yritä käyttää edellistä kokonaissummaa UDiscille
    if udisc_plays is None:
        if prev_path.exists():
            try:
                prev = json.loads(prev_path.read_text())
                udisc_plays = prev.get("udisc", {}).get("plays", 0)
                print(f"UDisc: käytetään edellistä {udisc_plays}")
            except:
                udisc_plays = 0
        else:
            udisc_plays = 0
    
    total_rounds = metrix_sum + (udisc_plays or 0)
    
    # Rakenna stats.json
    stats = {
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "updated_fi": time.strftime("%d.%m.%Y %H:%M", time.localtime()),
        "metrix": metrix_totals,
        "metrix_sum": metrix_sum,
        "udisc": {
            "plays": udisc_plays,
            "plays_30d": None,
            "source": "manual" if not fetch_udisc_plays else "scraped"
        },
        "total": {
            "rounds": total_rounds,
            "players": None,  # Täytetään kun saatavilla
            "playtime_hours": None,
            "steps": None,
            "kilometers": None
        },
        "sources": {
            "metrix_courses": [f"https://discgolfmetrix.com/course/{cid}" for cid in METRIX_IDS],
            "udisc_courses": UDISC_URLS + ["https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/manage/stats"]
        },
        "missing": metrix_missing
    }
    
    # Tallenna
    Path("data").mkdir(exist_ok=True)
    Path("data/stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Päivitä myös yksinkertainen versio frontendille
    simple = {
        "rounds": total_rounds,
        "metrix_sum": metrix_sum,
        "udisc": udisc_plays,
        "updated": stats["updated_fi"]
    }
    Path("data/simple.json").write_text(json.dumps(simple, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"\n=== Valmis ===")
    print(f"Metrix sum: {metrix_sum} ({metrix_totals})")
    print(f"UDisc: {udisc_plays}")
    print(f"TOTAL: {total_rounds}")
    print(f"Tallennettu data/stats.json")
    
    if metrix_missing:
        print(f"\nVAROITUS: Näiltä radoilta ei saatu kierroksia: {metrix_missing}")
        print("Suositus: Asenna Playwright GitHub Actionissa (katso workflow)")

if __name__ == "__main__":
    main()
