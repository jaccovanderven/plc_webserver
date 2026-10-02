"""3B Fundus.

De Master PLC levert de uitgelezen D-woorden.
"""

NAAM = "3B Fundus"
OMSCHRIJVING = ""

PLCS = {
    "master": {"naam": "Master PLC", "ip": "192.168.5.30"},
}

WAARDEN = [             # (sleutel, naam, DM-adres) - in de Master PLC
    ("d0", "D0", 0),
]


def waarden(plc, cfg):
    return {"waarden": [{"sleutel": s, "naam": n, "adres": f"D{a}", "waarde": plc.read_dm(a)}
                        for s, n, a in WAARDEN]}


API = {"waarden": waarden}   # bereikbaar als /klant/3b_fundus/api/master/waarden
