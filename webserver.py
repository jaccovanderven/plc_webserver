"""Webserver voor alle klant-PLC's op één adres (http://localhost:8080).

Elke submap van klanten/ met een klant.py verschijnt als knop op de
startpagina. Pas als een klantpagina wordt geopend, wordt verbinding
gemaakt met de PLC('s) van die klant; na IDLE_SEC seconden zonder
verzoeken wordt een verbinding weer gesloten.

klant.py definieert NAAM, OMSCHRIJVING en API = {naam: functie(plc, cfg)},
plus ofwel PLC_IP (één PLC) ofwel PLCS = {sleutel: {"naam", "ip", ...}}
(meerdere PLC's; cfg is dan de dict van die PLC), en optioneel
VNC = {sleutel: {"naam", "ip"}} voor HMI's die via VNC bereikbaar zijn. Endpoints:
    /klant/<klant>/info               klant- en PLC-overzicht
    /klant/<klant>/api/<naam>         (één PLC)
    /klant/<klant>/api/<plc>/<naam>   (meerdere PLC's)
    POST /klant/<klant>/vnc/<sleutel> VNC-viewer starten (alleen vanaf deze pc)

Start:  python webserver.py
Open:   http://localhost:8080
"""

import importlib.util
import json
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote, unquote, urlsplit

MAP = os.path.dirname(os.path.abspath(__file__))
KLANTEN_MAP = os.path.join(MAP, "klanten")
sys.path.insert(0, os.path.join(MAP, "..", "_tools", "plc_tool"))
from fins import FinsClient  # noqa: E402

MAKER = "Jacco van der Ven"
POORT = 8080
IDLE_SEC = 15                         # PLC-verbinding sluiten na zoveel s zonder verzoek
VERBODEN = (".py", ".pyc", ".ini")    # worden niet als bestand geserveerd
PING_CACHE_SEC = 4                    # online-status (ping) zo lang hergebruiken
VNC_VIEWER = r"C:\Program Files\RealVNC\VNC Viewer\vncviewer.exe"


def lees_changelog():
    """[{"versie", "datum", "wijzigingen": [...]}, ...] uit CHANGELOG.md, nieuwste eerst.
    Koppen '## X.Y.Z - JJJJ-MM-DD', daaronder regels '- wijziging'."""
    versies = []
    with open(os.path.join(MAP, "CHANGELOG.md"), encoding="utf-8") as f:
        for regel in f:
            kop = re.match(r"##\s+(\d+\.\d+\.\d+)\s*-\s*(\S+)", regel)
            if kop:
                versies.append({"versie": kop[1], "datum": kop[2], "wijzigingen": []})
            elif versies and regel.startswith("- "):
                versies[-1]["wijzigingen"].append(regel[2:].strip())
    return versies


CHANGELOG = lees_changelog()
VERSIE = CHANGELOG[0]["versie"]       # bovenste versie in CHANGELOG.md


def ping(ip):
    """True als het IP-adres antwoordt op één ping (Windows, 1 s timeout)."""
    try:
        r = subprocess.run(["ping", "-n", "1", "-w", "1000", ip], capture_output=True,
                           timeout=3, creationflags=subprocess.CREATE_NO_WINDOW)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return b"TTL=" in r.stdout.upper()


class Plc:
    """Eén PLC van een klant, met eigen FINS-verbinding."""

    def __init__(self, sleutel, cfg):
        self.sleutel = sleutel
        self.cfg = cfg
        self.naam = cfg.get("naam", sleutel)
        self.ip = cfg["ip"]
        self.client = FinsClient(self.ip, cfg.get("poort", 9600))
        self.lock = threading.Lock()
        self.laatst = 0.0
        self.online = None
        self.online_tijd = 0.0

    def info(self):
        return {"sleutel": self.sleutel, "naam": self.naam, "ip": self.ip,
                "verbonden": self.client.connected, "online": self.online}

    def controleer_online(self):
        if time.monotonic() - self.online_tijd > PING_CACHE_SEC:
            self.online = self.client.connected or ping(self.ip)
            self.online_tijd = time.monotonic()

    def lees(self, functie):
        tijd = datetime.now().strftime("%H:%M:%S")
        with self.lock:
            self.laatst = time.monotonic()
            try:
                if not self.client.connected:
                    self.client.connect()
                return {"ok": True, "tijd": tijd, **functie(self.client, self.cfg)}
            except Exception as e:
                self.client.close()
                return {"ok": False, "tijd": tijd, "fout": str(e)}

    def sluit_als_idle(self):
        with self.lock:
            if self.client.connected and time.monotonic() - self.laatst > IDLE_SEC:
                self.client.close()


class Vnc:
    """Eén HMI van een klant die via VNC bereikbaar is (alleen ping + viewer starten)."""

    def __init__(self, sleutel, cfg):
        self.sleutel = sleutel
        self.naam = cfg.get("naam", sleutel)
        self.ip = cfg["ip"]
        self.online = None
        self.online_tijd = 0.0

    def info(self):
        return {"sleutel": self.sleutel, "naam": self.naam, "ip": self.ip, "online": self.online}

    def controleer_online(self):
        if time.monotonic() - self.online_tijd > PING_CACHE_SEC:
            self.online = ping(self.ip)
            self.online_tijd = time.monotonic()

    def open(self):
        subprocess.Popen([VNC_VIEWER, self.ip])


