# Release-Vorlage 1.5.2

Diese Datei dient als vorbereitete Arbeitsgrundlage für die manuelle Veröffentlichung von **Bleepling 1.5.2**.

## Empfohlener Tag

`v1.5.2`

## Empfohlener Release-Titel

`Bleepling 1.5.2`

## Empfohlene Kurzbeschreibung für GitHub

Patch-Release mit wiederhergestellter echter `words.json`-Erzeugung aus WAV-Dateien, klar getrennten Audioausgaben, robusterem Render-Aufräumen unter Windows und aktualisierter Benutzerdokumentation.

## Vorschlag für den eigentlichen Release-Text

### Überblick

Version **1.5.2** korrigiert vor allem den Transkriptionsweg im praktischen Anonymisierungsworkflow. Aus WAV-Dateien werden wieder echte `words.json`-Dateien mit Wort-Zeitmarken erzeugt; leere Platzhalterdateien werden nicht mehr als erfolgreicher Arbeitsschritt ausgegeben.

### Wichtige Änderungen

- `words.json` aus WAV nutzt wieder die echte Transkription.
- Falls kein Legacy-Transkriptionsskript vorhanden ist, verwendet Bleepling direkt `faster-whisper`.
- Der kombinierte Prüfworkflow nutzt denselben echten Transkriptionsweg wie der Reiter **„Prüfen & Entscheiden“**.
- Gebleepte Audioexporte werden in `04_output/audio` abgelegt; Videoexporte bleiben in `04_output/videos`.
- Temporäre FFmpeg- und Nachbearbeitungsdateien werden unter Windows robuster aufgeräumt.
- Die Start-BAT-Dateien wurden vereinheitlicht; der Debug-Start zeigt zusätzliche technische Informationen.
- Das Benutzerhandbuch wurde als PDF auf Version 1.5.2 aktualisiert.

### Hinweise

- Lokale Testdaten, temporäre Testprojekte und Word-Arbeitsdateien sind vom GitHub-Release ausgeschlossen.
- Externe Komponenten wie **FFmpeg**, **VLC/libVLC** sowie optionale **CUDA/cuDNN**-Umgebungen bleiben weiterhin getrennt vom Projekt zu installieren.
- Eine menschliche Endkontrolle anonymisierter Medien bleibt weiterhin erforderlich.

## Empfohlene GitHub-Felder

### Release name

`Bleepling 1.5.2`

### Tag version

`v1.5.2`

### Target

aktueller Hauptstand, von dem die Veröffentlichung erfolgen soll

### Description

Den vorbereiteten Release-Text aus dieser Datei verwenden und bei Bedarf leicht kürzen.

### Assets

Sinnvoll können insbesondere sein:

- Quellcode-Archiv von GitHub
- Benutzerhandbuch als PDF

## Empfohlene letzte Prüfung vor Veröffentlichung

- Versionsstand in Code, README, Changelog und Handbuch gegenlesen
- `words.json`-Erzeugung aus WAV mit lokalem Testmaterial prüfen
- Audio- und Videoexport mit FFmpeg prüfen
- gezielte Nachbearbeitung mit zusätzlichem Bleep und optionaler Titelkarte prüfen
- GitHub-Release erst nach Merge in `main` und finalem Tag `v1.5.2` erstellen
