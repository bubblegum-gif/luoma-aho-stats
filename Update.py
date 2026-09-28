#!/usr/bin/env python3
"""
Luoma-ahon Frisbeegolfrata - Automaattinen päivitysskripti
Ajetaan GitHub Actionsilla 1h välein.

Tämä on runko - lisätään toimintoja 1 asia kerrallaan.
"""

import json
import os
from datetime import datetime, timezone
import zoneinfo

# Helsingin aikavyöhyke
TZ = zoneinfo.ZoneInfo("Europe/Helsinki")

DATA_FILE = "data.json"
HTML_FILE = "index.html"

def get_now():
    """Palauttaa tämän hetken Suomen ajassa"""
    now_utc = datetime.now(timezone.utc)
    now_fi = now_utc.astimezone(TZ)
    return now_fi

def update_data_json():
    """Päivittää data.json tiedoston timestampilla"""
    now = get_now()
    
    # Lue vanha data jos on olemassa
    data = {}
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = {}

    # Päivitä timestamp
    data["last_updated"] = now.isoformat()
    data["last_updated_fi"] = now.strftime("%d.%m.%Y klo %H:%M")
    data["version"] = data.get("version", 1)

    # Tulevat kentät - lisätään myöhemmin:
    # data["saa"] = ...
    # data["ratatilanne"] = ...
    # data["tulokset"] = ...

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ data.json päivitetty: {data['last_updated_fi']}")
    return data

def update_html_timestamp():
    """Päivittää index.html:ään viimeisin päivitysaika jos paikka löytyy"""
    if not os.path.exists(HTML_FILE):
        print(f"! {HTML_FILE} ei löytynyt, ohitetaan HTML päivitys")
        return

    now = get_now()
    timestamp_str = now.strftime("%d.%m.%Y klo %H:%M")

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    # Jos html:ssä on <!-- LAST_UPDATE --> placeholder, korvataan se
    if "<!-- LAST_UPDATE -->" in content:
        content = content.replace(
            "<!-- LAST_UPDATE -->",
            f"<!-- LAST_UPDATE -->{timestamp_str}"
        )
        # Tai parempi: etsitään elementti id:llä
    if 'id="last-update"' in content:
        # Yksinkertainen korvaus - päivitä sisältö
        import re
        content = re.sub(
            r'(<span id="last-update">)(.*?)(</span>)',
            rf'\g<1>{timestamp_str}\g<3>',
            content
        )
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✓ {HTML_FILE} timestamp päivitetty")

def main():
    print(f"--- Luoma-aho update.py käynnistetty ---")
    data = update_data_json()
    update_html_timestamp()
    print(f"--- Valmis ---\n")
    print(json.dumps(data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
