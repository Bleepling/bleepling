# Changelog

Alle nennenswerten Änderungen an **Bleepling** sollen in dieser Datei dokumentiert werden.

Die Struktur orientiert sich an einer einfachen, für Open-Source-Projekte gut lesbaren Versionshistorie.

## [1.5.1] - 2026-04-21

### Hinzugefügt
- rechter Mausklick mit Kontextmenü für Eingabefelder, Textfelder, Spinboxen und Comboboxen in allen Reitern
- Sicherheitsabfrage beim Export von Titelkarten in den Projektordner, wenn eine Datei mit gleichem Namen bereits existiert
- vogelgestützte Bestätigungsdialoge für kritische Aktionen wie Überschreiben von Titelkarten und Löschen von Projekten
- Button **„Bestehendes Projekt löschen“** im Reiter **„Projekt“**, bewusst rechts am Fensterrand positioniert
- interaktive Layout-Bearbeitung im Reiter **„Titelkarten“**: Dachzeile, zweite Dachzeile, Titelbox sowie beide Logo-Felder lassen sich in der Live-Vorschau verschieben und skalieren
- mittige Einrastfunktion mit sichtbaren Hilfslinien für Titelkarten-Layoutfelder
- zentrale Render-Einstellungen im Reiter **„Einstellungen / Logs“** unter **„Rendern / Ausgabe“** mit Backend, Qualität, Preset, Audio-Bitrate und Skalierung
- erklärende Fragezeichen-Hilfen zu allen neuen Render-Parametern

### Geändert
- die gezielte Nachbearbeitung übernimmt Codec, Qualität, Preset, Audio-Bitrate und Skalierung aus den zentralen Render-Einstellungen
- Standard für die gezielte Nachbearbeitung bleibt **Originalgröße beibehalten**, damit vorhandene Videos nicht unbemerkt herunterskaliert werden
- die echte Titelkarten-Ausgabe ist jetzt strikt von der Bearbeitungsansicht getrennt: Hilfsrahmen, Platzhalter und graue Vorschauflächen bleiben ausschließlich in der Live-Vorschau
- der Reiter **„Titelkarten“** speichert zusätzliche Layoutdaten für X-Positionen, Breiten und Höhen der interaktiven Felder
- globale Mausrad-Behandlung ist robuster gegenüber Tkinter-Combobox-Dropdowns, die Widgetpfade als String liefern

### Behoben
- Fehlermeldung beim Scrollen geöffneter Combobox-Dropdowns mit dem Mausrad
- versehentliches Überschreiben bestehender Titelkarten im Projektordner ohne Nachfrage
- fehlende Möglichkeit, vollständige bestehende Projektordner über die Oberfläche zu löschen
- graue Vorschauhintergründe und Hilfsrahmen konnten in exportierten oder nachträglich gerenderten Titelkarten sichtbar werden

## [1.5.0] - 2026-04-18

### Hinzugefügt
- Medien-Reiter als deutlich umfassendere Projektübersicht mit getrennten Bereichen für Quellvideos, Projektclips, Transkriptionsdateien, Kandidatenstände, Arbeitsvideos, Output-Dateien und Titelkarten
- abschnittsbezogene Buttons **„Ordner öffnen“** im Medien-Reiter
- zusätzliche Schalter zum gezielten Ausblenden von Dachzeile und zweiter Dachzeile im Reiter **„Titelkarten“**
- Buttons **„Output-Ordner öffnen“** und **„Ergebnis abspielen“** im Reiter **„Gezielte Nachbearbeitung“**

### Geändert
- Titelkarten-Vorschau und PNG-Export sind jetzt sauber getrennt: Platzhalter für Dachzeilen bleiben reine Vorschauhilfen
- Hintergrundbilder im Reiter **„Titelkarten“** werden auf das Zielformat eingepasst, statt unkontrolliert beschnitten zu werden
- Vor- und Nachspannbilder in **„Gezielte Nachbearbeitung“** werden mit synchron verlängerter stiller Audiospur zusammengesetzt
- Kommawerte wie `8,5` werden bei Vor- und Nachspandauern akzeptiert
- vorhandene Output-Dateien in der gezielten Nachbearbeitung werden nicht mehr überschrieben, sondern automatisch mit Suffixen wie `-01` fortgeschrieben
- Button-Hover, Mausrad-Scrolling und Fenster-/Dialogverhalten wurden reiterübergreifend vereinheitlicht
- der Reiter **„Einstellungen / Logs“** wurde sprachlich bereinigt; doppelte Prüf-Buttons entfallen
- README, Release-Unterlagen und Benutzerdokumentation auf den Stand **1.5.0** fortgeschrieben

