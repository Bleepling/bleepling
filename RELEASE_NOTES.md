# Release-Vorlage 1.4.1

Diese Datei dient als vorbereitete Arbeitsgrundlage für die manuelle Veröffentlichung von **Bleepling 1.4.1**.

## Empfohlener Tag

`v1.4.1`

## Empfohlener Release-Titel

`Bleepling 1.4.1`

## Empfohlene Kurzbeschreibung für GitHub

Kleines Patch-Release mit robusterem Import von PDF-Teilnehmerverzeichnissen, flexiblerer Teilnehmerlisten-Übernahme und verfeinertem Prüf-Reiter.

## Vorschlag für den eigentlichen Release-Text

### Überblick

Version **1.4.1** ist ein gezieltes Patch-Release auf Basis von **1.4.0**. Im Mittelpunkt stehen die nachträgliche Stabilisierung des Teilnehmerlisten-Imports, eine flexiblere Übernahme von Vor- und Nachnamen im Reiter **„Prüfen & Entscheiden“** sowie kleine sichtbare Verbesserungen an der Listenpflege.

### Wichtige sichtbare Änderungen

- Teilnehmerlisten können im Reiter **„Prüfen & Entscheiden“** jetzt wahlweise als **Nachnamen**, **Vornamen** oder in kombinierter Form übernommen werden
- ein zusätzlicher Button **„Akt.“** baut die zuletzt importierte Teilnehmerliste mit den aktuell gesetzten Optionen gezielt neu auf
- neben **Blocklist** und **Allowlist** werden jetzt kleine, live aktualisierte Summenzähler angezeigt
- die sichtbare Bedienung des kombinierten Prüf-Reiters und die zugrunde liegende Importlogik arbeiten wieder konsistent zusammen

### Technische Verbesserungen

- PDF-Teilnehmerverzeichnisse mit tabellarischer Struktur werden robuster ausgelesen
- verrutschte Spalten in PDF-Textausgaben führen seltener zu unvollständigen Namenslisten
- kurze, echte Nachnamen aus Teilnehmerverzeichnissen werden im PDF-Import nicht mehr unnötig verworfen
- importierte Teilnehmerlisten lassen sich neu anwenden, ohne manuelle Blocklist-Einträge zu verlieren

### Hinweise

- Der fachlich maßgebliche sichtbare Prüfworkflow bleibt weiterhin der Reiter **„Prüfen & Entscheiden“**
- Externe Komponenten wie **FFmpeg**, **VLC/libVLC** sowie optionale **CUDA/cuDNN**-Umgebungen bleiben weiterhin getrennt vom Projekt zu installieren
- Die aktualisierte Benutzerdokumentation kann wie bisher zusätzlich als separate PDF-Fassung für Anwenderinnen und Anwender bereitgestellt werden

## Empfohlene zu prüfende Release-Artefakte

- Quellcode des aktuellen Projektstands
- aktualisierte Benutzerdokumentation in der vorgesehenen Veröffentlichungsform

## Empfohlene GitHub-Felder

### Release name

`Bleepling 1.4.1`

### Tag version

`v1.4.1`

### Target

aktueller Hauptstand, von dem die Veröffentlichung erfolgen soll

### Description

Den vorbereiteten Release-Text aus dieser Datei verwenden und bei Bedarf leicht kürzen.

### Assets

Sinnvoll können insbesondere sein:

- Quellcode-Archiv von GitHub
- Benutzerhandbuch als PDF-Fassung

## Empfohlene letzte Prüfung vor Veröffentlichung

- Versionsstand in README, Changelog und Handbuch noch einmal kurz gegenlesen
- prüfen, dass Teilnehmerlisten im Reiter **„Prüfen & Entscheiden“** für Nachnamen, Vornamen und die kombinierte Auswahl nachvollziehbar funktionieren
- keine temporären Arbeitsordner oder Archivzwischenstände mitveröffentlichen
- einmal kurz den sichtbaren Reiterbestand gegen die Release-Beschreibung halten
