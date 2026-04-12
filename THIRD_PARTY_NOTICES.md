# Third-Party Notices

Dieses Projekt **Bleepling** verwendet oder unterstützt die Nutzung verschiedener Drittanbieter-Komponenten und Open-Source-Bibliotheken.

Diese Übersicht dient der Transparenz. Sie ersetzt nicht die jeweils maßgeblichen Lizenztexte der einzelnen Projekte.

## Grundsatz

Bleepling selbst wird unter der **MIT-Lizenz** veröffentlicht.

Einige für den Betrieb oder Teilfunktionen erforderliche Komponenten stammen von Drittanbietern und unterliegen deren jeweiligen Lizenzen.

Dabei ist besonders zu unterscheiden zwischen:

- **Python-Bibliotheken**, die typischerweise über `pip` installiert werden
- **externen Systemkomponenten**, die von Bleepling genutzt oder geprüft, aber **nicht mit dem Projekt ausgeliefert** werden

## Python-Bibliotheken

Nach aktuellem Projektstand werden insbesondere folgende Python-Pakete verwendet oder unterstützt:

### Pillow
- Zweck: Bildverarbeitung und grafische Funktionen
- Projekt: Pillow
- Lizenz: HPND

### faster-whisper
- Zweck: Transkription
- Projekt: faster-whisper
- Lizenz: MIT

### ctranslate2
- Zweck: Laufzeitumgebung für Transkriptionsfunktionen
- Projekt: CTranslate2
- Lizenz: MIT

### openpyxl
- Zweck: Import von XLSX-Dateien
- Projekt: openpyxl
- Lizenz: MIT

### python-docx
- Zweck: Import von DOCX-Dateien
- Projekt: python-docx
- Lizenz: MIT

### pdfplumber
- Zweck: strukturierter PDF-Import
- Projekt: pdfplumber
- Lizenz: MIT

### pypdf
- Zweck: PDF-Verarbeitung
- Projekt: pypdf
- Lizenz: BSD-3-Clause

### PyPDF2
- Zweck: zusätzliche beziehungsweise ältere PDF-Kompatibilität
- Projekt: PyPDF2
- Lizenz: BSD-3-Clause

### python-vlc
- Zweck: Python-Bindings für libVLC zur eingebetteten Vorschau und Wiedergabe
- Projekt: python-vlc
- Lizenz: LGPL-2.1-or-later
- Hinweis: **Das Paket bindet an eine bereits separat installierte VLC-/libVLC-Umgebung an.**

## Externe Systemkomponenten

### VLC / libVLC
- Zweck: optionale eingebettete Vorschau- und Wiedergabe-Engine insbesondere im Reiter **„Schnitt & Kapitel“**
- Lizenz: libVLC und weite Teile der libVLC-Module stehen nach VideoLAN unter LGPL 2.1 oder später
- Hinweis: **VLC wird nach der vorgesehenen Veröffentlichungsform nicht mit Bleepling ausgeliefert, sondern getrennt installiert und als externe Systemkomponente genutzt.**

### FFmpeg
- Zweck: Audio-/Video-Verarbeitung, Rendern, Export sowie Bildung von Arbeitsvideos und Clips
- Lizenz: je nach Build und Konfiguration, typischerweise LGPL 2.1+ oder GPL
- Hinweis: **FFmpeg ist nicht Bestandteil dieses Projekts und wird nicht mit Bleepling ausgeliefert.**

Bleepling kann FFmpeg prüfen, seine Verfügbarkeit melden und bei der Einrichtung unterstützen. Die Installation von FFmpeg erfolgt jedoch getrennt vom Projekt und in Verantwortung der Nutzerin oder des Nutzers.

### NVIDIA CUDA / cuDNN
- Zweck: optionale GPU-Beschleunigung für bestimmte Transkriptions- oder Laufzeitumgebungen
- Lizenz: proprietäre Lizenzen der jeweiligen Hersteller beziehungsweise Anbieter
- Hinweis: **CUDA- und cuDNN-Komponenten sind nicht Bestandteil dieses Projekts und werden nicht mit Bleepling ausgeliefert.**

Bleepling kann das Vorhandensein bestimmter CUDA- oder cuDNN-Dateien und -Pfade prüfen. Daraus folgt jedoch nicht, dass diese Komponenten Teil der Open-Source-Distribution von Bleepling sind.

## Modelle und transkriptionsbezogene Komponenten

Je nach Konfiguration können zusätzlich Modellgewichte oder weitere transkriptionsbezogene Ressourcen verwendet werden. Für deren Nutzung, Lizenzbedingungen und zulässige Weitergabe sind die jeweils einschlägigen Vorgaben der betreffenden Projekte maßgeblich.

Diese Ressourcen sind gesondert zu betrachten und nicht automatisch Teil dieses Repositorys.

## Keine Mitlieferung bestimmter Drittkomponenten

Zur Klarstellung:

Folgende Komponenten werden von Bleepling nach der derzeit vorgesehenen Veröffentlichungsform **nicht mitgeliefert**, sondern müssen bei Bedarf separat installiert werden:

- VLC / libVLC
- FFmpeg
- NVIDIA CUDA
- NVIDIA cuDNN
- sonstige systemnahe GPU- oder Laufzeitkomponenten

Bleepling bietet insoweit nur Unterstützung bei Prüfung, Diagnose und Einrichtung.

## Maßgeblichkeit der Original-Lizenzen

Für alle genannten Drittanbieter-Komponenten gelten die jeweiligen Original-Lizenztexte und Projektangaben.

Wer Bleepling weiterverbreitet, verändert oder in eigene Umgebungen integriert, sollte zusätzlich prüfen, ob weitere Drittkomponenten verwendet werden und ob diese Übersicht aktualisiert werden muss.