### Behoben
- Abbruchlogik beim Rendern von Arbeitsvideos, Clips und FFmpeg-Exports funktioniert jetzt tatsächlich, statt Benutzerabbrüche als Fehler zu melden
- der Fortschrittsdialog im FFmpeg-Export bleibt bei vielen Bleeps in Schritt 1 sichtbar aktiv
- bereits exportierte Titelkarten werden in der gezielten Nachbearbeitung zuverlässig wiedergefunden und als Ausgangspfad angeboten
- Medienlisten zeigen keine fachlich irreführenden Mischkategorien mehr wie JSON-Dateien zwischen Arbeitsvideos
- Auswahldialoge im Reiter **„Schnitt & Kapitel“** öffnen mittig statt links oben
- verschiedene Status-, Hilfe- und Wartetexte wurden sprachlich geglättet und an die tatsächliche Logik angepasst

## [1.4.1] - 2026-04-16

### Geändert
- Teilnehmerlisten im Reiter **„Prüfen & Entscheiden“** lassen sich jetzt flexibler als **Nachnamen**, **Vornamen** oder in kombinierter Form übernehmen
- der kombinierte Prüf-Reiter zeigt für **Blocklist** und **Allowlist** jetzt kleine, laufend aktualisierte Summenzähler direkt in der Oberfläche
- im Bereich der Teilnehmerlisten steht zusätzlich ein expliziter Button **„Akt.“** zur Verfügung, um die zuletzt importierte Liste mit den aktuell gesetzten Namensoptionen gezielt neu aufzubauen
- README, Release-Unterlagen und Benutzerdokumentation auf den Stand **1.4.1** fortgeschrieben

### Behoben
- PDF-Teilnehmerverzeichnisse mit tabellarischer Struktur werden robuster gelesen, insbesondere wenn Spalten in der Textausgabe verrutschen
- kurze echte Nachnamen aus Teilnehmerverzeichnissen werden im PDF-Import nicht mehr unnötig verworfen
- bereits importierte Teilnehmerlisten lassen sich im sichtbaren Reiter **„Prüfen & Entscheiden“** jetzt zuverlässig neu anwenden, ohne manuelle Blocklist-Einträge zu verlieren
- die sichtbare Oberfläche des kombinierten Prüf-Reiters und die interne Teilnehmerlisten-Logik des zugrunde liegenden Bleeping-Reiters wurden wieder auf denselben funktionalen Stand gebracht

## [1.4.0] - 2026-04-15

### Hinzugefügt
- erweiterter Reiter **„Titelkarten“** mit zusätzlicher **zweiter Dachzeile / Untertitel**
- getrennte Gestaltungsparameter für **Dachzeile**, **zweite Dachzeile** und **Titel** einschließlich Schriftgröße, Farbe, Position sowie Fett-/Kursiv-Schaltung
- sichtbare Platzhalter in der Live-Vorschau für leere Dachzeilen- und Logobereiche zur besseren Layout-Orientierung
- klarere Detail- und Hilfebereiche im Reiter **„Einstellungen / Logs“** mit sichtbaren Einrichtungsbefehlen

### Geändert
- der Reiter **„Titelkarten“** verarbeitet manuelle Zeilenumbrüche im Titel jetzt direkt in Vorschau und Export
- längere oder mehrzeilige Titel werden innerhalb der Titelbox robuster eingepasst, statt vorzeitig abgeschnitten zu werden
- vertikale Zentrierung, Zeilenabstände und Vorschauverhalten im Titelkarten-Layout wurden sichtbar verfeinert
- die Bedienoberfläche des Reiters **„Titelkarten“** wurde für Dachzeile, zweite Dachzeile und Titel kompakter und nachvollziehbarer angeordnet
- der Reiter **„Einstellungen / Logs“** wurde sprachlich und visuell geglättet; Prüfdetails, Hilfetexte und Einrichtungsbefehle sind jetzt klarer getrennt
- interne Hilfs- und Service-Strukturen für Zeitlogik, Render-Helfer und Reiterkopplungen wurden weiter bereinigt, ohne den Fachworkflow sichtbar zu ändern
- Dokumentation, README und Release-Unterlagen auf den Stand **1.4.0** fortgeschrieben

### Behoben
- unnötig langsame Reiterwechsel durch zu breit ausgelöste Aktualisierungen beim Tab-Wechsel
- wiederholte Vorschau-Neuberechnungen im Reiter **„Titelkarten“** beim Laden gespeicherter Zustände
- fehlerhafte oder unvollständige Darstellung mehrzeiliger Titel in der Titelbox
- inkonsistente Stilumschaltung bei Fett-/Kursiv-Kombinationen im Titelkarten-Layout
- uneinheitliches Erscheinungsbild von Hilfe-Dialogen in mehreren Reitern

### Hinweise
- Die zweite Dachzeile im Reiter **„Titelkarten“** ist als regulärer zusätzlicher Textblock gedacht und kann projektspezifisch leer bleiben oder aktiv genutzt werden.
- Für Titelkarten werden weiterhin nur lokal verfügbare Systemschriftarten verwendet; eigene Font-Dateien werden nicht mitgeliefert.
- Die technische Diagnose im Reiter **„Einstellungen / Logs“** unterstützt weiterhin bei der Einrichtung externer Komponenten, ersetzt aber keine manuelle Prüfung der lokalen Umgebung.

