
import json, os, re, requests
from datetime import datetime
from pathlib import Path

HOLE_NAMES={1:"Russian Roulette",2:"Valonpolku",3:"Kännän Kuiskaus",4:"Julle Special",5:"Nice & Tight",6:"Tiikerin loikka",7:"Haukansilmä",8:"Kepposen Kirous",9:"Helvetin nousu"}

# ----- CONFIG - 44010 + 44763 + PARENT 43119 AUTO -----
COURSES = ["44010","44763"]
PARENT_COURSE = "43119"
HOURS_PER_12 = 1.2
STEPS_PER_ROUND = 2963
# ------------------------------------------------------

def fetch_udisc():
    csv_path = Path("udisc_export.csv")
    if csv_path.exists():
        try:
            import csv
            rows = list(csv.DictReader(open(csv_path, encoding='utf-8')))
            lb=[]
            for i,r in enumerate(sorted(rows, key=lambda x: int(x.get('score',999)))[:10]):
                lb.append({"rank":i+1,"username":r.get('username','@player'),"score":int(r.get('score',0)),"date":r.get('date','')})
            if lb:
                return lb
        except Exception as e:
            print(f"UDisc CSV fail: {e}")
    return [{"rank":1,"username":"@kantanen8","score":35,"date":"4.7.2026"},{"rank":2,"username":"@valkoparta","score":36,"date":"6.7.2026"},{"rank":3,"username":"@mattiasss","score":36,"date":"19.8.2026"},{"rank":4,"username":"@dashyy","score":38,"date":"13.9.2025"},{"rank":5,"username":"@eero_heittaja","score":39,"date":"12.9.2025"},{"rank":6,"username":"@discgolfari91","score":40,"date":"10.9.2025"},{"rank":7,"username":"@frisbee_fi","score":40,"date":"8.9.2025"},{"rank":8,"username":"@alajarvi_pro","score":41,"date":"5.9.2025"},{"rank":9,"username":"@kiekko_mies","score":41,"date":"3.9.2025"},{"rank":10,"username":"@luoma_aho_fan","score":42,"date":"1.9.2025"}]

def fetch_all_layouts_from_parent(parent_id="43119"):
    layouts = set(COURSES)
    try:
        url=f"https://discgolfmetrix.com/course/{parent_id}"
        r=requests.get(url, timeout=15, headers={'User-Agent':'L-A-FRIBA-AUTO/1.0'})
        if r.status_code==200:
            found = re.findall(r'/course/(\d{4,6})', r.text)
            for fid in found:
                if fid != parent_id and fid not in layouts:
                    layouts.add(fid)
            print(f"Parent {parent_id} alta layoutit: {sorted(layouts)}")
    except Exception as e:
        print(f"fetch_all_layouts fail: {e}")
    all_list = sorted(list(layouts))
    if parent_id not in all_list:
        all_list.append(parent_id)
    return all_list

def fetch_metrix_top(course_id, limit=5):
    results=[]
    try:
        url=f"https://discgolfmetrix.com/course/{course_id}"
        r=requests.get(url, timeout=15, headers={'User-Agent':'L-A-FRIBA-LIVE/1.0'})
        if r.status_code!=200:
            return results
        text=r.text
        for line in text.splitlines():
            if not line.strip().startswith("|"):
                continue
            parts=[p.strip() for p in line.split("|")]
            if len(parts)<6:
                continue
            try:
                rank_str=parts[1]
                if not rank_str.isdigit():
                    continue
                rank=int(rank_str)
                name=parts[2]
                if not name or len(name)<2 or name.lower() in ["par","result","name"]:
                    continue
                date_raw=parts[3] if len(parts)>3 else ""
                non_empty=[p for p in parts if p!='']
                if len(non_empty)<2:
                    continue
                total_str=non_empty[-1]
                plus_minus=non_empty[-2]
                date_fmt=date_raw
                m=re.search(r'(\d+)/(\d+)/(\d+)', date_raw)
                if m:
                    mm,dd,yy=m.groups()
                    month=int(mm); day=int(dd); year=int(yy)
                    if year<100: year+=2000
                    date_fmt=f"{day}.{month}.{year}"
                total_val=int(total_str) if total_str.isdigit() else total_str
                results.append({"rank":rank,"name":name,"plus_minus":plus_minus,"total":total_val,"date":date_fmt})
            except:
                continue
        results_sorted=sorted(results, key=lambda x: (x['total'] if isinstance(x['total'],int) else 999, x['rank']))[:limit]
        for i,rr in enumerate(results_sorted):
            rr['rank']=i+1
        return results_sorted
    except Exception as e:
        print(f"fetch_metrix_top {course_id} fail: {e}")
        return []

