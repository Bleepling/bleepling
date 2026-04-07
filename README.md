# Bleepling

Bleepling is a locally running open-source application designed to anonymize audio and video files by selectively bleeping out spoken real names.
The application supports a transparent review workflow: Transcription data is generated from a video or audio source, potential names are identified from this data, reviewed by the user, and then used in the form of a Times file for the final bleep export.
Note: The project documentation is currently available only in German.

Bleepling ist eine lokal laufende Open-Source-Anwendung zur Anonymisierung von Audio- und Videodateien durch gezieltes Bleeping von gesprochenen Klarnamen.
Die Anwendung unterstützt einen nachvollziehbaren Prüf-Workflow: Aus einem Video oder einer Audioquelle werden Transkriptionsdaten erzeugt, daraus Kandidaten für mögliche Namensnennungen abgeleitet, diese werden durch den User geprüft und anschließend in Form einer Times-Datei für den finalen Bleep-Export verwendet.
Hinweis: Die Projektdokumentation ist derzeit überwiegend auf Deutsch verfügbar.

## Hauptfunktionen

- lokale Verarbeitung von Audio- und Videodateien
- Erzeugung von WAV-Dateien aus Videos
- Transkription mit Whisper beziehungsweise faster-whisper
- Erzeugung und Prüfung zeitgestempelter Kandidaten-Dateien
- Arbeit mit Blocklist, Allowlist und Teilnehmerlisten
- Erzeugung von Times-Dateien für gezielte Bleeps
- finaler Export gebleepter Video- oder Audiodateien über FFmpeg
- gezielte Nachbearbeitung bereits erzeugter Medien
- Einstellungs- und Log-Bereich für Prüfung, Installation und Fehlersuche

## Ziel des Projekts

Bleepling soll helfen, datenschutzrechtlich problematische Namensnennungen in Medien vor einer Veröffentlichung, Weitergabe oder Archivierung kontrolliert zu anonymisieren.

Die Anwendung ist nicht als kreative Videoschnittsoftware gedacht, sondern als fachlich orientiertes Werkzeug für einen strukturierten Datenschutz-Workflow.

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

### Optionale Komponenten

Für GPU-beschleunigte Transkription oder bestimmte Hardware-Setups können zusätzlich NVIDIA-CUDA- und cuDNN-Komponenten erforderlich sein.

Diese Komponenten sind **nicht Bestandteil dieses Projekts** und müssen bei Bedarf separat installiert werden.

## Einstellungen / Logs

Bleepling enthält einen eigenen Reiter **„Einstellungen / Logs“**. Dort kann die lokale Umgebung geprüft werden. Je nach Projektstand werden insbesondere kontrolliert:

- Python
- FFmpeg
- relevante Python-Module
- optionale CUDA-/cuDNN-Komponenten und Pfade
- Render-Backend und weitere technische Einstellungen

Der Bereich dient außerdem dazu, Installationshinweise und Installationskommandos bereitzustellen oder deren Ausführung lokal vorzubereiten.

Wichtig ist dabei: Externe Komponenten wie **FFmpeg**, **CUDA** oder **cuDNN** werden durch Bleepling nicht mitgeliefert. Die Anwendung prüft nur deren Vorhandensein und unterstützt bei der Einrichtung.

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

### 4. Optionale GPU-Komponenten installieren

Wenn GPU-Beschleunigung genutzt werden soll, müssen gegebenenfalls zusätzliche NVIDIA-CUDA- und cuDNN-Komponenten separat installiert werden.

Auch diese Komponenten sind **nicht Bestandteil** dieses Projekts.

### 5. Anwendung starten

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

1. Projekt anlegen oder laden
2. Video oder WAV-Datei importieren
3. WAV erzeugen, falls nur ein Video vorliegt
4. `words.json` aus WAV erzeugen
5. Kandidaten-Datei erzeugen
6. Kandidaten prüfen und Vorschau bewerten
7. Times-Datei erzeugen
8. gebleepte Audio- oder Videodatei exportieren
9. Ergebnis manuell kontrollieren

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
