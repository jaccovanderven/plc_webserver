# LiveLink

Versie **0.4.7** · Bosman van Zaal · Jacco van der Ven

Eén lokale webserver op **http://localhost:8080** voor het live uitlezen van Omron-PLC's bij klanten, via FINS. Je kiest een klant op de startpagina en opent de datapagina van die klant. Pas dan maakt de server verbinding met de PLC('s) van die klant.

## Waar staan we (v0.4.1, 3 oktober 2026)

- **Startpagina** heeft een pulldown-menu om een project te kiezen. Daaronder staat een kaart met de PLC's en HMI's van dat project: naam, IP-adres en online/offline (gecontroleerd met ping, elke 5 s). De browser onthoudt het laatst gekozen project.
  - **Monitor** opent de datapagina. De knop is alleen zichtbaar als minstens één PLC van het project online is.
  - **VNC &lt;HMI&gt;** start RealVNC Viewer op deze pc met het IP-adres van de HMI. De knop is alleen zichtbaar als de HMI online is, en werkt alleen vanaf de pc waarop de server draait.
  - In de kop staat links het LiveLink-logo en rechts het Bosman van Zaal-logo. Onderaan de pagina staat het versienummer met de link **About**: programma-info, versie en de wijzigingen per versie.
- **Datapagina's (Monitor)** per project verversen elke seconde. Ze hebben dezelfde kop als de startpagina (LiveLink links, Bosman van Zaal rechts), met "← Alle projecten" boven de titel.
- **PLC-verbinding** gaat via FINS/TCP en wordt pas gemaakt als een datapagina vraagt om data. Na 15 s zonder verzoeken sluit de server de verbinding weer.
- **Eén server tegelijk:** draait de server al, dan stopt een tweede start met de melding dat poort 8080 in gebruik is.
- **Huisstijl** van Bosman van Zaal (navy/oranje, Calibri), met logo en favicon.

### Versies

Alle wijzigingen per versie staan in [CHANGELOG.md](CHANGELOG.md). Op de startpagina zijn ze ook te zien via de knop **About**.

### Klanten

