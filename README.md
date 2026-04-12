# Bleepling

Bleepling ist eine lokal laufende Open-Source-Anwendung zur Anonymisierung von Audio- und Videodateien durch gezieltes Bleeping von gesprochenen Klarnamen.

Die Anwendung unterstützt einen nachvollziehbaren Prüf-Workflow: Aus einem Video oder einer Audioquelle werden Transkriptionsdaten erzeugt, daraus Kandidaten für mögliche Namensnennungen abgeleitet, diese werden menschlich geprüft und anschließend in Form einer Times-Datei für den finalen Bleep-Export verwendet.

Seit Version **1.2.1** enthält Bleepling zusätzlich den Reiter **„Titelkarten“**. Seit Version **1.3.0** kommt mit **„Schnitt & Kapitel“** ein weiterer Arbeitsbereich hinzu, mit dem aus vorhandenen Quellvideos zunächst ein Arbeitsvideo gebildet und daraus einzelne Clips für den weiteren Prüf-Workflow erzeugt werden können.

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
- Erstellung von PNG-Titelkarten über den Reiter **„Titelkarten“**
- Einstellungs- und Log-Bereich für Prüfung, Installation und Fehlersuche

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

Der Arbeitsstand **1.3.0** verwendet insbesondere diese sichtbaren Reiter:

- **Projekt** – Projekt anlegen, laden und verwalten
- **Medien** – Video- und WAV-Dateien ins Projekt übernehmen
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

- Dachzeile und Titeltext
- farbige Titelbox mit einstellbarer Größe
- vertikale Positionierung von Dachzeile und Titelbox
- Logos links unten und rechts unten
- Hintergrundbild als Grundlayout
- Export direkt in den Projektordner `04_output/titlecards`
- zusätzlicher PNG-Export an einen frei wählbaren Ort

Für Schriftarten werden **die lokal auf dem jeweiligen Windows-Rechner verfügbaren Systemschriftarten** genutzt. Bleepling liefert **keine eigenen Font-Dateien** mit. Die Prüfung der Nutzungsrechte verwendeter Schriftarten liegt daher beim jeweiligen Anwender.

## Einstellungen / Logs

Bleepling enthält einen eigenen Reiter **„Einstellungen / Logs“**. Dort kann die lokale Umgebung geprüft werden. Je nach Projektstand werden insbesondere kontrolliert:

- Python
- FFmpeg
- relevante Python-Module
- optionale CUDA-/cuDNN-Komponenten und Pfade
- python-vlc sowie optionale VLC-/libVLC-Komponenten
- Render-Backend und weitere technische Einstellungen

Der Bereich dient außerdem dazu, Installationshinweise und Installationskommandos bereitzustellen oder deren Ausführung lokal vorzubereiten.

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
6. Blocklist, Allowlist und Teilnehmerlisten pflegen, falls sinnvoll
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

### Titelkarten-bezogene Eingaben

- PNG
- JPG / JPEG
- BMP
- WEBP

## Projektstruktur

Im Projektstand 1.3.0 werden unter anderem diese projektbezogenen Pfade verwendet:

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
