
import json, os, re, requests, csv, io
from pathlib import Path
from datetime import datetime, timezone, timedelta

SEED = "43119"
KNOWN = ["48112","44763","44010"]
HEADERS = {"User-Agent":"Mozilla/5.0 (Luoma-aho Auto Bot)"}

def fetch_udisc_csv():
    """
    UDisc CSV import - toimii 100% automaattisesti kun lataat CSV:n
    - Mene UDisc: Course Tools -> Statistics -> Download CSV (tai Lifetime stats)
    - Lataa tiedosto data/udisc_stats.csv (tai data/udisc.csv)
    - Workflow lukee sen automaattisesti
    Tukee myös UDisc Fact Sheet ja monthly CSV:t
    """
    csv_paths = [
        Path("data/udisc_stats.csv"),
        Path("data/udisc.csv"),
        Path("data/udisc_lifetime.csv"),
        Path("udisc_stats.csv"),
    ]
    for p in csv_paths:
        if p.exists():
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
                # Yritä parsia
                # UDisc CSV formaatteja:
                # 1. Lifetime: Date, Plays, Unique players...
                # 2. Fact Sheet: total plays rivillä
                # Etsi numeroita
                reader = csv.DictReader(io.StringIO(text))
                total_plays = 0
                unique_players = set()
                max_unique = 0
                # Jos headerit on Plays, Unique
                for row in reader:
                    # etsi plays sarake
                    plays = 0
                    for k in ["Plays","plays","Total plays","Round count","Rounds"]:
                        if k in row and str(row[k]).isdigit():
                            plays = int(row[k])
                            break
                    if plays==0:
                        # yritä ensimmäinen numerokolumni
                        for v in row.values():
                            if str(v).strip().isdigit():
                                try:
                                    plays = int(str(v).strip())
                                    if plays>0: break
                                except: pass
                    total_plays += plays
                    # unique
                    for k in ["Unique players","Unique","Players","unique_players"]:
                        if k in row:
                            try:
                                uv = int(str(row[k]).strip())
                                if uv>max_unique: max_unique=uv
                            except: pass
                # Jos CSV on pelkkä teksti jossa "Total: 428 plays"
                if total_plays==0:
                    m = re.search(r"(\d+)\s*plays", text, re.I)
                    if m: total_plays = int(m.group(1))
                    m2 = re.search(r"(\d+)\s*unique", text, re.I)
                    if m2: max_unique = int(m2.group(1))
                
                if total_plays>0:
                    players = max_unique if max_unique>0 else int(total_plays * 0.1565)
                    print(f"UDisc CSV {p}: {total_plays} kierrosta, {players} pelaajaa")
                    return total_plays, players, f"csv:{p}"
            except Exception as e:
                print(f"UDisc CSV lukuvirhe {p}: {e}")

    return None

def fetch_udisc():
    # 1. CSV ensin (tarkin)
    csv_res = fetch_udisc_csv()
    if csv_res:
        return csv_res

    # 2. ENV
    env_rounds = os.getenv("UDISC_MANUAL_COUNT")
    env_players = os.getenv("UDISC_MANUAL_PLAYERS")
    if env_rounds and env_rounds.isdigit():
        rounds = int(env_rounds)
        players = int(env_players) if env_players and env_players.isdigit() else int(rounds * 0.1565)
        print(f"UDisc ENV: {rounds} kierrosta, {players} pelaajaa")
        return rounds, players, "env"

    # 3. override json
    for path in [Path("data/udisc_override.json"), Path("udisc_override.json")]:
        if path.exists():
            try:
                j = json.loads(path.read_text())
                plays = int(j.get("plays") or j.get("rounds") or 0)
                players = int(j.get("players") or j.get("unique") or (plays * 0.1565) if plays else 0)
                if plays>0:
                    print(f"UDisc override {path}: {plays} kierrosta, {players} pelaajaa")
                    return plays, players, f"override:{path}"
            except: pass

    # 4. Fallback edellinen / hardcoded
    for pf in [Path("data/stats.json"), Path("data.json")]:
        if pf.exists():
            try:
                prev = json.loads(pf.read_text())
                if isinstance(prev.get("udisc"), dict):
                    pr = prev["udisc"].get("plays")
                    pp = prev["udisc"].get("players")
                    if pr: return int(pr), int(pp or pr*0.1565), "prev_stats"
                if prev.get("udisc_rounds"):
                    return int(prev["udisc_rounds"]), int(prev.get("udisc_players",67)), "prev_simple"
            except: pass

    print("UDisc fallback 428/67")
    return 428, 67, "fallback_hardcoded"

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
                if cid==SEED and k+h==0: continue
                results[cid] = {"kilpailu":k,"harjoitus":h,"total":k+h}
            except Exception as e:
                if cid==SEED: continue
                results[cid] = {"kilpailu":0,"harjoitus":0,"total":0}
        browser.close()
    return results

def main():
    import io
    udisc_rounds, udisc_players, udisc_src = fetch_udisc()
    metrix_data = fetch_metrix_playwright(KNOWN)
    if not metrix_data or sum(v["total"] for v in metrix_data.values())==0:
        metrix_sum = 464
        metrix_players = 82
        kilpailu=122
        harjoitus=342
        metrix_src = "fallback_image_464"
    else:
        metrix_sum = sum(v["total"] for v in metrix_data.values())
        metrix_players = int(metrix_sum * 0.1565)
        kilpailu = sum(v["kilpailu"] for v in metrix_data.values())
        harjoitus = sum(v["harjoitus"] for v in metrix_data.values())
        metrix_src = "playwright"

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
        "updated_fi": now.strftime("%d.%m.%Y klo %H:%M") + f" (auto 1s/5min metrix:{metrix_src} udisc:{udisc_src})",
        "formula": "metrix + udisc",
        "sources": {"metrix": metrix_src, "udisc": udisc_src}
    }
    Path("data").mkdir(exist_ok=True)
    # Säilytä hole_stats jos olemassa
    try:
        hs_path = Path("data/hole_stats.json")
        if hs_path.exists():
            hs = json.loads(hs_path.read_text())
            out["hole_stats"] = hs.get("metrix_manual")
            out["udisc_monthly"] = hs.get("udisc_csv")
    except: pass
    Path("data.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("data/data.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("simple.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("data/simple.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("data/stats.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    Path("last_update.txt").write_text(f"{out['updated']} - {kierrosmaara} rounds ({metrix_sum}+{udisc_rounds}), {eri_pelaajat} players", encoding="utf-8")
    print(f"OK: {kierrosmaara} = {metrix_sum}+{udisc_rounds}, pelaajat {eri_pelaajat} = {metrix_players}+{udisc_players}")

if __name__=="__main__":
    main()
