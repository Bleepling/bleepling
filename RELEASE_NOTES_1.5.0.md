# Release-Vorlage 1.5.0

Diese Datei dient als vorbereitete Arbeitsgrundlage für die manuelle Veröffentlichung von **Bleepling 1.5.0**.

## Empfohlener Tag

`v1.5.0`

## Empfohlener Release-Titel

`Bleepling 1.5.0`

## Empfohlene Kurzbeschreibung für GitHub

Größeres Funktions- und Stabilitätsrelease mit überarbeiteter Medienübersicht, verbessertem Titelkarten- und Nachbearbeitungs-Workflow sowie wirksamer Abbruchlogik bei längeren Renderläufen.

## Vorschlag für den eigentlichen Release-Text

### Überblick

Version **1.5.0** bündelt zahlreiche sichtbare Verbesserungen im täglichen Arbeitsablauf. Im Mittelpunkt stehen der deutlich ausgebaute Reiter **„Medien“**, mehrere Korrekturen und Erweiterungen in **„Titelkarten“** und **„Gezielte Nachbearbeitung“** sowie eine spürbar verlässlichere Steuerung längerer Renderprozesse.

### Wichtige sichtbare Änderungen

- der Reiter **„Medien“** zeigt jetzt den relevanten Projektbestand deutlich vollständiger und sauberer gegliedert an
- pro Medienabschnitt kann der zugehörige Ordner direkt über **„Ordner öffnen“** geöffnet werden
- im Reiter **„Titelkarten“** bleiben Dachzeilen-Platzhalter auf die Live-Vorschau beschränkt und erscheinen nicht mehr versehentlich im PNG-Export
- Dachzeile und zweite Dachzeile lassen sich bei Bedarf gezielt ausblenden
- Hintergrundbilder werden im Titelkarten-Export passend in das Zielformat eingepasst
- im Reiter **„Gezielte Nachbearbeitung“** funktionieren Vor- und Nachspannbilder jetzt synchron zum eigentlichen Video, einschließlich still verlängerter Audiospur
- Kommawerte wie `8,5` werden bei Vor- und Nachspandauern akzeptiert
- unterhalb der Nachbearbeitung stehen jetzt **„Output-Ordner öffnen“** und **„Ergebnis abspielen“** direkt zur Verfügung

### Technische Verbesserungen

- Abbrechen bei längeren Renderläufen funktioniert jetzt tatsächlich in den relevanten Renderpfaden
- Benutzerabbrüche werden nicht mehr irreführend als fachliche Renderfehler gemeldet
- der FFmpeg-Fortschrittsdialog bleibt auch in längeren Schritt-1-Phasen sichtbar aktiv
- vorhandene Ausgabedateien werden in der gezielten Nachbearbeitung nicht mehr überschrieben, sondern automatisch fortlaufend benannt
- Button-Hover, Dialogzentrierung, globale Mausrad-Unterstützung und einzelne Hilfetexte wurden projektweit geglättet

### Hinweise

- Der maßgebliche sichtbare Prüfworkflow bleibt weiterhin der Reiter **„Prüfen & Entscheiden“**
- Externe Komponenten wie **FFmpeg**, **VLC/libVLC** sowie optionale **CUDA/cuDNN**-Umgebungen bleiben weiterhin getrennt vom Projekt zu installieren
- Die aktualisierte Benutzerdokumentation kann wie bisher zusätzlich als separate PDF-Fassung für Anwenderinnen und Anwender bereitgestellt werden

## Empfohlene zu prüfende Release-Artefakte

- Quellcode des aktuellen Projektstands
- aktualisierte Benutzerdokumentation in der vorgesehenen Veröffentlichungsform

## Empfohlene GitHub-Felder

### Release name

`Bleepling 1.5.0`

### Tag version

`v1.5.0`

### Target

aktueller Hauptstand, von dem die Veröffentlichung erfolgen soll

### Description

Den vorbereiteten Release-Text aus dieser Datei verwenden und bei Bedarf leicht kürzen.

### Assets

Sinnvoll können insbesondere sein:

- Quellcode-Archiv von GitHub
- Benutzerhandbuch als PDF-Fassung

## Empfohlene letzte Prüfung vor Veröffentlichung

- Versionsstand in README, Changelog und Handbuch noch einmal kurz gegenlesen
- prüfen, dass Titelkarten ohne Dachzeilentext keine Platzhalter mehr exportieren
- prüfen, dass Vor- und Nachspannbilder in der gezielten Nachbearbeitung zeitlich synchron bleiben
- prüfen, dass Abbrechen bei längeren Renderläufen nachvollziehbar funktioniert
- keine temporären Arbeitsordner oder Archivzwischenstände mitveröffentlichen
- einmal kurz den sichtbaren Reiterbestand gegen die Release-Beschreibung halten
