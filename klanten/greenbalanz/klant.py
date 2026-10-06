"""Greenbalanz.

Sorteer PLC - Lege Schijven Buffer: leest D18857 (baan die momenteel
gelost wordt), D(17700 + baan) (aantal cups dat nog in die baan staat)
en W450.03 (vrijgave lossen).
"""

NAAM = "Greenbalanz"
OMSCHRIJVING = ""

PLCS = {                # op IP-volgorde
    "container": {"naam": "Container PLC", "ip": "192.168.38.211"},  # alleen online-controle
    "sorteer": {"naam": "Sorteer PLC", "ip": "192.168.38.212"},
}

ADRES_BAAN = 18857
BASIS_CUPS = 17700   # cups van baan n staan in D(17700 + n)
AREA_WR = 0xB1       # FINS-code W-gebied (work area), woord
VRIJGAVE_WOORD, VRIJGAVE_BIT = 450, 3   # W450.03 = vrijgave lossen


def baan(plc, cfg):
    b = plc.read_dm(ADRES_BAAN)
    adres_cups = BASIS_CUPS + b
    cups = plc.read_dm(adres_cups)
    w = plc.read_words(AREA_WR, VRIJGAVE_WOORD, 1)[0]
    return {"baan": b, "adres_cups": f"D{adres_cups}", "cups": cups,
            "vrijgave": bool((w >> VRIJGAVE_BIT) & 1)}


API = {"baan": baan}   # bereikbaar als /klant/greenbalanz/api/sorteer/baan
