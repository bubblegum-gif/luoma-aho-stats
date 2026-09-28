
"""
Luoma-ahon Frisbeegolfrata - Täysautomaatio
- 5min välein GitHub Actions
- Hakee Metrix 4 rataa Playwright + requests fallback
- UDisc: env UDISC_MANUAL_COUNT, data/udisc_override.json, data/stats.json edellinen
- Laskee skaalatut: players, hours, steps, km
- Tuottaa 3 JSON: data.json, data/stats.json, data/simple.json
- Estää datan nollaantumisen: käyttää edellistä jos scrape epäonnistuu
"""
import json, re, os, time
from pathlib import Path
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

METRIX_IDS = ["43119","48112","44763","44010"]
HEADERS = {"User-Agent":"Mozilla/5.0 (Luoma-aho Stats Bot) AppleWebKit/537.36", "Accept-Language":"fi-FI,fi;q=0.9,en;q=0.8"}

# Skaalauskertoimet UDisc referenssistä 428 -> 67,603,1275690
REF = {"rounds":428, "players":67, "hours":603, "steps":1275690}
PLAYERS_PER_ROUND = REF["players"]/REF["rounds"] # 0.1565
HOURS_PER_ROUND = REF["hours"]/REF["rounds"] # 1.409
STEPS_PER_ROUND = REF["steps"]/REF["rounds"] # 2980
KM_PER_STEP = 0.0008
KM_COURSE_PER_ROUND = 2.5

def fetch_metrix_requests(cid):
    url = f"https://discgolfmetrix.com/course/{cid}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
        text = soup.get_text(" ", strip=True)
        # Yleiset patternit
        patterns = [
            r'Rounds played[^\d]*(\d+)',
            r'Pelattuja kierroksia[^\d]*(\d+)',
            r'Kierroksia yhteensä[^\d]*(\d+)',
            r'Total rounds[^\d]*(\d+)',
            r'"totalRounds"\s*:\s*(\d+)',
        ]
        for pat in patterns:
            m = re.search(pat, text, re.I)
            if m:
                return int(re.sub(r'\D','', m.group(1)))
        return None
    except Exception as e:
        print(f"Metrix {cid} req fail: {e}")
        return None

def fetch_metrix_playwright():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright ei asennettu")
        return {}
    results={}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent=HEADERS["User-Agent"])
        page = context.new_page()
        for cid in METRIX_IDS:
            try:
                page.goto(f"https://discgolfmetrix.com/course/{cid}", wait_until="networkidle", timeout=40000)
                page.wait_for_timeout(3500)
                content = page.content()
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text(" ", strip=True)
                # Etsi Course statistics -taulukosta
                m = re.search(r'(?:Total|Yhteensä|Rounds).*?(\d{2,6})', text)
                # Parempi: etsi monthly stats sum
                # Yritä löytää kaikki numerot statistics-alueelta
                if m:
                    # validoi ettei ole liian pieni
                    val = int(m.group(1))
                    if val>5:
                        results[cid]=val
                        print(f"Metrix {cid} PW: {val}")
                        continue
                # fallback: etsi JSON:sta
                scripts = soup.find_all("script")
                for sc in scripts:
                    if sc.string and "total" in sc.string.lower():
                        nums = re.findall(r'(\d{3,6})', sc.string)
                        cands = [int(n) for n in nums if 10<int(n)<200000]
                        if cands:
                            results[cid]=max(cands)
                            break
                if cid not in results:
                    results[cid]=None
            except Exception as e:
                print(f"PW {cid} err {e}")
                results[cid]=None
        browser.close()
    return results

def fetch_udisc():
    # 1. override json
    for path in [Path("data/udisc_override.json"), Path("udisc_override.json")]:
        if path.exists():
            try:
                j=json.loads(path.read_text())
                if j.get("plays",0)>0:
                    print(f"UDisc override {j['plays']}")
                    return int(j["plays"])
            except: pass
    # 2. ENV
    man=os.getenv("UDISC_MANUAL_COUNT")
    if man and man.isdigit() and int(man)>0:
        print(f"UDisc ENV {man}")
        return int(man)
    # 3. yritä julkiselta (vain 30d, ei total) - ohitetaan totalissa
    # 4. fallback edellinen
    prev_files=[Path("data/stats.json"), Path("data/simple.json"), Path("data.json")]
    for pf in prev_files:
        if pf.exists():
            try:
                prev=json.loads(pf.read_text())
                # eri formaatit
                for key in ["udisc","plays","rounds"]:
                    v=prev.get("udisc",{}).get("plays") if isinstance(prev.get("udisc"),dict) else None
                    if v: return int(v)
                    if isinstance(prev.get("udisc"),int): return int(prev["udisc"])
                if prev.get("rounds"): return int(prev["rounds"])
            except: pass
    print("UDisc ei löytynyt, palautetaan 0 ja käytetään edellistä jos on")
    return None

