# F1_24: Telemetriai adatok elemzése az F1 24 játékból

Ez a Python-alapú alkalmazás az F1 2024 szimulátorjátékból származó telemetriai adatokat gyűjti, elemzi és vizualizálja. A cél, hogy a játékosok számára is közérthető formában mutasson rá a vezetési teljesítményt befolyásoló tényezőkre. Az adatfeldolgozás során adatbányászati és gépi tnaulási algoritmusok, névszerint a **K-means klaszterezés** és a **CART döntési fa** kerülnek alkalmazásra.

A program hasznos eszköz lehet a *game analytics* megközelítésben, akár fejlesztőknek, akár szimulátorral játszó versenyzőknek, akik gyorsabb köridőket szeretnének elérni vagy jobban megérteni saját teljesítményüket.


## Használat

A program egyelőre nem rendelkezik önálló `.exe` fájllal. A futtatáshoz Python környezet szükséges.

### 1. Klónozd a repót

git clone https://github.com/Syrayama/XZIY3B_Szakdolgozat
cd Pixel-Bugs

### 2. Telepítsd a szükséges csomagokat
pip install -r requirements.txt

### 3. Indítsd a programot
python main.py

### 4. Adatgyűjtés/Betöltés
Indítsd el az adatgyűjtést és körözz vagy töltsd be az előre mentett valós adatokat.

### 5. Indítsd el az elemzési folyamatot
Az Elemzés gombra kattintva elkezdődik a háttérben az algoritmusok lefuttatása a kívánt szakaszokra.

### 6. Válaszd ki melyik szakaszt akarod elemezni
A lenyíló menüből válassz a szakaszok közül.

### 7. Elemzések emgtekintése
Megjelennek az elemzések, vizualizációk és tancsok 3 különböző ablakban.

### 8. Legyél gyorsabb
Próbáld ki a pályán a kapott tanácsokat és ekrülj a többiek elé!
Jó körözést!
