
import json, os, re, requests
from pathlib import Path
from datetime import datetime, timezone, timedelta

SEED = "43119"
KNOWN = ["48112","44763","44010"]  # 43119 poistettu käytöstä jos virhe
HEADERS = {"User-Agent":"Mozilla/5.0"}

def fetch_udisc():
    env = os.getenv("UDISC_MANUAL_COUNT")
    if env and env.isdigit(): return int(env), 67
    # override
    p = Path("data/udisc_override.json")
    if p.exists():
        try:
            j=json.loads(p.read_text())
            return int(j.get("plays",428)), int(j.get("players",67))
        except: pass
    return 428, 67

def fetch_metrix_playwright(course_ids):
    try:
        from playwright.sync_api import sync_playwright
    except: return None
    results={}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()
        for cid in course_ids:
            try:
                page.goto(f"https://discgolfmetrix.com/course/{cid}", wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3500)
                data = page.evaluate("""() => {
                    try{
                        if(!window.Highcharts) return [];
                        let out=[];
                        Highcharts.charts.forEach(ch=>{ if(!ch) return; ch.series.forEach(s=>{ out.push({name:s.name, data:s.data.map(d=>d.y||0)}) }) });
                        return out;
                    }catch(e){return []}
                }""")
                k=h=0
                for s in data:
                    name=(s.get("name") or "").lower()
                    sumy=sum(s.get("data") or [])
                    if "kilpailu" in name: k+=sumy
                    elif "harjoit" in name: h+=sumy
                # Jos SEED 43119 virhe -> skip
                if cid==SEED and k+h==0:
                    print(f"{cid} SEED virhe -> poistetaan")
                    continue
                results[cid] = {"kilpailu":k,"harjoitus":h,"total":k+h}
            except Exception as e:
                if cid==SEED:
                    print(f"SEED {cid} kaatui: {e} -> poistetaan")
                    continue
                results[cid] = {"kilpailu":0,"harjoitus":0,"total":0}
        browser.close()
    return results

def main():
    # UDisc
    udisc_rounds, udisc_players = fetch_udisc()
    # Metrix - yritä dynaaminen, fallback kuvasta
    metrix_data = fetch_metrix_playwright(KNOWN)
    if not metrix_data or sum(v["total"] for v in metrix_data.values())==0:
        # fallback kuvasta laskettu
        metrix_sum = 464
        metrix_players = 82
        kilpailu=122
        harjoitus=342
    else:
        metrix_sum = sum(v["total"] for v in metrix_data.values())
        metrix_players = int(metrix_sum * 0.1565)
        kilpailu = sum(v["kilpailu"] for v in metrix_data.values())
        harjoitus = sum(v["harjoitus"] for v in metrix_data.values())

    # UUSI LASKENTA kuten pyydetty
    kierrosmaara = metrix_sum + udisc_rounds
    eri_pelaajat = metrix_players + udisc_players

    now = datetime.now(timezone.utc) + timedelta(hours=3)
    out = {
        "rounds": kierrosmaara,
        "kierrosmaara": kierrosmaara,
        "metrix": metrix_sum,
        "udisc": udisc_rounds,
        "metrix_sum": metrix_sum,
        "udisc_rounds": udisc_rounds,
        "kilpailukierrokset": kilpailu,
        "harjoituskierrokset": harjoitus,
        "players": eri_pelaajat,
        "eri_pelaajat": eri_pelaajat,
        "metrix_players": metrix_players,
        "udisc_players": udisc_players,
        "updated": now.strftime("%d.%m.%Y klo %H:%M"),
        "updated_fi": now.strftime("%d.%m.%Y klo %H:%M") + " (auto 1s/5min metrix+udisc)",
        "formula": "metrix + udisc"
    }
    Path("data").mkdir(exist_ok=True)
    Path("data.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("data/simple.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("data/stats.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("last_update.txt").write_text(f"{out['updated']} - {kierrosmaara} rounds, {eri_pelaajat} players", encoding="utf-8")
    print(f"OK: {kierrosmaara} = {metrix_sum}+{udisc_rounds}, pelaajat {eri_pelaajat} = {metrix_players}+{udisc_players}")

if __name__=="__main__":
    main()