def load_prev_stats():
    for p in [Path("data/stats.json"), Path("data.json")]:
        if p.exists():
            try:
                return json.loads(p.read_text())
            except: pass
    return {}

def main():
    print("=== Luoma-aho Auto Update START ===")
    prev = load_prev_stats()
    prev_metrix = prev.get("metrix",{}) if isinstance(prev.get("metrix"),dict) else {}
    prev_total_rounds = prev.get("total",{}).get("rounds") or prev.get("rounds") or 0

    pw = fetch_metrix_playwright()
    metrix={}
    metrix_sum=0
    for cid in METRIX_IDS:
        cnt = pw.get(cid) if pw else None
        if cnt is None:
            cnt = fetch_metrix_requests(cid)
        if cnt is None:
            # käytä edellistä ettei nollaannu
            cnt = int(prev_metrix.get(cid,0)) if prev_metrix.get(cid) else 0
            print(f"Metrix {cid}: fallback edellinen {cnt}")
        metrix[cid]=cnt
        metrix_sum+=cnt

    udisc = fetch_udisc()
    if udisc is None:
        # käytä edellistä
        udisc = int(prev.get("udisc",{}).get("plays",0) if isinstance(prev.get("udisc"),dict) else 0) or 0
        # jos vielä 0 ja meillä on referenssi 428
        if udisc==0 and prev_total_rounds>0:
            udisc = max(0, prev_total_rounds - metrix_sum)
        if udisc==0:
            udisc = 428  # viimeinen fallback referenssistä

    # Jos Metrix sum 0 (scrape ei toimi), käytä totalia UDiscina jotta luvut säilyy
    total_rounds = metrix_sum + udisc
    if metrix_sum==0:
        total_rounds = udisc if udisc>0 else (prev_total_rounds or 428)

    # Skaalatut
    players = int(round(total_rounds * PLAYERS_PER_ROUND))
    hours = round(total_rounds * HOURS_PER_ROUND, 1)
    steps = int(round(total_rounds * STEPS_PER_ROUND))
    km_steps = round(steps * KM_PER_STEP,1)
    km_course = round(total_rounds * KM_COURSE_PER_ROUND,1)

    now_utc = datetime.now(timezone.utc)
    now_fi_str = now_utc.astimezone().strftime("%d.%m.%Y klo %H:%M")
    # Suomen aika: käytetään UTC+3 kesäaikaan yksinkertaistettuna
    from datetime import timedelta
    fi_time = now_utc + timedelta(hours=3)
    fi_iso = fi_time.isoformat()

    stats = {
        "updated": now_utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated_fi": f"{fi_time.strftime('%d.%m.%Y klo %H:%M')} (auto 5min)",
        "updated_fi_iso": fi_iso,
        "metrix": metrix,
        "metrix_sum": metrix_sum,
        "udisc": {"plays": udisc, "source": "auto"},
        "total": {
            "rounds": total_rounds,
            "players": players,
            "playtime_hours": hours,
            "steps": steps,
            "kilometers_steps": km_steps,
            "kilometers_course": km_course,
            "kilometers": km_steps
        },
        "scaling": {
            "reference": f"UDisc {REF['rounds']} rounds = {REF['players']} players, {REF['hours']}h, {REF['steps']} steps",
            "players_per_round": PLAYERS_PER_ROUND,
            "hours_per_round": HOURS_PER_ROUND,
            "steps_per_round": STEPS_PER_ROUND,
            "km_per_step": KM_PER_STEP
        }
    }

    simple = {
        "rounds": total_rounds,
        "metrix_sum": metrix_sum,
        "udisc": udisc,
        "unique_players": players,
        "players": players,
        "recreation_hours": hours,
        "hours": hours,
        "steps": steps,
        "km": km_steps,
        "km_course": km_course,
        "updated": stats["updated_fi"],
        "updated_iso": stats["updated"]
    }

    scaled = {
        "rounds": total_rounds,
        "players": players,
        "hours": hours,
        "steps": steps,
        "km": km_steps,
        "km_course": km_course,
        "updated": stats["updated_fi"],
        "reference": REF
    }

    Path("data").mkdir(exist_ok=True)
    Path("data/stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("data/simple.json").write_text(json.dumps(simple, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("data/scaled.json").write_text(json.dumps(scaled, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("data.json").write_text(json.dumps(simple, indent=2, ensure_ascii=False), encoding="utf-8")  # rootille helppo fetch
    Path("last_update.txt").write_text(f"{stats['updated_fi']} - {total_rounds} rounds", encoding="utf-8")

    print(f"VALMIS: {total_rounds} rounds ({metrix_sum} metrix + {udisc} udisc) -> {players} pelaajaa, {hours}h")
    return stats

if __name__=="__main__":
    main()
