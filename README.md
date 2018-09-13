# Kalendervisning och Närvarostatus (Dosprojektet version2)
__Ett projekt som visar kalender och aktuell status (Välkommen / Upptaget / Ingen Inne) på en person och rum utifrån en ics-fil eller via en fysisk dosa med knappar i det aktuella rummet. Skriptet sätter automatiskt status beroende på vad aktuell kalenderhändelse innehåller, där ordet 'möte' exempelvis genererar 'upptaget'. Temperatur i rummet visas också.__

### Hur?
Ett pythonskript körs på en Raspberry Pi som lyssnar efter input från antingen fysiska knappar (Upptagen, Välkommen eller Inte inne) eller en publik onlinekalender (i dagsläget iCloud eller Google) och skapar en webbsida som den laddar upp på din server.<br />
Därifrån kan du med gamla överblivna paddor eller liknande skärmar visa status på rummen utanför exempelvis konferensrum, klassrum eller kontor.

### Disclaimer
Det här är ytterligare ett fortbildningsprojekt för mig i syfte att lära mig enklare programmering. Därmed får jag även möjlighet att faktiskt bygga prylar och ha lite roligt - samtidigt som jag kan lösa ett eller annat problem. Med andra ord, var snälla och hugg inte för hårt på mina kodkunskaper. :)

### Credits
Kalenderimportfunktionaliteten är en omarbetning och vidareutveckling av [jeinarsson](https://gist.github.com/jeinarsson) https://gist.github.com/jeinarsson/989329deb6906cae49f6e9f979c46ae7

### Uppdateringar
__2018-09-13 | Start av projekt__
Projektet är inte klart ännu, då fler funktioner ska läggas till. Men det är en början och allt funkar. Mer info kommer.

### Hårdvara och verktyg
* Raspberry Pi 3
* Pekplatta med internet och webbläsare
* 3d-printer (eller möjlighet att printa från någon annans printer)
* Webbserver med möjlighet till SFTP för filuppladdning

### Python setup
Projektet körs på Python 3.7, men det funkar nog på valfri 3.x. Följande paket behöver installeras;
* iCalendar - för att läsa in kalender // pip3 install iCalendar
* paramiko - för att ladda upp filer via sftp // pip3 install paramiko
* yaml // pip3 install pyyaml
