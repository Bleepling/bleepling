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
- [ ] neuer Reiter `Schnitt & Kapitel` ist in Code, Doku und Release-Unterlagen konsistent berücksichtigt
- [ ] Reiter `Titelkarten` ist weiterhin in Code, Doku und Release-Unterlagen konsistent berücksichtigt
- [ ] zweite Dachzeile sowie die erweiterten Text- und Vorschaufunktionen im Reiter `Titelkarten` sind in Code, Doku und Release-Unterlagen konsistent berücksichtigt
- [ ] Reiter `Einstellungen / Logs` ist in Beschriftung, Hilfe und sichtbaren Einrichtungsbefehlen konsistent dokumentiert

## 3. Aufräumen vor Veröffentlichung

- [ ] `__pycache__`-Ordner entfernt
- [ ] `*.pyc`-Dateien entfernt
- [ ] `*.old`-Dateien entfernt oder bewusst ausgelagert
- [ ] veraltete Legacy-Dateien entfernt oder klar als Archiv gekennzeichnet
- [ ] keine versehentlich mitgelieferten temporären Dateien
- [ ] keine lokalen Log-Dateien im öffentlichen Paket
- [ ] keine unbeabsichtigt mitgelieferten Medien-, Test- oder Beispieldateien mit sensiblen Inhalten
- [ ] keine zur Laufzeit erzeugten Projektdateien wie `99_config/titlecards_state.json`, Arbeitsvideos oder Inhalte aus `04_output/titlecards` und `01_input/video` im Release

## 4. Abhängigkeiten und externe Komponenten

- [ ] `requirements.txt` ist aktuell und plausibel
- [ ] nur tatsächlich benötigte Python-Pakete sind enthalten
- [ ] FFmpeg ist **nicht** im Paket enthalten
- [ ] README weist klar darauf hin, dass FFmpeg separat installiert werden muss
- [ ] optionale VLC-/libVLC-Komponenten sind **nicht** im Paket enthalten
- [ ] optionale CUDA-/cuDNN-Komponenten sind **nicht** im Paket enthalten
- [ ] Dokumentation trennt sauber zwischen mitgelieferter Software und externen Systemkomponenten
- [ ] es werden keine Font-Dateien mitgeliefert, wenn nur lokale Systemschriftarten verwendet werden

## 5. Rechtliche und inhaltliche Prüfung

- [ ] nur Dateien im Paket, an denen die erforderlichen Rechte bestehen
- [ ] keine fremden Texte, Grafiken oder Codebestandteile mit unklarer Lizenzlage
- [ ] Logos und grafische Elemente bewusst geprüft
- [ ] Kontaktdaten im Projekt bewusst gewählt
- [ ] Formulierungen im README sind sachlich und nicht irreführend
- [ ] Hinweis auf notwendige menschliche Endkontrolle ist enthalten
- [ ] Hinweis zur eigenverantwortlichen Prüfung verwendeter Systemschriftarten ist dort enthalten, wo der Titelkarten-Reiter beschrieben wird
- [ ] Hinweis auf die optionale VLC-/libVLC-Umgebung für `Schnitt & Kapitel` ist dort enthalten, wo die Funktion beschrieben wird

## 6. Technische Prüfung

- [ ] Anwendung startet auf dem vorgesehenen Hauptsystem
- [ ] Start über `start_bleepling.bat` funktioniert
- [ ] alternativer Python-Startweg funktioniert
- [ ] Reiter `Einstellungen / Logs` arbeitet nachvollziehbar
- [ ] Reiter `Schnitt & Kapitel` startet und arbeitet mit dem vorgesehenen Grundworkflow nachvollziehbar
- [ ] Arbeitsvideo-Erzeugung funktioniert
- [ ] vorhandene Arbeitsvideos lassen sich auswählen oder wiedererkennen
- [ ] Clip-Erzeugung aus dem Schnittfenster funktioniert
- [ ] Reiter `Titelkarten` startet und speichert ohne Fehlermeldung
- [ ] Dachzeile, zweite Dachzeile und mehrzeiliger Titel werden in Vorschau und PNG-Export konsistent dargestellt
- [ ] bestehende ältere Projekte lassen sich trotz neuer Titelkarten- und Schnitt-Struktur laden
- [ ] Export nach `04_output/titlecards` funktioniert
- [ ] freier PNG-Export funktioniert
- [ ] Titelkarten mit leerem Startzustand, mit Hintergrundbild und mit Logos testweise durchlaufen
- [ ] typischer Standardworkflow ist praktisch funktionsfähig
- [ ] keine offensichtlichen Platzhalter oder veralteten Texte in Oberfläche und Doku

## 7. Dokumentation

- [ ] Benutzerdokumentation ist beigefügt oder verlinkt
- [ ] README beschreibt Installation und Start korrekt
- [ ] typische Arbeitsabläufe sind nachvollziehbar beschrieben
- [ ] Einschränkungen und Grenzen des Projekts sind dokumentiert
- [ ] Third-Party-Hinweise sind mit dem Projektstand konsistent
- [ ] neue Funktion `Schnitt & Kapitel` ist in README, Changelog und Benutzerdokumentation konsistent beschrieben
- [ ] Funktion `Titelkarten` ist weiterhin in README, Changelog und Benutzerdokumentation konsistent beschrieben
- [ ] zweite Dachzeile / Untertitel und die verfeinerte Titelkarten-Vorschau sind in README, Changelog und Benutzerdokumentation konsistent beschrieben
- [ ] Bereich `Einstellungen / Logs` ist mit seiner aktuellen Struktur in README, Changelog und Benutzerdokumentation konsistent beschrieben

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
- [ ] Release-Notiz für 1.4.1 erwähnt die flexiblere Teilnehmerlisten-Übernahme im Reiter `Prüfen & Entscheiden`
- [ ] Release-Notiz für 1.4.1 erwähnt die robustere PDF-Verarbeitung von Teilnehmerverzeichnissen
- [ ] Release-Notiz erwähnt weiterhin den Reiter `Schnitt & Kapitel`, soweit dies für die Gesamteinordnung des aktuellen Funktionsstands sinnvoll ist

## Notiz

Diese Checkliste ersetzt keine rechtliche Einzelberatung, hilft aber dabei, die häufigsten praktischen und organisatorischen Fehler vor einer Open-Source-Veröffentlichung zu vermeiden.
