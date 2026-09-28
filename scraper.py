
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
    
    
    # --- SKAALATTU LASKENTA UDISC-DATASTA ---
    # UDisc referenssi (kuvasta 13.05.2026):
    # 428 rounds, 67 unique, 603h, 1 275 690 steps
    UD_REF_ROUNDS = 428
    UD_REF_PLAYERS = 67
    UD_REF_HOURS = 603
    UD_REF_STEPS = 1275690
    UD_REF_KM_PER_STEP = 0.0008  # 0.8m per askel
    
    # Kertoimet
    players_per_round = UD_REF_PLAYERS / UD_REF_ROUNDS  # 0.1565
    hours_per_round = UD_REF_HOURS / UD_REF_ROUNDS      # 1.409h
    steps_per_round = UD_REF_STEPS / UD_REF_ROUNDS      # 2980.35
    km_per_step = UD_REF_KM_PER_STEP
    
    # Skaalatut totaalit (Metrix + UDisc)
    total_players_est = int(round(total_rounds * players_per_round)) if total_rounds > 0 else 0
    total_hours_est = round(total_rounds * hours_per_round, 1) if total_rounds > 0 else 0
    total_steps_est = int(round(total_rounds * steps_per_round)) if total_rounds > 0 else 0
    total_km_est = round(total_steps_est * km_per_step, 1) if total_steps_est > 0 else 0
    
    # Jos halutaan käyttää myös ratapituuteen perustuvaa km (2.5km/kierros), lasketaan myös se
    km_per_round_course = 2.5
    total_km_course = round(total_rounds * km_per_round_course, 1)
    
    # Käytetään askel-pohjaista km:ää ensisijaisena (tarkempi), mutta tallennetaan molemmat

    # Rakenna stats.json
    stats = {
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "updated_fi": time.strftime("%d.%m.%Y %H:%M", time.localtime()),
        "metrix": metrix_totals,
        "metrix_sum": metrix_sum,
        "udisc": {
            "plays": udisc_plays,
            "unique_players": 67,
            "recreation_hours": 603,
            "steps": 1275690,
            "source": "UDisc screenshot 13.05.2026 - scaled"
        },
        "scaling": {
            "reference": "UDisc 428 rounds = 67 players, 603h, 1275690 steps",
            "players_per_round": round(players_per_round, 4),
            "hours_per_round": round(hours_per_round, 3),
            "steps_per_round": round(steps_per_round, 1),
            "km_per_step": km_per_step
        },
        "total": {
            "rounds": total_rounds,
            "players": total_players_est,
            "playtime_hours": total_hours_est,
            "steps": total_steps_est,
            "kilometers_steps": total_km_est,
            "kilometers_course": total_km_course,
            "kilometers": total_km_est  # primary
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
        "players": total_players_est,
        "playtime_hours": total_hours_est,
        "steps": total_steps_est,
        "kilometers": total_km_est,
        "kilometers_course": total_km_course,
        "updated": stats["updated_fi"],
        "scaling_note": "Skaalattu UDisc referenssistä: 428 kier = 67 pelaajaa, 603h, 1275690 askelta"
    }
    Path("data/simple.json").write_text(json.dumps(simple, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Tallenna myös erillinen skaalattu tiedosto frontendille
    Path("data/scaled.json").write_text(json.dumps({
        "rounds": total_rounds,
        "players": total_players_est,
        "hours": total_hours_est,
        "steps": total_steps_est,
        "km": total_km_est,
        "updated": stats["updated_fi"]
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    
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
