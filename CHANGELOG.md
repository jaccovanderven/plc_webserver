# Changelog

Alle wijzigingen per versie. Nieuwste bovenaan. Versienummers volgen [Semantic Versioning](https://semver.org/lang/nl/).
De bovenste versie is de versie van de server: `webserver.py` leest hem uit dit bestand en toont deze lijst via de knop **About** op de startpagina.

## 0.3.0 - 2026-10-03

- Knop **About** op de startpagina: programma-info, versie en de wijzigingen per versie
- Versienummer en wijzigingen staan nu op één plek: `CHANGELOG.md`

## 0.2.5 - 2026-10-03

- Slijkerman Insights: status alleen als tekst (bijv. "Rust"), zonder PLC-waarde; onbekende waarde toont "Onbekend"

## 0.2.4 - 2026-10-03

- Slijkerman Insights: kolomkop "CTR" heet nu "Machine"

## 0.2.3 - 2026-10-03

- Startpagina: IP-adressen van PLC's en HMI's verticaal uitgelijnd

## 0.2.2 - 2026-10-03

- Logo in de kop van alle pagina's groter (52 → 68 px)

## 0.2.1 - 2026-10-03

- Slijkerman Insights: posities en status in één tabel in plaats van losse tegels, zonder D-adressen

## 0.2.0 - 2026-10-03

- VNC-knop voor HMI's (start RealVNC Viewer, alleen zichtbaar als de HMI online is)
- Slijkerman: HMI 192.168.100.110
- Knop Verbinden heet nu **Insights** en is alleen zichtbaar als een PLC online is
- Server weigert dubbel starten op poort 8080

## 0.1.0 - 2026-10-02

- Eerste versie: startpagina met pulldown-menu om een klant te kiezen, kaart met PLC's (online/offline via ping)
- Klanten Greenbalanz, Slijkerman en 3B Fundus
- Bosman van Zaal-huisstijl en favicon
