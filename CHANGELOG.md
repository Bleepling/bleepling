# Changelog

Alle nennenswerten Änderungen an **Bleepling** sollen in dieser Datei dokumentiert werden.

Die Struktur orientiert sich an einer einfachen, für Open-Source-Projekte gut lesbaren Versionshistorie.

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

## [Unreleased]

### Geplant
- weitere Bereinigung und Vereinheitlichung der öffentlichen Repository-Struktur
- mögliche Ergänzung technischer Entwicklerdokumentation
- weitere Tests und Verfeinerungen von Import-, Prüf- und Exportabläufen
