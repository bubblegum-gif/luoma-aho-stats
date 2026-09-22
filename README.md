# Luoma-ahon Frisbeegolfrata - JSON + HTML Paketti (EI App.tsx)

## Rakenne - puhdas HTML + JSON, ei React buildia tarvita!

```
Luoma-Aho-JSON-HTML-PAKETTI/
├── index.html (UUSI - lukee JSONit, toimii suoraan!)
├── data/
│   ├── ratainfo.json (12 riviä rataesittely)
│   ├── vaylat.json (12 väylää Par/Avg/HUOM/Birdie%)
│   ├── tilastot.json (1060 tulosta, 229 pelaajaa...)
│   ├── top5.json (Väyläopaste TOP 6 + 2 kierrosta TOP, Par rating 990/972)
│   ├── udisc_top10.json (UDisc Leaderboard TOP10)
│   ├── saa.json (Foreca 14°C + 4h ennuste)
│   └── header.json (9 nappia config, Metrix transparent oranssi, Tähti poistettu)
├── legacy-bundle-10nappia-ILMAN-TAHTIA.html (vanha bundle 3.89MB, toimii offline)
└── legacy-OIKEA-119afd2b505f-ORIGINAL.html (alkuperäinen 10 nappia)
```

## Käyttö GitHubissa

### Tapa 1: GitHub Pages (suositus)
1. Luo repo `luoma-aho-frisbeegolf`
2. Lataa KAIKKI tiedostot tähän zipistä repoosi (index.html + data kansio)
3. Settings -> Pages -> Source: Deploy from branch -> main / root
4. Valmis! https://USERNAME.github.io/luoma-aho-frisbeegolf/

### Tapa 2: Vain JSON datat
- Voit käyttää `data/*.json` missä vaan - esim. omaan appiin, WordPressiin, Frisbeegolfradat.fi
- Kaikki JSON validia, UTF-8, indent 2

## JSON Esimerkkejä

**ratainfo.json:**
```json
{
  "ratainfo": ["Kalliopohjaisessa mäkisessä...", "12 väylää, Par 46..."]
}
```

**vaylat.json:**
```json
{
  "par_yhteensa": 46,
  "vaylat": [{"vayla":1,"par":4,"avg_yhdist":4.51,"huom_overPar":0.51,...}]
}
```

**tilastot.json:**
```json
{
  "tulos_kirjatut_ja_kierrosten_maara": 1060,
  "eri_pelaajia": 229,
  "peliaika": "58 pv 21 h"
}
```

## Kirurgiset korjaukset vs OIKEA 119afd2b505f
- Metrix: valkoinen pohja poistettu -> transparent, vain oranssi logo, rounded-full 9999px
- Tähti pilli: poistettu headerista (ei toiminut oikein)

## index.html
- Ei App.tsx, ei npm, ei build
- Pelkkä HTML + Tailwind CDN + vanilla JS fetch(data/*.json)
- Toimii heti kun avaat selaimessa tai GitHub Pagesissa
- Musta header 76/92px kuten OIKEA

## Legacy bundlet mukana
Jos haluat vanhan toimivan offline-version (3.89MB kaikki base64 sisällä), käytä `legacy-*.html`

---
Alajärvi 2025 - Luoma-ahon Frisbeegolfrata
