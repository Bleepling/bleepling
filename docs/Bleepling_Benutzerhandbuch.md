# Bleepling

![Bleepling-Icon](../assets/vogel1_appicon_512.png)

> Dieses Benutzerhandbuch wird direkt im Projekt als Markdown-Datei fortgeschrieben. Es ist die zentrale Handbuchquelle für Bleepling und kann aus der Anwendung bei Bedarf als HTML exportiert werden.

## Benutzerdokumentation für Anwenderinnen und Anwender

## Inhaltsverzeichnis

- [1. Sinn und Zweck der App](#1.-sinn-und-zweck-der-app)
- [2. Betriebsvoraussetzungen](#2.-betriebsvoraussetzungen)
- [3. Schnellstart](#3.-schnellstart)
- [4. Projektstruktur und Dateitypen](#4.-projektstruktur-und-dateitypen)
- [5. Reiter im Überblick](#5.-reiter-im-uberblick)
- [6. Reiter Projekt](#6.-reiter-projekt)
- [7. Reiter Medien](#7.-reiter-medien)
- [8. Reiter Schnitt & Kapitel](#8.-reiter-schnitt-kapitel)
- [9. Reiter Prüfen & Entscheiden](#9.-reiter-pruefen-entscheiden)
- [10. Reiter Video & Audio / FFmpeg](#10.-reiter-video-audio-ffmpeg)
- [11. Reiter Gezielte Nachbearbeitung](#11.-reiter-gezielte-nachbearbeitung)
- [12. Reiter Titelkarten](#12.-reiter-titelkarten)
- [13. Reiter Einstellungen / Logs](#13.-reiter-einstellungen-logs)
- [14. Typische Arbeitsabläufe](#14.-typische-arbeitsablaeufe)
- [15. Häufige Missverständnisse und wichtige Hinweise](#15.-haeufige-missverstaendnisse-und-wichtige-hinweise)
- [16. Häufige Fehler und Lösungen](#16.-haeufige-fehler-und-loesungen)
- [17. Unterstützte Formate und Grenzen](#17.-unterstuetzte-formate-und-grenzen)
- [18. Empfehlungen für den praktischen Einsatz](#18.-empfehlungen-fuer-den-praktischen-einsatz)
- [19. Geänderte Dateien in Version 1.5.3 gegenüber der Vorversion 1.5.2](#19.-geaenderte-dateien-in-version-1.5.3-gegenueber-der-vorversion-1.5.2)
- [20. Geänderte Dateien in Version 1.5.2 gegenüber der Vorversion 1.5.1](#20.-geaenderte-dateien-in-version-1.5.2-gegenueber-der-vorversion-1.5.1)
- [21. Geänderte Dateien in Version 1.5.1 gegenüber der Vorversion 1.5.0](#21.-geaenderte-dateien-in-version-1.5.1-gegenueber-der-vorversion-1.5.0)

Stand: Version 1.5.3 auf Basis des Projektstands „Bleepling 1.5.3“ (28.04.2026)

> Bleepling dient der Anonymisierung von Video- und Audiodateien, in denen Klarnamen genannt werden. Das Ziel ist, datenschutzrechtlich problematische Veröffentlichungen oder Weitergaben von Medien zu vermeiden, indem Namensnennungen gezielt erkannt, geprüft und anschließend gebleept werden.
>
> **Wichtig:** Bleepling ist eine sehr hilfreiche Software, kann aber Namen übersehen. Daher wird zur Vermeidung von Verstößen gegen datenschutzrechtliche Bestimmungen dringend empfohlen, immer noch zusätzlich eine persönliche Endkontrolle vorzunehmen!

# 1. Sinn und Zweck der App
Bleepling ist für Situationen gedacht, in denen Video- oder Audiodateien inhaltlich veröffentlicht, weitergegeben oder archiviert werden sollen, diese dabei aber personenbezogene Namensnennungen enthalten, die für die weitere Verarbeitung oder dauerhafte Speicherung unnötig oder gar unzulässig sind. Die App hilft, solche Medien gezielt zu anonymisieren. Im Mittelpunkt stehen dabei insbesondere Klarnamen in gesprochenem Wort.
Der typische Einsatzfall ist also nicht die kreative Videobearbeitung, sondern ein fachlich kontrollierter und vollständig lokal ablaufender Datenschutz-Workflow: Namen sollen zunächst als mögliche Treffer erkannt, anschließend menschlich geprüft und erst danach automatisiert gebleept werden.
Dabei unterstützt Bleepling mit mehreren Hauptfunktionen:
- Schutz vor problematischen Veröffentlichungen mit erkennbaren Klarnamen durch Ersetzen eines oder mehrere Tonspurabschnitte gegen die Originaltonspur (also nicht nur ein Überblenden) in Audio- oder Videoaufnahmen durch einen “bleep”. (Das Bleepen hat dann auch unseren Bleepling herbeigelockt, der nun freundlich Pate dieser App geworden ist. 😊)
- Unterstützung eines nachvollziehbaren Prüf- und Freigabeprozesses.
- Zusammenstellung mehrerer Quellvideos und manuelle Clip-Erzeugung vor dem eigentlichen Prüfworkflow.
- Gezielte Nachbearbeitung bereits bearbeiteter Medien mit zuvor nicht gesetzten Bleeps, ohne die ursprünglichen Bleeps anzufassen.
- Export in browserkompatible Videoformate insbesondere für Webanwendungen.
- Erstellung neutraler oder individuell gestalteter Titelkarten als PNG-Dateien für Vor- und Nachspann, die mit Bleepling dann auch direkt am Anfang und / oder am Ende eines Videos mit variabler Zeitdauer eingesetzt werden können.

# 2. Betriebsvoraussetzungen
Bleepling benötigt für seine vollständige Funktion mehrere Programme und Python-Bibliotheken. Nicht jeder Baustein wird in jedem Arbeitsgang gebraucht. Einige Komponenten sind jedoch für bestimmte Teilfunktionen zwingend erforderlich.

| Komponente | Wofür benötigt | Zwingend? | Hinweis |
| --- | --- | --- | --- |
| Python 3 | Ausführung der App | Ja | Die App wird in einer Python-Umgebung gestartet. |
| Tkinter | Grafische Oberfläche | Ja | Bei Standard-Python unter Windows meist bereits enthalten. |
| FFmpeg | Audio-/Video-Verarbeitung, Rendern, Export | Ja | Ohne FFmpeg keine finale Medienerzeugung. |
| faster-whisper | Transkription | Für Transkriptions-Workflow | Wird benötigt, wenn aus WAV eine words.json entstehen soll. |
| ctranslate2 | Betrieb von faster-whisper | Für Transkriptions-Workflow | GPU/CPU-Laufzeitkomponente. |
| openpyxl | Import von XLSX-Teilnehmerlisten | Nur für XLSX-Import | Für Teilnehmerlisten aus Excel. |
| python-docx | Import von DOCX-Teilnehmerlisten | Nur für DOCX-Import | Für Teilnehmerlisten aus Word-Dateien. |
| pdfplumber | PDF-Teilnehmerlisten importieren | Nur für PDF-Import | Bevorzugter Weg für strukturierte PDF-Teilnehmerverzeichnisse. |
| pypdf / PyPDF2 | Einfacher PDF-Import | Optional | Zusätzliche PDF-Unterstützung; nicht so verlässlich wie pdfplumber. |
| Pillow | Logos / GUI-Grafiken | Praktisch ja | Für Bilddarstellung in der Oberfläche. |
| NVIDIA CUDA / cuDNN | GPU-Beschleunigung | Optional | Nur nötig, wenn GPU-gestützte Transkription genutzt werden soll. Wenn es Spaß machen soll, aber schon seeehr nützlich.. 😊 |
| VLC Desktop / libVLC | Interne Vorschau im Reiter „Schnitt & Kapitel“ | Für den Schnittdialog empfohlen | Für den bisherigen Standard-Bleeping-Workflow nicht zwingend, für den integrierten Schnittdialog jedoch praktisch erforderlich. |
| python-vlc | Python-Anbindung des Schnittfensters | Für den Schnittdialog empfohlen | Ermöglicht die interne Vorschau und das präzise Markensetzen im Reiter „Schnitt & Kapitel“. |

Wichtig: Nach Einrichtung einer passenden Python-Umgebung kann der Reiter „Einstellungen / Logs“ viel Arbeit ersparen. Dort lassen sich fehlende Komponenten prüfen, Installationsbefehle kopieren und – soweit vorgesehen – direkt in einem CMD-Fenster ausführen.

# 3. Schnellstart
1. Projekt anlegen oder ein bestehendes Projekt laden.
1. Im Reiter „Medien“ das Ausgangsvideo oder die WAV-Datei importieren.
1. Optional im Reiter „Schnitt & Kapitel“ aus einem oder mehreren Quellvideos zunächst ein Arbeitsvideo bilden, im Schnittfenster Marken setzen und daraus einzelne Arbeitsclips erzeugen.
1. Im Reiter „Prüfen & Entscheiden“ im Bereich „Vorbereitung“ aus dem Video eine korrespondierende Audio-WAV-Datei erzeugen, falls noch keine WAV vorliegt.
1. Im selben Reiter aus der WAV-Datei eine words.json-Datei erzeugen.
1. Aus der words.json eine Kandidaten-Datei erzeugen.
1. Optional im Bereich „Namenslisten und Regeln“ Teilnehmerliste, Blocklist und Allowlist pflegen oder ergänzen.
1. Im Bereich „Kandidaten prüfen“ die Auswertung der automatisch erstellten Bleep-Vorschläge starten.
1. Im Feld „Bleep-Parameter“ die globalen Parameter für Frequenz, Lautstärke, Vorlauf und Nachlauf festlegen und mit „Anwenden“ verbindlich übernehmen.
1. In „Trefferliste und Feinprüfung“ die Treffer anhören, den Satz-Kontext nachlesen, bei Bedarf Beginn und Ende feinjustieren und die gewünschten Treffer auf „bleepen“ setzen, alle anderen verwerfen.
1. Den Prüfstand speichern und anschließend eine Times-Datei mit Intervallen der gewünschten Bleeps ableiten.
1. Im Reiter „Video & Audio / FFmpeg“ das gebleepte Medium rendern.
1. Das Endergebnis stichprobenartig anhören bzw. ansehen und eine persönliche Endkontrolle durchführen.

# 4. Projektstruktur und Dateitypen
Beim Anlegen eines Projekts erstellt Bleepling eine feste Ordnerstruktur. Diese Struktur trennt Eingaben, Transkriptionsdaten, Prüfdateien, Zeitschnittlisten und finale Ausgaben.
- 01_input/video – Ausgangsvideos
- 01_input/audio bzw. 02_transcription/wav – Audio-/WAV-Dateien
- 03_processing/04_cutting/working_video – intern erzeugte Arbeitsvideos für den Reiter „Schnitt & Kapitel“
- 02_transcription/json – words.json-Dateien
- 04_output/videos, 04_output/audio und 04_output/titlecards – fertige Ausgabedateien für Videos, reine Audioexporte und Titelkarten
- Für die praktische Arbeit sind insbesondere sieben Dateitypen wichtig: Video- oder Audioquellen, interne Arbeitsvideos, words.json-Dateien, Kandidaten-Dateien, reviewed-Dateien, Times-Dateien mit Intervallen und PNG-Titelkarten.
- 06_presets / 99_config – Konfiguration, Voreinstellungen und gespeicherter Titelkarten-Status

# 5. Reiter im Überblick

| Reiter | Zweck | Typischer Einsatz |
| --- | --- | --- |
| Schnitt & Kapitel | Quellvideos zusammenstellen, Arbeitsvideo bilden, Clips manuell schneiden | Optionaler Vorbau vor dem Prüfworkflow |
| Projekt | Projekt anlegen, laden und verwalten | Startpunkt jeder Arbeit |
| Medien | Video- und Audiodateien ins Projekt bringen | Zu Beginn des Workflows |
| Prüfen & Entscheiden | Vorbereitung, Listenpflege, Trefferprüfung, Audio-Vorschau, Feintuning und Times-Datei | Zentraler Prüf- und Entscheidungsreiter |
| Video & Audio / FFmpeg | Rendern und Exportieren | Finaler Medienexport |
| Gezielte Nachbearbeitung | Zusätzliche Bleeps, Vor-/Nachspannbilder | Korrekturen und Ergänzungen |
| Titelkarten | Erstellen und Exportieren von Titelkarten als PNG | Vorbereitung von Vor- und Nachspannbildern |
| Einstellungen / Logs | Umgebung prüfen, Installieren, Diagnose | Einrichtung und Fehlersuche |

# 6. Reiter Projekt
Der Reiter „Projekt“ ist der Einstiegspunkt in jede Arbeit mit Bleepling. Hier wird entschieden, in welchem Projektordner gearbeitet wird und damit zugleich, auf welche Ordnerstruktur, Eingabedateien, Bearbeitungsstände und Ausgabeverzeichnisse die App zugreift. Ohne ein geladenes Projekt sind die übrigen Reiter zwar sichtbar, praktisch aber noch nicht sinnvoll nutzbar.

## 6.1 Wofür der Reiter gedacht ist
- Anlegen eines neuen Bleepling-Projekts in einem frei wählbaren übergeordneten Zielordner.
- Laden eines bereits vorhandenen Bleepling-Projektordners.
- Schnelle Orientierung darüber, ob überhaupt schon ein Projekt geladen ist und welcher Projektpfad aktuell verwendet wird.
- Sauberer Einstieg in einen neuen Arbeitsgang, ohne Eingabe-, Bearbeitungs- und Ausgabedateien verschiedener Fälle zu vermischen.

## 6.2 Typische Bedienelemente

| Bedienelement | Bedeutung | Praktische Funktion |
| --- | --- | --- |
| Neues Projekt anlegen | Startet die Projektanlage | Erzeugt einen neuen Projektordner mit der von Bleepling erwarteten Standardstruktur. |
| Bestehendes Projekt laden | Öffnet einen vorhandenen Projektordner | Bindet ein bereits angelegtes Bleepling-Projekt wieder in die App ein. |
| Hinweisfeld / Statuszeile im Reiter | Zeigt den aktuellen Stand | Meldet etwa „Noch kein Projekt geladen.“ oder zeigt den aktuell geladenen Projektpfad. |
| Abfrage zum zuletzt geöffneten Projekt | Komfortfunktion beim Laden | Beim Laden kann Bleepling zunächst anbieten, das zuletzt geöffnete Projekt erneut zu öffnen. |

## 6.3 Sinnvolle Reihenfolge der Nutzung
1. Zuerst prüfen, ob bereits ein passendes Projekt existiert.
1. Nur wenn noch kein Projektordner vorhanden ist, ein neues Projekt anlegen.
1. Nach dem Laden kurz kontrollieren, ob der angezeigte Projektpfad wirklich der gewünschte Fall ist.
1. Erst danach in die übrigen Reiter wechseln und mit Medienimport, Prüfen & Entscheiden oder Rendern fortfahren.

## 6.4 Neues Projekt anlegen
Der Button „Neues Projekt anlegen“ dient für den Fall, dass zu einem neuen Medium oder einem neuen Vorgang noch kein Projektordner vorhanden ist. Der Ablauf ist bewusst zweistufig aufgebaut, damit versehentliche Projektanlagen vermieden werden.
- Zuerst wird ein bereits existierender übergeordneter Ordner ausgewählt, in dem das neue Bleepling-Projekt liegen soll.
- Anschließend fragt die App nach dem Projektnamen.
- Aus übergeordnetem Ordner und Projektname wird der konkrete Projektpfad gebildet.
- Existiert zu diesem Namen noch kein Ordner, fragt Bleepling zur Sicherheit nach, ob der neue Projektordner jetzt tatsächlich angelegt werden soll.
- Wird dies bestätigt, erzeugt Bleepling automatisch die komplette Projektstruktur.
Die automatische Projektstruktur ist besonders wichtig, weil Bleepling mit fest erwarteten Unterordnern arbeitet, etwa für Eingabevideos, WAV-Dateien, JSON-Dateien, Kandidatenprüfstände, Times-Dateien, Ausgabemedien, Logs und Konfiguration. Wer außerhalb dieser Struktur arbeitet, riskiert Verwechslungen oder Fehlermeldungen beim Laden.

## 6.5 Bestehendes Projekt laden
„Bestehendes Projekt laden“ ist der normale Weg, wenn an einem bereits angelegten Fall weitergearbeitet werden soll. Praktisch ist diese Funktion besonders dann, wenn ein Video schon importiert, eine WAV-Datei bereits erzeugt oder im Reiter „Prüfen & Entscheiden“ schon erste Prüfstände vorhanden sind.
- Bleepling kann zunächst anbieten, das zuletzt geöffnete Projekt erneut zu laden.
- Wird dieses Angebot nicht genutzt, kann ein Projektordner manuell ausgewählt werden.
- Vor dem eigentlichen Laden prüft die App, ob der gewählte Ordner ein vollständiges Bleepling-Projekt ist.
- Erst wenn die Mindeststruktur vorhanden ist, wird das Projekt geladen und an die übrigen Reiter übergeben.

## 6.6 Was beim Laden intern geprüft wird
Beim Laden eines bestehenden Projekts prüft Bleepling nicht nur, ob der Ordner existiert, sondern auch, ob er die erwartete Projektstruktur enthält. Dazu gehören insbesondere die fachlich wichtigen Unterordner für Input, Transkription, Verarbeitung, Ausgabe, Logs und Konfiguration. Außerdem wird geprüft, ob die Datei 99_config/project.json vorhanden ist. Fehlt diese Struktur, wird der Ordner zu Recht nicht als gültiges Bleepling-Projekt akzeptiert.

## 6.7 Typische Fehlerquellen im Reiter „Projekt“

| Typischer Fehler | Wie man ihn vermeidet oder behebt |
| --- | --- |
| Falschen Ordner geladen | Immer auf den vollständigen Projektpfad achten. Sinnvoll ist ein kurzer Blick auf die Statusanzeige direkt nach dem Laden. |
| Vorhandenen, aber unvollständigen Ordner als Projekt verwenden wollen | Nicht jeder Ordner mit Medien ist schon ein Bleepling-Projekt. Wenn die Struktur oder project.json fehlt, sollte entweder das richtige Projekt gewählt oder ein neues Projekt angelegt werden. |
| Projektanlage im falschen Elternordner | Vor dem Bestätigen kurz prüfen, ob der gewählte übergeordnete Ordner wirklich der gewünschte Speicherort ist. |
| Projektname zu unsauber oder doppelt vergeben | Für Klarheit helfen sprechende, eindeutige Projektnamen. Existiert der Ordner bereits, sollte bewusst entschieden werden, ob geladen oder neu angelegt werden soll. |
| Ohne geladenes Projekt in anderen Reitern weiterarbeiten wollen | Der Reiter „Projekt“ sollte immer zuerst abgeschlossen sein; erst danach sind Medienimport, Bleeping und Rendern sinnvoll. |

## 6.8 Praktische Empfehlungen

## 6.8a Bestehendes Projekt löschen
Seit Version 1.5.1 enthält der Reiter „Projekt“ zusätzlich den Button „Bestehendes Projekt löschen“. Der Button ist bewusst am rechten Rand der Buttonzeile positioniert, damit er nicht versehentlich mit den normalen Aktionen „Neues Projekt anlegen“ oder „Bestehendes Projekt laden“ verwechselt wird.
Beim Löschen wählt man zunächst den zu löschenden Projektordner aus. Bleepling prüft danach ohne automatische Reparatur, ob es sich um ein vollständiges Bleepling-Projekt handelt. Dazu gehören insbesondere die erwarteten Standardordner und die Datei 99_config/project.json. Wenn diese Prüfung fehlschlägt, erscheint eine Meldung und es wird nichts gelöscht.
Ist der Ordner ein vollständiges Projekt, erscheint eine Sicherheitsabfrage mit Vogelbild. Erst wenn diese Abfrage bestätigt wird, wird der gesamte Projektordner entfernt. Das betrifft alle Eingabedateien, Zwischenstände, Ausgaben, Titelkarten, Logs und Projekteinstellungen innerhalb dieses Ordners.
Empfehlung: Die Löschfunktion sollte nur für eindeutig identifizierte Projektordner verwendet werden. Für Tests empfiehlt sich immer eine Kopie eines Projekts. Wenn ein gelöschtes Projekt zuvor als zuletzt geöffnetes Projekt gespeichert war, entfernt Bleepling diesen Verweis aus dem lokalen App-Zustand.
- Pro Medium bzw. Fall ein eigenes Projekt verwenden. Das erleichtert Nachvollziehbarkeit und spätere Korrekturen.
- Bereits bearbeitete Projekte möglichst immer wieder laden, statt für denselben Fall neue Projektordner anzulegen.
- Projektordner nicht manuell „halb“ umbauen. Die feste Struktur ist Teil der Arbeitslogik von Bleepling.
- Vor längeren Bearbeitungsschritten kurz kontrollieren, ob wirklich das richtige Projekt geladen ist – besonders nach einem Neustart der App.

## 6.9 Zusammenfassung
Der Reiter „Projekt“ ist organisatorisch schlicht, aber fachlich grundlegend. Er entscheidet, wo Bleepling arbeitet, welche Dateien zur Verfügung stehen und welcher Bearbeitungsstand in den übrigen Reitern sichtbar wird. Wer hier sauber arbeitet, vermeidet später viele Fehler in Medienimport, Prüfen & Entscheiden und Rendern.

# 7. Reiter Medien
Der Reiter „Medien“ ist für den kontrollierten Eingang von Medien in das Projekt gedacht. Hier werden die eigentlichen Arbeitsdateien in die Bleepling-Projektstruktur übernommen, damit sie anschließend in den weiteren Reitern verarbeitet werden können.
Sein Zweck ist bewusst einfach gehalten: Der Reiter soll nicht transkribieren, nicht rendern und nicht über Bleeps entscheiden. Er sorgt vielmehr dafür, dass die benötigten Video- und Audioquellen sauber im Projekt liegen und dass die Anwenderin oder der Anwender einen schnellen Überblick über den aktuellen Projektbestand erhält.
Im Gesamtworkflow steht der Reiter „Medien“ deshalb typischerweise direkt nach dem Reiter „Projekt“. Danach gibt es zwei sinnvolle Wege: Entweder es wird direkt im Reiter „Prüfen & Entscheiden“ weitergearbeitet, oder – wenn aus längeren bzw. mehreren Ausgangsvideos zunächst Einzelclips gebildet werden sollen – zuerst der Reiter „Schnitt & Kapitel“ genutzt.

## 7.1 Wofür der Reiter gedacht ist
- Der Reiter erfüllt drei Hauptaufgaben:
- den Import von Ausgangsvideos,
- den Import bereits vorhandener WAV-Dateien und
- die übersichtliche Anzeige der im Projekt bereits vorhandenen Medien-, Arbeits- und Ausgabedateien.
Das ist besonders praktisch, wenn ein Projekt nicht nur aus einem einzigen Video besteht, sondern mehrere Varianten, Testdateien, Titelkarten oder bereits vorbereitete Audiodateien enthält. Die Anwenderin oder der Anwender sieht dann sofort, was schon vorhanden ist, wie die Dateien fachlich eingeordnet sind und kann die zugehörigen Ordner direkt aus dem Reiter heraus öffnen.
Die wichtigsten Elemente des Reiters sind:

| Element | Wofür gedacht | Praktischer Nutzen |
| --- | --- | --- |
| Video importieren | Übernahme eines Ausgangsvideos in das Projekt | Das Video steht danach im Projekt sauber zur weiteren Bearbeitung bereit. |
| WAV importieren | Übernahme einer bereits vorhandenen WAV-Datei | Sinnvoll, wenn Audio schon separat vorbereitet wurde und nicht erst aus dem Video erzeugt werden soll. |
| Liste aktualisieren | Neuladen der angezeigten Projektdateien | Hilfreich, wenn Dateien außerhalb der App kopiert, gelöscht oder neu erzeugt wurden. |
| Dateiliste links | Anzeige der im Projekt vorhandenen Videos, WAV-Dateien, words.json-Dateien und Kandidaten-Dateien | Schneller Überblick über den aktuellen Projektstand. |
| Vogelgrafik rechts | Visuelle Auflockerung und Themenbezug | Keine Fachfunktion, aber Teil der Benutzeroberfläche. |

## 7.2 Sinnvolle Reihenfolge der Nutzung
Der Reiter „Medien“ sollte normalerweise unmittelbar nach dem Laden oder Anlegen eines Projekts benutzt werden. Die sinnvolle Reihenfolge lautet in der Praxis: zuerst Projekt öffnen, dann Medien importieren, anschließend die Dateiliste kurz kontrollieren und danach im Reiter „Prüfen & Entscheiden“ mit der Vorbereitung beginnen.
Der typische Standardfall ist: Ein Ausgangsvideo liegt auf dem Rechner vor und wird über „Video importieren“ in das Projekt kopiert. Danach erscheint es in der passenden Medienkategorie und kann im Reiter „Prüfen & Entscheiden“ als Ausgangsvideo ausgewählt werden.
Ein zweiter häufiger Fall ist: Die Audio-Datei liegt bereits separat als WAV vor. Dann kann diese direkt über „WAV importieren“ in das Projekt übernommen werden. Das spart einen Zwischenschritt, weil im Reiter „Prüfen & Entscheiden“ nicht erst eine WAV aus dem Video erzeugt werden muss.
Empfohlener Kurzablauf:
1. Projekt anlegen oder laden.
1. Ausgangsvideo importieren oder eine vorhandene WAV-Datei übernehmen.
1. Mit „Liste aktualisieren“ den sichtbaren Projektbestand prüfen, falls nötig.
1. Im Reiter „Prüfen & Entscheiden“ mit der technischen Vorbereitung fortfahren.

## 7.3 Was genau importiert wird
Beim Import werden die Dateien nicht nur referenziert, sondern physisch in die Projektstruktur kopiert. Das ist wichtig, weil Bleepling projektbezogen arbeitet und die weitere Verarbeitung auf den im Projekt abgelegten Dateien aufsetzt.
Der Medien-Reiter unterstützt dabei für den Videoimport die typischen Formate MP4, MOV, MKV, AVI, M4V und WMV. Für Audio ist der direkte Import im aktuellen Stand auf WAV-Dateien ausgelegt. Das passt zur weiteren Verarbeitung, weil WAV als sauberes Arbeitsformat für die Transkription besonders geeignet ist.
Nach dem Import wird die Anzeige aktualisiert. Zusätzlich wird – soweit möglich – auch der Reiter „Prüfen & Entscheiden“ intern mit aktualisiert, damit neu importierte Dateien dort ohne zusätzlichen Umweg zur Auswahl stehen.

## 7.4 Was in der Dateiliste angezeigt wird
Im linken Bereich des Reiters zeigt Bleepling nicht nur die unmittelbar importierten Videos und WAV-Dateien, sondern auch weitere projektbezogene Arbeitsstände. Sichtbar sind insbesondere getrennte Bereiche für Quellvideos, Projektclips, WAV, words.json, Kandidaten-Dateien, Arbeitsvideos, Ausgabedateien und Titelkarten.
Das hat einen großen praktischen Vorteil: Der Reiter „Medien“ dient nicht nur als Importstelle, sondern zugleich als schneller Projektmonitor. Man erkennt auf einen Blick, welche Quellen schon vorhanden sind, ob bereits eine Transkriptionsdatei erzeugt wurde, welche Arbeitsstände im Projekt liegen und kann die jeweiligen Ordner bei Bedarf sofort öffnen.
Im aktuellen Stand können projektbezogen zusätzlich Titelkarten als PNG-Dateien im Ausgabebereich des Projekts liegen. Außerdem werden im Reiter „Schnitt & Kapitel“ erzeugte Arbeitsclips, Arbeitsvideos und zugehörige Metadaten sauber getrennt dargestellt.
Wichtig ist dabei: Nicht jede dort sichtbare Datei wird in diesem Reiter erzeugt. Eine words.json-Datei oder eine Kandidaten-Datei entsteht typischerweise in anderen Reitern, wird hier aber trotzdem als Teil des Projektbestands angezeigt. Der Reiter „Medien“ ist deshalb zugleich Eingangsbereich und Bestandsübersicht.

## 7.5 Typische Buttons und ihre Funktion
- „Video importieren“ öffnet einen Dateidialog und kopiert das ausgewählte Video in den Projektordner für Videos.
- „WAV importieren“ öffnet einen Dateidialog und kopiert eine vorhandene WAV-Datei in den projektinternen Audio-/Transkriptionsbereich.
- „Liste aktualisieren“ liest die Projektordner erneut ein und aktualisiert die sichtbaren Listen im Reiter.
- Die Dateiliste selbst dient der Kontrolle; sie ist keine direkte Bearbeitungsfunktion im engeren Sinn.
Auffällig ist bewusst, dass der Reiter „Medien“ inhaltlich relativ schlicht gehalten ist. Genau das ist seine Stärke: Er soll keine zweite Schaltzentrale sein, sondern ein klarer und risikoarmer Startpunkt für die Medienübernahme.

## 7.6 Typische Fehlerquellen und wie man sie vermeidet
Eine häufige Fehlerquelle ist, dass noch gar kein Projekt geladen wurde. Dann kann der Reiter die Dateien zwar grundsätzlich auswählen, aber nicht sinnvoll in eine Projektstruktur übernehmen. In diesem Fall erscheint auch ein entsprechender Hinweis, dass zunächst ein Projekt benötigt wird.
Ebenfalls typisch ist die Verwechslung zwischen „Datei auf dem Rechner vorhanden“ und „Datei im Projekt vorhanden“. Für den weiteren Workflow maßgeblich sind die Dateien im Projekt. Deshalb sollte nach jedem Import kurz geprüft werden, ob die Datei tatsächlich in der Liste erscheint.
Praktisch relevant ist außerdem der Umgang mit Dateinamen. Wenn bereits eine Datei mit demselben Namen im Projekt liegt, kann das zu unbeabsichtigtem Überschreiben oder zu Verwechslungen führen. Sinnvoll ist es daher, mit sprechenden und stabilen Dateinamen zu arbeiten, insbesondere wenn mehrere Fassungen desselben Mediums existieren.

# 8. Reiter Schnitt & Kapitel
Der Reiter „Schnitt & Kapitel“ erweitert Bleepling um einen optionalen Vorbau vor dem eigentlichen Prüf- und Entscheidungsworkflow. Er ist für Fälle gedacht, in denen nicht bereits fertige Einzelvideos vorliegen, sondern zunächst aus einem oder mehreren Quellvideos sinnvolle Arbeitsclips hergestellt werden sollen.
Wichtig ist die Abgrenzung: Der Reiter ersetzt den bisherigen Direktworkflow nicht. Wer schon ein fertig geschnittenes Einzelvideo besitzt, kann weiterhin wie bisher direkt mit „Medien“ und anschließend mit „Prüfen & Entscheiden“ arbeiten. Der neue Reiter kommt nur dann ins Spiel, wenn aus längeren oder mehreren Ausgangsvideos zunächst einzelne Kapitel oder Arbeitsclips herausgeschnitten werden sollen.

## 8.1 Wofür der Reiter gedacht ist
- Zusammenstellung mehrerer Quellvideos in einer gewünschten Reihenfolge.
- Erzeugung eines projektinternen Arbeitsvideos als technische Schnittgrundlage.
- Präzises Markensetzen in einem eigenen Schnittfenster mit interner Vorschau, Sprunglogik und Millisekunden-Feinkorrektur.
- Anlage einzelner Clips mit sprechenden Dateinamen.
- Erzeugung dieser Clips als reguläre Projektmedien, die anschließend im Reiter „Prüfen & Entscheiden“ wie jedes andere Einzelvideo weiterbearbeitet werden können.

## 8.2 Grundlogik und Verhältnis zum bisherigen Workflow
Die fachliche Idee des Reiters ist bewusst pragmatisch. Bleepling versucht nicht, Programmpunkte automatisch aus Veranstaltungsunterlagen abzuleiten und ersetzt auch keine allgemeine Videoschnittsoftware. Stattdessen bietet der Reiter einen kontrollierten, lokal ablaufenden und für typische Tagungs- oder Seminaraufzeichnungen geeigneten Manuell-Workflow.
Der Ablauf lautet typischerweise: Quellvideos auswählen, Reihenfolge festlegen, daraus ein Arbeitsvideo bilden, im Schnittfenster Start- und Endmarken setzen, daraus einen oder mehrere Clips anlegen und diese Clips anschließend als neue Projektvideos erzeugen. Diese erzeugten Clips bilden danach den Einstieg in den gewohnten Prüfworkflow.
Damit existieren in Bleepling nun zwei gleichberechtigte Einstiegspfade in die Anonymisierung: entweder direkt mit einem bereits fertigen Einzelvideo oder vorgelagert über den Reiter „Schnitt & Kapitel“.

## 8.3 Bereich 1 – Quellvideos und Reihenfolge
Im linken oberen Bereich werden die im Projekt vorhandenen Quellvideos zusammengestellt. Sichtbar ist eine Liste der aktuell ausgewählten Videos; daneben befinden sich die Buttons „Video hinzufügen“, „Entfernen“, „Nach oben“, „Nach unten“ und „Quellvideo-Ordner öffnen“.
Die Logik ist einfach: Es werden nur solche Videos ausgewählt, die gemeinsam in einem späteren Arbeitsvideo verarbeitet werden sollen. Mit „Nach oben“ und „Nach unten“ wird die Reihenfolge festgelegt. Diese Reihenfolge ist fachlich relevant, denn sie entscheidet unmittelbar darüber, in welcher Abfolge die Quellvideos im Arbeitsvideo liegen.
Praktischer Hinweis: Dieser Bereich ist kein bloßer Dateibrowser, sondern eine bewusste Zusammenstellung. Wer versehentlich ein falsches Video aufnimmt oder die Reihenfolge vertauscht, schneidet später im falschen Material. Deshalb sollte diese Liste vor dem Bilden des Arbeitsvideos kurz kontrolliert werden.

## 8.4 Bereich 2 – Arbeitsvideo und Zielordner
Rechts oben wird das projektbezogene Arbeitsvideo verwaltet. Sichtbar sind Name, Pfad und Arbeitsvideo-Ordner sowie der Clip-Zielordner. Die Buttons erlauben insbesondere: „Arbeitsvideo aus Auswahl bilden“, „Arbeitsvideo aus Auswahl erneut bilden“, „Vorhandenes Arbeitsvideo wählen“, „Schnittfenster öffnen“, „Arbeitsvideo öffnen“, „Arbeitsvideo-Ordner öffnen“ und „Clip-Ordner öffnen“.
Das Arbeitsvideo ist ein interner Zwischenschritt. Es dient nicht der Veröffentlichung, sondern nur als gemeinsame Schnittgrundlage. Deshalb ist hier nicht die inhaltliche Exportqualität entscheidend, sondern die technische Verlässlichkeit des Materials für den späteren Schnitt.
Praktisch sehr wichtig ist die Wiederverwendbarkeit: Wurde zu derselben Quellvideo-Auswahl bereits ein passendes Arbeitsvideo erzeugt, kann dieses erneut genutzt werden. Dadurch entfällt unnötiges Neubauen. Nur wenn sich die Quellvideo-Auswahl oder deren Reihenfolge geändert hat oder bewusst ein neuer Stand erzeugt werden soll, sollte das Arbeitsvideo neu gebildet werden.

## 8.5 Bereich 3 – Vorschau, Position und Marken
Der große linke Hauptbereich des Reiters zeigt im Hauptfenster die aktuell gesetzten Marken und verweist zugleich auf das eigentliche Schnittfenster. Dort findet die präzise Arbeit statt. Im Hauptfenster lassen sich aktuelle Position, Startmarke und Endmarke sehen und – soweit nötig – ebenfalls kontrollieren.
Maßgeblich für die tatsächliche Schnittarbeit ist jedoch das Schnittfenster. Dort wird das Arbeitsvideo mit interner Vorschau geöffnet. Zur Verfügung stehen ein Schieberegler, Play/Pause/Stopp, Sprünge zum Anfang, zum Ende, zur Start- und Endmarke sowie Feinsprünge in Millisekunden- und Sekundenschritten. Außerdem können Start- und Endmarke direkt aus der aktuellen Position gesetzt oder auf Anfang beziehungsweise Ende des Videos gelegt werden.
Der Bereich ist bewusst auf präzise, aber nachvollziehbare Bedienung ausgerichtet. Die Anwenderin oder der Anwender soll nicht mit einer komplexen Profi-Timeline arbeiten müssen, aber trotzdem in der Lage sein, Schnittpunkte hinreichend genau zu setzen.

## 8.6 Bereich 4 – Clip anlegen und benennen
Rechts im Hauptfenster und nochmals im Schnittfenster gibt es den Bereich „Clip anlegen und benennen“. Dort werden Titel beziehungsweise Dateiname des künftigen Clips geführt und es stehen die Buttons „Clip aus Marken anlegen“, „Clip aktualisieren“ und „Clip löschen“ zur Verfügung.
Die App schlägt dabei automatisch einen sinnvollen Dateinamen vor, der sich am Namen des Arbeitsvideos orientiert und bereits vorhandene Clipnummern berücksichtigt. Dadurch werden doppelte Dateinamen möglichst vermieden und die Reihenfolge der Clips bleibt übersichtlich.
Wichtig ist die fachliche Validierung: Ein Clip kann nur sinnvoll angelegt werden, wenn die Endmarke zeitlich nach der Startmarke liegt. Für diesen Fall gibt Bleepling einen deutlichen Warnhinweis aus. Damit soll verhindert werden, dass versehentlich unbrauchbare oder logisch widersprüchige Clipdefinitionen angelegt werden.

## 8.7 Bereich 5 – Clip-Liste und Erzeugung
Im unteren Bereich des Hauptreiters wird die Clip-Liste mit laufender Nummer, Beginn, Ende und Titel/Dateiname angezeigt. Von dort aus können einzelne Clips ausgewählt, erneut in die Bearbeitung übernommen und anschließend erzeugt werden. Die wichtigsten Buttons sind „Ausgewählten Clip erzeugen“, „Alle Clips erzeugen“ und „Clip-Ordner öffnen“.
Das Prinzip ist bewusst zweistufig: Zunächst werden Marken gesetzt und Clipdefinitionen angelegt, erst danach werden die tatsächlichen Clipdateien gerendert. Das ist praktisch, weil so mehrere Clips vorbereitet und erst anschließend gesammelt erzeugt werden können. Gerade bei längeren Tagungs- oder Seminarvideos ist das deutlich angenehmer als ein sofortiges Rendern nach jedem einzelnen Schnitt.
Die erzeugten Clips werden wieder als reguläre Projektvideos behandelt. Sie erscheinen damit im weiteren Workflow wie gewöhnliche importierte Medien und können anschließend direkt im Reiter „Prüfen & Entscheiden“ anonymisiert werden.

## 8.8 Empfohlener Arbeitsablauf im Reiter Schnitt & Kapitel
1. Projekt laden und die benötigten Quellvideos im Reiter „Medien“ oder bereits zuvor im Projekt bereitstellen.
1. Im Reiter „Schnitt & Kapitel“ die Quellvideos auswählen und in die gewünschte Reihenfolge bringen.
1. Das Arbeitsvideo bilden oder ein bereits passendes Arbeitsvideo übernehmen.
1. Das Schnittfenster öffnen und die gewünschten Schnittmarken präzise setzen.
1. Einen sinnvollen Clipnamen prüfen, den Clip anlegen und gegebenenfalls weitere Clips definieren.
1. Den ausgewählten Clip oder alle vorbereiteten Clips erzeugen.
1. Die erzeugten Clips anschließend im Reiter „Prüfen & Entscheiden“ wie gewohnt weiterverarbeiten.

## 8.9 Typische Fehler und wie man sie vermeidet
Typische Fehlerquelle ist eine falsche Quellvideo-Reihenfolge. Wer hier ungenau arbeitet, schneidet später zwar technisch korrekt, aber inhaltlich am falschen Abschnitt. Ebenso problematisch ist es, ein altes Arbeitsvideo wiederzuverwenden, obwohl sich die Quellvideo-Auswahl geändert hat.
Ein weiterer häufiger Fehler ist die Verwechslung von Navigationssprung und Markenlogik. Der Button zum Springen an das Ende dient nur der Navigation im Player. Maßgeblich für den späteren Clip ist dagegen die tatsächlich gesetzte Endmarke. Ebenso sollte immer darauf geachtet werden, dass die Endmarke zeitlich nach der Startmarke liegt.
Schließlich ist wichtig zu verstehen, dass der Reiter noch keine Anonymisierung vornimmt. Die hier erzeugten Clips sind lediglich besser handhabbare Arbeitsmedien. Die eigentliche datenschutzrechtliche Prüfung und die endgültige Bleep-Entscheidung erfolgen erst im nächsten fachlichen Schritt.

## 8.10 Kurzfazit
Der Reiter „Schnitt & Kapitel“ macht Bleepling in Version 1.3.0 deutlich allgemeiner einsetzbar. Er ersetzt keine vollwertige Filmschnittsoftware, schließt aber die bislang fehlende Lücke zwischen Rohmaterial und eigentlichem Prüfworkflow. Für Anwenderinnen und Anwender, die mit längeren Aufzeichnungen und mehreren Programmabschnitten arbeiten, ist er damit ein echter Produktivitätsgewinn.
Schließlich sollte man beachten, dass der Reiter „Medien“ bewusst nur den Eingang organisiert. Wer dort bereits erwartet, aus einem Video automatisch eine WAV oder aus einer WAV automatisch eine words.json zu erzeugen, ist im falschen Bereich. Diese Arbeitsschritte gehören in den Reiter „Prüfen & Entscheiden“.

# 9. Reiter Prüfen & Entscheiden
Der Reiter „Prüfen & Entscheiden“ ist der Kernbereich für die inhaltliche Prüfung. Hier wird festgelegt, welche erkannten Namensnennungen später tatsächlich gebleept werden und welche nicht. Die Benutzeroberfläche ist in mehrere logisch aufeinander folgende Bereiche gegliedert.

## 9.1 Bereich 1 – Vorbereitung
Im oberen Bereich des Reiters „Prüfen & Entscheiden“ werden die technischen Vorstufen für die Namensprüfung vorbereitet. Inhaltlich knüpft dieser Bereich an den früheren Reiter „Bleeping“ an, ist nun aber unmittelbar mit der späteren Einzelprüfung verbunden.
Typische Bedienelemente sind:
- Ausgangsvideo – Auswahl eines im Projekt vorhandenen Videos
- WAV – Auswahl einer vorhandenen Audio-Arbeitsdatei
- WAV aus Video erzeugen – erstellt die Audio-Datei aus dem gewählten Video
- words.json aus WAV – erzeugt die Transkriptionsdaten aus der gewählten WAV-Datei
- Kandidaten erzeugen – erstellt die zeitgestempelte Kandidaten-Datei aus den Transkriptionsdaten
Für die alltägliche Nutzung ist wichtig: Dieser Bereich erzeugt noch keine fertige Bleepliste, sondern die Arbeitsgrundlagen für die spätere Entscheidung im selben Reiter.
Praktischer Standardworkflow: Ausgangsvideo auswählen -> WAV aus Video erzeugen -> words.json aus WAV erzeugen -> Kandidaten aus words.json erzeugen.
Seit Version 1.5.2 erzeugt der Button „words.json aus WAV“ wieder echte Transkriptionsdaten mit Wort-Zeitmarken. Wenn kein altes Legacy-Transkriptionsskript vorhanden ist, nutzt Bleepling direkt das Python-Modul faster-whisper. Eine leere Platzhalter-JSON-Datei wird dabei nicht mehr als erfolgreicher Arbeitsschritt ausgegeben.

## 9.2 Bereich 2 – Namenslisten und Regeln
Dieser Bereich dient dazu, unterstützende Namenslisten zu pflegen. Er entscheidet noch nicht selbst über den späteren Bleep, sondern beeinflusst die Auswertung der Kandidaten-Datei.
- Blocklist (optional): Namen, die besonders aufmerksam geprüft werden sollen.
- Allowlist (optional): Namen oder Schreibweisen, die später nicht gebleept werden sollen.
- Teilnehmerliste importieren: Übernimmt Namen aus TXT, CSV, XLSX, DOCX oder PDF in eine Namensbasis.
- Nachnamen: übernimmt nur Nachnamen aus der zuletzt importierten Teilnehmerliste.
- Vornamen: übernimmt nur Vornamen oder ergänzt die Nachnamen, wenn beide Optionen aktiv sind.
- Akt.: baut die zuletzt importierte Teilnehmerliste mit den aktuell gesetzten Namensoptionen erneut auf, ohne manuelle Blocklist-Einträge zu überschreiben.
Blocklist aus Kandidaten füllen / Allowlist aus Kandidaten füllen: übernehmen Schreibweisen aus der Kandidaten-Datei als Bearbeitungshilfe.
- Blocklist leeren / Allowlist leeren: setzen die jeweilige Liste vollständig zurück.
Wichtig ist die klare Abgrenzung: Eine Teilnehmerliste ist keine Kandidaten-Datei. Sie enthält nur Namen, aber keine Zeitstempel. Sie kann also die spätere Prüfung erleichtern, erzeugt aber nicht selbst eine verwendbare Times-Datei.
Ebenso wichtig: Die Blocklist erzwingt keinen automatischen Bleep. Sie ist eine Prüfhilfe. Maßgeblich bleibt die Kombination aus Kandidaten-Auswertung, Trefferliste, Audio-Prüfung und der später aus den finalen Intervallen abgeleiteten Times-Datei.

## 9.3 Bereich 3 – Kandidaten prüfen
Hier wird die eigentliche Trefferdatei eingelesen und mit den hinterlegten Regeln abgeglichen. Dieser Bereich enthält insbesondere:
- Kandidaten-Datei – Auswahl oder Laden der zeitgestempelten Trefferdatei
- Blocklist-Fuzzy % – Schwellenwert für unscharfe Zuordnung zur Blocklist
- Allowlist-Fuzzy % – Schwellenwert für unscharfe Zuordnung zur Allowlist
- Auswertung starten – vergleicht die Kandidaten-Datei mit Blocklist und Allowlist und lädt das Ergebnis direkt in die Trefferliste zur Feinprüfung
- Schnell-Nachbleepen – erzeugt zusätzliche Verdachtsstellen für einen späteren Korrekturdurchgang
- Liste aktualisieren – liest Kandidaten- und Medienbestand neu ein
Die beiden Fuzzy-Werte steuern, wie ähnlich eine Schreibweise einem Blocklist- oder Allowlist-Eintrag sein muss, um als Treffer zu gelten. Höhere Werte sind strenger, niedrigere toleranter.
Im praktischen Betrieb bedeutet das: Wer viele Varianten, Versprecher oder leicht abweichende Schreibweisen erwartet, muss diese Werte mit Bedacht wählen. Zu strenge Werte übersehen Treffer; zu großzügige Werte erzeugen Fehlalarme.

## 9.4 Bereich 4 – Trefferliste, Feinprüfung und Times-Datei
Dieser Bereich ist der eigentliche Entscheidungspunkt. Hier laufen die frühere Bleeping-Vorschau und die frühere Audio-Einzelprüfung erstmals in einer gemeinsamen Arbeitsfläche zusammen.
Die Trefferliste zeigt die laufende Nummer, Beginn, Ende, Treffer, Ergebnis und Regelhinweis. Der vollständige Kontext des aktiven Treffers wird darunter angezeigt.
Die wichtigsten Funktionen sind:
- Treffer in der Liste markieren, einzeln oder in Mehrfachauswahl
- Prüfclip anhören, erneut abspielen oder direkt zur Trefferstelle springen
- Beginn und Ende des Bleeps in Millisekundenschritten feinjustieren
- Treffer auf „bleepen“, „verwerfen“ oder „offen lassen“ setzen
- Treffer in Blocklist oder Allowlist übernehmen
- Prüfstand speichern und daraus eine Times-Datei mit Intervallen ableiten
Die zentrale Logik lautet: Die globalen Bleep-Parameter gelten zunächst für alle Treffer. Darauf bauen die individuellen Start- und Endkorrekturen pro Treffer auf. Erst aus dieser Kombination entstehen die wirksamen Intervalle, die später in die Times-Datei geschrieben und beim Rendern verwendet werden.
Wer hier systematisch arbeitet, sollte Treffer nicht vorschnell übernehmen, sondern den Kontext mitprüfen. Gerade ähnliche Nachnamen, Organisationsbegriffe oder Rollenbezeichnungen können sonst unnötige Fehlbleeps erzeugen.

## 9.5 Unterschied zwischen Teilnehmerliste, Kandidaten-Datei, Blocklist und Allowlist
Dieses Zusammenspiel ist erfahrungsgemäß der häufigste Erklärungsbedarf. Deshalb gilt unverändert:
Teilnehmerliste: enthält Namen, aber keine Zeitstempel. Sie hilft beim Aufbau der Namensbasis, besonders für die Blocklist.
Kandidaten-Datei: enthält Treffer mit Kontext und Zeitstempeln. Sie ist die Arbeitsdatei für die Auswertung.
Blocklist: enthält prüfbedürftige Namen. Sie erhöht die Aufmerksamkeit bei der Auswertung.
Allowlist: enthält freizugebende Namen oder Schreibweisen. Sie hat Vorrang bei der Freigabe und vermeidet unnötige Bleeps.
Neu in 1.2.0 ist, dass die eigentliche operative Entscheidung nicht mehr in einer separaten Vorschautabelle und danach noch einmal in einem zweiten Reiter getroffen wird. Maßgeblich ist nun die Trefferliste im Reiter „Prüfen & Entscheiden“, aus der der Prüfstand gespeichert und die Intervall-Times-Datei abgeleitet wird.

## 9.6 Empfohlener Arbeitsablauf im Reiter Prüfen & Entscheiden
1. Zuerst die technischen Vorstufen im Bereich 1 abschließen.
1. Nur wenn sinnvoll, eine Teilnehmerliste importieren oder Blocklist/Allowlist pflegen.
1. Danach die Kandidaten-Datei laden und die Auswertung starten.
1. Die Trefferliste und den Kontext sorgfältig prüfen.
1. Die globalen Bleep-Parameter festlegen und mit „Anwenden“ verbindlich übernehmen.
1. Auffällige Treffer im Prüfclip anhören und Beginn bzw. Ende feinjustieren.
1. Treffer auf „bleepen“, „verwerfen“ oder „offen lassen“ setzen.
1. Zum Schluss den Prüfstand speichern und die Times-Datei mit Intervallen ableiten.

## 9.7 Typische Fehler und wie man sie vermeidet
- Teilnehmerliste und Kandidaten-Datei verwechseln: Eine Teilnehmerliste enthält keine Zeitpunkte und kann deshalb keine Times-Datei ersetzen.
- Zu viel Vertrauen in die Blocklist: Sie ist eine Prüfhilfe, aber kein Automatismus.
- Globale Bleep-Parameter ändern, aber nicht auf „Anwenden“ klicken: Dann bleibt die Trefferliste zunächst auf dem alten Stand.
- Treffer feinjustieren, aber keine neue Times-Datei ableiten: Dann rendert FFmpeg noch mit einem älteren Stand.
- PDF-Teilnehmerlisten überschätzen: Sie können funktionieren, XLSX ist in der Praxis häufig robuster.
Faustregel: Die Prüfung ist erst dann vollständig, wenn Trefferliste, Prüfclip und daraus abgeleitete Times-Datei denselben Stand widerspiegeln.

# 10. Reiter Video & Audio / FFmpeg
Der Reiter „Video & Audio / FFmpeg“ ist der technische Ausgabebereich der App. Hier werden aus der bereits fachlich geprüften Times-Datei die eigentlichen Ausgabeformate erzeugt: entweder ein gebleeptes Video oder – bei reinen Audioquellen – eine gebleepte Audiodatei. Als Ausgangsmedium können dabei sowohl ursprünglich importierte Einzelvideos als auch im Reiter „Schnitt & Kapitel“ erzeugte Arbeitsclips dienen.
Während der Reiter „Prüfen & Entscheiden“ die inhaltliche und akustische Festlegung der wirksamen Bleepspannen übernimmt, setzt der Reiter „Video & Audio / FFmpeg“ diese Entscheidung technisch um.
In der Arbeitslogik folgt dieser Reiter daher in aller Regel erst nach dem Reiter „Prüfen & Entscheiden“. Zunächst werden Kandidaten geprüft, Treffer feinjustiert und daraus eine Times-Datei mit Intervallen erzeugt. Erst danach wird hier das endgültige Medium gerendert.

## 10.1 Bereich Quelle und Ausgabe
Der obere Bereich dient dazu, Eingabe- und Ausgabedateien festzulegen. Er ist der Startpunkt jeder Arbeit in diesem Reiter. Typische Bedienelemente sind:
- Mediadatei im Projekt – Auswahl eines im Projekt vorhandenen Videos oder einer vorhandenen Audiodatei.
- Liste aktualisieren – liest die im Projekt vorhandenen Medien erneut ein und aktualisiert die Auswahl.
- Times-Datei – Auswahl der Zeitschnittliste, die die später zu bleependen Zeitpunkte enthält.
- Datei auswählen – lädt eine konkrete Times-Datei aus dem Projektverzeichnis.
- Ausgabedatei – frei editierbarer Name der späteren Ausgabedatei.
- Web-Standard setzen – setzt den Reiter auf eine browserfreundliche Standardkonfiguration zurück.
- Ausgangsmedium – Informationszeile mit Codec, Auflösung, Bildrate, Dauer und ungefährer Dateigröße des gewählten Quellmediums.
Sinnvoll genutzt wird dieser Bereich in folgender Reihenfolge: zuerst das Ausgangsmedium wählen, danach die passende Times-Datei kontrollieren, anschließend den Ausgabedateinamen festlegen. Besonders wichtig ist dabei die Unterscheidung zwischen Video- und Audioquellen. Liegt nur eine Audiodatei vor oder enthält das Quellmedium kein Video, sollte später nicht „Gebleeptes Video erzeugen“, sondern „Gebleeptes Audio erzeugen“ verwendet werden.
Typische Fehlerquelle: Es wird versehentlich eine unpassende Times-Datei ausgewählt oder eine ältere Times-Datei aus einem früheren Bearbeitungsstand verwendet. Das führt zwar technisch oft zu einem Renderlauf, aber fachlich zu einem falschen Ergebnis. Vor jedem Export sollte deshalb geprüft werden, ob Medium und Times-Datei wirklich zusammengehören.

## 10.2 Bereich Exportprofil
Der Bereich „Exportprofil“ legt fest, in welchem technischen Format die Ausgabe erzeugt wird. Dabei verbindet der Reiter benutzerfreundliche Profilvorgaben mit der Möglichkeit, die zentralen Parameter manuell anzupassen. Typische Elemente sind:
- Profil – Auswahl einer Profilgruppe wie „web“, „qualität“, „kleinste datei“ oder „wie quellvideo“.
- Profil anwenden – übernimmt die Werte der gewählten Profilgruppe in die übrigen Einstellfelder.
- Eigenes Profil – Auswahl eines zuvor selbst gespeicherten Profils.
- Profil laden – lädt ein bereits gespeichertes benutzerdefiniertes Profil.
- Profil speichern – speichert die aktuelle Kombination der Einstellungen als eigenes Profil.
- Video-Codec – Auswahl des Video-Codecs, insbesondere H.264 mit GPU-Unterstützung, H.264 auf CPU oder H.265 auf CPU.
- Preset – Wahl zwischen Geschwindigkeits- und Qualitätsstufen von „ultrafast“ bis „veryslow“.
- Qualität (CQ/CRF) – Qualitätsregler des Exports; kleinere Werte bedeuten in der Regel höhere Qualität und größere Dateien, größere Werte kleinere Dateien mit stärkerer Kompression.
- Audio-Codec – Auswahl zwischen AAC und MP3.
- Audio-Bitrate – Feinsteuerung der Audiokompression.
- Skalierung – Wahl, ob die Originalgröße beibehalten oder z. B. auf 1280 oder 1920 Pixel Breite ausgegeben werden soll.
- Web-Optimierung (faststart) – verbessert insbesondere bei MP4-Dateien die Nutzbarkeit für Webanwendungen.
- Voraussichtliche Ausgabegröße / Voraussichtliche Renderdauer – grobe technische Schätzwerte zur Orientierung.
Für die tägliche Praxis ist wichtig: Die Profilgruppe „web“ ist der Normalfall für browserkompatible Ausgaben. „Qualität“ zielt stärker auf eine hochwertigere Ausgabe, „kleinste datei“ auf stärkere Kompression, und „wie quellvideo“ orientiert sich näher am Quellmedium, ohne dieses bitgenau zu kopieren. Wer keine besonderen Anforderungen hat, fährt mit dem Web-Profil in aller Regel am sichersten.
Benutzerdefinierte Profile sind vor allem dann sinnvoll, wenn wiederholt mit denselben Exportwerten gearbeitet wird, etwa bei immer gleichartigen Seminarvideos oder immer gleichen Audioausgaben. So lässt sich vermeiden, dass Parameter wie Skalierung, Audio-Bitrate oder Qualitätswert jedes Mal neu gesetzt werden müssen.
Typische Fehlerquelle: Aus der Bezeichnung „wie quellvideo“ wird manchmal geschlossen, dass eine praktisch identische Kopie des Ausgangsvideos entsteht. Tatsächlich handelt es sich eher um eine Orientierung an den wesentlichen Quelldaten. Wer eine sehr spezielle technische Vorgabe erfüllen muss, sollte deshalb die Einzelparameter bewusst kontrollieren.

## 10.3 Bereich Erklärung
Der Bereich „Erklärung“ hat keine eigene Steuerfunktion, sondern erläutert die Grundlogik des Exportbereichs. Er weist darauf hin, dass die Standardausgabe auf browserkompatible Formate zielt, dass H.264 für Webanwendungen besonders kompatibel ist, dass AAC der empfohlene Audio-Codec für MP4-Ausgaben ist und dass die Größen- und Zeitschätzungen nur grobe Näherungen darstellen. Für Anwenderinnen und Anwender ist dieser Abschnitt vor allem dann nützlich, wenn sie die Auswirkungen von Exportprofil, Codec und Datenrate besser einordnen wollen.

## 10.4 Bereich Bleep-Parameter
Im aktuellen Projektstand werden die fachlich maßgeblichen Bleep-Parameter nicht mehr im Reiter „Video & Audio / FFmpeg“, sondern im Reiter „Prüfen & Entscheiden“ festgelegt. Dort werden Frequenz, Lautstärke, Vorlauf und Nachlauf gesetzt, auf alle Treffer angewendet und bei Bedarf mit individuellen Trefferkorrekturen kombiniert.
Der FFmpeg-Reiter ist damit nicht mehr der Ort, an dem die Länge oder Lage eines Bleeps inhaltlich nachgeschärft werden soll. Er setzt den bereits geprüften Stand um.
Für ältere Projekte mit klassischen Punkt-Times-Dateien bleibt die Rückwärtskompatibilität erhalten. Für neue Prüfstände in 1.2.0 sind aber die im Prüfreiter erzeugten Intervall-Times-Dateien maßgeblich.

## 10.5 Bereich Rendern
Der Bereich „Rendern“ setzt die ausgewählten Einstellungen in einen tatsächlichen FFmpeg-Arbeitsgang um. Typische Bedienelemente sind:
- FFmpeg-Befehl prüfen – zeigt den vorbereiteten Befehl an und eignet sich besonders zur Kontrolle oder Fehlersuche.
- Gebleeptes Video erzeugen – startet den Videoexport mit Bleepsignal und schreibt die Ausgabe in den Video-Ausgabeordner.
- Gebleeptes Audio erzeugen – erzeugt statt eines Videos nur eine gebleepte Audiodatei, z. B. als M4A oder MP3.
Während des Renderns erscheint ein eigenes Fortschrittsfenster. Dieses zeigt den laufenden Export an und erlaubt auch einen Abbruch. Parallel dazu dient der Protokoll- bzw. Logbereich am unteren Rand des Reiters als Rückmeldung für vorbereitete Befehle, Fehlermeldungen und Statushinweise. Gerade bei längeren Exporten oder unerwarteten Problemen sollte dieser Bereich immer mitgelesen werden.
Praktische Reihenfolge: Zuerst den FFmpeg-Befehl prüfen, wenn Unsicherheit über die Einstellungen besteht. Danach den eigentlichen Export starten. Bei Audioquellen sollte direkt „Gebleeptes Audio erzeugen“ gewählt werden; bei Videodateien in der Regel „Gebleeptes Video erzeugen“.
Typische Fehlerquelle: Es wird versucht, aus einer reinen Audiodatei ein Video zu rendern. Der Reiter reagiert darauf zwar mit einem Hinweis, dennoch ist das ein häufiger Bedienfehler. Ebenso problematisch ist es, eine Ausgabedatei im Kopf bereits manuell so zu benennen, dass die Endung nicht mehr zum gewählten Ausgabetyp passt. Deshalb sollte der Dateiname zwar bewusst gewählt, aber nicht unnötig technisch verfremdet werden.
Seit Version 1.5.2 werden reine Audioexporte in 04_output/audio abgelegt. Videoexporte bleiben in 04_output/videos. Dadurch sind gebleepte Audiodateien und gebleepte Videodateien im Projekt klarer getrennt.
Außerdem wartet Bleepling beim Aufräumen temporärer FFmpeg-Dateien nun robuster, falls Windows eine gerade erzeugte Datei noch für einen kurzen Moment gesperrt hält.

## 10.6 Empfohlener Arbeitsablauf im Reiter Video & Audio / FFmpeg
1. Das richtige Ausgangsmedium auswählen und prüfen, ob es sich um Video oder reine Audiodatei handelt.
1. Die passende Times-Datei kontrollieren und nur dann fortfahren, wenn sie zum gewählten Medium gehört.
1. Einen sinnvollen Ausgabedateinamen vergeben.
1. Ein Exportprofil wählen und – falls nötig – manuell nachschärfen.
1. Bei Unsicherheit zuerst den FFmpeg-Befehl prüfen.
1. Danach das gebleepte Video oder das gebleepte Audio erzeugen.
1. Das Ergebnis anschließend immer noch einmal anhören bzw. ansehen und stichprobenartig kontrollieren.
Wichtig ist dabei: Die inhaltliche Festlegung der Bleepspannen sollte zu diesem Zeitpunkt bereits im Reiter „Prüfen & Entscheiden“ abgeschlossen sein.

## 10.7 Typische Fehler und wie man sie vermeidet
- Falsches Medium gewählt: Vor dem Export immer prüfen, ob wirklich das gewünschte Ausgangsvideo oder die richtige Audiodatei ausgewählt ist.
- Falsche Times-Datei verwendet: Medium und Times-Datei müssen zusammengehören; sonst entstehen technisch korrekte, aber fachlich falsche Bleeps.
- Erwarten, dass sich Bleeplänge oder Bleep-Lage im FFmpeg-Reiter noch inhaltlich nachregeln lassen: In 1.2.0 soll die fachlich maßgebliche Festlegung bereits vorher erfolgt sein.
- Datei wird zu groß oder Rendern dauert zu lange: Ein kleineres Profil, stärkere Skalierung oder ein höherer CQ/CRF-Wert kann helfen.
- Audioformat ungeeignet gewählt: AAC ist der sichere Standard für Videoausgaben; MP3 ist vor allem für reine Audiodateien sinnvoll.
- GPU wird erwartet, aber nicht tatsächlich genutzt: In diesem Fall das eingestellte Render-Backend im Reiter „Einstellungen / Logs“ prüfen und die Schätzungen bzw. Laufzeiten nicht überinterpretieren.
- Zu viel Vertrauen in die Schätzwerte: Die Angaben zu Dateigröße und Renderdauer sind nur Orientierungswerte und können je nach Quellmaterial deutlich abweichen.

# 11. Reiter Gezielte Nachbearbeitung
Der Reiter „Gezielte Nachbearbeitung“ ist für Korrekturen und Ergänzungen gedacht, nachdem der normale Prüf- und Bleep-Workflow bereits gelaufen ist oder wenn ein Medium nur punktuell nachbearbeitet werden soll. Er ersetzt den Hauptworkflow nicht, sondern ergänzt ihn dort, wo einzelne zusätzliche Bleeps, ein Vorspannbild oder ein Nachspannbild benötigt werden. Vor- und Nachspannbilder werden dabei so zusammengesetzt, dass die eigentliche Tonspur des Ausgangsvideos synchron bleibt und während der Bildphasen nur stille Abschnitte ergänzt werden.

## 11.1 Zweck und Einsatzbereich
Der Reiter dient vor allem drei typischen Anwendungsfällen:
- in einem bereits bearbeiteten Video sollen einzelne weitere Stellen gezielt nachgebleept werden;
- vor das Medium soll für einige Sekunden ein Bild ohne hörbaren Ton gesetzt werden, etwa als Einleitung oder Hinweisgrafik;
- an das Ende des Mediums soll ein Bild ohne hörbaren Ton angehängt werden, etwa als Abspann-, Hinweis- oder Abschlussfolie.
Wichtig ist die Abgrenzung: Der Reiter ist nicht für die eigentliche inhaltliche Erstprüfung aller Namensnennungen gedacht. Diese Aufgabe liegt im Reiter „Prüfen & Entscheiden“. Die gezielte Nachbearbeitung setzt typischerweise dort an, wo ein Medium bereits vorhanden ist und nur noch punktuell ergänzt oder korrigiert werden soll.

## 11.2 Auswahl des Ausgangsmediums
Im oberen Bereich wird das Medium ausgewählt, das nachbearbeitet werden soll. Dabei können nicht nur ursprüngliche Eingabevideos aus dem Projekt genutzt werden, sondern auch bereits gerenderte Projektvideos aus dem Ausgabeordner. Das ist praktisch, wenn eine erste Bleep-Fassung schon erzeugt wurde und nur noch einzelne Korrekturen oder Vor- beziehungsweise Nachspannbilder ergänzt werden sollen.
- Quelle wählen: Im Feld für das Projektvideo wird das Medium ausgewählt, auf das sich alle weiteren Schritte beziehen.
- Liste aktualisieren: Mit diesem Befehl wird die Dateiliste neu eingelesen. Das ist sinnvoll, wenn zwischenzeitlich neue Ausgabedateien erzeugt wurden.
- Hinweis zur Bildgröße: Der Reiter liest nach Möglichkeit die Auflösung des gewählten Mediums aus und zeigt an, in welcher Größe ein Vorspann- oder Nachspannbild idealerweise vorliegen sollte.
Sinnvolle Reihenfolge: Zuerst immer prüfen, ob tatsächlich das richtige Ausgangsmedium gewählt ist. Gerade wenn im selben Projekt mehrere Zwischen- und Endfassungen liegen, ist das eine häufige Fehlerquelle.

## 11.3 Bereich „Gezieltes Nachbleepen“
Im Bereich „Gezieltes Nachbleepen“ werden einzelne zusätzliche Bleep-Zeitpunkte eingetragen. Die Eingabe erfolgt zeilenweise, typischerweise im Format HH:MM:SS.mmm. Jeder Eintrag steht für eine Stelle, an der zusätzlich ein Bleep gesetzt werden soll.
- Vorlauf (ms): bestimmt, wie viele Millisekunden vor dem eingetragenen Zeitpunkt der Bleep beginnen soll.
- Nachlauf (ms): bestimmt, wie viele Millisekunden nach dem Zeitpunkt der Bleep weiterlaufen soll.
- Zeitliste: enthält die einzelnen Zielzeitpunkte, jeweils eine Zeile pro Treffer.
Die hier eingetragenen Zeiten beziehen sich immer auf das ausgewählte Ausgangsmedium. Werden im selben Renderlauf zusätzlich ein Vor- oder Nachspannbild ergänzt, sorgt die App intern dafür, dass die gezielten Bleeps zunächst auf das eigentliche Medium angewendet werden und die Bilder erst danach davor oder dahinter gesetzt werden. Dadurch verschieben sich die nachzutragenden Bleep-Zeitpunkte nicht künstlich.
Für Klang und Charakter des Bleeps werden die allgemeinen Bleep-Parameter aus dem Reiter „Video & Audio / FFmpeg“ übernommen, insbesondere Frequenz und Lautstärke. Im Reiter „Gezielte Nachbearbeitung“ werden dagegen nur die zeitlichen Sicherheitszuschläge – also Vorlauf und Nachlauf – separat eingestellt.

## 11.4 Bereich „Bild voranstellen“
In diesem Bereich kann vor das gewählte Medium ein statisches Bild ohne Ton gesetzt werden. Das ist nützlich, wenn vor dem eigentlichen Video ein kurzer Hinweis, eine Einblendung, eine Startfolie oder ein Titelbild erscheinen soll.
- Bild auswählen: lädt die gewünschte Bilddatei.
- Dauer in Sekunden: legt fest, wie lange das Bild vor dem eigentlichen Medium sichtbar bleiben soll.
Wer häufiger gleichartige Vor- oder Nachspannbilder benötigt, erstellt diese sinnvollerweise zuvor im Reiter „Titelkarten“ und verwendet anschließend die exportierte PNG-Datei in der gezielten Nachbearbeitung.
- Automatische Anpassung: Das Bild wird beim Rendern an die Größe des Ausgangsmediums angepasst und passend eingepasst.
Die App erwartet kein perfekt vorbereitetes Bild, aber die Qualität wird besser, wenn die Bilddatei bereits möglichst nah an der Videogröße liegt. Zu kleine oder stark abweichende Seitenverhältnisse können zu unschönen Rändern oder Skalierungseffekten führen.

## 11.5 Bereich „Bild hintenanstellen“
Der Bereich „Bild hintenanstellen“ funktioniert in derselben Logik wie das Voranstellen, nur bezogen auf das Ende des Mediums. Er eignet sich etwa für Abspannhinweise, Quellenangaben, Schlussfolien oder datenschutzrechtliche Hinweise.
- Bild auswählen: lädt das Schlussbild.
Auch Schlussbilder können vorab im Reiter „Titelkarten“ erstellt und danach hier wiederverwendet werden.
- Dauer in Sekunden: bestimmt, wie lange das Bild am Ende angezeigt wird.
- Automatische Größenanpassung: Das Bild wird an die Auflösung des Ausgangsmediums angepasst und mit still verlängerter Audiospur ans Ende gesetzt.
Vor- und Nachspannbild können unabhängig voneinander gesetzt werden. Es ist also möglich, nur ein Vorspannbild, nur ein Nachspannbild oder beides zusammen zu verwenden.

## 11.6 Änderungen rendern
Beim Klick auf „Änderungen rendern“ verwendet Bleepling seit Version 1.5.1 nicht mehr nur fest eingebaute Renderwerte. Codec, Backend, Qualität, Preset, Audio-Bitrate und Skalierung werden aus dem Bereich „Rendern / Ausgabe“ im Reiter „Einstellungen / Logs“ übernommen.
Der Standardwert für die Skalierung lautet „Originalgröße beibehalten“. Das ist absichtlich so gewählt: Die gezielte Nachbearbeitung wird häufig auf ein bereits fertig erzeugtes oder bereits abgestimmtes Video angewendet. Ohne ausdrückliche Änderung soll dieses Video daher nicht unbemerkt auf 1280 Pixel Breite heruntergerechnet oder auf 1920 Pixel hochskaliert werden.
Die Felder im Reiter „Gezielte Nachbearbeitung“ bleiben für die fachlichen Änderungen zuständig: zusätzliche Bleep-Zeitpunkte, Vorlauf, Nachlauf, Vor- und Nachspannbild sowie deren Dauer. Die allgemeinen Renderwerte werden dagegen zentral im Einstellungsreiter gesetzt, damit die technische Ausgabequalität projektweit nachvollziehbar bleibt.
Wichtig: Wird nur ein zusätzlicher Bleep gesetzt, rendert Bleepling die Videospur mit den zentralen Renderwerten neu zusammen. Werden Vor- oder Nachspannbilder verwendet, werden diese Bildsegmente auf die Zielgröße eingepasst, mit stiller Audiospur versehen und anschließend gemeinsam mit dem eigentlichen Video zusammengesetzt.
Seit Version 1.5.2 schreibt die gezielte Nachbearbeitung das Endergebnis direkter in die finale Ausgabedatei und räumt temporäre Dateien mit kurzen Wiederholversuchen auf. Das reduziert besonders unter Windows die Gefahr, dass ein fertiges Video zwar erzeugt wurde, aber beim Umbenennen oder Löschen temporärer Dateien als fehlgeschlagen gemeldet wird.
Der eigentliche Arbeitsbefehl des Reiters ist „Änderungen rendern“. Damit werden alle ausgewählten Ergänzungen in einem zusammenhängenden Ablauf verarbeitet.
- Zuerst werden – falls vorhanden – die gezielten Zusatzbleeps auf das gewählte Medium angewendet.
- Danach werden – falls gesetzt – Vor- und Nachspannbild mit dem Medium zusammengefügt.
- Am Ende entsteht eine neue Ausgabedatei im Projekt, typischerweise mit einem Zusatz wie „_edited“ im Dateinamen.
Während des Renderns erscheint ein eigenes Fortschrittsfenster mit Vogelgrafik, Fortschrittsbalken und Abbrechen-Schaltfläche. Dieses Fenster dient nicht nur der optischen Rückmeldung, sondern zeigt auch, dass die App gerade aktiv arbeitet. Das ist wichtig, weil Renderläufe – je nach Videolänge und Codec – einige Zeit dauern können.

## 11.7 Verhältnis zum Hauptworkflow
Der Reiter ist als Ergänzungswerkzeug gedacht. In den meisten Fällen ist die sinnvolle Reihenfolge deshalb:
- zuerst normaler Prüfworkflow im Reiter „Prüfen & Entscheiden“;
- danach regulärer Export im Reiter „Video & Audio / FFmpeg“;
- anschließend – nur falls nötig – gezielte Nachbearbeitung des bereits erstellten Mediums.
Das bedeutet in der Praxis: Der Reiter ist ideal für den zweiten Durchgang, für Korrekturen oder für gestalterische Ergänzungen. Er ist nicht der richtige Ort, um den gesamten Namensprüfprozess zu ersetzen.

## 11.8 Empfohlener Arbeitsablauf
1. Das richtige Ausgangsmedium auswählen.
1. Falls zusätzliche Namensstellen gebleept werden sollen, die Zielzeiten in die Zeitliste eintragen und Vorlauf/Nachlauf festlegen.
1. Falls gewünscht, ein Vorspannbild auswählen und die Anzeigedauer festlegen.
1. Falls gewünscht, ein Nachspannbild auswählen und die Anzeigedauer festlegen.
1. Mit „Änderungen rendern“ den gesamten Nachbearbeitungslauf starten.
1. Die erzeugte Datei anschließend inhaltlich kurz kontrollieren.

## 11.9 Typische Fehler und wie man sie vermeidet
- Falsches Ausgangsmedium gewählt: Vor dem Rendern immer den Dateinamen prüfen, besonders wenn im Projekt schon mehrere Ausgabefassungen liegen.
- Zeitpunkte auf das falsche Medium bezogen: Zusatzbleeps müssen sich auf das tatsächlich ausgewählte Video beziehen, nicht auf eine frühere oder andere Fassung.
- Zu kurze oder zu lange Vor- und Nachlaufzeiten: Bei Unsicherheit lieber mit etwas großzügigerem Sicherheitszuschlag arbeiten und das Ergebnis anschließend kontrollieren.
- Bildformat ungeeignet: Sehr kleine oder stark abweichende Bildformate können optisch unschöne Ergebnisse erzeugen; ideal ist eine Bildgröße nahe der Videoauflösung.
- Gezielte Nachbearbeitung mit Hauptworkflow verwechselt: Der Reiter ist für Korrekturen und Ergänzungen gedacht, nicht als Ersatz für die inhaltliche Erstauswertung im Reiter „Prüfen & Entscheiden“.
- Kein Kontrolllauf nach dem Rendern: Auch nach gezielter Nachbearbeitung sollte die Enddatei noch einmal kurz überprüft werden.

## 11.10 Kurzfazit
Der Reiter „Gezielte Nachbearbeitung“ ist das Werkzeug für den zweiten, präzisen Korrekturdurchgang. Er eignet sich besonders dann, wenn ein Medium inhaltlich schon weitgehend fertig ist, aber noch einzelne Zusatzbleeps oder ein Vor- beziehungsweise Nachspannbild benötigt. Richtig eingesetzt spart der Reiter viel Zeit, weil solche Änderungen nicht den gesamten Hauptworkflow erneut erfordern.

# 12. Reiter Titelkarten
Der Reiter „Titelkarten“ dient der Erstellung statischer Titelkarten im Format 1920 × 1080 Pixel. Er ist damit ein Ergänzungswerkzeug für Fälle, in denen vor ein Video ein Vorspannbild oder an das Ende eines Videos ein Nachspannbild gestellt werden soll, ohne dass diese Grafik zuvor in externer Software entworfen werden muss.
Die Funktion ist bewusst praxisnah angelegt: In Bleepling können Dachzeile, zweite Dachzeile, Titel, farbige Titelbox, Hintergrundbild sowie Logos links und rechts kombiniert und unmittelbar als PNG-Datei exportiert werden. Der Reiter ersetzt keine allgemeine Layoutsoftware, deckt aber die im Arbeitsalltag typischen Standardfälle zuverlässig, schnell und ohne Medienbruch ab.

## 12.1 Wofür der Reiter gedacht ist
- Erstellung neutraler oder individualisierter Titelkarten für Vor- und Nachspann.
- Export der Titelkarte als PNG-Datei im Format 1920 × 1080 Pixel.
- Projektbezogene Ablage der erzeugten Titelkarten im Unterordner 04_output/titlecards.
- Nutzung lokal vorhandener Systemschriftarten des jeweiligen Rechners, ohne dass Bleepling eigene Schriftdateien mitliefern muss.
- Zwischenspeicherung des letzten Bearbeitungsstands in 99_config/titlecards_state.json.

## 12.2 Grundlogik des Reiters
Die Bedienlogik des Reiters ist bewusst einfach gehalten. Links werden die Eingaben und Gestaltungsparameter gesetzt, rechts erscheint eine Live-Vorschau. Aus dieser Vorschau wird anschließend entweder direkt in das Projekt oder frei als PNG-Datei exportiert.
Wichtig ist die klare Trennung der Aufgaben: Der Reiter „Titelkarten“ erzeugt nur statische Bilddateien. Das eigentliche Voranstellen oder Hintenanstellen dieser Bilder erfolgt weiterhin im Reiter „Gezielte Nachbearbeitung“.

## 12.3 Grundlayout und Vorschau
Die Live-Vorschau ist seit Version 1.5.1 stärker als echte Bearbeitungsfläche ausgelegt. Dachzeile, zweite Dachzeile, Titelbox, Logo links unten und Partnerlogo rechts unten können in der Vorschau angeklickt, verschoben und über den Anfasser unten rechts skaliert werden.
Beim Verschieben und Skalieren arbeitet Bleepling mit den Koordinaten des echten 1920-×-1080-Zielbilds. Die Vorschau ist also nur verkleinert dargestellt; gespeichert und exportiert werden die tatsächlichen Layoutwerte für das volle Ausgabeformat.
Damit mittige Layouts leichter gelingen, besitzt die Vorschau eine Einrastfunktion. Wenn die Mitte eines Feldes nahe an der horizontalen oder vertikalen Bildmitte liegt, rastet das Feld dort ein. Währenddessen erscheinen blaue gestrichelte Hilfslinien. Diese Hilfslinien sind reine Bearbeitungshilfen und werden nicht exportiert.
Die Live-Vorschau darf bewusst neutrale Hilfsrahmen, Platzhalter und Bearbeitungslinien anzeigen. Der eigentliche PNG-Export und die später in Videos verwendeten Titelkarten werden dagegen sauber ohne diese Hilfen erzeugt. Ohne eigenes Hintergrundbild ist der Ausgabehintergrund weiß.
Im Bereich „Grundlayout“ kann ein ganzflächiges Hintergrundbild gewählt werden. Dieses kann entweder als eigentliche Hintergrundgrafik dienen oder deaktiviert bleiben, wenn stattdessen eine neutrale Grundfläche mit Platzhaltern verwendet werden soll.
Die Live-Vorschau ist nicht bloß dekorativ, sondern die maßgebliche Arbeitskontrolle. Sie zeigt sofort, wie Dachzeile, Titelbox, Titeltext und Logos voraussichtlich stehen. Platzhalter für leere Dachzeilen dienen dabei nur der Orientierung in der Vorschau und werden nicht automatisch in den PNG-Export übernommen.

## 12.4 Texte und Gestaltung
Im Reiter lassen sich für Dachzeile, zweite Dachzeile und Titel getrennt die wichtigsten Gestaltungsparameter festlegen. Dazu gehören insbesondere Schriftgröße, Textfarbe, Schriftart, Fettdruck, Kursivsatz und die Ausrichtung des Titels.
Zusätzlich können die vertikale Position der Dachzeile und der Titelbox sowie Breite und Höhe der Titelbox direkt gesteuert werden. Damit lässt sich das Layout an verschiedene Hausstile oder konkrete Veranstaltungsgrafiken anpassen, ohne dass dazu externer Layoutaufwand nötig wird.
Leere Felder für Dachzeile oder zweite Dachzeile werden im Export bewusst nicht angezeigt. In der Vorschau können sie bei Bedarf als Orientierung sichtbar bleiben oder gezielt ausgeblendet werden.

## 12.5 Logos und Schriftarten
Für den unteren linken und rechten Bereich können eigene Logos eingebunden werden. Liegen keine Logos vor, zeigt die Vorschau neutrale Platzhalter an. Dadurch bleibt der Reiter auch ohne vorhandene Bilddateien verständlich bedienbar, ohne dass diese Platzhalter versehentlich mit exportiert werden.
Bei den Schriftarten bietet Bleepling die auf dem jeweiligen Rechner vorhandenen Systemschriftarten an. Häufig genutzte Standardschriften werden in der Liste bewusst nach oben sortiert. Die rechtliche Verantwortung für die konkrete Nutzung einer lokal vorhandenen Schriftart liegt jedoch beim Anwender oder bei der Anwenderin. Bleepling selbst liefert keine eigenen Schriftdateien mit.

## 12.6 Export und Speicherung
Beim projektbezogenen Export nach 04_output/titlecards prüft Bleepling seit Version 1.5.1, ob dort bereits eine Datei mit demselben Namen existiert. Ist das der Fall, erscheint eine Sicherheitsabfrage mit Vogelbild. Nur bei Bestätigung wird die vorhandene Datei überschrieben.
Die Layoutpositionen der interaktiven Felder werden zusammen mit dem übrigen Titelkarten-Zustand in 99_config/titlecards_state.json gespeichert. Dazu gehören neben den sichtbaren Text- und Farbwerten auch X-Positionen, Breiten und Höhen der Felder, die teilweise nur über die Live-Vorschau verändert werden.
Praktische Auswirkung: Man kann ein Projekt später wieder öffnen und an derselben Titelkarten-Anordnung weiterarbeiten, ohne die Felder neu ausrichten zu müssen.
Der Reiter unterstützt zwei Exportwege: „In Projekt exportieren“ speichert die PNG-Datei in 04_output/titlecards. „PNG exportieren unter …“ erlaubt dagegen eine freie Ablage an einem beliebigen Speicherort.
Der vorgeschlagene Dateiname wird aus dem Titeltext abgeleitet. Ist der Titel leer, wird standardmäßig „titelkarte.png“ verwendet. Der Dateiname kann vor dem Export jederzeit manuell geändert werden.
Zusätzlich speichert Bleepling den aktuellen Bearbeitungsstand des Reiters projektbezogen. Dadurch stehen beim erneuten Öffnen desselben Projekts die zuletzt gewählten Werte für Layout, Farben, Schriftarten, Positionen und Logos wieder zur Verfügung.

## 12.7 Empfohlener Arbeitsablauf
1. Zunächst entscheiden, ob eine neutrale Titelkarte oder eine Titelkarte auf Basis eines vorhandenen Hintergrundbilds benötigt wird.
1. Dachzeile und Titel nur soweit füllen, wie sie im konkreten Fall tatsächlich gebraucht werden.
1. Bei Bedarf Logos, Farben, Positionen und Größe der Titelbox an den jeweiligen Veranstaltungskontext anpassen.
1. Die Vorschau sorgfältig kontrollieren, insbesondere bei längeren Titeln oder ungewöhnlich breiten Logos.
1. Die Titelkarte entweder direkt in das Projekt oder frei als PNG exportieren.
1. Die exportierte PNG-Datei anschließend im Reiter „Gezielte Nachbearbeitung“ als Vor- oder Nachspannbild verwenden.

## 12.8 Typische Fehler und wie man sie vermeidet
Typischer Fehler: Man erwartet im Reiter „Titelkarten“ bereits das automatische Voranstellen oder Hintenanstellen im Video. Tatsächlich erzeugt der Reiter nur die Bilddatei; die Einbindung in das Video erfolgt später in der gezielten Nachbearbeitung.
Typischer Fehler: Ein sehr langes Veranstaltungslogo wird hochgeladen, aber in der Vorschau nicht kontrolliert. Gerade breite Logos sollten nach dem Einfügen kurz auf Größe, Lesbarkeit und Proportion geprüft werden.
Typischer Fehler: Es wird angenommen, dass alle auf dem Rechner sichtbaren Schriften rechtlich unproblematisch seien. Bleepling stellt zwar die vorhandenen Systemschriftarten bereit, prüft aber nicht deren lizenzrechtliche Zulässigkeit für einen bestimmten Einsatzzweck.

## 12.9 Kurzfazit
Der Reiter „Titelkarten“ ist in seiner aktuellen Form eine praktische, bewusst leichtgewichtige Bildfunktion. Er ist kein allgemeines Grafikprogramm, aber ein sehr nützliches Werkzeug für standardisierte Vor- und Nachspannbilder innerhalb des bestehenden Projektworkflows.

# 13. Reiter Einstellungen / Logs
Der Reiter „Einstellungen / Logs“ ist der technische Kontroll- und Diagnosebereich von Bleepling. Hier wird nicht inhaltlich über Treffer entschieden und es werden auch keine Medien importiert oder gerendert. Stattdessen dient dieser Reiter dazu, die Arbeitsumgebung zu prüfen, projektspezifische Einstellungen zu speichern und Probleme mit Python, FFmpeg, Transkription, GPU-Nutzung oder Darstellung der Oberfläche schneller einzugrenzen.
Kurz gesagt: Dieser Reiter ist das Wartungs-, Diagnose- und Komfortzentrum der App. Er ist besonders dann wichtig, wenn Bleepling auf einem neuen Rechner eingerichtet wird, wenn Transkription oder GPU-Beschleunigung nicht wie erwartet funktionieren oder wenn die Oberfläche an persönliche Bedürfnisse angepasst werden soll.

## 13.1 Wofür der Reiter gedacht ist
- Prüfung, ob die für Bleepling benötigten Programme und Python-Module überhaupt vorhanden und ladbar sind.
- Unterstützung bei der Einrichtung von Transkription, CUDA-/cuDNN-Pfaden und Render-Backend.
- Speichern projektbezogener Einstellungen etwa für Transkriptionsmodus, Whisper-Modell, Compute-Type oder Render-Backend.
- Sofortige Anpassung der Darstellung der Oberfläche, insbesondere Theme und Textgröße.
- Schneller Zugriff auf Installations- und PATH-Befehle sowie auf leicht verständliche Hilfetexte.

## 13.2 Sinnvolle Reihenfolge der Nutzung
Der Reiter „Einstellungen / Logs“ wird in der Praxis vor allem in drei Situationen gebraucht: erstens bei der Ersteinrichtung auf einem neuen Rechner, zweitens bei technischen Problemen und drittens dann, wenn bestimmte Arbeitsweisen dauerhaft oder projektspezifisch gespeichert werden sollen.
Die sinnvolle Reihenfolge lautet meist: zunächst ein Projekt laden, dann die gewünschten Einstellungen prüfen oder ändern, anschließend die technische Prüfung ausführen und erst danach – wenn die Umgebung sauber ist – in die fachlichen Reiter wie „Prüfen & Entscheiden“ oder „Video & Audio / FFmpeg“ wechseln.
Besonders wichtig ist dieser Reiter vor dem ersten Transkriptionslauf. Wenn etwa faster-whisper, ctranslate2 oder FFmpeg fehlen, zeigt sich das hier deutlich früher und übersichtlicher als mitten im eigentlichen Arbeitsprozess.

## 13.3 Bereich „Transkription, GPU, VLC und Darstellung“

## 13.3a Bereich „Rendern / Ausgabe“
Seit Version 1.5.1 enthält der Reiter „Einstellungen / Logs“ einen eigenen Bereich „Rendern / Ausgabe“. Diese Einstellungen sind projektbezogen und beeinflussen insbesondere die gezielte Nachbearbeitung. Sie dienen dazu, technische Render-Parameter sichtbar und nachvollziehbar zu machen, statt sie fest im Programmcode zu verstecken.
Backend: „auto“ nutzt nach Möglichkeit GPU-Encoding, wenn ein NVIDIA-Encoder verfügbar ist, und fällt sonst auf CPU zurück. „gpu“ versucht bevorzugt den NVIDIA-Encoder; ist er nicht verfügbar, arbeitet Bleepling sicherheitshalber mit CPU-Encoding weiter. „cpu“ nutzt bewusst den Prozessor. CPU ist meist langsamer, aber sehr kompatibel.
Qualität (CQ/CRF): Niedrigere Werte bedeuten höhere Qualität und größere Dateien, höhere Werte bedeuten stärkere Kompression und kleinere Dateien. Der Bereich 18 bis 23 ist eher qualitätsorientiert, 24 bis 30 ein typischer Alltagsbereich, 31 bis 38 eher sparsam. Der Standard 30 entspricht dem bisherigen Verhalten der gezielten Nachbearbeitung.
Preset: Das Preset steuert, wie viel Zeit FFmpeg in die Kompression investieren darf. Sehr schnelle Presets wie ultrafast oder veryfast rendern schneller, erzeugen bei vergleichbarer Qualität aber tendenziell größere Dateien. Langsamere Presets wie slow oder veryslow brauchen mehr Zeit, können aber effizienter komprimieren. Bei NVIDIA-GPU werden diese Stufen intern auf passende NVENC-Presets übertragen.
Audio-Bitrate: Die Audio-Bitrate betrifft die AAC-Tonspur. 96k ist der bisherige Standard und für reine Sprache meist ausreichend. 128k ist ein guter allgemeiner Standard, 160k oder 192k sind sinnvoll, wenn Musik, Atmo oder allgemeiner Ton stärker ins Gewicht fallen.
Skalierung: „Originalgröße beibehalten“ verändert die Auflösung nicht und ist der sichere Standard für gezielte Nachbearbeitung. „1280 px Breite“ erzeugt kleinere Web-Dateien, reduziert aber bei größeren Quellen die Detailauflösung. „1920 px Breite“ ist Full-HD-orientiert und kann kleinere Quellen unnötig hochskalieren, ohne echte Bilddetails hinzuzufügen.
Zu jedem dieser Felder gibt es einen Fragezeichen-Button. Diese Hilfen erklären nicht nur den Zweck des Parameters, sondern auch die Bedeutung der jeweiligen Auswahlmöglichkeiten.
Im oberen Bereich des Reiters werden die zentralen technischen Grundeinstellungen gesetzt. Die Benutzeroberfläche bündelt diese bewusst an einer Stelle, damit zusammengehörige Parameter nicht über mehrere Reiter verteilt sind.
Die wichtigsten Einstellfelder sind:

| Einstellung | Bedeutung | Praktischer Hinweis |
| --- | --- | --- |
| Transkriptionsmodus | Legt fest, ob Bleepling automatisch zwischen GPU und CPU wählt oder bewusst nur GPU bzw. nur CPU nutzt. | „auto“ ist der normale Standard. „gpu“ ist nur sinnvoll, wenn die GPU-Einrichtung tatsächlich funktioniert. „cpu“ hilft vor allem zur Fehlersuche oder auf schwächeren/fremden Rechnern. |
| Whisper-Modell | Bestimmt, wie groß und genau das Transkriptionsmodell arbeiten soll. | „Schnell“ ist flotter, „Ausgewogen“ der empfohlene Standard, „Genauer“ oft präziser, aber deutlich langsamer. |
| Compute-Type | Steuert die Rechenart für die Transkription. | Auf modernen NVIDIA-Systemen ist „float16“ meist die beste Standardwahl. Andere Werte sind eher Sonderfälle bei Speicher- oder Stabilitätsproblemen. |
| Zusätzliche CUDA-Pfade | Hier können Ordner ergänzt werden, in denen Bleepling nach CUDA- oder cuDNN-Dateien sucht. | Das ist besonders nützlich, wenn die GPU vorhanden ist, die benötigten DLL-Dateien aber nicht automatisch im Laufzeitpfad gefunden werden. |
| Theme | Schaltet zwischen heller und dunkler Darstellung der Oberfläche um. | Die Änderung wirkt sofort und dient ausschließlich der Bedienbarkeit, nicht der fachlichen Verarbeitung. |
| Render-Backend | Bestimmt, ob FFmpeg nach Möglichkeit die GPU oder nur die CPU nutzen soll. | Diese Einstellung wirkt sich vor allem auf das Verhalten im Reiter „Video & Audio / FFmpeg“ und auf die dortigen Profile aus. |
| Textgröße | Vergrößert oder verkleinert die Darstellung der Schrift in der App. | „Normal“ ist Standard; „etwas größer“ und „groß“ helfen vor allem auf hochauflösenden oder ungünstig skalierten Bildschirmen. |

Besonders praktisch ist, dass Theme und Textgröße sofort wirksam werden. Diese beiden Einstellungen dienen also nicht nur der späteren Speicherung, sondern geben bereits während der Arbeit eine direkte Rückmeldung, ob die Darstellung für den eigenen Arbeitsplatz angenehm ist.

## 13.4 Prüfung und Diagnose
Der mittlere Funktionsbereich des Reiters ist auf technische Selbstdiagnose ausgelegt. Über „Prüfung ausführen“ oder „Prüfung erneut ausführen“ kontrolliert Bleepling, ob die wichtigsten Bestandteile der Arbeitsumgebung vorhanden sind und ob typische GPU-Voraussetzungen erkannt werden.
Geprüft werden dabei insbesondere Python selbst, FFmpeg, die Module faster-whisper, ctranslate2, openpyxl, python-docx, pdfplumber sowie pypdf beziehungsweise PyPDF2. Hinzu kommen in 1.2.0 auch optionale Prüfungen für VLC Desktop, python-vlc, libvlc.dll und den VLC-Plugin-Bestand.
Die Ergebnisse werden in einer Prüfliste mit den Spalten „Prüfpunkt“ und „Status“ dargestellt. So lässt sich schnell erkennen, ob ein Punkt in Ordnung ist oder ob ein Warnhinweis vorliegt.
Wird ein Prüfpunkt in der Liste ausgewählt, erscheinen darunter die zugehörigen Detailinformationen. Gerade bei fehlenden Modulen oder nicht gefundenen DLL-Dateien ist dieser Detailbereich der eigentliche Ort, an dem sich die technische Ursache erkennen lässt.

## 13.5 Hilfe, Details und Erklärungen in normalem Deutsch
Ein sehr benutzerfreundliches Element des Reiters ist die Hilfe in einfachem Deutsch. Neben mehreren Einstellfeldern befinden sich kleine Hilfe-Buttons. Sie erklären die Bedeutung einzelner Optionen so, dass auch nicht ständig mit Python, CUDA oder Render-Backends arbeitende Anwenderinnen und Anwender die Entscheidung besser einordnen können.
Zusätzlich zeigt Bleepling nach einer Prüfung eine schrittweise Handlungsempfehlung an. Diese erklärt in sinnvoller Reihenfolge, wie bei Warnhinweisen vorzugehen ist: Prüfung starten, problematischen Punkt auswählen, Details lesen, Installationsbefehl nutzen oder Zusatzpfad ergänzen und danach die Prüfung erneut ausführen.
Der Reiter ist deshalb nicht nur ein Diagnosewerkzeug für Technikaffine, sondern bewusst auch eine Orientierungshilfe für den normalen Betrieb.
Seit Version 1.5.3 gehört das Anwenderhandbuch selbst direkt zur Anwendung. Oben in der App gibt es den globalen Button „Handbuch öffnen“. Zusätzlich verweisen viele Fragezeichen-Hilfen jetzt nicht nur auf kurze Erklärungstexte, sondern auch direkt auf das passende Kapitel im Benutzerhandbuch.
Im Handbuchfenster selbst kann nach Begriffen gesucht werden. Außerdem lässt sich das aktuelle Handbuch bei Bedarf als HTML-Datei exportieren. Eine ausgelieferte PDF- oder DOCX-Fassung gehört seit Version 1.5.3 nicht mehr zum offiziellen Release-Bestand.

## 13.6 Projekt speichern und was dabei gesichert wird
Mit dem Button „Projekt speichern“ werden die im Reiter gesetzten Werte in die Projekteinstellungen geschrieben. Dazu gehören insbesondere Transkriptionsmodus, Whisper-Modell, Compute-Type, zusätzliche CUDA-Pfade, Theme, Render-Backend und Textgröße.
Praktisch bedeutet das: Ein Projekt kann nicht nur Medien und Bearbeitungsstände enthalten, sondern auch die dazu passende technische Arbeitskonfiguration. Das ist sinnvoll, wenn bestimmte Projekte regelmäßig mit denselben Parametern bearbeitet werden sollen.
Wichtig ist zugleich die Unterscheidung zwischen sofort wirksamer Darstellung und dauerhafter Speicherung. Theme und Textgröße werden bereits beim Umschalten sichtbar angewendet; durch „Projekt speichern“ werden diese Einstellungen zusätzlich dauerhaft gesichert.

## 13.7 Installations-CMD, CUDA-/PATH-CMD und Zusatzpfade
Mehrere Buttons im Reiter dienen nicht der Diagnose selbst, sondern der praktischen Behebung typischer Probleme.
„Installations-CMD kopieren“ kopiert den von Bleepling vorbereiteten Installationsbefehl in die Zwischenablage. In 1.2.0 kann dieser Befehl – soweit vorgesehen – neben den Python-Bausteinen auch die optionale VLC-Komponente berücksichtigen.
„Installations-CMD ausführen“ versucht, ein neues CMD-Fenster zu öffnen und den vorbereiteten Installationsbefehl direkt dort zu starten. Das ist vor allem für die schnelle Nachinstallation fehlender Module oder der optionalen VLC-Umgebung nützlich.
„CUDA-/PATH-CMD kopieren“ erzeugt einen Befehl, mit dem gefundene CUDA-Verzeichnisse in den Laufzeitpfad aufgenommen werden können. Das ist besonders hilfreich, wenn CUDA- oder cuDNN-Dateien zwar vorhanden sind, von Bleepling aber ohne zusätzlichen Pfad nicht gefunden werden.
Das Feld „Zusätzliche CUDA-Pfade“ dient genau diesem Zweck innerhalb der App. Dort können ein oder mehrere Ordner eingetragen werden; Bleepling berücksichtigt diese dann bei der Diagnose und beim Aufbau seiner Laufzeitumgebung.

## 13.8 Zusammenspiel mit den übrigen Reitern
Für die gezielte Nachbearbeitung ist besonders wichtig: Die dortigen Bleep-Zeitpunkte, Vor-/Nachlaufwerte und Vor-/Nachspannbilder werden weiterhin im Reiter „Gezielte Nachbearbeitung“ eingestellt. Die technische Ausgabequalität – Backend, Qualität, Preset, Audio-Bitrate und Skalierung – kommt dagegen aus „Einstellungen / Logs“ > „Rendern / Ausgabe“.
Der normale Reiter „Video & Audio / FFmpeg“ behält seine eigenen Exportprofile. Die neuen zentralen Werte sind vor allem dafür gedacht, dass Nachbearbeitungen nicht mit unsichtbaren Festwerten laufen und dass die Standardentscheidung „Originalgröße beibehalten“ bewusst nachvollziehbar ist.
Der Reiter „Einstellungen / Logs“ wirkt fachlich nicht isoliert, sondern unterstützt mehrere andere Bereiche der App.
Für den Reiter „Prüfen & Entscheiden“ ist er wichtig, weil Transkriptionsmodus, Whisper-Modell, Compute-Type und GPU-Erreichbarkeit unmittelbar beeinflussen, ob und wie schnell aus einer WAV-Datei eine words.json erzeugt und daraus eine Kandidaten-Datei aufgebaut werden kann.
Für den Reiter „Prüfen & Entscheiden“ ist zusätzlich bedeutsam, ob FFmpeg und die Audio-Vorschau sauber arbeiten. Seit Version 1.3.0 ist die optionale VLC-Prüfung außerdem unmittelbar für den Reiter „Schnitt & Kapitel“ relevant, weil dort das interne Schnittfenster auf die VLC-/python-vlc-Umgebung zurückgreift.
Auch für den praktischen Einsatz auf fremden oder neu eingerichteten Rechnern ist dieser Zusammenhang wesentlich: Wenn Transkription oder Rendern in anderen Reitern nicht funktionieren, liegt die Ursache häufig nicht dort selbst, sondern in einer fehlenden oder unvollständigen technischen Umgebung, die in diesem Reiter sichtbar wird.

## 13.9 Typische Fehler und wie man sie vermeidet

| Typischer Fehler | Wie man ihn vermeidet oder behebt |
| --- | --- |
| Prüfung wird gar nicht erst ausgeführt | Zunächst prüfen, ob überhaupt ein Projekt geladen ist und ob die App vollständig gestartet wurde. Danach die Prüfung erneut anstoßen. |
| GPU wird erwartet, aber nicht erkannt | Nicht vorschnell von einem App-Fehler ausgehen. Zuerst die Prüfpunkte zu CUDA-Pfaden, DLL-Dateien und GPU-Probe lesen und gegebenenfalls Zusatzpfade ergänzen. |
| Fehlende Python-Module | Installations-CMD kopieren oder ausführen und danach die Prüfung erneut starten. Entscheidend ist, dass in derselben Python-Umgebung installiert wird, mit der Bleepling läuft. |
| Theme oder Textgröße werden geändert, aber nicht dauerhaft gesichert | Die Vorschau wirkt zwar sofort, sollte aber zusätzlich mit „Projekt speichern“ gesichert werden, wenn die Einstellung erhalten bleiben soll. |
| CPU- oder GPU-Modus ohne Anlass fest erzwingen | Im Zweifel zunächst mit „auto“ arbeiten. Feste Vorgaben sind eher für bekannte Sonderfälle oder gezielte Fehlersuche sinnvoll. |
| PATH-Befehl missverstanden | Der CUDA-/PATH-CMD ist eine Hilfe für die Windows-Umgebung, kein Ersatz für eine fehlende CUDA-/cuDNN-Installation. |

## 13.10 Kurzfazit
Der Reiter „Einstellungen / Logs“ sichert die technische Arbeitsfähigkeit von Bleepling. Er hilft, Installation, Laufzeitumgebung, GPU-Nutzung, Darstellungsfragen und projektbezogene Einstellungen auf einen belastbaren Stand zu bringen, bevor die fachlichen Reiter genutzt werden.
Der Reiter „Einstellungen / Logs“ ist kein Nebenbereich, sondern die technische Absicherung des gesamten Workflows. Er hilft, Transkription, GPU-Nutzung, Dateiformat-Unterstützung und Bedienoberfläche auf einen belastbaren Stand zu bringen. Wer diesen Reiter auf neuen Rechnern oder bei Problemen frühzeitig nutzt, spart später viel Zeit in den fachlichen Reitern.

# 14. Typische Arbeitsabläufe

## 14.1 Standardfall: Video mit Namensbleeps
Dies ist der typische Hauptanwendungsfall der App: Ein Video liegt vor, darin sollen erkannte Namensnennungen geprüft und anschließend datenschutzgerecht gebleept werden. Sinnvoll ist dabei folgende Reihenfolge:
1. Projekt anlegen oder laden.
1. Im Reiter „Medien“ das Ausgangsvideo importieren.
1. Im Reiter „Prüfen & Entscheiden“ aus dem Video eine WAV-Datei erzeugen.
1. Aus der WAV-Datei eine words.json erzeugen.
1. Aus der words.json eine Kandidaten-Datei erzeugen.
1. Optional Teilnehmerliste, Blocklist und Allowlist vorbereiten oder ergänzen.
1. Die Kandidaten auswerten, die Treffer anhören und bei Bedarf feinjustieren.
1. Die globalen Bleep-Parameter anwenden und den Prüfstand speichern.
1. Aus dem Prüfstand eine Times-Datei mit Intervallen ableiten.
1. Im Reiter „Video & Audio / FFmpeg“ das gebleepte Video rendern.
1. Das Endergebnis stichprobenartig ansehen und anhören.
Dieser Ablauf ist der neue Normalfall, weil er technische Vorbereitung, menschliche Prüfung und operative Ableitung der Intervall-Times-Datei in einem Reiter bündelt.

## 14.2 Rohvideos zu Einzelclips vorbereiten
Dieser Ablauf ist neu in Version 1.3.0 und eignet sich für längere Aufzeichnungen, die zunächst in handhabbare Arbeitsclips zerlegt werden sollen.
1. Projekt laden und die relevanten Quellvideos im Reiter „Medien“ bereitstellen.
1. Im Reiter „Schnitt & Kapitel“ die Quellvideos auswählen und in die gewünschte Reihenfolge bringen.
1. Ein Arbeitsvideo bilden oder ein bereits vorhandenes passendes Arbeitsvideo übernehmen.
1. Im Schnittfenster Start- und Endmarken für die gewünschten Abschnitte setzen und daraus einzelne Clips definieren.
1. Die Clips erzeugen und anschließend im Reiter „Prüfen & Entscheiden“ wie normale Projektvideos anonymisieren.

## 14.3 Nur Audio
Liegt kein Video, sondern nur eine Audiodatei vor, verkürzt sich der Ablauf. Eine geeignete WAV-Datei kann direkt importiert oder im Projekt bereitgestellt werden. Danach werden wie gewohnt words.json, Kandidaten-Datei, Trefferliste und Intervall-Times-Datei erzeugt. Im Reiter „Video & Audio / FFmpeg“ wird am Ende nicht „Gebleeptes Video erzeugen“, sondern „Gebleeptes Audio erzeugen“ verwendet.
Praktischer Vorteil dieses Ablaufs: Der fachliche Prüfteil bleibt nahezu identisch; lediglich der Exporttyp ändert sich.

## 14.4 Teilnehmerliste importieren
Der Import einer Teilnehmerliste ist besonders sinnvoll, wenn in einem Seminar, einer Besprechung oder einer Aufzeichnung von Beginn an bekannt ist, welche Namen im Material typischerweise vorkommen. Die Teilnehmerliste dient dabei als Hilfsmittel für die spätere Prüfung, nicht als Ersatz für die eigentliche Trefferdatei.
Empfohlener Ablauf: Teilnehmerliste importieren, bei Bedarf Nachnamen, Vornamen oder beide gemeinsam übernehmen und die Einstellung bei Bedarf über „Akt.“ neu anwenden. Anschließend Kandidaten-Datei auswerten und die Trefferliste kontrollieren. Gerade bei ähnlichen oder häufigen Namen bleibt die manuelle Sichtprüfung unverzichtbar.

## 14.5 Schnell-Nachbleepen
Schnell-Nachbleepen ist für den Fall gedacht, dass nach der ersten Auswertung noch einzelne zusätzliche Verdachtsstellen oder Nachträge erzeugt werden sollen. Die Funktion eignet sich deshalb vor allem für einen zweiten Korrekturdurchgang.
Sinnvoll ist diese Funktion insbesondere dann, wenn die erste Intervall-Times-Datei bereits weitgehend tragfähig ist, aber noch einzelne zusätzliche Zeitbereiche ergänzt werden müssen.

## 14.6 Gezielte Nachbearbeitung
Vor einer gezielten Nachbearbeitung lohnt sich ein kurzer Blick in „Einstellungen / Logs“ > „Rendern / Ausgabe“. Dort sollte insbesondere die Skalierung geprüft werden. Für Korrekturen an bereits fertigen Videos ist „Originalgröße beibehalten“ meist die richtige Wahl.
Wenn kleinere Webdateien gewünscht sind, kann bewusst 1280 px Breite gewählt werden. Das sollte aber eine fachliche Entscheidung sein, weil es bei größeren Quellen sichtbar Details reduziert.
Für wiederkehrende Veranstaltungsformate Titelkarten nach Möglichkeit projektbezogen erzeugen und im Reiter „Gezielte Nachbearbeitung“ weiterverwenden, statt jedes Vor- oder Nachspannbild extern neu zu bauen.
Die gezielte Nachbearbeitung ist der richtige Weg, wenn ein Medium bereits fertig oder nahezu fertig gerendert wurde und danach nur noch punktuelle Ergänzungen nötig sind, etwa zusätzliche Bleeps, ein Vorspannbild oder ein Nachspannbild.
Empfohlener Ablauf: Zuerst die reguläre Fassung erzeugen, anschließend diese Fassung im Reiter „Gezielte Nachbearbeitung“ auswählen, gewünschte Zusatzzeiten und Bildergänzungen eintragen und danach die Änderungen rendern.

## 14.7 Treffer im Audio feinprüfen
Dieser Ablauf ist nun vollständig in den Reiter „Prüfen & Entscheiden“ integriert. Auffällige Treffer können dort in der Trefferliste ausgewählt, im kurzen Prüfclip angehört und bei Bedarf vorne oder hinten in Millisekundenschritten nachjustiert werden.
Wichtig ist dabei: Nach Änderungen an globalen Bleep-Parametern oder individuellen Trefferspannen sollte die Times-Datei erneut aus den sichtbaren Intervallen abgeleitet werden, damit der FFmpeg-Reiter denselben Stand rendert.

# 15. Häufige Missverständnisse und wichtige Hinweise
Im praktischen Einsatz entstehen manche Fehler nicht wegen technischer Probleme, sondern wegen falscher Erwartungen an die Arbeitslogik der App. Die folgenden Hinweise helfen, typische Missverständnisse früh zu vermeiden.
Eine Teilnehmerliste ist keine Kandidaten-Datei. Sie enthält Namen, aber keine Zeitstempel und kann deshalb keine Times-Datei ersetzen.
Eine Blocklist erzwingt keinen automatischen Bleep. Sie erhöht nur die Aufmerksamkeit bei der Auswertung.
Die Allowlist hat in der Freigabelogik Vorrang. Sie verhindert, dass bestimmte Namen oder Schreibweisen unnötig gebleept werden.
Maßgeblich für das spätere Bleepsignal ist nicht mehr eine bloße Punkt-Times-Datei, sondern die aus dem Reiter „Prüfen & Entscheiden“ abgeleitete Times-Datei mit Intervallen.
Globale Bleep-Parameter gelten im neuen Prüfreiter zunächst für alle Treffer. Individuelle Korrekturen pro Treffer kommen zusätzlich hinzu und ersetzen die globalen Werte nicht vollständig.
Änderungen an den globalen Bleep-Parametern werden erst nach „Anwenden“ verbindlich. Erst danach sollte weiter geprüft, gespeichert oder eine Times-Datei abgeleitet werden.
Eine Änderung der Blocklist oder Allowlist wirkt sich nicht rückwirkend auf die bereits erzeugte Kandidaten-Datei aus, wohl aber auf deren erneute Bewertung. Wer nach dem Anpassen von Blocklist oder Allowlist eine neue Trefferliste erhalten möchte, muss die Auswertung erneut starten.
Eine Änderung der Namenserkennungslogik oder der zugrunde liegenden words.json erfordert dagegen einen neuen Lauf über „Kandidaten aus words.json erzeugen“, weil sich dabei die eigentliche Kandidatenbasis ändert.
Die Mehrfachauswahl in der Trefferliste sollte bewusst genutzt werden, insbesondere per Strg-Klick, Umschalt-Klick, Umschalt plus Pfeiltasten und Strg+A, wenn größere Gruppen von Treffern gemeinsam bearbeitet werden sollen.
Der FFmpeg-Reiter ist nicht der richtige Ort, um Bleep-Länge oder Bleep-Lage fachlich nachzujustieren. Diese Festlegung gehört in den Reiter „Prüfen & Entscheiden“.

# 16. Häufige Fehler und Lösungen
Hilfsrahmen oder graue Flächen in Titelkarten: Die Live-Vorschau zeigt bewusst Bearbeitungshilfen. In der echten Ausgabe dürfen diese nicht erscheinen. Wenn sie dennoch sichtbar sind, prüfen, ob die Titelkarte mit der aktuellen Version neu exportiert wurde.
Gezielte Nachbearbeitung verändert unerwartet die Auflösung: Im Reiter „Einstellungen / Logs“ den Bereich „Rendern / Ausgabe“ prüfen. Für unveränderte Auflösung muss „Originalgröße beibehalten“ gewählt sein.
Projekt soll gelöscht werden, aber Bleepling verweigert das Löschen: Dann erkennt Bleepling den gewählten Ordner nicht als vollständiges Projekt. In diesem Fall wird bewusst nichts gelöscht; stattdessen fehlende oder ungültige Projektbestandteile prüfen.
Die folgende Übersicht bündelt typische praktische Störungen oder Unsicherheiten und zeigt, wo in Bleepling der naheliegende Ansatz zur Behebung liegt.
Fehlende Python-Bibliotheken: Im Reiter „Einstellungen / Logs“ die Prüfung ausführen, den fehlenden Prüfpunkt auswählen und den Installationsbefehl kopieren oder direkt per CMD starten.
FFmpeg wird nicht gefunden: Prüfen, ob FFmpeg installiert ist und im Windows-PATH liegt. Danach die Prüfung erneut ausführen.
GPU wird nicht genutzt: Transkriptionsmodus, Compute-Type, Zusatzpfade und Diagnose im Reiter „Einstellungen / Logs“ kontrollieren. Gegebenenfalls CUDA- oder cuDNN-Ordner ergänzen.
Whisper-Modell oder HuggingFace-Cache meldet Zugriffsfehler: Prüfen, ob der Cacheordner beschreibbar ist. Standard ist häufig C:\Users\<Benutzer>\.cache\huggingface. Alternativ kann ein eigener beschreibbarer Cachepfad über HF_HOME oder HF_HUB_CACHE gesetzt werden.
PDF-Teilnehmerliste liefert schlechte Ergebnisse: Nach Möglichkeit auf XLSX ausweichen oder die PDF-Struktur prüfen. Nicht jeder PDF-Inhalt ist zuverlässig auslesbar.
Zu viele oder zu wenige Treffer in der Trefferliste: Blocklist, Allowlist und Fuzzy-Werte nachschärfen und die Auswertung erneut starten.
Geänderte globale Bleep-Parameter wirken nicht sichtbar: Im Reiter „Prüfen & Entscheiden“ nach der Änderung auf „Anwenden“ klicken und danach die Trefferliste sowie gegebenenfalls die Times-Datei neu ableiten.
Gebleepte Stellen im finalen Rendern klingen anders als in der Prüfung: Prüfen, ob die richtige Intervall-Times-Datei verwendet wurde und ob nach den letzten Änderungen an Parametern oder Treffern eine neue Times-Datei abgeleitet wurde.
Rendern dauert sehr lange oder die Datei wird zu groß: Im Reiter „Video & Audio / FFmpeg“ ein passenderes Exportprofil wählen, Skalierung und Qualitätswert prüfen und gegebenenfalls GPU-Encoding nutzen.
Falsches Medium oder falsche Times-Datei verwendet: Vor jedem Rendern prüfen, ob Ausgangsmedium und Times-Datei wirklich zum selben Bearbeitungsstand gehören.

# 17. Unterstützte Formate und Grenzen
Bleepling unterstützt im aktuellen Projektstand die folgenden Formate und Arbeitsstände. Entscheidend ist dabei weniger die theoretische Dateiendung als die Frage, ob das Material in der konkreten Situation sauber eingelesen und weiterverarbeitet werden kann.
Für die Namenserkennung ist außerdem zu beachten, dass die Qualität der Kandidaten stark von der Qualität der words.json abhängt. Werden Namen in der Transkription selbst falsch, unvollständig oder uneinheitlich erkannt, kann auch die nachgelagerte Kandidatenlogik nur eingeschränkt zuverlässig arbeiten.
Videoquellen: insbesondere MP4, MOV, MKV, AVI, M4V und WMV für den Import in den Reiter „Medien“.
Audioquellen: insbesondere WAV als bevorzugtes Arbeitsformat für Transkription, Prüfung und weitere Verarbeitung.
Teilnehmerlisten: TXT, CSV, XLSX, DOCX und PDF.
Arbeitsdateien innerhalb des Projekts: words.json, Kandidaten-Dateien, reviewed-Dateien und Times-Dateien. Im neuen Prüfworkflow werden Times-Dateien als Intervalle abgeleitet.
Grenzen bestehen vor allem dort, wo Dateien zwar formal lesbar sind, aber strukturell ungünstig aufgebaut wurden. Das betrifft insbesondere PDF-Dateien mit uneinheitlicher Tabellenstruktur oder Inhalte, die eher als Bild denn als echter Text vorliegen. In solchen Fällen ist XLSX für Namenslisten im Regelfall deutlich robuster.
Für den Export ist außerdem zu beachten, dass nicht jedes technisch mögliche Format gleichermaßen sinnvoll ist. Für browsernahe Videoausgaben ist H.264 mit AAC im Regelfall die sicherste Wahl. Reine Audioausgaben sollten bewusst als Audio und nicht künstlich als Video exportiert werden.
Wenn nach einer Änderung an Blocklist oder Allowlist ein neuer Prüfstand gewünscht ist, die vorhandene Kandidatenbasis aber gleich bleiben soll, genügt ein erneuter Lauf über „Auswertung starten“; eine neue Kandidatenerzeugung ist dafür nicht nötig.
Gerade bei isolierten Vornamen empfiehlt sich trotz verbesserter Heuristik weiterhin ein besonders sorgfältiger Kontrolllauf, weil diese Fälle kontextabhängiger und damit störanfälliger sind als eindeutige Nachnamen.

# 18. Empfehlungen für den praktischen Einsatz
Für den praktischen Einsatz von Bleepling haben sich einige Grundsätze als besonders hilfreich erwiesen. Sie betreffen weniger einzelne Buttons als die gesamte Arbeitsweise mit der App.
Für Teilnehmerlisten möglichst XLSX bevorzugen, weil dieses Format im Regelfall am zuverlässigsten strukturierte Namen liefert.
Vor dem finalen Rendern die Trefferliste sorgfältig prüfen und nicht allein auf automatische Trefferlogik vertrauen.
Blocklist und Allowlist bewusst als Hilfsmittel verstehen, nicht als endgültige Entscheidungsebene.
Globale Bleep-Parameter im Reiter „Prüfen & Entscheiden“ bewusst festlegen und nach Änderungen immer auf „Anwenden“ klicken.
Nach wesentlichen Änderungen an Treffern oder Parametern eine neue Intervall-Times-Datei ableiten, bevor im FFmpeg-Reiter gerendert wird.
Bei neuen oder fremden Rechnern zuerst den Reiter „Einstellungen / Logs“ nutzen, um Python-Bausteine, FFmpeg und GPU-Pfade zu prüfen.
Bei wichtigen Veröffentlichungen oder sensiblen Inhalten immer einen zusätzlichen Kontrolllauf einplanen.
Pro Fall möglichst ein eigenes Projekt verwenden und die Projektstruktur nicht manuell zerlegen oder vermischen.
Die wichtigste Empfehlung lautet jedoch: Bleepling ist ein starkes Werkzeug zur Entlastung, aber keine vollautomatische Garantie gegen Datenschutzfehler. Gerade bei Veröffentlichungen oder Weitergaben mit Außenwirkung sollte deshalb immer noch eine persönliche Endkontrolle stattfinden.

# 19. Geänderte Dateien in Version 1.5.3 gegenüber der Vorversion 1.5.2
- src/bleepling/utils/handbook_dialog.py – integrierten Handbuch-Viewer mit Suche, Kapitelsprüngen und HTML-Export ergänzt.
- src/bleepling/utils/help_dialog.py – Hilfe-Popups so erweitert, dass sie direkt auf passende Kapitel im Benutzerhandbuch verweisen können.
- src/bleepling/gui/main_window.py – globalen Button „Handbuch öffnen“ in die Kopfzeile der Anwendung aufgenommen.
- src/bleepling/tabs/bleeping_tab.py, src/bleepling/tabs/combined_review_tab.py, src/bleepling/tabs/cut_tab.py, src/bleepling/tabs/media_tab.py und src/bleepling/tabs/settings_tab.py – vorhandene Hilfe-Einstiege auf die neue Handbuchlogik umgestellt.
- docs/Bleepling_Benutzerhandbuch.md – Benutzerhandbuch als zentrale Projektquelle aufgenommen, redaktionell geglättet, Anker im Inhaltsverzeichnis vereinheitlicht und auf Version 1.5.3 fortgeschrieben.
- README.md, CHANGELOG.md, CONTRIBUTING.md, SECURITY.md, RELEASE_CHECKLIST_Bleepling.md und RELEASE_NOTES_1.5.3.md – Dokumentation und Release-Unterlagen auf den Stand 1.5.3 gebracht.
- .gitignore – erzeugte Handbuch-Exporte wie HTML oder PDF vom Repository getrennt.
- docs/Bleepling_Benutzerhandbuch.pdf – aus dem offiziellen Release-Bestand entfernt; das Handbuch wird nicht mehr als ausgelieferte PDF-Datei veröffentlicht.
In Version 1.5.3 wurde vor allem der Dokumentations- und Hilfeworkflow neu aufgesetzt: Das Anwenderhandbuch ist jetzt Teil der Anwendung, Hilfe-Buttons führen gezielt an die passende Stelle, und veröffentlichte Handbuchformate außerhalb des Projekts werden nicht mehr mit ausgeliefert.

# 20. Geänderte Dateien in Version 1.5.2 gegenüber der Vorversion 1.5.1
- src/bleepling/tabs/bleeping_tab.py – Erzeugung der words.json wieder an die echte Transkription angebunden; Platzhalterausgabe entfernt; WAV-Erzeugung über den zentralen Service vereinheitlicht.
- src/bleepling/services/bleeping_service.py – Fallback auf faster-whisper ergänzt, wenn das Legacy-Transkriptionsskript nicht vorhanden ist; verständlichere Fehlermeldung bei HuggingFace-Cacheproblemen ergänzt.
- src/bleepling/tabs/combined_review_tab.py – kombinierter Prüfworkflow nutzt denselben echten words.json-Erzeugungsweg wie der Reiter „Prüfen & Entscheiden“.
- src/bleepling/models/project.py und src/bleepling/services/project_service.py – eigener Ausgabeordner 04_output/audio für gebleepte Audiodateien ergänzt.
- src/bleepling/tabs/ffmpeg_tab.py – Audioausgabe in den neuen Audio-Ausgabeordner verlagert und temporäre Dateien robuster bereinigt.
- src/bleepling/tabs/targeted_edit_tab.py – gezielte Nachbearbeitung unter Windows robuster gemacht, insbesondere beim finalen Schreiben und Aufräumen temporärer Renderdateien.
- start_bleepling.bat, start_bleepling_silent.bat und start_bleepling_debug.bat – Startskripte vereinheitlicht; Debug-Start zeigt Arbeitsordner, PYTHONPATH und Python-Version an.
- tools/function_smoke_test.py und tools/gui_full_test.py – lokale Funktionstests und GUI-Integrationstest ergänzt. Die Testwerkzeuge nutzen lokale, ignorierte Testdaten und veröffentlichen keine Testmedien.
- .gitignore – lokale Testdaten, temporäre Testprojekte und lokale Arbeitsdateien vom GitHub-Release ausgeschlossen.
Veröffentlichungsrelevante Dokumentation
docs/Bleepling_Benutzerhandbuch.md – Benutzerhandbuch-Inhalt auf den Stand der Version 1.5.2 fortgeschrieben.
In Version 1.5.2 wurde vor allem der reale Transkriptionsweg abgesichert: Aus WAV-Dateien entstehen wieder echte words.json-Dateien mit Wort-Zeitmarken statt leerer Platzhalter. Zusätzlich wurden Audioausgaben, temporäre Renderdateien, Startskripte und lokale Testabsicherung für den Veröffentlichungsstand geglättet.

# 21. Geänderte Dateien in Version 1.5.1 gegenüber der Vorversion 1.5.0
- src/bleepling/__init__.py – Versionsstand auf 1.5.1 erhöht.
- src/bleepling/gui/main_window.py – globale Mausrad- und Rechtsklick-Behandlung erweitert; Kontextmenü für Eingabefelder ergänzt; Combobox-Scrollfehler abgefangen.
- src/bleepling/tabs/project_tab.py – Button zum Löschen vollständiger bestehender Projekte ergänzt, inklusive Sicherheitsprüfung und Bestätigungsdialog.
- src/bleepling/tabs/titlecards_tab.py – interaktive Layoutfelder, mittiges Einrasten, Überschreibwarnung und saubere Exportausgabe ohne Vorschauhilfen ergänzt.
- src/bleepling/tabs/settings_tab.py – neuer Bereich „Rendern / Ausgabe“ mit Backend, Qualität, Preset, Audio-Bitrate, Skalierung und erklärenden Hilfen.
- src/bleepling/tabs/targeted_edit_tab.py – gezielte Nachbearbeitung nutzt zentrale Render-Parameter und behält standardmäßig die Originalgröße bei.
- src/bleepling/models/project.py – projektbezogene Standardwerte für zentrale Render-Parameter ergänzt.
- README.md, CHANGELOG.md, RELEASE_NOTES_1.5.1.md, RELEASE_CHECKLIST_Bleepling.md, SECURITY.md und CONTRIBUTING.md – Dokumentation und Release-Unterlagen auf Version 1.5.1 fortgeschrieben.
- docs/Bleepling_Benutzerhandbuch.md – Benutzerdokumentation mit den neuen Bedien- und Renderfunktionen in die fortgeschriebene Projektdokumentation übernommen.
Veröffentlichungsrelevante Dokumentation
docs/Bleepling_Benutzerhandbuch.md – Benutzerhandbuch auf den damaligen Stand der Version 1.5.1 fortgeschrieben.
In Version 1.5.1 wurde der Projektstand vor allem an den Stellen nachgeschärft, die sich im längeren Echtbetrieb gezeigt haben: sicherere Bedienung, interaktive Titelkarten-Layouts, saubere Trennung zwischen Vorschau und Export, zentrale Render-Parameter und robustere globale Eingabebedienung.
