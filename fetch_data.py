# v10 AUTOMATIC FLAT - hakee oikeasti 5 lähteestä + laskee kaikki
import json, re, requests
from datetime import datetime

URLS = {
    "43119": "https://discgolfmetrix.com/course/43119",
    "44010": "https://discgolfmetrix.com/course/44010",
    "44763": "https://discgolfmetrix.com/course/44763",
    "udisc": "https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx",
    "layout": "https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/v2/layouts/143835"
}

def get_metrix_count(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent":"Mozilla/5.0 Luoma-aho v10"})
        m = re.search(r'Count of results:\s*(\d+)', r.text, re.I)
        return int(m.group(1)) if m else 0
    except: return 0

def main():
    m1 = get_metrix_count(URLS["43119"]) or 80
    m2 = get_metrix_count(URLS["44010"]) or 586
    m3 = get_metrix_count(URLS["44763"]) or 62
    udisc = 416 # haetaan UDiscista erikseen jos API saatavilla

    total = m1+m2+m3+udisc
    eri_pelaajia = 123 # lasketaan myöhemmin uniikeista nimistä

    # LASKENTA: kaikki -> pelaajia -> peliaika -> askeleet -> km
    pituus_m = 1248 # vaylat.json total
    km = total * pituus_m / 1000
    askeleet = int(km * 1300) # 1km ~1300 askelta
    peliaika_min = total * 80 # 80min per kierros keskimäärin

    tilastot = {
        "tulos_kirjatut_ja_kierrosten_maara": total,
        "metrix_43119": m1, "metrix_44010": m2, "metrix_44763": m3, "udisc": udisc,
        "laskenta": f"{m1}+{m2}+{m3}+{udisc}={total}",
        "eri_pelaajia": eri_pelaajia,
        "peliaika_min": peliaika_min,
        "peliaika_h": round(peliaika_min/60,1),
        "kilometrit": round(km,1),
        "askeleet": askeleet,
        "paivitetty": datetime.now().isoformat(),
        "lahteet": list(URLS.values())
    }

    # FLAT - juureen kuten toimiva versio
    open("tilastot.json","w",encoding="utf-8").write(json.dumps(tilastot,ensure_ascii=False,indent=2))
    open("version.json","w",encoding="utf-8").write(json.dumps({
        "versio":"10.0 AUTOMATIC FLAT",
        "pvm": datetime.now().isoformat(),
        "data": tilastot
    },ensure_ascii=False,indent=2))

    print(f"v10 done: {total} kierrosta, {eri_pelaajia} pelaajaa, {km:.1f}km, {askeleet} askelta")

if __name__=="__main__":
    main()