| Klant | PLC('s) | Wat wordt uitgelezen |
|---|---|---|
| **3B Fundus** | Master PLC 192.168.5.30 | D0 |
| **Greenbalanz** | Container PLC .211, Sorteer PLC .212, Afleveren .213, BST .214, CTR .215, Linear Robot 1 .216, 2 .217, 3 .218 (192.168.38.x) | Lege Schijven Buffer (Sorteer PLC): baan die gelost wordt (D18857), aantal cups in die baan (D17700 + baan), vrijgave lossen (W450.03). Bij alle andere PLC's wordt alleen gecontroleerd of hij online is. |
| **Slijkerman** | Master PLC 192.168.100.115, CTR Rechts .116, CTR Links .117, BST 104 .118, OHT 105 .119, OHT 106 .120; HMI 192.168.100.110 (VNC) | Uit de Master PLC: CTR Links positie D5056 / status D5053, CTR Rechts positie D5006 / status D5003 (1 = Rust). Bij de CTR-PLC's, BST 104, OHT 105 en OHT 106 wordt alleen gecontroleerd of ze online zijn. |

## Starten

Benodigd: Python 3 op Windows. Er zijn geen extra pakketten nodig. Voor de VNC-knop moet RealVNC Viewer geïnstalleerd zijn (`C:\Program Files\RealVNC\VNC Viewer\vncviewer.exe`).

```bat
start_webserver.bat
```

of `python webserver.py`. Open daarna http://localhost:8080. Stoppen doe je met Ctrl+C.

### Automatisch starten bij inloggen

```bat
powershell -ExecutionPolicy Bypass -File autostart.ps1
```

Dit maakt de Windows-taak **LiveLink** aan (Taakplanner). Die start de server bij elke keer inloggen op de achtergrond (`pythonw`, geen venster) en herstart hem bij een crash. Het gebeurt bij inloggen en niet bij het opstarten van de pc, omdat de VNC-knop de viewer op het bureaublad moet openen.

| Wat | Commando (PowerShell) |
|---|---|
| Herstarten na een wijziging | `Stop-ScheduledTask LiveLink; Start-ScheduledTask LiveLink` |
| Tijdelijk stoppen | `Stop-ScheduledTask LiveLink` |
| Autostart verwijderen | `powershell -ExecutionPolicy Bypass -File autostart.ps1 -Verwijderen` |

Draait de taak al, dan weigert `start_webserver.bat` te starten ("Poort 8080 is al in gebruik").

**Afhankelijkheid:** de FINS-client (`fins.py`) komt uit het project [plc_tool](https://github.com/jaccovanderven/plc_tool). De server verwacht die in `..\_tools\plc_tool\` naast deze map.

## Opbouw

```
webserver.py          server: klanten laden, FINS-verbindingen, API, statische bestanden
index.html            startpagina (pulldown + PLC-kaart)
autostart.ps1         Windows-taak LiveLink: server starten bij inloggen
logo.png, favicon.*   huisstijl Bosman van Zaal
livelink_*.svg        LiveLink-logo (woordmerk en icoon)
klanten/<klant>/
    klant.py          instellingen en uitleesfuncties van de klant
    index.html        datapagina van de klant
```

### Endpoints

| Pad | Inhoud |
|---|---|
| `/api/klanten` | alle klanten met hun PLC's en online-status |
| `/api/versie` | versie van de server |
| `/klant/<klant>/` | datapagina |
| `/klant/<klant>/info` | klant- en PLC-overzicht |
| `/klant/<klant>/api/<plc>/<functie>` | live data (bij één PLC zonder `<plc>/`) |
| `POST /klant/<klant>/vnc/<hmi>` | VNC-viewer starten (alleen vanaf deze pc) |

## Nieuwe klant toevoegen

1. Maak de map `klanten/<klant>/` aan. Gebruik kleine letters, met een underscore in plaats van een spatie.
2. Zet daarin een `klant.py`:

   ```python
   NAAM = "Klantnaam"
   OMSCHRIJVING = ""

   PLCS = {
       "master": {"naam": "Master PLC", "ip": "192.168.x.x"},
   }

   def waarden(plc, cfg):
       return {"d0": plc.read_dm(0)}

   API = {"waarden": waarden}   # /klant/<klant>/api/master/waarden

   VNC = {                      # optioneel: HMI's met VNC-knop
       "hmi": {"naam": "HMI", "ip": "192.168.x.x"},
   }
   ```

   `PLCS = {}` mag ook. De klant staat dan wel in het menu, maar heeft nog geen PLC's.
3. Zet er een `index.html` bij die de data ophaalt met `fetch("api/master/waarden")`. Kopieer een bestaande klantpagina voor de huisstijl, inclusief `<link rel="icon" href="/favicon.png">`.
4. Herstart de server.

## Nieuwe versie uitbrengen

Versienummers volgen [Semantic Versioning](https://semver.org/lang/nl/): **MAJOR.MINOR.PATCH**.

| Ophogen | Wanneer | Voorbeeld |
|---|---|---|
| **PATCH** | foutoplossing of kleine aanpassing (tekst, opmaak, bugfix), niets nieuws | 0.2.0 → 0.2.1 |
| **MINOR** | nieuwe functie, bestaande klanten/pagina's blijven werken | 0.2.1 → 0.3.0 |
| **MAJOR** | wijziging die het oude breekt, bijv. andere opbouw van `klant.py` | 0.9.0 → 1.0.0 |

Een hoger deel zet de lagere delen terug op 0. **0.x.y** betekent "in ontwikkeling"; **1.0.0** wordt de eerste stabiele versie.

Zet bij elke wijziging bovenaan in [CHANGELOG.md](CHANGELOG.md) een nieuwe kop `## X.Y.Z - JJJJ-MM-DD` met daaronder de wijzigingen als `- regel`. De server haalt zijn versienummer uit die bovenste kop. Het nummer staat dan vanzelf onderaan de startpagina, en de wijzigingen staan onder **About**. Pas daarna `Versie` bovenaan deze README aan, herstart de server, en commit, tag en push:

```bat
git commit -am "..."
git tag -a v0.x.0 -m "LiveLink v0.x.0"
git push --follow-tags
```

## Volgende stappen / ideeën

- 3B Fundus: meer adressen uitlezen dan alleen D0.
- VPN per klant vanuit de startpagina (inloggegevens uit KeePass). Hier is een proefversie van gemaakt, met Cisco AnyConnect voor Greenbalanz, maar die is weer teruggedraaid en zit **niet** in deze versie. Bij Slijkerman loopt de verbinding via Secomea (LinkManager → SiteManager); daar is nog geen koppeling voor.
