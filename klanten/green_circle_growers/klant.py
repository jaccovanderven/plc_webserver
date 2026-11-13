"""Green Circle Growers.

Alle PLC's: voorlopig alleen online-controle, er worden nog geen
adressen uitgelezen. Vul API (en eventueel VNC) aan zodra die bekend zijn.
"""

NAAM = "Green Circle Growers"
OMSCHRIJVING = ""

PLCS = {
    "master": {"naam": "Master PLC", "ip": "192.168.250.2"},  # alleen online-controle
    "wasser": {"naam": "Wasser", "ip": "192.168.250.3"},  # alleen online-controle
    "bst401": {"naam": "BST 401", "ip": "192.168.250.4"},  # alleen online-controle
    "bst402": {"naam": "BST 402", "ip": "192.168.250.5"},  # alleen online-controle
}

API = {}                # bijv. {"waarden": waarden} -> /klant/green_circle_growers/api/master/waarden
