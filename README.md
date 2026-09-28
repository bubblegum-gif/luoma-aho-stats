
# Luoma-ahon Frisbeegolfrata - Tilastoautomaatio

Automaattinen skraperi joka laskee yhteen:

- 4 Disc Golf Metrix rataa: 43119, 48112, 44763, 44010
- UDisc: Luoma-ahon frisbeegolfrata + layout 143835 + /manage/stats

Päivittyy GitHub Actionsissa 1h välein -> `data/stats.json`

## Käyttöönotto

1. Luo GitHub repo, pushaa nämä tiedostot
2. Settings -> Secrets -> New secret: `UDISC_MANUAL_COUNT` = esim 2500 (kokonaispelit UDiscista)
   - Koska UDisc vaatii Pro-kirjautumisen /manage/stats sivulle, helpoin tapa on päivittää manuaalisesti
   - Vaihtoehto: päivitä `data/udisc_override.json` tiedostoon oikea luku kun katsot sen UDiscista

3. Workflow ajetaan automaattisesti joka tunti

## Frontend käyttö

`data/simple.json` sisältää:
```json
{
  "rounds": 12458,
  "metrix_sum": 8458,
  "udisc": 4000,
  "updated": "13.05.2026 15:00"
}
```

Haetaan sivulla:
```js
fetch('https://raw.githubusercontent.com/USERNAME/REPO/main/data/simple.json')
  .then(r => r.json())
  .then(data => document.getElementById('rounds').textContent = data.rounds)
```

## UDisc manuaalinen päivitys

Koska lähettämäsi kuva oli rikki (vain väripalkkeja), en voinut lukea UDisc-dataa.

Mene: https://udisc.com/courses/luoma-ahon-frisbeegolfrata-YNEx/manage/stats
- Katso "Total plays" tai "All time"
- Päivitä `data/udisc_override.json` -> `plays`: 1234
- Commit & push, tai aseta Secret

## Metrix tarkka skrapaus

Metrix lataa tilastot JavaScriptillä, joten perus requests ei aina riitä.
Workflow asentaa Playwrightin joka renderöi sivun oikeasti ja lukee Course usage datan.

Jos silti ei löydy, tarkista Metrix-sivuilta mikä elementti sisältää kokonaismäärän ja päivitä scraper.py regex.
