git add index.html
git commit -m "poista korttien alimmainen skaalaus-info teksti"
git push
git add index.html
git commit -m "poista Kirjatut kierrokset ja UDisc+Metrix teksti"
git push
git add index.html data/
git commit -m "poista sininen laatikko + skaalausinfot, lisää Väylätilastot omaksi kortiksi"
git push
git add index.html data/
git commit -m "fix: poista korttien alainfot, lisää Väylätilastot omaksi kortiksi 1s/5min"
git push
git add -A
git add -f data/ data.json data/stats.json data/simple.json data/data.json simple.json index.html
git commit -m "fix data folder - 892 kierrosta + Väylätilastot + poista sininen laatikko"
git push