class Klant:
    """Eén klant: module uit klanten/<sleutel>/klant.py plus zijn PLC('s)."""

    def __init__(self, sleutel, map_, module):
        self.sleutel = sleutel
        self.map = map_
        self.module = module
        self.naam = getattr(module, "NAAM", sleutel)
        self.omschrijving = getattr(module, "OMSCHRIJVING", "")
        plcs = getattr(module, "PLCS", None)   # PLCS = {} mag: klant nog zonder PLC's
        if plcs is None:
            plcs = {"plc": {"naam": self.naam, "ip": module.PLC_IP,
                            "poort": getattr(module, "PLC_POORT", 9600)}}
        self.plcs = {s: Plc(s, dict(cfg)) for s, cfg in plcs.items()}
        self.vnc = {s: Vnc(s, cfg) for s, cfg in getattr(module, "VNC", {}).items()}

    def info(self):
        return {"sleutel": self.sleutel, "naam": self.naam,
                "omschrijving": self.omschrijving,
                "plcs": [p.info() for p in self.plcs.values()],
                "vnc": [v.info() for v in self.vnc.values()]}

    def api(self, rest):
        delen = rest.split("/")
        if len(delen) == 1 and len(self.plcs) == 1:
            plc = next(iter(self.plcs.values()))
        elif len(delen) == 2:
            plc = self.plcs.get(delen[0])
        else:
            return None
        functie = getattr(self.module, "API", {}).get(delen[-1])
        if plc is None or functie is None:
            return None
        return plc.lees(functie)

    def sluit_als_idle(self):
        for p in self.plcs.values():
            p.sluit_als_idle()


def laad_klanten():
    klanten = {}
    if not os.path.isdir(KLANTEN_MAP):
        return klanten
    for sleutel in sorted(os.listdir(KLANTEN_MAP)):
        pad = os.path.join(KLANTEN_MAP, sleutel, "klant.py")
        if not os.path.isfile(pad):
            continue
        spec = importlib.util.spec_from_file_location(f"klant_{sleutel}", pad)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            klanten[sleutel] = Klant(sleutel, os.path.dirname(pad), module)
        except Exception as e:
            print(f"Klant '{sleutel}' overgeslagen: {e}")
    return klanten


KLANTEN = laad_klanten()


def bewaker():
    while True:
        time.sleep(5)
        for k in KLANTEN.values():
            k.sluit_als_idle()


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=MAP, **kwargs)

    def do_GET(self):
        pad = unquote(urlsplit(self.path).path)

        if pad == "/api/klanten":
            apparaten = [a for k in KLANTEN.values()
                         for a in (*k.plcs.values(), *k.vnc.values())]
            if apparaten:
                with ThreadPoolExecutor(len(apparaten)) as pool:
                    list(pool.map(lambda a: a.controleer_online(), apparaten))
            return self.stuur_json([k.info() for k in KLANTEN.values()])

        if pad == "/api/versie":
            return self.stuur_json({"versie": VERSIE})

        if pad == "/api/about":
            return self.stuur_json({"naam": "PLC Webserver", "versie": VERSIE, "maker": MAKER,
                                    "bedrijf": "Bosman van Zaal", "changelog": CHANGELOG})

        if pad.startswith("/klant/"):
            sleutel, _, rest = pad[len("/klant/"):].partition("/")
            klant = KLANTEN.get(sleutel)
            if klant is None:
                return self.send_error(404, "Onbekende klant")
            if not pad.startswith(f"/klant/{sleutel}/"):
                self.send_response(301)
                self.send_header("Location", f"/klant/{quote(sleutel)}/")
                self.end_headers()
                return
            if rest == "info":
                return self.stuur_json(klant.info())
            if rest.startswith("api/"):
                data = klant.api(rest[len("api/"):])
                if data is None:
                    return self.send_error(404, "Onbekende API")
                return self.stuur_json(data)
            return self.stuur_bestand(klant.map, rest)

        if pad.startswith("/klanten/"):
            return self.send_error(404)   # alleen via /klant/<naam>/
        return self.stuur_bestand(MAP, pad.lstrip("/"))

    def do_POST(self):
        """POST /klant/<klant>/vnc/<sleutel>: VNC-viewer op deze pc starten."""
        delen = unquote(urlsplit(self.path).path).strip("/").split("/")
        if self.client_address[0] not in ("127.0.0.1", "::1"):
            return self.send_error(403, "Alleen vanaf deze pc")
        if len(delen) != 4 or delen[0] != "klant" or delen[2] != "vnc":
            return self.send_error(404)
        klant = KLANTEN.get(delen[1])
        vnc = klant.vnc.get(delen[3]) if klant else None
        if vnc is None:
            return self.send_error(404, "Onbekende VNC")
        try:
            vnc.open()
            return self.stuur_json({"ok": True})
        except OSError as e:
            return self.stuur_json({"ok": False, "fout": str(e)})

    def stuur_bestand(self, map_, rest):
        if rest.lower().endswith(VERBODEN):
            return self.send_error(404)
        self.directory = map_
        self.path = "/" + quote(rest)
        super().do_GET()

    def list_directory(self, path):
        self.send_error(404)   # geen mapweergave

    def stuur_json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass  # geen request-spam in de console


if __name__ == "__main__":
    print(f"PLC Webserver v{VERSIE}: http://localhost:{POORT}  (Ctrl+C om te stoppen)")
    for k in KLANTEN.values():
        ips = ", ".join(f"{p.naam} {p.ip}" for p in k.plcs.values())
        print(f"  - {k.naam} ({ips})  ->  /klant/{k.sleutel}/")
    threading.Thread(target=bewaker, daemon=True).start()
    try:
        # geen SO_REUSEADDR: anders kan op Windows een tweede server ongemerkt op dezelfde poort draaien
        ThreadingHTTPServer.allow_reuse_address = False
        try:
            server = ThreadingHTTPServer(("0.0.0.0", POORT), Handler)
        except OSError:
            sys.exit(f"Poort {POORT} is al in gebruik - draait de webserver al?")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
