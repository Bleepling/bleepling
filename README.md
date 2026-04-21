# Bleepling

Bleepling ist eine lokal laufende Open-Source-Anwendung zur Anonymisierung von Audio- und Videodateien durch gezieltes Bleeping von gesprochenen Klarnamen.

Die Anwendung unterstützt einen nachvollziehbaren Prüf-Workflow: Aus einem Video oder einer Audioquelle werden Transkriptionsdaten erzeugt, daraus Kandidaten für mögliche Namensnennungen abgeleitet, diese werden menschlich geprüft und anschließend in Form einer Times-Datei für den finalen Bleep-Export verwendet.

Seit Version **1.2.1** enthält Bleepling zusätzlich den Reiter **„Titelkarten“**. Seit Version **1.3.0** kommt mit **„Schnitt & Kapitel“** ein weiterer Arbeitsbereich hinzu, mit dem aus vorhandenen Quellvideos zunächst ein Arbeitsvideo gebildet und daraus einzelne Clips für den weiteren Prüf-Workflow erzeugt werden können. Mit Version **1.4.0** wurde insbesondere der Titelkarten-Reiter deutlich ausgebaut und der Reiter **„Einstellungen / Logs“** klarer strukturiert. Version **1.4.1** verbessert zusätzlich den Import und die flexible Übernahme von Teilnehmerlisten im Reiter **„Prüfen & Entscheiden“**. Version **1.5.0** bündelt zahlreiche sichtbare Workflow-Verbesserungen bei **Titelkarten**, **Gezielter Nachbearbeitung**, **Medienübersicht**, **Render-Abbruch**, **Button-/Scroll-Verhalten** und **Einstellungen / Logs**. Version **1.5.1** ergänzt Sicherheitsabfragen, Projektlöschung, interaktive Titelkarten-Positionierung und zentrale Render-Parameter für die gezielte Nachbearbeitung.

## Hauptfunktionen

- lokale Verarbeitung von Audio- und Videodateien
- Erzeugung von WAV-Dateien aus Videos
- Transkription mit Whisper beziehungsweise faster-whisper
- Erzeugung und Prüfung zeitgestempelter Kandidaten-Dateien
- Arbeit mit Blocklist, Allowlist und Teilnehmerlisten
- kombinierter Prüf- und Entscheidungsworkflow im Reiter **„Prüfen & Entscheiden“**
- Erzeugung von Times-Dateien mit Intervallen für gezielte Bleeps
- neuer Reiter **„Schnitt & Kapitel“** zur Bildung eines Arbeitsvideos, zum manuellen Setzen von Schnittmarken und zur Erzeugung einzelner Clips als neue Projektmedien
- finaler Export gebleepter Video- oder Audiodateien über FFmpeg
- gezielte Nachbearbeitung bereits erzeugter Medien
- Vor- und Nachspannbilder mit synchron verlängerter Stille sowie Komma-Unterstützung bei Sekundeneingaben
- Erstellung von PNG-Titelkarten über den Reiter **„Titelkarten“**
- zweite Dachzeile / Untertitel sowie mehrzeilige Titelkarten-Layouts mit Live-Vorschau
- interaktive Titelkarten-Layoutfelder für Dachzeilen, Titelbox und Logos mit Verschieben, Skalieren und mittigem Einrasten
- projektweite Medienübersicht mit kategorisierten Dateibeständen und abschnittsbezogenem Öffnen der jeweiligen Ordner
- Einstellungs- und Log-Bereich für Prüfung, Installation, Render-Parameter und Fehlersuche

## Ziel des Projekts

Bleepling soll helfen, datenschutzrechtlich problematische Namensnennungen in Medien vor einer Veröffentlichung, Weitergabe oder Archivierung kontrolliert zu anonymisieren.

Die Anwendung ist nicht als allgemeine kreative Videoschnittsoftware gedacht, sondern als fachlich orientiertes Werkzeug für einen strukturierten Datenschutz-Workflow. Der Reiter **„Schnitt & Kapitel“** ergänzt diesen Workflow um eine bewusst manuelle, kontrollierbare Vorbereitung größerer Ausgangsmedien. Der Reiter **„Titelkarten“** erweitert ihn zusätzlich um eine einfache, lokal arbeitende Möglichkeit zur Erstellung von Vor- und Nachspannkarten, ohne dafür separate Grafiksoftware zu benötigen.

## Wichtiger Hinweis

Bleepling kann sehr hilfreich sein, garantiert aber keine vollständige Erkennung aller personenbezogenen Namensnennungen.

Vor einer Veröffentlichung, Weitergabe oder sonstigen Nutzung anonymisierter Medien sollte deshalb immer eine zusätzliche menschliche Endkontrolle erfolgen.

## Open-Source-Status

