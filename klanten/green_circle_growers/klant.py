"""Green Circle Growers.

Master PLC - overzicht van de 17 posities (Y-140 t/m Y-178), nagebouwd van
het HMI-scherm: prioriteit OHC 1/2, oppakken en neerzetten (actief en
beschikbaar), schoon/vuil, aantal op stapel en opslag. Oppakken actief,
neerzetten actief, schoon/vuil en opslag naar/van zijn schrijfbaar (zet_bit), de rest alleen lezen.

Bij de bitkolommen hoort rij n bij bit n vanaf het basiswoord: rij 1 = x.01,
rij 15 = x.15, rij 16 = (x+1).00, rij 17 = (x+1).01.

De andere PLC's worden alleen op online-status gecontroleerd.
"""

import struct

NAAM = "Green Circle Growers"
OMSCHRIJVING = ""

PLCS = {                # op IP-volgorde
    "master": {"naam": "Master PLC", "ip": "192.168.250.2"},  # leest het positie-overzicht
    "wasser": {"naam": "Wasser", "ip": "192.168.250.3"},  # alleen online-controle
    "bst401": {"naam": "BST 401", "ip": "192.168.250.4"},  # alleen online-controle
    "bst402": {"naam": "BST 402", "ip": "192.168.250.5"},  # alleen online-controle
}

AREA_CIO, AREA_WR, AREA_HR, AREA_DM = 0xB0, 0xB1, 0xB2, 0x82   # FINS-codes, woord

POSITIES = [            # (rij, Y-positie, naam)
    (1, "Y-140", "(Ont)Stapelaar"), (2, "Y-146", "Positie"), (3, "Y-152", "Positie"),
    (4, "Y-158", "Positie"), (5, "Y-159", "Stapels"), (6, "Y-160", "Stapels"),
    (7, "Y-161", "Stapels"), (8, "Y-162", "Stapels"), (9, "Y-163", "Stapels"),
    (10, "Y-164", "Stapels"), (11, "Y-165", "Stapels"), (12, "Y-166", "Wasser"),
    (13, "Y-171", "Stapels"), (14, "Y-172", "Stapels"), (15, "Y-173", "Stapels"),
    (16, "Y-174", "Stapels"), (17, "Y-178", "Positie"),
]

# Woordkolommen: (sleutel, DM-basis, rijen) - rij n staat in D(basis + n)
WOORDEN = [
    ("prio1", 5900, range(1, 17)),                              # D5901..D5916
    ("prio2", 6000, range(2, 18)),                              # D6002..D6017
    ("aantal", 5700, [1, *range(5, 12), *range(13, 18)]),       # D5701, D5705..11, D5713..17
]

# Bitkolommen: (sleutel, gebied, letter, basiswoord, rijen)
ALLE, OPSLAG = range(1, 18), range(5, 12)
BITS = [
    ("oppakken_actief", AREA_HR, "H", 116, ALLE),               # H116.01 ..
    ("oppakken_beschikbaar", AREA_CIO, "CIO ", 5800, ALLE),     # CIO 5800.01 ..
    ("neerzetten_actief", AREA_HR, "H", 110, ALLE),             # H110.01 ..
    ("neerzetten_beschikbaar", AREA_CIO, "CIO ", 5806, ALLE),   # CIO 5806.01 ..
    ("vuil", AREA_HR, "H", 122, ALLE),                          # H122.01 .. (aan = vuil)
    ("opslag_naar", AREA_HR, "H", 72, OPSLAG),                  # H72.05 .. H72.11
    ("opslag_van", AREA_HR, "H", 73, OPSLAG),                   # H73.05 .. H73.11
    ("opslag_103", AREA_WR, "W", 70, OPSLAG),                   # W70.05 .. W70.11
    ("opslag_102", AREA_WR, "W", 74, OPSLAG),                   # W74.05 .. W74.11
]


def overzicht(plc, cfg):
    rijen = {nr: {"nr": nr, "y": y, "naam": naam} for nr, y, naam in POSITIES}

    for sleutel, basis, nrs in WOORDEN:
        w = plc.read_words(AREA_DM, basis + 1, 17)
        for nr in nrs:
            rijen[nr][sleutel] = {"waarde": w[nr - 1], "adres": f"D{basis + nr}"}

    for sleutel, gebied, letter, basis, nrs in BITS:
        w = plc.read_words(gebied, basis, 2)
        for nr in nrs:
            woord, bit = divmod(nr, 16)
            rijen[nr][sleutel] = {"waarde": bool((w[woord] >> bit) & 1),
                                  "adres": f"{letter}{basis + woord}.{bit:02d}"}

    return {"rijen": list(rijen.values())}


API = {"overzicht": overzicht}   # bereikbaar als /klant/green_circle_growers/api/master/overzicht


# --- schrijven (POST /klant/green_circle_growers/api/master/zet_bit) -------------
SCHRIJFBAAR = ("oppakken_actief", "neerzetten_actief", "vuil",
               "opslag_naar", "opslag_van")                       # alleen deze kolommen
BIT_AREA = {AREA_CIO: 0x30, AREA_WR: 0x31, AREA_HR: 0x32}        # FINS-code voor bittoegang


def zet_bit(plc, cfg, params):
    """Zet één bit aan/uit. params: {"kolom": ..., "nr": 1..17, "waarde": true/false}."""
    kolom, nr, waarde = params.get("kolom"), params.get("nr"), params.get("waarde")
    if kolom not in SCHRIJFBAAR or not isinstance(nr, int) or isinstance(nr, bool) \
            or not isinstance(waarde, bool):
        raise ValueError("Ongeldig verzoek")
    _, gebied, letter, basis, nrs = next(b for b in BITS if b[0] == kolom)
    if nr not in nrs:                      # opslag alleen rij 5 t/m 11
        raise ValueError("Ongeldig verzoek")
    woord, bit = divmod(nr, 16)
    plc._send_command(bytes([0x01, 0x02, BIT_AREA[gebied]]) + struct.pack(">H", basis + woord)
                      + bytes([bit]) + struct.pack(">H", 1) + bytes([1 if waarde else 0]))
    nu = bool((plc.read_words(gebied, basis + woord, 1)[0] >> bit) & 1)   # teruglezen
    return {"kolom": kolom, "nr": nr, "waarde": nu, "adres": f"{letter}{basis + woord}.{bit:02d}"}


SCHRIJF = {"zet_bit": zet_bit}
