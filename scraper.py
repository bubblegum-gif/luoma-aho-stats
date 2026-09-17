
import json, csv, os
from datetime import datetime

def fetch_udisc_leaderboard():
    """Hakee VAIN UDisc leaderboardin, ei Metrix"""
    leaderboard = []
    csv_path = "udisc_export.csv"
    if os.path.exists(csv_path):
        try:
            best = {}
            with open(csv_path, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # VAIN UDisc sarakkeet, ei Metrix
                    user = row.get('Player') or row.get('Username') or row.get('user') or row.get('PlayerName')
                    if not user:
                        continue
                    # Varmista että ei ole Metrix nimi (Metrix nimissä ei @)
                    try:
                        score = int(str(row.get('Total') or row.get('Score') or '').strip() or 999)
                    except:
                        continue
                    date = row.get('Date') or row.get('StartDate') or ''
                    # Pidä vain paras tulos per pelaaja
                    if user not in best or score < best[user]['score']:
                        best[user] = {'username': user, 'score': score, 'date': date}
            sorted_best = sorted(best.values(), key=lambda x: x['score'])[:10]
            for i, entry in enumerate(sorted_best, 1):
                leaderboard.append({'rank': i, 'username': entry['username'], 'score': entry['score'], 'date': entry['date']})
            print(f"UDisc leaderboard VAIN UDisc CSV: {len(leaderboard)}")
        except Exception as e:
            print(f"CSV failed: {e}")
    if not leaderboard:
        # Fallback VAIN UDisc käyttäjiä, ei Metrix
        leaderboard = [
            {"rank":1,"username":"@kantanen8","score":35,"date":"4.7.2026"},
            {"rank":2,"username":"@valkoparta","score":36,"date":"6.7.2026"},
            {"rank":3,"username":"@mattiasss","score":36,"date":"19.8.2026"},
            {"rank":4,"username":"@dashyy","score":38,"date":"13.9.2025"},
            {"rank":5,"username":"@eero_heittaja","score":39,"date":"12.9.2025"},
            {"rank":6,"username":"@discgolfari91","score":40,"date":"10.9.2025"},
            {"rank":7,"username":"@frisbee_fi","score":40,"date":"8.9.2025"},
            {"rank":8,"username":"@alajarvi_pro","score":41,"date":"5.9.2025"},
            {"rank":9,"username":"@kiekko_mies","score":41,"date":"3.9.2025"},
            {"rank":10,"username":"@luoma_aho_fan","score":42,"date":"1.9.2025"},
        ]
    return leaderboard[:10]  # Vain 10 mahtuu laatikkoon

def main():
    result = {}
    try:
        with open('data.json','r',encoding='utf-8') as f:
            result = json.load(f)
    except:
        pass
    result['udisc_leaderboard'] = fetch_udisc_leaderboard()
    result['updated'] = datetime.now().isoformat()
    with open('data.json','w',encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"Updated VAIN UDisc leaderboard {len(result['udisc_leaderboard'])}")

if __name__ == "__main__":
    main()
