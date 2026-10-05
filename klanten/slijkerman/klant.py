"""Slijkerman - CTR.

De Master PLC levert de huidige positie van CTR Links en CTR Rechts;
de CTR-PLC's, BST 104, OHT 105 en OHT 106 worden op de startpagina alleen op online-status gecontroleerd.
"""

NAAM = "Slijkerman"
OMSCHRIJVING = ""

PLCS = {                # op IP-volgorde
    "master": {"naam": "Master PLC", "ip": "192.168.100.115"},   # leest de posities
    "ctr_rechts": {"naam": "CTR Rechts", "ip": "192.168.100.116"},  # alleen online-controle
    "ctr_links": {"naam": "CTR Links", "ip": "192.168.100.117"},  # alleen online-controle
    "bst104": {"naam": "BST 104", "ip": "192.168.100.118"},  # alleen online-controle
    "oht105": {"naam": "OHT 105", "ip": "192.168.100.119"},  # alleen online-controle
    "oht106": {"naam": "OHT 106", "ip": "192.168.100.120"},  # alleen online-controle
}

VNC = {
    "hmi": {"naam": "HMI", "ip": "192.168.100.110"},   # knop "VNC HMI" op de startpagina
}

MACHINES = [            # (sleutel, naam, DM positie, DM status of None) - in de Master PLC
    ("links", "CTR Links", 5056, 5053),
    ("rechts", "CTR Rechts", 5006, 5003),
]

STATUS_TEKST = {1: "Rust"}


def machine(plc, s, n, a_pos, a_status):
    m = {"sleutel": s, "naam": n, "adres": f"D{a_pos}", "positie": plc.read_dm(a_pos)}
    if a_status is not None:
        status = plc.read_dm(a_status)
        m.update(status=status, status_adres=f"D{a_status}",
                 status_tekst=STATUS_TEKST.get(status, "Onbekend"))
    return m


def positie(plc, cfg):
    return {"posities": [machine(plc, *m) for m in MACHINES]}


API = {"positie": positie}   # bereikbaar als /klant/slijkerman/api/master/positie
