# Kalendervisning och Närvarostatus (Dosprojektet version2)
Ett projekt som visar kalender och aktuell status på antingen personer eller rum utifrån en ics-fil eller via en fysisk dosa med knappar i det aktuella rummet. 

### Hur?
Ett pythonskript körs på en Raspberry Pi som lyssnar efter input från antingen fysiska knappar (Upptagen, Välkommen eller Inte inne) eller en publik onlinekalender (i dagsläget iCloud eller Google) och skapar en webbsida som den laddar upp på din server.<br />
Därifrån kan du med gamla överblivna paddor eller liknande skärmar visa status på rummen utanför exempelvis konferensrum, klassrum eller kontor.

### Förusättningar och material
* Raspberry Pi 3
* Pekplatta med internet och webbläsare
* 3d-printer (eller möjlighet att printa från någon annans printer)
* Webbserver med möjlighet till SFTP för filuppladdning

### Python setup
Projektet körs på Python 3.7, men det funkar nog på valfri 3.x. Följande paket behöver installeras;
* iCalendar - för att läsa in kalender // pip3 install iCalendar
* paramiko - för att ladda upp filer via sftp // pip3 install paramiko
* yaml // pip3 install pyyaml

### Credits
Kalenderimportfunktionaliteten är en omarbetning och vidareutveckling av [jeinarsson](https://gist.github.com/jeinarsson) https://gist.github.com/jeinarsson/989329deb6906cae49f6e9f979c46ae7


### 2018-09-13 | Start av projekt
Projektet är inte klart ännu, då fler funktioner ska läggas till. Men det är en början och allt funkar. Mer info kommer.
