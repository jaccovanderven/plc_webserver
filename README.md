# PLC Webserver

Versie **0.1.0** · Bosman van Zaal · Jacco van der Ven

Eén lokale webserver op **http://localhost:8080** voor het live uitlezen van Omron-PLC's bij klanten, via FINS. Je kiest een klant op de startpagina en opent de datapagina van die klant. Pas dan maakt de server verbinding met de PLC('s) van die klant.

## Waar staan we (v0.1.0, 2 oktober 2026)

- **Startpagina** heeft een pulldown-menu om een klant te kiezen. Daaronder staat een kaart met de PLC's van die klant: naam, IP-adres en online/offline (gecontroleerd met ping, elke 5 s). De knop **Verbinden** opent de datapagina. De browser onthoudt de laatst gekozen klant.
- **Datapagina's** per klant verversen elke seconde.
- **PLC-verbinding** gaat via FINS/UDP en wordt pas gemaakt als een datapagina vraagt om data. Na 15 s zonder verzoeken sluit de server de verbinding weer.
- **Huisstijl** van Bosman van Zaal (navy/oranje, Calibri), met logo en favicon.

### Klanten

| Klant | PLC('s) | Wat wordt uitgelezen |
|---|---|---|
| **3B Fundus** | Master PLC 192.168.5.30 | D0 |
| **Greenbalanz** | Sorteer PLC 192.168.38.212 | Lege Schijven Buffer: baan die gelost wordt (D18857), aantal cups in die baan (D17700 + baan), vrijgave lossen (W450.03) |
| **Slijkerman** | Master PLC 192.168.100.115, CTR Links .117, CTR Rechts .116 | Uit de Master PLC: CTR Links positie D5056 / status D5053, CTR Rechts positie D5006 / status D5003 (1 = Rust). Bij de CTR-PLC's wordt alleen gecontroleerd of ze online zijn. |

## Starten

Benodigd: Python 3 op Windows. Er zijn geen extra pakketten nodig.

```bat
start_webserver.bat
```

of `python webserver.py`. Open daarna http://localhost:8080. Stoppen doe je met Ctrl+C.

**Afhankelijkheid:** de FINS-client (`fins.py`) komt uit het project [plc_tool](https://github.com/jaccovanderven/plc_tool). De server verwacht die in `..\_tools\plc_tool\` naast deze map.

## Opbouw

```
webserver.py          server: klanten laden, FINS-verbindingen, API, statische bestanden
index.html            startpagina (pulldown + PLC-kaart)
logo.png, favicon.*   huisstijl
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
   ```

   `PLCS = {}` mag ook. De klant staat dan wel in het menu, maar heeft nog geen PLC's.
3. Zet er een `index.html` bij die de data ophaalt met `fetch("api/master/waarden")`. Kopieer een bestaande klantpagina voor de huisstijl, inclusief `<link rel="icon" href="/favicon.png">`.
4. Herstart de server.

## Volgende stappen / ideeën

- Greenbalanz: meer PLC's toevoegen.
- 3B Fundus: meer adressen uitlezen dan alleen D0.
- VPN per klant vanuit de startpagina (inloggegevens uit KeePass). Hier is een proefversie van gemaakt, met Cisco AnyConnect voor Greenbalanz, maar die is weer teruggedraaid en zit **niet** in v0.1.0. Bij Slijkerman loopt de verbinding via Secomea (LinkManager → SiteManager); daar is nog geen koppeling voor.