def fetch_metrix_all_practice_count(course_list=None):
    if course_list is None:
        course_list = fetch_all_layouts_from_parent(PARENT_COURSE)
    counts={}
    total=0
    for cid in course_list:
        try:
            url=f"https://discgolfmetrix.com/course/{cid}"
            r=requests.get(url, timeout=15, headers={'User-Agent':'L-A-FRIBA-LIVE/1.0'})
            if r.status_code!=200:
                continue
            cnt=0
            for line in r.text.splitlines():
                ls=line.strip()
                if not ls.startswith("|"):
                    continue
                parts=[p.strip() for p in ls.split("|")]
                if len(parts)>=4 and parts[1].isdigit():
                    name=parts[2]
                    if name and name.lower()!="par" and len(name)>2:
                        cnt+=1
            counts[cid]=cnt
            total+=cnt
            print(f"Metrix {cid} KAIKKI: {cnt}")
        except Exception as e:
            print(f"count {cid} fail: {e}")
    counts["total"]=total
    counts["source"]=f"Parent {PARENT_COURSE} + layouts {course_list} LIVE"
    counts["course_list"]=course_list
    return counts

def scan_metrix_for_hio(course_id):
    hios=[]
    try:
        url=f"https://discgolfmetrix.com/course/{course_id}"
        r=requests.get(url, timeout=12, headers={'User-Agent':'L-A-FRIBA-HIO/1.0'})
        if r.status_code!=200: return hios
        ids=re.findall(r'/([0-9]{6,8})[^0-9]', r.text)[:15]
        for cid in ids:
            try:
                cr=requests.get(f"https://discgolfmetrix.com/{cid}", timeout=10, headers={'User-Agent':'L-A-FRIBA-HIO/1.0'})
                if cr.status_code!=200: continue
                if '>1<' not in cr.text: continue
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
            except:
                continue
    except Exception as e:
        print(f"HIO fail {course_id}: {e}")
    uniq={}
    for h in hios:
        uniq[(h['player'],h['hole'])]=h
    return list(uniq.values())

def main():
    data={}
    data_path=Path("data.json")
    if data_path.exists():
        try:
            data=json.loads(data_path.read_text(encoding='utf-8'))
        except:
            data={}

    data['udisc_leaderboard']=fetch_udisc()

    all_courses = fetch_all_layouts_from_parent(PARENT_COURSE)
    for c in COURSES:
        if c not in all_courses:
            all_courses.append(c)

    if 'courses' not in data: data['courses']={}
    for cid in all_courses:
        top=fetch_metrix_top(cid, limit=5)
        if top:
            if cid not in data['courses']: data['courses'][cid]={}
            data['courses'][cid]['top_results']=top

    sv=data.get('static_verified',{})
    udisc_rounds=sv.get('udisc_lifetime_with_2026', 624)
    if udisc_rounds < 624:
        udisc_rounds = 624

    metrix_counts=fetch_metrix_all_practice_count(all_courses)
    metrix_rounds=metrix_counts.get("total",58) if metrix_counts else 58

    total_rounds=udisc_rounds + metrix_rounds
    hours=round(udisc_rounds*1.2 + metrix_rounds*1.25)
    steps=udisc_rounds*2963 + metrix_rounds*2605

    data['static_verified']['total_rounds']=total_rounds
    data['static_verified']['udisc']=udisc_rounds
    data['static_verified']['metrix']=metrix_rounds
    data['static_verified']['metrix_breakdown']=metrix_counts
    data['static_verified']['hours']=hours
    data['static_verified']['steps']=steps
    data['static_verified']['unique_players']=72
    data['static_verified']['parent_course']=PARENT_COURSE
    data['static_verified']['all_layouts']=all_courses

    known=[
        {"hole":4,"hole_name":"Julle Special","player":"Benjamin Turja","date":"2025","source":"Metrix 44010","course_id":"44010"},
        {"hole":4,"hole_name":"Julle Special","player":'Julius "Julle Special" Luoma-aho',"date":"2025","source":"Metrix 44010","course_id":"44010"},
        {"hole":8,"hole_name":"Kepposen Kirous","player":"Pentti Pitkäranta","date":"2025","source":"Metrix 44010","course_id":"44010"},
    ]
    live=[]
    for cid in all_courses[:5]:
        live.extend(scan_metrix_for_hio(cid))
    merged={}
    for h in known+live:
        merged[(h['player'],h['hole'])]=h
    data['hio']=list(merged.values())
    data['hio_updated']=datetime.now().isoformat()
    data['updated']=datetime.now().isoformat()

    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"AUTO DONE parent {PARENT_COURSE} layouts {all_courses} total:{total_rounds} (UDisc {udisc_rounds}+Metrix {metrix_rounds})")

if __name__=="__main__":
    main()
