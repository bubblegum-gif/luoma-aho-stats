import json, os, re, requests
from datetime import datetime
HOLE_NAMES={1:"Russian Roulette",2:"Valonpolku",3:"Kännän Kuiskaus",4:"Julle Special",5:"Nice & Tight",6:"Tiikerin loikka",7:"Haukansilmä",8:"Kepposen Kirous",9:"Helvetin nousu"}

def fetch_udisc():
    return [{"rank":1,"username":"@kantanen8","score":35,"date":"4.7.2026"},{"rank":2,"username":"@valkoparta","score":36,"date":"6.7.2026"},{"rank":3,"username":"@mattiasss","score":36,"date":"19.8.2026"},{"rank":4,"username":"@dashyy","score":38,"date":"13.9.2025"},{"rank":5,"username":"@eero_heittaja","score":39,"date":"12.9.2025"},{"rank":6,"username":"@discgolfari91","score":40,"date":"10.9.2025"},{"rank":7,"username":"@frisbee_fi","score":40,"date":"8.9.2025"},{"rank":8,"username":"@alajarvi_pro","score":41,"date":"5.9.2025"},{"rank":9,"username":"@kiekko_mies","score":41,"date":"3.9.2025"},{"rank":10,"username":"@luoma_aho_fan","score":42,"date":"1.9.2025"}]

def scan_metrix_for_hio(course_id):
    hios=[]
    try:
        url=f"https://discgolfmetrix.com/course/{course_id}"
        r=requests.get(url, timeout=12, headers={'User-Agent':'L-A-FRIBA-HIO-Bot/1.0'})
        if r.status_code!=200: return hios
        # Find result pages
        ids=re.findall(r'/([0-9]{6,8})[^0-9]', r.text)[:15]
        for cid in ids:
            try:
                cr=requests.get(f"https://discgolfmetrix.com/{cid}", timeout=10, headers={'User-Agent':'L-A-FRIBA-HIO-Bot/1.0'})
                if cr.status_code!=200: continue
                if '>1<' not in cr.text: continue
                # try parse
                try:
                    from bs4 import BeautifulSoup
                    soup=BeautifulSoup(cr.text,'html.parser')
                    for tr in soup.find_all('tr'):
                        tds=tr.find_all('td')
                        if len(tds)<5: continue
                        for idx, td in enumerate(tds):
                            if td.get_text(strip=True)=='1':
                                player=tds[1].get_text(strip=True) if len(tds)>1 else ''
                                if not player or len(player)<3 or player=='Par': continue
                                hole=idx-2
                                if 1<=hole<=18:
                                    if hole>9: hole=((hole-1)%9)+1
                                    hios.append({'hole':hole,'hole_name':HOLE_NAMES.get(hole,f'Vayla {hole}'),'player':player,'date':datetime.now().strftime('%d.%m.%Y'),'source':f'Metrix {course_id}','course_id':str(course_id),'competition':cid})
                except Exception as e:
                    print(f"parse fail {cid}: {e}")
            except Exception as e:
                print(e)
                continue
    except Exception as e:
        print(f"HIO scan fail {course_id}: {e}")
    # dedup
    uniq={}
    for h in hios:
        uniq[(h['player'],h['hole'])]=h
    return list(uniq.values())

def main():
    data={}
    try:
        with open('data.json','r',encoding='utf-8') as f: data=json.load(f)
    except: pass

    data['udisc_leaderboard']=fetch_udisc()

    # LIVE TOP 10 Metrixistä
    total_metrix_rounds = 0
    for cid in ["44010","44763"]:
        top = fetch_metrix_top(cid, limit=10)
        if top:
            if 'courses' not in data: data['courses']={}
            if cid not in data['courses']: data['courses'][cid]={}
            data['courses'][cid]['top_results']=top
            print(f"Metrix {cid} top {len(top)} haettu")

    # --- UUSI: PELIAIKA LASKENTA KIERROKSISTA ---
    # Luetaan olemassa olevat luvut jos ei uutta dataa
    udisc_rounds = data.get('static_verified',{}).get('udisc', 413)
    metrix_rounds = data.get('static_verified',{}).get('metrix', 60)

    # Jos haluat tulevaisuudessa lukea oikean määrän Metrix APIsta, päivitä nämä:
    # esim. len(fetch_all_practice_rounds)

    total_rounds = udisc_rounds + metrix_rounds

    # Oletus: 12 väylää = 1.25h, 24 väylää = 2.5h
    # Tässä yksinkertaistus: kaikki lasketaan 12 väylän mukaan
    # Jos haluat erotella: 44010 * 1.25 + 44763 * 2.5
    hours_per_round = 1.25 # vaihda 1.5 jos haluat 1,5h
    hours = round(total_rounds * hours_per_round)
    steps_per_round = 2605
    steps = total_rounds * steps_per_round

    if 'static_verified' not in data: data['static_verified']={}
    data['static_verified']['total_rounds'] = total_rounds
    data['static_verified']['hours'] = hours
    data['static_verified']['steps'] = steps
    # --------------------------------------------

    known=[
        {"hole":4,"hole_name":"Julle Special","player":"Benjamin Turja","date":"2025","source":"Metrix 44010","course_id":"44010"},
        {"hole":4,"hole_name":"Julle Special","player":'Julius "Julle Special" Luoma-aho',"date":"2025","source":"Metrix 44010","course_id":"44010"},
        {"hole":8,"hole_name":"Kepposen Kirous","player":"Pentti Pitkäranta","date":"2025","source":"Metrix 44010","course_id":"44010"},
    ]
    live=[]
    for cid in ["44010","44763"]:
        live.extend(scan_metrix_for_hio(cid))
    merged={}
    for h in known+live:
        merged[(h['player'],h['hole'])]=h
    data['hio']=list(merged.values())
    data['hio_updated']=datetime.now().isoformat()
    data['updated']=datetime.now().isoformat()
    with open('data.json','w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2)
    print(f"Done total:{total_rounds} hours:{hours}h steps:{steps} LB:{len(data['udisc_leaderboard'])} HIO:{len(data['hio'])}")

if __name__=="__main__":
    main()