Dieses Projekt wird als Open-Source-Software veröffentlicht.

**Lizenz:** MIT

## Voraussetzungen

Für den vollständigen Funktionsumfang werden insbesondere benötigt:

- Python 3
- Tkinter
- FFmpeg
- Pillow
- faster-whisper
- ctranslate2
- openpyxl
- python-docx
- pdfplumber
- pypdf
- PyPDF2
- python-vlc

### Optionale Komponenten

Für GPU-beschleunigte Transkription oder bestimmte Hardware-Setups können zusätzlich NVIDIA-CUDA- und cuDNN-Komponenten erforderlich sein.

Für die eingebettete Vorschau im Reiter **„Schnitt & Kapitel“** wird zusätzlich eine lokal installierte **VLC-/libVLC-Umgebung** benötigt. Bleepling liefert diese Umgebung nicht mit, sondern bindet sie – soweit vorhanden – lokal an.

Diese Komponenten sind **nicht Bestandteil dieses Projekts** und müssen bei Bedarf separat installiert werden.

## Reiter im Überblick

Der Arbeitsstand **1.5.1** verwendet insbesondere diese sichtbaren Reiter:

- **Projekt** – Projekt anlegen, laden und vollständige Projektordner nach Sicherheitsabfrage löschen
- **Medien** – Projektmedien importieren und vorhandene Projektdateien strukturiert überblicken
- **Schnitt & Kapitel** – Quellvideos sortieren, Arbeitsvideo bilden, manuell schneiden und Clips erzeugen
- **Prüfen & Entscheiden** – Vorbereitung, Namenslisten, Kandidatenprüfung, Audio-Feinprüfung, Bleep-Parameter und Times-Ableitung
- **Video & Audio / FFmpeg** – finaler Export gebleepter Video- oder Audiodateien
- **Gezielte Nachbearbeitung** – zusätzliche Einzel-Bleeps sowie Vor- und Nachspannbilder
- **Titelkarten** – Erstellung, Vorschau und Export von PNG-Titelkarten
- **Einstellungen / Logs** – technische Prüfung, Diagnose und Unterstützung bei Installationsschritten

Die früheren Reiter **„Bleeping“** und **„Treffer prüfen“** sind im sichtbaren Workflow weiterhin durch den kombinierten Reiter **„Prüfen & Entscheiden“** ersetzt.

## Schnitt & Kapitel

Der Reiter **„Schnitt & Kapitel“** ist für die kontrollierte Vorbereitung größerer Quellmedien gedacht. Er ergänzt den bisherigen Direktworkflow, ersetzt ihn aber nicht.

Unterstützt werden insbesondere:

- Auswahl und Sortierung mehrerer Quellvideos innerhalb eines Projekts
- Bildung eines projektbezogenen Arbeitsvideos
- Öffnen eines internen Schnittfensters mit eingebetteter Vorschau
- Setzen von Start- und Endmarken
- Anlegen, Aktualisieren und Löschen einzelner Clips
- Erzeugung ausgewählter oder aller Clips als neue Projektmedien im Projektordner

Wichtig ist dabei: Wer bereits mit fertig vorbereiteten Einzelvideos arbeiten möchte, kann weiterhin direkt im Reiter **„Prüfen & Entscheiden“** einsteigen. Der neue Reiter ist ein zusätzlicher Vorbau und keine Pflichtstufe.

## Titelkarten

Der Reiter **„Titelkarten“** ist für die Erstellung statischer PNG-Karten im Format **1920 × 1080** gedacht. Diese Karten können insbesondere als Vor- oder Nachspannbilder im weiteren Workflow verwendet werden.

Unterstützt werden unter anderem:

- Dachzeile, zweite Dachzeile / Untertitel und Titeltext
- farbige Titelbox mit einstellbarer Größe
- vertikale Positionierung von Dachzeile, zweiter Dachzeile und Titelbox
- getrennte Farben, Schriftgrößen und Stilumschaltungen für die einzelnen Textebenen
- mehrzeilige Titel mit automatischer Einpassung in die verfügbare Titelbox
- Platzhalter für Dachzeilen nur in der Live-Vorschau, nicht im PNG-Export
- gezieltes Ausblenden von Dachzeile und zweiter Dachzeile
- Logos links unten und rechts unten
- interaktive Positionierung und Größenänderung von Dachzeile, zweiter Dachzeile, Titelbox sowie beiden Logo-Feldern direkt in der Live-Vorschau
- magnetisches Einrasten auf die Bildmitte mit sichtbaren Hilfslinien
- Sicherheitsabfrage beim projektbezogenen Export, wenn eine Titelkarte mit gleichem Dateinamen bereits vorhanden ist
- Hintergrundbild als Grundlayout mit automatischer Einpassung in das Zielformat
- Export direkt in den Projektordner `04_output/titlecards`
- zusätzlicher PNG-Export an einen frei wählbaren Ort

