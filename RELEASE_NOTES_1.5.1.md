# Release-Vorlage 1.5.1

Diese Datei dient als vorbereitete Arbeitsgrundlage für die manuelle Veröffentlichung von **Bleepling 1.5.1**.

## Empfohlener Tag

`v1.5.1`

## Empfohlener Release-Titel

`Bleepling 1.5.1`

## Empfohlene Kurzbeschreibung für GitHub

Patch- und Bedienrelease mit interaktiver Titelkarten-Positionierung, sicheren Projekt- und Exportdialogen, zentralen Render-Parametern für die gezielte Nachbearbeitung und mehreren Korrekturen aus dem Echtbetrieb.

## Vorschlag für den eigentlichen Release-Text

### Überblick

Version **1.5.1** verfeinert den mit 1.5.0 ausgebauten Workflow an mehreren Stellen, die sich im produktiven Einsatz als wichtig erwiesen haben. Im Mittelpunkt stehen sicherere Bedienung, ein deutlich flexiblerer Titelkarten-Reiter und besser nachvollziehbare Render-Parameter für die gezielte Nachbearbeitung.

### Wichtige sichtbare Änderungen

- im Reiter **„Titelkarten“** können Dachzeile, zweite Dachzeile, Titelbox und beide Logo-Felder direkt in der Live-Vorschau verschoben und skaliert werden
- eine mittige Einrastfunktion mit sichtbaren Hilfslinien erleichtert die saubere Zentrierung von Titelkarten-Elementen
- Titelkarten-Export und Live-Vorschau sind nun strikt getrennt: Hilfsrahmen, Platzhalter und graue Vorschauflächen erscheinen nicht mehr in der echten Ausgabe
- beim Export einer Titelkarte in den Projektordner fragt Bleepling vor dem Überschreiben einer bestehenden Datei nach
- im Reiter **„Projekt“** kann ein bestehender vollständiger Projektordner nach Sicherheitsabfrage gelöscht werden; der Löschbutton ist bewusst rechts am Fensterrand positioniert
- Rechtsklick-Kontextmenüs für Ausschneiden, Kopieren, Einfügen und Alles auswählen funktionieren nun projektweit in den relevanten Eingabefeldern

### Rendern und gezielte Nachbearbeitung

- der Reiter **„Einstellungen / Logs“** enthält den neuen Bereich **„Rendern / Ausgabe“**
- dort können Backend, Qualität, Preset, Audio-Bitrate und Skalierung zentral eingestellt werden
- die **gezielte Nachbearbeitung** übernimmt diese Werte für das Rendern von Änderungen
- Standard bleibt **„Originalgröße beibehalten“**, damit bestehende Videos bei Nachbearbeitungen nicht unbemerkt auf Webgröße verkleinert werden
- Fragezeichen-Hilfen erklären die Auswirkungen der neuen Render-Parameter und ihrer Auswahlmöglichkeiten

### Behoben

- Fehlermeldung beim Mausrad-Scrollen in geöffneten Combobox-Dropdowns
- versehentliches Überschreiben bestehender Titelkarten ohne Nachfrage
- sichtbare Hilfs- und Platzhalterelemente aus der Titelkarten-Vorschau in exportierten oder gerenderten Titelkarten
- fehlende Löschmöglichkeit für bestehende Projektordner über die Oberfläche

### Hinweise

- Die interaktive Titelkarten-Vorschau ist eine Bearbeitungshilfe. Maßgeblich für Export und Videorender ist weiterhin die sauber erzeugte Ausgabe ohne Hilfsrahmen.
- Die neuen Render-Parameter wirken projektbezogen und werden in den Projekteinstellungen gespeichert.
- Externe Komponenten wie **FFmpeg**, **VLC/libVLC** sowie optionale **CUDA/cuDNN**-Umgebungen bleiben weiterhin getrennt vom Projekt zu installieren.
- Eine menschliche Endkontrolle anonymisierter Medien bleibt weiterhin erforderlich.

## Empfohlene zu prüfende Release-Artefakte

- Quellcode des aktuellen Projektstands
- aktualisierte Benutzerdokumentation in der vorgesehenen Veröffentlichungsform

## Empfohlene GitHub-Felder

### Release name

`Bleepling 1.5.1`

### Tag version

`v1.5.1`

### Target

aktueller Hauptstand, von dem die Veröffentlichung erfolgen soll

### Description

Den vorbereiteten Release-Text aus dieser Datei verwenden und bei Bedarf leicht kürzen.

### Assets

Sinnvoll können insbesondere sein:

- Quellcode-Archiv von GitHub
- Benutzerhandbuch als PDF- oder DOCX-Fassung

## Empfohlene letzte Prüfung vor Veröffentlichung

- Versionsstand in README, Changelog und Handbuch gegenlesen
- Titelkarte mit und ohne Logos exportieren und prüfen, dass keine Hilfsrahmen oder grauen Vorschauflächen enthalten sind
- interaktives Verschieben, Skalieren und mittiges Einrasten im Reiter **„Titelkarten“** kurz praktisch prüfen
- Überschreibwarnung beim Titelkarten-Export in den Projektordner prüfen
- Projektlöschung nur an einem kopierten Testprojekt prüfen
- gezielte Nachbearbeitung mit Standardwert **„Originalgröße beibehalten“** und mindestens einem geänderten Render-Parameter testen
- keine temporären Arbeitsordner oder Archivzwischenstände mitveröffentlichen
