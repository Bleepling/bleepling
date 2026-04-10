# Changelog

Alle nennenswerten Änderungen an **Bleepling** sollen in dieser Datei dokumentiert werden.

Die Struktur orientiert sich an einer einfachen, für Open-Source-Projekte gut lesbaren Versionshistorie.

## [1.2.0] - 2026-04-11

### Hinzugefügt
- neuer Reiter **„Prüfen & Entscheiden“** als zentrale Arbeitsoberfläche für den gesamten Prüf- und Entscheidungsworkflow
- durchgehende Verbindung von technischer Vorbereitung, Namenslisten, Kandidatenprüfung, Audio-Vorschau, Feinjustierung und Times-Datei-Ableitung in einem Reiter
- nummerierte Trefferliste zur besseren Orientierung bei größeren Treffermengen
- direkte Audio-Prüfvorschau mit Bedienlogik für **Prüf**, **Zum Treffer**, **Play**, **Pause**, **Stopp** und **Nächster**
- globale **Bleep-Parameter** im Reiter **„Prüfen & Entscheiden“** mit Hilfe-Funktion
- Buttons zum gezielten Leeren von **Blocklist** und **Allowlist**
- direkte Übernahme markierter Treffer in **Blocklist** und **Allowlist** aus dem Prüfworkflow heraus
- Intervall-basierte **Times-Datei** aus dem Prüfergebnis statt bloßer Punktzeiten
- aktualisierte Benutzerdokumentation für den zusammengeführten Prüfworkflow
- erweiterte technische Prüfung optionaler **VLC/libVLC**-Komponenten im Reiter **„Einstellungen / Logs“**

### Geändert
- die bisherige zweistufige Logik aus **„Bleeping“** und **„Treffer prüfen“** wurde funktional in den neuen Reiter **„Prüfen & Entscheiden“** überführt
- die Reiter **„Bleeping“** und **„Treffer prüfen“** wurden aus der sichtbaren Oberfläche entfernt
- der Prüfworkflow ist jetzt so angelegt, dass globale Bleep-Parameter und individuelle Trefferkorrekturen gemeinsam den maßgeblichen Prüfstand bilden
- **Beginn** und **Ende** von Treffern werden im Prüfworkflow als echte Bleepspannen behandelt und nicht mehr nur als Einzelzeitpunkte verstanden
- **FFmpeg** verarbeitet Intervall-Times-Dateien direkt; ältere Punkt-Times-Dateien bleiben aus Gründen der Rückwärtskompatibilität lesbar
- die aktive Bleep-Steuerung im Reiter **„Video & Audio / FFmpeg“** wurde zugunsten des führenden Prüfreiters entschärft
- die Tastatur-Mehrfachauswahl in der Trefferliste wurde an das übliche Windows-Verhalten angenähert, einschließlich **Strg+A** sowie stabiler **Shift+Pfeil**-Markierung
- Blocklist- und Allowlist-Bearbeitung im Prüfworkflow wurde projektbezogen stabilisiert
- die Medienauswahl für die Audio-Prüfung bevorzugt jetzt die projektinterne WAV-/Transkriptionsseite gegenüber bereits gerenderten Ausgabedateien
- das Startfenster wurde in der Standardgröße angepasst
- die Benutzerdokumentation wurde auf den Kandidatenstand **1.2.0** fortgeschrieben

### Übernommen aus dem internen Entwicklungsstand zwischen 1.1.0 und 1.2.0
- Audio-Feinprüfung mit sichtbaren Spalten **Beginn** und **Ende** pro Treffer
- kurze Audio-Prüfclips statt ausschließlicher Nutzung einer groben Vorschauentscheidung
- Millisekunden-Feintuning für **Bleep-Beginn** und **Bleep-Ende**
- Filterlogik für offene bzw. prüfbedürftige Treffer
- Statusarbeit für Einzel- und Mehrfachauswahl im Trefferworkflow
- technische Vorbereitung optionaler VLC-/libVLC-Prüfungen im Reiter **„Einstellungen / Logs“**
- Ergänzungen an `requirements.txt` und `THIRD_PARTY_NOTICES.md` für den erweiterten technischen Stand

### Behoben
- Asynchronitäten zwischen Prüfvorschau und finalem Render, die dadurch entstanden waren, dass Vorschau und Export nicht denselben operativen Datenstand verwendeten
- fehlerhafte oder unvollständige Übernahme von Mehrfachmarkierungen in der Trefferliste
- Probleme bei der Tastaturauswahl mit **Shift + Pfeil nach oben/unten**
- Alias-Konflikte in der älteren Audio-Vorschau-Logik
- Inkonsistenzen bei der Auswahl geeigneter Prüfmedien im Vergleich zwischen Video-, WAV- und bereits gerenderten Ausgabedateien
- Fälle, in denen globale Bleep-Parameter zwar in der Vorschau, aber noch nicht konsistent in Trefferliste, Times-Datei und Renderpfad ankamen

### Hinweise
- **1.2.0** ist die erste veröffentlichte GitHub-Fassung, in der der neue Reiter **„Prüfen & Entscheiden“** den früheren sichtbaren Doppelworkflow aus **„Bleeping“** und **„Treffer prüfen“** ersetzt
- Für die operative Prüfung und Ableitung der Times-Datei ist nun der Reiter **„Prüfen & Entscheiden“** maßgeblich
- Eine menschliche Endkontrolle anonymisierter Medien bleibt weiterhin erforderlich

## [1.0.0] - 2026-04-06

### Hinzugefügt
- erste veröffentlichungsfähige Open-Source-Fassung von Bleepling
- Projektstruktur für lokale, projektbezogene Verarbeitung von Audio- und Videodateien
- Reiter **Projekt** zum Anlegen und Laden von Bleepling-Projekten
- Reiter **Medien** zum Import von Video- und WAV-Dateien
- Reiter **Bleeping** für Transkriptionsvorbereitung, Kandidatenprüfung, Blocklist/Allowlist und Times-Datei-Erzeugung
- Reiter **Video & Audio / FFmpeg** für den finalen Export gebleepter Audio- und Videodateien
- Reiter **Gezielte Nachbearbeitung** für zusätzliche Einzel-Bleeps sowie Vor- und Nachspannbilder
- Reiter **Einstellungen / Logs** zur Umgebungsprüfung, Diagnose und Unterstützung bei Installationsschritten
- Benutzerdokumentation für Anwenderinnen und Anwender
- Open-Source-Begleitdokumente wie README, LICENSE, CONTRIBUTING, SECURITY, CODE_OF_CONDUCT und THIRD_PARTY_NOTICES

### Unterstützt
- lokale Verarbeitung ohne mitgelieferte Cloud-Abhängigkeit
- FFmpeg als extern installierte Systemkomponente
- Import von Teilnehmerlisten aus TXT, CSV, XLSX, DOCX und PDF
- Import und Verarbeitung typischer Video- und Audioformate
- optional unterstützte GPU-bezogene Umgebungsprüfung für CUDA/cuDNN-Setups

### Hinweise
- FFmpeg ist nicht Bestandteil der Distribution und muss separat installiert werden
- optionale GPU-Komponenten wie CUDA oder cuDNN sind nicht Bestandteil der Distribution
- eine menschliche Endkontrolle anonymisierter Medien bleibt erforderlich
