# Kalendervisning och Närvarostatus (Dosprojektet version2)
__Ett projekt som visar kalender och aktuell status (Välkommen / Upptaget / Ingen Inne) på en person och rum utifrån en ics-fil eller via en fysisk dosa med knappar i det aktuella rummet. Skriptet sätter automatiskt status beroende på vad aktuell kalenderhändelse innehåller, där ordet 'möte' exempelvis genererar 'upptaget'. Givetvis kan du 'override' det genom de fysiska knapparna. Temperatur i rummet visas också.__

### Hur?
Ett pythonskript körs på en Raspberry Pi som lyssnar efter input från antingen fysiska knappar (Upptagen, Välkommen eller Inte inne) eller en publik onlinekalender (i dagsläget iCloud eller Google) och skapar en webbsida som den laddar upp på din server.<br />
Därifrån kan du med gamla överblivna paddor eller liknande skärmar visa status på rummen utanför exempelvis konferensrum, klassrum eller kontor.<br />
Rörelsedetektor finns också som exempelvis säger till om du glömt att slå igång automatiskt läge. Med text to speech så talar den även.

### Disclaimer
Det här är ytterligare ett fortbildningsprojekt för mig i syfte att lära mig enklare programmering. Därmed får jag även möjlighet att faktiskt bygga prylar och ha lite roligt - samtidigt som jag kan lösa ett eller annat problem. Med andra ord, var snälla och hugg inte för hårt på mina kodkunskaper. :)

### Credits
Kalenderimportfunktionaliteten är en omarbetning och vidareutveckling av [jeinarsson](https://gist.github.com/jeinarsson) https://gist.github.com/jeinarsson/989329deb6906cae49f6e9f979c46ae7

### Uppdateringar
__2018-09-23 | v1.3 - Rörelsedetektor och text-to-speech__<br />
Nu finns detta implementerat. Mer info kommer.<br /><br />
__2018-09-23 | Fler komponenter tillagda__<br />
Nu har jag lagt till en LCD-skärm som ska sitta i dosan samt en PIR (rörelsedetektor). Kod finns även förberett för text-to-speech.<br /><br />
__2018-09-13 | Start av projekt__<br />
Projektet är inte klart ännu, då fler funktioner ska läggas till. Men det är en början och allt funkar. Mer info kommer.

### Buggar och att-göra
__Att göra:__
* Rensa upp kod.
* Designa om dosa och elektronik.

__Buggar:__
* Inget just nu.

### Hårdvara och verktyg
![Hardware](https://github.com/mickekring/Kalendervisning-och-N-rvarostatus/raw/master/images/Dosan-v2_bb.png)
* Raspberry Pi 3
* En gammal padda eller liknande med internet och webbläsare
* 3d-printer (eller möjlighet att printa från någon annans printer)
* Webbserver med möjlighet till SFTP för filuppladdning
* Kioskprogramvara till paddan som ska köra innehållet - exempelvis Kiosk Pro Basic (som jag använder) https://itunes.apple.com/se/app/kiosk-pro-basic/id409918026?mt=8
* Diverse elektronik - motstånd, potentiometer, knappar, kabel mm
* LCD 16x2
* Therminstor
* PIR - Motion detector

### Python setup
Projektet körs på Python 3.7, men det funkar nog på valfri 3.x. Följande paket behöver installeras;
* iCalendar - för att läsa in kalender // sudo pip3 install iCalendar
* paramiko - för att ladda upp filer via sftp // sudo pip3 install paramiko
* yaml // sudo pip3 install pyyaml
* mpg123 // sudo apt-get install mpg123
* gTTS // sudo pip3 install gTTS
* alsaaudio // sudo pip3 install pyalsaaudio

### 3D-filer
* Då jag kommer designa om hårdvaran, dröjer det ett tag innan detta kommer. Håll koll här eller på sociala medier.

### Filer
__main.py__<br />
main.py är huvudprogrammet som ska köras. Här görs alla ändringar.<br /><br />
__ics.py och rrule_patched.py__<br />
Dessa två filer sköter hand om kalenderimporten och sortering av händelserna. Inga ändringar behövs göras i dessa filer.<br /><br />
__credentials.yml__<br />
I den här filen lagrar vi lösenord och annat som main.py behöver för att exempelvis kunna koppla upp sig mot SFTP-servern för att ladda upp filer. De enda två ställen som behöver innehåll är __user:__ och __urlcalendar:__ där den förra är användaruppgifter till SFTP och den andra är url:en till den kalender som ska läsas in.<br />
Fyll i dina uppgifter utan '' eller "", det vill säga så här:<br />
username: dittanvändarnamn<br />
password: dittlösenord123<br /><br />
__index.html__<br />
Denna fil körs på den enhet (exempevis iPad) som ska visa upp statusen. Körs med fördel lokalt (i kiosk-appen) då den uppdaterar sig själv - och försöker läsa in index2.html via embed - varannan minut. Detta utifall internetuppkopplingen försvinner. Då fortsätter denna fil att försöka ladda index2.html. Pythonprogrammet gör inga förändringar i denna fil.<br /><br />
__index2.html__<br />
Den här filen byggs av pythonprogrammet och laddas upp på din server. Det är innehållet. Ändra i main.py om du vill ändra innehållet här. Filen uppdaterar sig själv var 12:e sekund.<br /><br />
__style.css__<br />
Stylesheet. Styla som ni vill. Laddas upp initialt.<br /><br />
__style_bg.css__</br>
Styr färgen på bakgrunden av skärmen, det vill säga rött för upptaget, grönt för välkommen och svart för inte inne. Laddas upp vid byte av status.<br /><br />
__user_pic.jpg__<br />
Den bild som visas på skärmen. Laddas upp initialt.
