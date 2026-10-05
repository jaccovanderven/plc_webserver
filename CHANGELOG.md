# Changelog

Alle wijzigingen per versie. Nieuwste bovenaan. Versienummers volgen [Semantic Versioning](https://semver.org/lang/nl/).
De bovenste versie is de versie van de server: `webserver.py` leest hem uit dit bestand en toont deze lijst via de link **About** onderaan de startpagina.

## 0.4.3 - 2026-10-05

- Slijkerman: machine OHT106 (192.168.100.120) toegevoegd, met online-controle op de startpagina

## 0.4.2 - 2026-10-04

- Nieuw LiveLink-symbool: witte Venlo-kas met oranje datapuls op donkerblauw (zelfde als de GitHub-avatar, zonder initialen); "Live" in het logo nu oranje; favicons vernieuwd

## 0.4.1 - 2026-10-03

- Knop naar de datapagina heet nu **Monitor** (was Insights)

## 0.4.0 - 2026-10-03

- Automatisch starten bij inloggen: `autostart.ps1` maakt de Windows-taak LiveLink aan (op de achtergrond, herstart bij een crash); `-Verwijderen` haalt hem weer weg

## 0.3.9 - 2026-10-03

- Nieuw LiveLink-icoon: Venlo-kas met een PLC erin en een oranje datapuls naar buiten (kas, PLC en data in één beeld)

## 0.3.8 - 2026-10-03

- Insights-pagina's: zelfde kop als de startpagina, LiveLink-logo links (klikbaar, terug naar start) en Bosman van Zaal-logo rechts
- "← Alle projecten" staat nu boven de paginatitel

## 0.3.7 - 2026-10-03

- "Klant" heet op de pagina's nu "Project": keuzemenu, uitlegtekst, About en "← Alle projecten" op de Insights-pagina's

## 0.3.6 - 2026-10-03

- Startpagina: knop About uit de kop, Bosman van Zaal-logo groter (44 → 68 px)
- About is nu een klikbare tekst achter het versienummer onderaan de pagina

## 0.3.5 - 2026-10-03

- Nieuw LiveLink-icoon: PLC-module (klemmenstroken, statusleds, I/O-leds) met oranje signaalbogen voor de live verbinding

## 0.3.4 - 2026-10-03

- Programma heet nu **LiveLink** (was GreenSight): naam, woordmerk "LiveLink", paginatitel, About; logobestanden heten nu `livelink_logo.svg` en `livelink_icon.svg`

## 0.3.3 - 2026-10-03

- Startpagina: GreenSight-logo links in de kop (boven de oranje lijn), Bosman van Zaal-logo rechts met kleine knop About eronder
- www.bosmanvanzaal.com staat nu in het About-venster in plaats van in de kop
- Tekst "Kies een klant om de live PLC-gegevens te bekijken" staat onder het pulldown-menu

## 0.3.2 - 2026-10-03

- GreenSight-logo: Venlo-kas met oranje tandwiel (automatisering) en blad (teelt), als kop op de startpagina en in het About-venster (`greensight_logo.svg`, `greensight_icon.svg`)

## 0.3.1 - 2026-10-03

- Programma heet nu **GreenSight** (was "PLC Webserver"): paginatitel, kop, About en console

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
