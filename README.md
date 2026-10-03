# LiveLink

Versie **0.3.5** · Bosman van Zaal · Jacco van der Ven

Eén lokale webserver op **http://localhost:8080** voor het live uitlezen van Omron-PLC's bij klanten, via FINS. Je kiest een klant op de startpagina en opent de datapagina van die klant. Pas dan maakt de server verbinding met de PLC('s) van die klant.

## Waar staan we (v0.3.5, 3 oktober 2026)

- **Startpagina** heeft een pulldown-menu om een klant te kiezen. Daaronder staat een kaart met de PLC's en HMI's van die klant: naam, IP-adres en online/offline (gecontroleerd met ping, elke 5 s). De browser onthoudt de laatst gekozen klant.
  - **Insights** opent de datapagina. De knop is alleen zichtbaar als minstens één PLC van de klant online is.
  - **VNC &lt;HMI&gt;** start RealVNC Viewer op deze pc met het IP-adres van de HMI. De knop is alleen zichtbaar als de HMI online is, en werkt alleen vanaf de pc waarop de server draait.
  - In de kop staat links het LiveLink-logo en rechts het Bosman van Zaal-logo met de knop **About**. About toont programma-info, versie en de wijzigingen per versie. Onderaan de pagina staat het versienummer.
- **Datapagina's** per klant verversen elke seconde.
- **PLC-verbinding** gaat via FINS/TCP en wordt pas gemaakt als een datapagina vraagt om data. Na 15 s zonder verzoeken sluit de server de verbinding weer.
- **Eén server tegelijk:** draait de server al, dan stopt een tweede start met de melding dat poort 8080 in gebruik is.
- **Huisstijl** van Bosman van Zaal (navy/oranje, Calibri), met logo en favicon.

### Versies

Alle wijzigingen per versie staan in [CHANGELOG.md](CHANGELOG.md). Op de startpagina zijn ze ook te zien via de knop **About**.

### Klanten

| Klant | PLC('s) | Wat wordt uitgelezen |
|---|---|---|
| **3B Fundus** | Master PLC 192.168.5.30 | D0 |
| **Greenbalanz** | Sorteer PLC 192.168.38.212 | Lege Schijven Buffer: baan die gelost wordt (D18857), aantal cups in die baan (D17700 + baan), vrijgave lossen (W450.03) |
| **Slijkerman** | Master PLC 192.168.100.115, CTR Links .117, CTR Rechts .116; HMI 192.168.100.110 (VNC) | Uit de Master PLC: CTR Links positie D5056 / status D5053, CTR Rechts positie D5006 / status D5003 (1 = Rust). Bij de CTR-PLC's wordt alleen gecontroleerd of ze online zijn. |

## Starten

Benodigd: Python 3 op Windows. Er zijn geen extra pakketten nodig. Voor de VNC-knop moet RealVNC Viewer geïnstalleerd zijn (`C:\Program Files\RealVNC\VNC Viewer\vncviewer.exe`).

```bat
start_webserver.bat
```

of `python webserver.py`. Open daarna http://localhost:8080. Stoppen doe je met Ctrl+C.

**Afhankelijkheid:** de FINS-client (`fins.py`) komt uit het project [plc_tool](https://github.com/jaccovanderven/plc_tool). De server verwacht die in `..\_tools\plc_tool\` naast deze map.

## Opbouw

```
webserver.py          server: klanten laden, FINS-verbindingen, API, statische bestanden
index.html            startpagina (pulldown + PLC-kaart)
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

- Greenbalanz: meer PLC's toevoegen.
- 3B Fundus: meer adressen uitlezen dan alleen D0.
- VPN per klant vanuit de startpagina (inloggegevens uit KeePass). Hier is een proefversie van gemaakt, met Cisco AnyConnect voor Greenbalanz, maar die is weer teruggedraaid en zit **niet** in deze versie. Bij Slijkerman loopt de verbinding via Secomea (LinkManager → SiteManager); daar is nog geen koppeling voor.
