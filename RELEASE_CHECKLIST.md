# Release Checklist

Diese Checkliste dient dazu, einen öffentlichen Release von **Bleepling** vor der Veröffentlichung systematisch zu prüfen.

## 1. Lizenz und Grunddokumente

- [ ] `LICENSE` ist vorhanden und enthält die gewünschte Lizenz
- [ ] `README.md` ist vorhanden und inhaltlich aktuell
- [ ] `THIRD_PARTY_NOTICES.md` ist vorhanden
- [ ] `CONTRIBUTING.md` ist vorhanden
- [ ] `SECURITY.md` ist vorhanden
- [ ] `CODE_OF_CONDUCT.md` ist vorhanden
- [ ] `CHANGELOG.md` ist vorhanden

## 2. Repository-Struktur

- [ ] Projektwurzel ist sauber und nachvollziehbar aufgebaut
- [ ] keine unnötigen Testreste im Hauptverzeichnis
- [ ] keine lokalen Hilfsdateien oder privaten Notizen im Release
- [ ] Verzeichnisstruktur für `src`, Dokumentation und Hilfsdateien ist konsistent
- [ ] Startdateien und Startwege sind dokumentiert

## 3. Aufräumen vor Veröffentlichung

- [ ] `__pycache__`-Ordner entfernt
- [ ] `*.pyc`-Dateien entfernt
- [ ] `*.old`-Dateien entfernt oder bewusst ausgelagert
- [ ] veraltete Legacy-Dateien entfernt oder klar als Archiv gekennzeichnet
- [ ] keine versehentlich mitgelieferten temporären Dateien
- [ ] keine lokalen Log-Dateien im öffentlichen Paket
- [ ] keine unbeabsichtigt mitgelieferten Medien-, Test- oder Beispieldateien mit sensiblen Inhalten

## 4. Abhängigkeiten und externe Komponenten

- [ ] `requirements.txt` ist aktuell und plausibel
- [ ] nur tatsächlich benötigte Python-Pakete sind enthalten
- [ ] FFmpeg ist **nicht** im Paket enthalten
- [ ] README weist klar darauf hin, dass FFmpeg separat installiert werden muss
- [ ] optionale CUDA-/cuDNN-Komponenten sind **nicht** im Paket enthalten
- [ ] Dokumentation trennt sauber zwischen mitgelieferter Software und externen Systemkomponenten

## 5. Rechtliche und inhaltliche Prüfung

- [ ] nur Dateien im Paket, an denen die erforderlichen Rechte bestehen
- [ ] keine fremden Texte, Grafiken oder Codebestandteile mit unklarer Lizenzlage
- [ ] Logos und grafische Elemente bewusst geprüft
- [ ] Kontaktdaten im Projekt bewusst gewählt
- [ ] Formulierungen im README sind sachlich und nicht irreführend
- [ ] Hinweis auf notwendige menschliche Endkontrolle ist enthalten

## 6. Technische Prüfung

- [ ] Anwendung startet auf dem vorgesehenen Hauptsystem
- [ ] Start über `start_bleepling.bat` funktioniert
- [ ] alternativer Python-Startweg funktioniert
- [ ] Reiter `Einstellungen / Logs` arbeitet nachvollziehbar
- [ ] zentrale Projektfunktionen einmal testweise durchlaufen
- [ ] typischer Standardworkflow ist praktisch funktionsfähig
- [ ] keine offensichtlichen Platzhalter oder veralteten Texte in Oberfläche und Doku

## 7. Dokumentation

- [ ] Benutzerdokumentation ist beigefügt oder verlinkt
- [ ] README beschreibt Installation und Start korrekt
- [ ] typische Arbeitsabläufe sind nachvollziehbar beschrieben
- [ ] Einschränkungen und Grenzen des Projekts sind dokumentiert
- [ ] Third-Party-Hinweise sind mit dem Projektstand konsistent

## 8. Vor dem finalen ZIP

- [ ] finalen Projektordner noch einmal vollständig durchsehen
- [ ] nur die tatsächlich zu veröffentlichenden Dateien einpacken
- [ ] ZIP-Datei sinnvoll und eindeutig benennen
- [ ] ZIP-Datei testweise öffnen und Struktur kontrollieren
- [ ] finalen Stand noch einmal gegen diese Checkliste halten

## 9. Vor der Veröffentlichung auf Plattformen

- [ ] Repository-Name endgültig festgelegt
- [ ] Kurzbeschreibung des Projekts vorbereitet
- [ ] Lizenz auf der Plattform korrekt gesetzt
- [ ] erste Release-Notiz vorbereitet
- [ ] Entscheidung über GitHub, Codeberg oder beides getroffen
- [ ] gegebenenfalls Topics/Schlagwörter vorbereitet

## Notiz

Diese Checkliste ersetzt keine rechtliche Einzelberatung, hilft aber dabei, die häufigsten praktischen und organisatorischen Fehler vor einer Open-Source-Veröffentlichung zu vermeiden.