Die Live-Vorschau darf Hilfsrahmen, Platzhalter und Bearbeitungslinien anzeigen. Der eigentliche PNG-Export und die Verwendung als Vor- oder Nachspannbild werden dagegen ohne diese Hilfen erzeugt; ohne eigenes Hintergrundbild ist der Ausgabehintergrund weiß.

Im Zusammenspiel mit **„Gezielte Nachbearbeitung“** ist wichtig: Vor- und Nachspannbilder werden dort synchron zum eigentlichen Medium zusammengesetzt. Die vorgeschalteten oder angehängten Bildsegmente verlängern intern auch die Audiospur mit stillen Abschnitten, sodass Bild- und Tonlauf des eigentlichen Videos erhalten bleiben.

Für Schriftarten werden **die lokal auf dem jeweiligen Windows-Rechner verfügbaren Systemschriftarten** genutzt. Bleepling liefert **keine eigenen Font-Dateien** mit. Die Prüfung der Nutzungsrechte verwendeter Schriftarten liegt daher beim jeweiligen Anwender.

## Einstellungen / Logs

Bleepling enthält einen eigenen Reiter **„Einstellungen / Logs“**. Dort kann die lokale Umgebung geprüft werden. Je nach Projektstand werden insbesondere kontrolliert:

- Python
- FFmpeg
- relevante Python-Module
- optionale CUDA-/cuDNN-Komponenten und Pfade
- python-vlc sowie optionale VLC-/libVLC-Komponenten
- Render-Backend und weitere technische Einstellungen

Seit Version **1.5.1** enthält dieser Reiter außerdem den Bereich **„Rendern / Ausgabe“**. Dort werden projektbezogen zentrale Renderwerte festgelegt:

- **Backend**: `auto` nutzt nach Möglichkeit GPU-Encoding und fällt sonst auf CPU zurück; `gpu` versucht bevorzugt den NVIDIA-Encoder; `cpu` nutzt bewusst den Prozessor.
- **Qualität (CQ/CRF)**: niedrigere Werte liefern höhere Qualität und größere Dateien; höhere Werte komprimieren stärker. Der Standard `30` entspricht dem bisherigen Verhalten der gezielten Nachbearbeitung.
- **Preset**: schnellere Presets rendern flotter, langsamere Presets können bei gleicher Qualität effizienter komprimieren.
- **Audio-Bitrate**: `96k` ist für Sprache meist ausreichend; höhere Werte sind sinnvoll, wenn Musik oder allgemeiner Ton wichtiger ist.
- **Skalierung**: **„Originalgröße beibehalten“** ist der sichere Standard für die gezielte Nachbearbeitung. `1280 px` erzeugt kleinere Web-Dateien, `1920 px` ist Full-HD-orientiert und kann kleine Quellen unnötig hochskalieren.

Die gezielte Nachbearbeitung übernimmt diese zentralen Renderwerte für Codec, Qualität, Preset, Audio-Bitrate und Skalierung. Die dortigen Fachparameter wie Bleep-Zeiten, Vorlauf, Nachlauf sowie Vor- und Nachspannbild bleiben weiterhin im Reiter **„Gezielte Nachbearbeitung“**.

Der Bereich dient außerdem dazu, Installationshinweise, sichtbare Einrichtungsbefehle und Hilfetexte für typische Diagnosefälle bereitzustellen oder deren Ausführung lokal vorzubereiten.

Die sichtbare Prüfaktion läuft im aktuellen Stand über einen einzigen klaren Button **„Prüfung ausführen“**. Wenn eine Kontrolle nach Änderungen erneut nötig ist, wird dieselbe Prüfung einfach noch einmal über denselben Button gestartet.

Wichtig ist dabei: Externe Komponenten wie **FFmpeg**, **VLC/libVLC**, **CUDA** oder **cuDNN** werden durch Bleepling nicht mitgeliefert. Die Anwendung prüft nur deren Vorhandensein und unterstützt bei der Einrichtung.

## Installation

### 1. Repository klonen oder herunterladen

Projekt lokal in einen beliebigen Ordner kopieren.

### 2. Python-Umgebung einrichten

Empfohlen wird eine virtuelle Umgebung.

Beispiel unter Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. FFmpeg separat installieren

FFmpeg muss separat installiert werden und systemweit verfügbar sein oder im PATH liegen.

FFmpeg ist **nicht Bestandteil** dieses Projekts.

### 4. VLC / libVLC bei Bedarf separat installieren

Für die eingebettete Vorschau im Reiter **„Schnitt & Kapitel“** sollte eine lokal installierte VLC-/libVLC-Umgebung vorhanden sein.