## [1.3.0] - 2026-04-12

### Hinzugefügt
- neuer Reiter **„Schnitt & Kapitel“** als zusätzlicher Vorbau vor den bisherigen Prüfworkflow
- Bildung eines projektbezogenen **Arbeitsvideos** aus ausgewählten Quellvideos
- internes **Schnittfenster** mit eingebetteter Vorschau, Sprungbuttons und Markensetzung
- Möglichkeit, Start- und Endmarken manuell zu setzen und daraus einzelne Clips anzulegen
- Erzeugung ausgewählter oder aller Clips als neue Projektmedien
- Wiederverwendung vorhandener Arbeitsvideos einschließlich Auswahl- und Erkennungslogik
- Hilfe-Buttons im Hauptreiter **„Schnitt & Kapitel“** und im zugehörigen Schnittfenster
- projektbezogene Clip-Logik mit Dateinamensvorschlägen und Validierung

### Geändert
- sichtbarer Hauptworkflow erweitert um den Reiter **„Schnitt & Kapitel“**
- Dokumentation, README und Release-Unterlagen auf den Stand **1.3.0** fortgeschrieben
- Reiter **„Einstellungen / Logs“** und Third-Party-Hinweise berücksichtigen die optional genutzte VLC-/libVLC-Umgebung nun auch im Zusammenhang mit dem neuen Schnitt-Reiter
- Benutzerdokumentation um den neuen vorbereitenden Schnitt-Workflow ergänzt

### Behoben
- fehlende oder inkonsistente Fortschreibung von Clip-Dateinamen bei mehrfacher Clip-Erzeugung
- fehlende Plausibilitätsprüfung, wenn Endmarke vor oder auf Startmarke liegt
- fehlerhafte Weiterverwendung bereits vorhandener Arbeitsvideos
- UI-Unklarheiten bei Clip-Erzeugung und fehlende Rückmeldung bei längeren Clip-Renderläufen
- Ton, der nach dem Schließen des Schnittfensters im Hintergrund weiterlief

### Hinweise
- Der Reiter **„Schnitt & Kapitel“** ergänzt den bisherigen Direktworkflow, ersetzt ihn aber nicht. Wer mit bereits vorbereiteten Einzelvideos arbeitet, kann weiterhin direkt mit **„Prüfen & Entscheiden“** beginnen.
- Die eingebettete Vorschau im Schnittfenster nutzt eine lokal vorhandene **VLC-/libVLC-Umgebung**, soweit diese installiert ist.
- Eine menschliche Endkontrolle anonymisierter Medien bleibt weiterhin erforderlich.

## [1.2.1] - 2026-04-12

### Hinzugefügt
- neuer Reiter **„Titelkarten“** zur Erstellung von PNG-Titelkarten im Format **1920 × 1080**
- projektbezogener Export von Titelkarten nach `04_output/titlecards`
- projektbezogene Speicherung des Titelkarten-Zustands in `99_config/titlecards_state.json`
- größere Live-Vorschau mit neutraler Standardansicht im Titelkarten-Reiter
- zusätzliche Regler für **Y-Position der Dachzeile**, **Y-Position der Titelbox**, **Breite der Titelbox** und **Höhe der Titelbox**

### Geändert
- Systemschriftarten werden im Reiter **„Titelkarten“** dynamisch aus dem jeweiligen Windows-System geladen
- gängige Standardschriftarten werden in der Auswahlliste bevorzugt nach oben sortiert
- leere Dachzeilen- und Titelfelder werden in der Vorschau nicht mehr künstlich angezeigt
- neutrale Startansicht im Titelkarten-Reiter ohne veranstaltungsspezifische Demo-Inhalte
- bestehende Projekte werden beim Laden um die neue Titelkarten-Struktur ergänzt, statt wegen fehlender Unterordner abgewiesen zu werden
- Benutzerdokumentation, README und Release-Unterlagen auf den Stand **1.2.1** fortgeschrieben

### Behoben
- Import- und Ladeprobleme älterer Projekte wegen fehlendem Ordner `04_output/titlecards`
- unpassende oder irreführende Standardinhalte in der neutralen Vorschau des Titelkarten-Reiters
- Verlust der Layout-Steuerung für vertikale Position und Größe der Titelbox in einer Zwischenfassung
- unnötig kleine Vorschau und störende Platzhalterreste in frühen Fassungen des Titelkarten-Reiters

### Hinweise
- Für Schriftarten werden **keine Font-Dateien mitgeliefert**
- Die Nutzungs- und Lizenzprüfung verwendeter Systemschriftarten liegt beim jeweiligen Anwender
- Titelkarten sind eine Ergänzung des bestehenden Workflows und können insbesondere in Verbindung mit dem Reiter **„Gezielte Nachbearbeitung“** für Vor- und Nachspannbilder verwendet werden

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
