
# Luoma-ahon Frisbeegolfrata - Auto-päivittyvä kävijälaskuri

Hakee automaattisesti:
- https://discgolfmetrix.com/course/44010 (12 väylää)
- https://discgolfmetrix.com/course/44763 (24 väylää)
- https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/v2/layouts/143835

## Miten toimii
1. GitHub Action ajaa `scraper.py` joka päivä 08:00 Suomen aikaa
2. Päivittää `data.json`
3. GitHub Pages tarjoaa `index.html` joka lukee `data.json` ja näyttää live tilastot

## Asennus 2 min
1. Luo uusi repo GitHubissa: luoma-aho-stats
2. Lataa tämän kansion tiedostot repoosi
3. Mene Settings -> Pages -> Source: main / root
4. Ota Actions päälle
5. Valmis! Sivusi on https://KAYTTAJANIMI.github.io/luoma-aho-stats/

## Linkitys Metrix / fgr.fi / UDisc
Kun sivu on pystyssä, lisää Metrixin radan kuvaukseen PELKKÄ URL (ei HTML):
```
Live tilastot: https://KAYTTAJANIMI.github.io/luoma-aho-stats/
```
Sama linkki toimii fgr.fi ja frisbeegolfradat.fi

## UDisc päivitys
UDisc public sivu on JS-raskas, joten botti käyttää viimeisintä varmistettua 413 lukua. Kun lataat uuden ambassador CSV:n, päivitä `static_verified.udisc` arvo data.jsonissa tai aja `python scraper.py` paikallisesti.

