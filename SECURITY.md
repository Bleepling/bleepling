# Security Policy

## Sicherheitsrelevante Hinweise zu Bleepling

Bleepling ist ein lokal laufendes Werkzeug zur kontrollierten Anonymisierung von Audio- und Videodateien. Obwohl das Projekt keinen klassischen Netzwerkdienst bereitstellt, können sicherheitsrelevante Probleme trotzdem auftreten, etwa durch fehlerhafte Dateiverarbeitung, problematische externe Aufrufe oder unbeabsichtigte Auswirkungen bestimmter Installations- und Systemfunktionen.

## Was als Sicherheitsproblem gemeldet werden sollte

Bitte melde insbesondere:

- Schwachstellen, durch die unbeabsichtigt Dateien gelesen, überschrieben oder gelöscht werden können
- Probleme bei externen Aufrufen, insbesondere im Zusammenhang mit FFmpeg oder systemnahen Befehlen
- Risiken durch Pfadmanipulation, unsichere Dateinamen oder problematische temporäre Dateien
- Sicherheitsprobleme bei Importfunktionen für Medien, PDF-, DOCX-, XLSX- oder sonstige Dateien
- Fehler, die zu unbeabsichtigter Offenlegung personenbezogener Inhalte führen können
- Risiken im Zusammenhang mit optionalen Installations- oder Diagnosefunktionen
- Probleme, durch die lokale Systembefehle in unerwarteter Weise ausgelöst werden könnten

## Was nicht als Sicherheitsproblem gilt

Nicht jeder Fehler ist automatisch ein Sicherheitsproblem. Normale Funktionsfehler, Abstürze ohne Sicherheitsbezug, Darstellungsprobleme oder reine Bedienungsfehler können weiterhin als gewöhnliche Bugs gemeldet werden.

## Bitte keine öffentlichen Sicherheitsmeldungen als Erstmeldung

Wenn du glaubst, eine echte Sicherheitslücke gefunden zu haben, melde sie bitte **nicht zuerst öffentlich** über ein Issue oder in Diskussionen, sondern zunächst direkt per E-Mail.

## Kontakt für Sicherheitsmeldungen

**Andreas Ritz**  
E-Mail: bleepling@email.de

Bitte beschreibe dabei möglichst genau:

- die betroffene Version oder den betroffenen Projektstand
- die betroffene Datei oder Funktion
- die Schritte zur Reproduktion
- die möglichen Auswirkungen
- gegebenenfalls Screenshots, Logauszüge oder Beispielkonstellationen

Bitte sende dabei keine vertraulichen Originaldateien, wenn diese personenbezogene oder sonst sensible Inhalte enthalten.

## Umgang mit Meldungen

Sicherheitsmeldungen sollen nach Möglichkeit zeitnah geprüft und eingeordnet werden. Je nach Schwere und Reproduzierbarkeit kann es erforderlich sein, Rückfragen zu stellen oder zunächst eine interne Korrektur vorzubereiten, bevor Details öffentlich dokumentiert werden.

## Unterstützte Versionen

Aktiv unterstützt wird im Zweifel nur der jeweils aktuelle veröffentlichte Projektstand. Für das anstehende Release ist dies der Stand **1.5.0**.

Ältere Zwischenstände, experimentelle Branches oder lokale Testfassungen können von dieser Unterstützung abweichen.

## Grundsatz zur sicheren Nutzung

Bleepling verarbeitet potenziell sensible Medieninhalte. Deshalb wird empfohlen:

- nur mit lokal kontrollierten Dateien zu arbeiten
- Ergebnisse vor Weitergabe immer zusätzlich manuell zu prüfen
- externe Komponenten wie FFmpeg oder optionale GPU-Laufzeitumgebungen nur aus vertrauenswürdigen Quellen zu installieren
- Logs und Testdateien darauf zu prüfen, ob sie personenbezogene Informationen enthalten

## Keine Gewähr für vollständige Anonymisierung

Bleepling kann bei der Anonymisierung helfen, ersetzt aber keine fachliche Endkontrolle. Auch aus Sicherheits- und Datenschutzsicht bleibt eine menschliche Prüfung des Endergebnisses erforderlich.