Auch diese Komponente ist **nicht Bestandteil** dieses Projekts.

### 5. Optionale GPU-Komponenten installieren

Wenn GPU-Beschleunigung genutzt werden soll, müssen gegebenenfalls zusätzliche NVIDIA-CUDA- und cuDNN-Komponenten separat installiert werden.

Auch diese Komponenten sind **nicht Bestandteil** dieses Projekts.

### 6. Anwendung starten

Unter Windows stehen typischerweise folgende Startwege zur Verfügung:

#### Normaler Start ohne sichtbares Konsolenfenster

Doppelklick auf:

- `start_bleepling.vbs`

#### Stiller Start über Batch-Datei

Doppelklick auf:

- `start_bleepling_silent.bat`

#### Debug-Start mit sichtbarem Konsolenfenster

Doppelklick auf:

- `start_bleepling_debug.bat`

Dieser Startweg ist besonders hilfreich bei Fehlersuche und Entwicklungsarbeiten.

#### Alternativer Start über Python

```bash
set PYTHONPATH=src
python -m bleepling.app
```

## Typischer Arbeitsablauf

### Direktworkflow mit bereits vorbereiteten Einzelvideos

1. Projekt anlegen oder laden
2. Video oder WAV-Datei importieren
3. im Reiter **„Prüfen & Entscheiden“** eine WAV erzeugen, falls nur ein Video vorliegt
4. `words.json` aus WAV erzeugen
5. Kandidaten-Datei erzeugen
6. Blocklist, Allowlist und Teilnehmerlisten pflegen, falls sinnvoll; Teilnehmerlisten können dabei als Nachnamen, Vornamen oder in kombinierter Form übernommen werden
7. Kandidaten auswerten, Treffer im Audio prüfen und erforderlichenfalls feinjustieren
8. Bleep-Parameter im Reiter **„Prüfen & Entscheiden“** festlegen und anwenden
9. Times-Datei mit Intervallen ableiten
10. bei Bedarf im Reiter **„Titelkarten“** eine Vor- oder Nachspannkarte erzeugen
11. gebleepte Audio- oder Videodatei über **„Video & Audio / FFmpeg“** exportieren
12. Ergebnis manuell kontrollieren

### Erweiterter Workflow über „Schnitt & Kapitel“

1. Projekt anlegen oder laden
2. Quellvideos importieren
3. im Reiter **„Schnitt & Kapitel“** Quellvideos sortieren
4. Arbeitsvideo aus der Auswahl bilden oder vorhandenes Arbeitsvideo wiederverwenden
5. im Schnittfenster Start- und Endmarken setzen
6. Clips anlegen und erzeugen
7. erzeugte Clips anschließend wie normale Projektmedien im Reiter **„Prüfen & Entscheiden“** weiterverarbeiten
8. danach wie gewohnt Times-Datei ableiten und final exportieren

## Unterstützte Eingaben

### Medien

- MP4
- MOV
- MKV
- AVI
- M4V
- WMV
- WAV

### Teilnehmerlisten

- TXT
- CSV
- XLSX
- DOCX
- PDF

Im Reiter **„Prüfen & Entscheiden“** können importierte Teilnehmerlisten wahlweise als **Nachnamen**, **Vornamen** oder in kombinierter Form in die Blocklist-Vorlage übernommen werden. Ein zusätzlicher Button **„Akt.“** baut die zuletzt importierte Teilnehmerliste mit den aktuell gesetzten Optionen erneut auf, ohne manuelle Blocklist-Einträge zu überschreiben.

### Titelkarten-bezogene Eingaben

- PNG
- JPG / JPEG
- BMP
- WEBP

## Projektstruktur

Im Projektstand 1.5.1 werden unter anderem diese projektbezogenen Pfade verwendet:

- `01_input/video`
- `03_processing/04_cutting/working_video`
- `04_output/videos`
- `04_output/titlecards`
- `99_config/app_state.json`
- `99_config/titlecards_state.json`

Fehlende neue Projektordner werden beim Laden bestehender Projekte nach Möglichkeit automatisch ergänzt, damit ältere Projekte weiterhin verwendet werden können.

## Projektstatus

Bleepling befindet sich in aktiver Weiterentwicklung.

Der aktuelle Stand kann funktionale, technische oder dokumentarische Unschärfen enthalten.

## Dokumentation

Eine Benutzerdokumentation liegt dem Projekt bei.

Weitere projektbezogene Dokumentationsdateien können je nach Veröffentlichungsstand ergänzt werden.

## Mitwirken

Beiträge, Fehlermeldungen und Verbesserungsvorschläge sind willkommen.

Weitere Hinweise folgen in einer separaten Datei `CONTRIBUTING.md`.

## Kontakt

Andreas Ritz  
E-Mail: bleepling@email.de
