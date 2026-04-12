# Contributing to Bleepling

Vielen Dank für dein Interesse an **Bleepling**.

Beiträge, Fehlermeldungen, Verbesserungsvorschläge und Tests sind willkommen. Ziel ist es, Bleepling als praktisch nutzbares Open-Source-Werkzeug für die kontrollierte Anonymisierung von Audio- und Videodateien weiterzuentwickeln.

## Grundgedanke

Bleepling ist kein beliebiges Medienprojekt, sondern ein Werkzeug mit datenschutzbezogenem Anwendungsbezug. Beiträge sollten deshalb nicht nur technisch funktionieren, sondern auch fachlich nachvollziehbar, vorsichtig und möglichst robust sein.

Besonders wichtig sind:

- nachvollziehbare Arbeitsabläufe
- klare und verständliche Benutzerführung
- lokale und kontrollierbare Verarbeitung
- transparente Fehlermeldungen
- zurückhaltende, ehrliche Dokumentation ohne überzogene Versprechen

## Aktueller Workflow-Stand

Der sichtbare Hauptworkflow läuft im Projektstand **1.2.1** vor allem über den Reiter **„Prüfen & Entscheiden“** für den eigentlichen Anonymisierungsprozess sowie ergänzend über den Reiter **„Titelkarten“** für statische PNG-Karten, die im weiteren Workflow insbesondere als Vor- oder Nachspannbilder verwendet werden können.

Beiträge an Bedienlogik, Statusführung, Times-Ableitung, Renderübergabe und Titelkarten-Export sollten diesen Workflow respektieren.

## Arten von Beiträgen

Willkommen sind insbesondere:

- Bug-Reports
- Verbesserungsvorschläge für Bedienoberfläche und Workflow
- Korrekturen an Dokumentation und Hinweisen
- technische Verbesserungen an Stabilität, Import, Export und Diagnose
- Tests mit unterschiedlichen Medienformaten und Anwendungsfällen
- Vorschläge zur besseren Open-Source-Dokumentation

## Vor dem Beitragen

Bitte prüfe nach Möglichkeit vorab:

- ob das Problem bereits gemeldet wurde
- ob sich das Verhalten mit dem aktuellen Projektstand reproduzieren lässt
- ob der Fehler mit konkreten Beispieldateien, Screenshots oder Log-Hinweisen beschrieben werden kann

## Bug-Reports

Ein guter Bug-Report sollte möglichst enthalten:

- kurze Problembeschreibung
- erwartetes Verhalten
- tatsächliches Verhalten
- Schritte zur Reproduktion
- verwendetes Betriebssystem
- Python-Version
- installierte oder fehlende Komponenten wie FFmpeg oder GPU-Unterstützung
- relevante Fehlermeldungen aus Logs oder Oberfläche

Wenn personenbezogene oder vertrauliche Inhalte betroffen sind, bitte keine sensiblen Originaldateien hochladen.

## Vorschläge für Änderungen

Bei größeren Änderungen ist es sinnvoll, die beabsichtigte Anpassung zunächst kurz zu beschreiben, bevor umfangreicher Code geschrieben wird.

Das gilt besonders für Änderungen an:

- Projektstruktur
- Bleep-Logik
- Prüf- und Entscheidungsworkflow
- Exportlogik
- Titelkarten-Logik und PNG-Erzeugung
- Einstellungen und Diagnoseroutinen
- Dateiformaten und Importpfaden

## Stil und Grundsätze für Codebeiträge

Bitte nach Möglichkeit:

- bestehenden Projektstil respektieren
- Änderungen möglichst klein und nachvollziehbar halten
- keine unnötigen Großumbauten mit vielen Nebeneffekten einreichen
- Fehlermeldungen benutzerverständlich formulieren
- Dateipfade, externe Abhängigkeiten und Systemaufrufe vorsichtig behandeln
- neue externe Abhängigkeiten nur mit guter Begründung einführen

## Dokumentation

Wenn sich durch eine Änderung sichtbares Verhalten der Anwendung ändert, sollte die Dokumentation nach Möglichkeit mit angepasst werden.

Das betrifft insbesondere:

- README
- Benutzerdokumentation
- Installationshinweise
- Changelog
- Third-Party-Hinweise
- Einstellungen / Logs
- neue oder geänderte Arbeitsabläufe

## Rechtliches und Lizenzen

Mit einem Beitrag erklärst du dich damit einverstanden, dass dein Beitrag unter der für das Projekt geltenden Lizenz weiterverwendet und veröffentlicht werden darf.

Bitte reiche nur Beiträge ein, an denen du die erforderlichen Rechte hast.

Keine fremden Codebestandteile, Grafiken, Texte, Schriftdateien oder sonstigen Inhalte einreichen, wenn deren Lizenzlage unklar oder mit dem Projekt unvereinbar ist.

## Externe Komponenten

Bleepling nutzt oder prüft teilweise externe Komponenten wie FFmpeg oder optionale GPU-bezogene Laufzeitumgebungen.

Solche Komponenten sind nicht automatisch Teil des Repositorys. Beiträge sollten diese Trennung respektieren und keine Drittsoftware ungeprüft in das Projekt einführen.

Für den Reiter **„Titelkarten“** gilt zusätzlich:

- es sollen grundsätzlich **keine Font-Dateien ins Repository aufgenommen** werden, wenn die Funktion mit lokal vorhandenen Systemschriftarten arbeitet
- bei Änderungen an der Titelkarten-Funktion ist zu beachten, dass projektbezogene Laufzeitdateien wie `99_config/titlecards_state.json` und exportierte PNG-Dateien nicht in das Repository gehören

## Qualität vor Tempo

Lieber eine kleine, saubere und gut erklärte Verbesserung als ein großer, riskanter Schnellschuss.

Gerade bei einem Werkzeug für Anonymisierung und datenschutzbezogene Prüfprozesse ist Verlässlichkeit wichtiger als spektakuläre Komplexität.

## Kontakt

Für Rückfragen oder Vorschläge:

**Andreas Ritz**  
E-Mail: bleepling@email.de