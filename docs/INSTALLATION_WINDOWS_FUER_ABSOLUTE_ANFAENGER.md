# Bleepling unter Windows installieren

![Bleepling-Icon](../assets/vogel1_appicon_512.png)

Diese Anleitung ist für Menschen geschrieben, die **keine Entwicklerinnen oder Entwickler** sind und einfach nur möchten, dass **Bleepling auf ihrem Windows-PC läuft**.

Wenn du bei Computern schnell unsicher wirst: Das ist okay. Diese Anleitung erklärt auch Dinge, die für andere vielleicht selbstverständlich wirken.

Wichtig: **Alles, was in dieser Anleitung installiert oder heruntergeladen wird, ist kostenlos.**

## Inhaltsverzeichnis

- [1. Was du am Ende haben wirst](#1-was-du-am-ende-haben-wirst)
- [2. Was die seltsamen Wörter bedeuten](#2-was-die-seltsamen-woerter-bedeuten)
- [3. Was du vor dem Start wissen solltest](#3-was-du-vor-dem-start-wissen-solltest)
- [4. Bleepling von GitHub herunterladen](#4-bleepling-von-github-herunterladen)
- [5. Python installieren](#5-python-installieren)
- [6. FFmpeg installieren](#6-ffmpeg-installieren)
- [7. VLC installieren oder bewusst überspringen](#7-vlc-installieren-oder-bewusst-überspringen)
- [8. Die Bleepling-Pakete installieren](#8-die-bleepling-pakete-installieren)
- [9. Bleepling zum ersten Mal starten](#9-bleepling-zum-ersten-mal-starten)
- [10. Was beim ersten echten Einsatz passieren kann](#10-was-beim-ersten-echten-einsatz-passieren-kann)
- [11. Was du später zum Starten immer benutzt](#11-was-du-später-zum-starten-immer-benutzt)
- [12. Fehlerhilfe für absolute Anfänger](#12-fehlerhilfe-für-absolute-anfaenger)
- [13. Wenn du möglichst wenig installieren willst](#13-wenn-du-möglichst-wenig-installieren-willst)
- [14. Direktlinks](#14-direktlinks)

## 1. Was du am Ende haben wirst

Wenn alles geklappt hat, hast du am Ende:

- einen Ordner mit Bleepling auf deinem Rechner
- Python als Laufzeitumgebung
- FFmpeg für Audio und Video
- auf Wunsch VLC für die eingebaute Vorschau
- eine Startdatei, auf die du einfach doppelklicken kannst

Die wichtigste Startdatei ist später:

`start_bleepling.bat`

## 2. Was die seltsamen Wörter bedeuten

### GitHub

GitHub ist eine Website, auf der Programmcode liegt. Du musst **kein Entwicklerkonto** haben, nur um Bleepling herunterzuladen.

### ZIP-Datei

Eine ZIP-Datei ist ein gepackter Ordner. Du lädst ihn herunter und entpackst ihn danach.

### Python

Python ist die Programmiersprache, in der Bleepling geschrieben ist. Ohne Python kann Bleepling auf diesem Weg nicht starten.

### FFmpeg

FFmpeg ist ein kostenloses Werkzeug für Audio und Video. Bleepling braucht es für:

- WAV aus Video erzeugen
- Audio und Video rendern
- Clips und Arbeitsvideos bauen

### VLC

VLC ist ein kostenloser Medienplayer. Bleepling braucht VLC **nicht für alles**, aber für bestimmte Vorschau- und Wiedergabefunktionen ist VLC sehr hilfreich, besonders im Bereich **Schnitt & Kapitel**.

### Notepad

Notepad ist einfach der Windows-Editor, auf Deutsch oft **Editor** genannt. Er ist bei Windows normalerweise schon dabei. Du brauchst ihn nicht zwingend für die Installation, aber manchmal ist es hilfreich, damit eine Textdatei oder eine Fehlermeldung zu öffnen.

So findest du Notepad:

1. Drücke die Windows-Taste.
2. Tippe `Editor` oder `Notepad`.
3. Klicke auf das gefundene Programm.

### Eingabeaufforderung / Command Prompt / CMD

Das ist das schwarze oder dunkle Fenster, in das man Befehle eintippt. Windows nennt es oft **Eingabeaufforderung**.

Ein **Command** ist einfach ein Befehl, den du dort hineinkopierst oder eintippst.

Beispiel:

```bat
python --version
```

Das ist kein Zauberspruch. Das bedeutet nur: "Zeig mir, welche Python-Version installiert ist."

So öffnest du die Eingabeaufforderung:

1. Drücke die Windows-Taste.
2. Tippe `cmd`.
3. Klicke auf **Eingabeaufforderung**.

### PowerShell

PowerShell ist ein moderneres Befehlsfenster von Windows. Für diese Anleitung ist das nicht wichtig. Wenn du statt der Eingabeaufforderung versehentlich PowerShell öffnest, ist das in den meisten Fällen auch okay.

## 3. Was du vor dem Start wissen solltest

### Diese Anleitung ist für Windows gedacht

Sie ist **nicht** für Mac und **nicht** für Linux geschrieben.

### Du brauchst Internet

Für Download und Installation brauchst du Internet. Später kann Bleepling vieles lokal erledigen.

### Beim ersten Transkriptionslauf kann noch etwas aus dem Internet nachgeladen werden

Bleepling nutzt für die Transkription `faster-whisper`. Beim ersten echten Transkriptionslauf kann deshalb zusätzlich ein Sprachmodell aus dem Internet geladen werden. Das ist normal.

### Du brauchst kein Git

Du musst **nicht** lernen, wie man mit Git arbeitet. Wir laden den Projektordner als ZIP herunter.

### Nimm für den Anfang die einfache Variante

Wenn du nicht genau weißt, was du tust, dann:

- installiere **Python normal**
- installiere **FFmpeg normal**
- installiere **VLC normal**

Die portable Variante erkläre ich weiter unten extra.

## 4. Bleepling von GitHub herunterladen

### Die einfache Methode

1. Öffne diese Seite im Browser:  
   [https://github.com/Bleepling/bleepling](https://github.com/Bleepling/bleepling)
2. Klicke oben auf den grünen Button **Code**.
3. Klicke auf **Download ZIP**.
4. Warte, bis der Download fertig ist.
5. Öffne deinen Download-Ordner.
6. Dort liegt dann eine Datei, die wahrscheinlich so heißt:  
   `bleepling-main.zip`
7. Mache einen Rechtsklick auf diese ZIP-Datei.
8. Klicke auf **Alle extrahieren...**
9. Wähle als Ziel am besten einen Ort, den du wiederfindest, zum Beispiel:  
   `Dokumente\Bleepling`
10. Klicke auf **Extrahieren**.

### Was danach passiert sein sollte

Du hast jetzt einen echten Ordner, nicht mehr nur die ZIP-Datei.

Gehe in diesen entpackten Ordner hinein. Dort solltest du unter anderem sehen:

- `requirements.txt`
- `start_bleepling.bat`
- `start_bleepling_debug.bat`
- `src`

Wenn du diese Dinge nicht siehst, bist du wahrscheinlich noch **in der ZIP-Datei** oder **im falschen Ordner**.

## 5. Python installieren

### Warum Python nötig ist

Bleepling startet in dieser Form nicht alleine. Python ist der Motor darunter.

### Wichtiger Hinweis

Bitte installiere für Bleepling möglichst **Python 3.13 für Windows 64-Bit**. Dieser Projektstand wurde mit Python 3.13 getestet.

### So installierst du Python

1. Öffne diese Seite:  
   [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)
2. Suche dort nach einer **stabilen Python-3.13-Version für Windows 64-bit**.
3. Klicke auf **Windows installer (64-bit)**.
4. Warte, bis die Datei heruntergeladen ist.
5. Öffne die heruntergeladene Datei mit Doppelklick.
6. Ganz wichtig: Setze unten den Haken bei  
   **Add Python to PATH**
7. Klicke danach auf **Install Now**.
8. Warte, bis die Installation fertig ist.
9. Wenn Windows oder Python irgendetwas bestätigt haben will, bestätige es.
10. Wenn fertig, klicke auf **Close**.

### Prüfen, ob Python wirklich installiert ist

1. Öffne die **Eingabeaufforderung**.
2. Tippe diesen Befehl ein:

```bat
python --version
```

3. Drücke Enter.

Wenn alles gut ist, siehst du etwas wie:

```text
Python 3.13.7
```

Wenn stattdessen eine Fehlermeldung kommt wie "python wurde nicht gefunden", dann ist Python nicht richtig installiert oder der PATH-Haken war nicht gesetzt.

## 6. FFmpeg installieren

### Warum FFmpeg nötig ist

Bleepling braucht FFmpeg für fast alles, was mit echter Audio- oder Videoverarbeitung zu tun hat.

### Wichtiger Realitätshinweis

Die offizielle FFmpeg-Seite stellt für Windows nicht einfach selbst einen Installer bereit, sondern verweist auf fertige Windows-Builds.

### Einfache Methode für Anfänger

1. Öffne diese Seite:  
   [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Scrolle bis zu **Windows EXE Files**.
3. Klicke auf **Windows builds from gyan.dev**.
4. Auf der geöffneten Seite suche den Bereich **release builds**.
5. Klicke dort auf **ffmpeg-release-essentials.zip**.
6. Warte, bis die ZIP-Datei fertig heruntergeladen ist.

### FFmpeg entpacken

1. Öffne deinen Download-Ordner.
2. Mache einen Rechtsklick auf die heruntergeladene FFmpeg-ZIP-Datei.
3. Klicke auf **Alle extrahieren...**
4. Entpacke sie an einen leicht merkbaren Ort, zum Beispiel:  
   `C:\ffmpeg`

Am Ende solltest du einen Ordner haben, in dem ein Unterordner `bin` liegt. Darin liegen typischerweise:

- `ffmpeg.exe`
- `ffprobe.exe`
- oft auch `ffplay.exe`

### FFmpeg für Windows sichtbar machen

Jetzt muss Windows wissen, wo `ffmpeg.exe` liegt.

1. Öffne den FFmpeg-Ordner im Explorer.
2. Gehe in den Unterordner `bin`.
3. Klicke oben in die Adresszeile des Explorers.
4. Kopiere den kompletten Pfad. Er sieht zum Beispiel so aus:  
   `C:\ffmpeg\ffmpeg-8.1-essentials_build\bin`

### PATH setzen

1. Drücke die Windows-Taste.
2. Tippe:  
   `Umgebungsvariablen`
3. Klicke auf **Umgebungsvariablen für dieses Konto bearbeiten** oder **Systemumgebungsvariablen bearbeiten**.
4. Im Bereich **Benutzervariablen** markiere **Path**.
5. Klicke auf **Bearbeiten**.
6. Klicke auf **Neu**.
7. Füge den eben kopierten `bin`-Pfad ein.
8. Klicke mehrfach auf **OK**, bis alle Fenster geschlossen sind.

### Prüfen, ob FFmpeg sichtbar ist

1. Schließe die alte Eingabeaufforderung.
2. Öffne eine **neue** Eingabeaufforderung.
3. Tippe:

```bat
ffmpeg -version
```

4. Drücke Enter.

Wenn jetzt viele Zeilen Text erscheinen, ist alles gut.

## 7. VLC installieren oder bewusst überspringen

### Brauche ich VLC?

**Kurzfassung:**  
Wenn du Bleepling nur grundlegend benutzen willst, kannst du es erstmal **ohne VLC** versuchen.

**Empfehlung:**  
Wenn du die eingebaute Vorschau ordentlich nutzen willst, installiere VLC gleich mit.

### Normale VLC-Installation

1. Öffne diese Seite:  
   [https://images.videolan.org/vlc/download-windows.html](https://images.videolan.org/vlc/download-windows.html)
2. Lade die normale **64-Bit-Installer-Version** für Windows herunter.
3. Öffne die Datei per Doppelklick.
4. Klicke dich durch die Installation.
5. Die Standardvorgaben sind für die meisten Menschen okay.

### Wichtiger Hinweis

Bleepling braucht nicht einfach "irgendein Video-Programm", sondern genau die VLC-/libVLC-Umgebung. Darum bitte **offizielles VLC** von VideoLAN verwenden.

## 8. Die Bleepling-Pakete installieren

Jetzt kommen die Python-Pakete dran, die Bleepling braucht.

### Schritt 1: Eingabeaufforderung öffnen

1. Drücke die Windows-Taste.
2. Tippe `cmd`.
3. Öffne die **Eingabeaufforderung**.

### Schritt 2: In den Bleepling-Ordner wechseln

Wenn du Bleepling nach `Dokumente\Bleepling\bleepling-main` entpackt hast, gib diesen Befehl ein:

```bat
cd /d "%USERPROFILE%\Documents\Bleepling\bleepling-main"
```

Wenn dein Ordner woanders liegt, musst du den Pfad entsprechend anpassen.

### So prüfst du, ob du im richtigen Ordner bist

Tippe:

```bat
dir
```

Dann solltest du in der Ausgabe unter anderem sehen:

- `requirements.txt`
- `start_bleepling.bat`
- `src`

Wenn du das nicht siehst, bist du im falschen Ordner.

### Schritt 3: Pip aktualisieren

Tippe:

```bat
python -m pip install --upgrade pip
```

Drücke Enter und warte, bis der Befehl fertig ist.

### Schritt 4: Alle benötigten Pakete installieren

Tippe:

```bat
python -m pip install -r requirements.txt
```

Drücke Enter.

Jetzt wird eine Weile lang etwas heruntergeladen und installiert. Das kann je nach Rechner und Internet einige Minuten dauern.

### Wenn eine Rückfrage von Windows kommt

Wenn Windows fragt, ob etwas erlaubt werden soll, lies den Text kurz und bestätige es nur dann, wenn klar ist, dass es zu Python oder der Installation gehört.

## 9. Bleepling zum ersten Mal starten

### Die normale Startdatei

Gehe in den Bleepling-Ordner zurück und doppelklicke auf:

`start_bleepling.bat`

### Wenn nichts passiert oder etwas unklar ist

Dann doppelklicke stattdessen auf:

`start_bleepling_debug.bat`

Diese Datei ist extra für Fehlersuche gedacht. Sie zeigt mehr Informationen an.

### Wenn Bleepling startet

Dann ist die Installation im Wesentlichen geschafft.

## 10. Was beim ersten echten Einsatz passieren kann

### Erste Transkription dauert länger

Beim ersten echten Transkriptionslauf kann Bleepling zusätzlich ein Sprachmodell herunterladen. Das ist normal.

### FFmpeg wird geprüft

Im Reiter **Einstellungen / Logs** kannst du prüfen, ob Python, FFmpeg und weitere Dinge korrekt gefunden werden.

### VLC kann fehlen

Wenn VLC nicht installiert ist, funktionieren Teile der Vorschau möglicherweise nicht so, wie sie sollen. Das ist nicht automatisch ein Totalschaden der ganzen Software.

## 11. Was du später zum Starten immer benutzt

Im Alltag brauchst du normalerweise nur noch diese Datei:

`start_bleepling.bat`

Wenn etwas seltsam ist, nimm stattdessen:

`start_bleepling_debug.bat`

## 12. Fehlerhilfe für absolute Anfänger

### Fehler 1: `python wurde nicht gefunden`

Bedeutung:

- Python ist nicht installiert
- oder beim Installieren wurde **Add Python to PATH** nicht angehakt

Lösung:

1. Python noch einmal installieren
2. unbedingt den Haken bei **Add Python to PATH** setzen
3. danach die Eingabeaufforderung komplett schließen und neu öffnen

### Fehler 2: `ffmpeg wurde nicht gefunden`

Bedeutung:

- FFmpeg ist nicht installiert
- oder der `bin`-Ordner von FFmpeg ist nicht im PATH

Lösung:

1. FFmpeg prüfen
2. kontrollieren, ob wirklich der Ordner mit `ffmpeg.exe` im PATH steht
3. Eingabeaufforderung neu öffnen

### Fehler 3: `requirements.txt` wird nicht gefunden

Bedeutung:

Du bist im falschen Ordner.

Lösung:

1. Mit `dir` prüfen, was im aktuellen Ordner liegt
2. nur dann den Installationsbefehl ausführen, wenn du dort `requirements.txt` wirklich siehst

### Fehler 4: Doppelklick auf `start_bleepling.bat` schließt sich sofort

Lösung:

1. Starte stattdessen `start_bleepling_debug.bat`
2. fotografiere oder kopiere die Fehlermeldung
3. schicke genau diese Fehlermeldung an die Person, die dir hilft

### Fehler 5: Bleepling startet, aber bestimmte Vorschauen gehen nicht

Mögliche Ursache:

- VLC fehlt
- VLC ist zwar installiert, aber die Umgebung wird nicht sauber gefunden

Lösung:

1. VLC normal von der offiziellen Seite installieren
2. Bleepling neu starten
3. im Reiter **Einstellungen / Logs** die Prüfung ausführen

### Fehler 6: Die Transkription läuft nicht

Mögliche Ursachen:

- beim ersten Lauf ist das Sprachmodell noch nicht sauber geladen
- Internet oder Rechte haben gestört
- Python-Paketinstallation ist unvollständig

Lösung:

1. Bleepling schließen
2. `start_bleepling_debug.bat` starten
3. im Reiter **Einstellungen / Logs** die Prüfung ausführen
4. Fehlermeldung notieren

## 13. Wenn du möglichst wenig installieren willst

### Python

Python solltest du für diese Anleitung **normal installieren**. Das ist für Anfänger fast immer einfacher als eine portable Speziallösung.

### FFmpeg

FFmpeg gibt es auch als ZIP-Paket. Genau das verwenden wir in dieser Anleitung schon. Man kann also sagen:

- **herunterladen**
- **entpacken**
- **den `bin`-Ordner in den PATH eintragen**

Das ist bereits relativ "portable", auch wenn man noch den PATH setzen muss.

### VLC

VLC bietet auf der offiziellen Windows-Seite neben dem normalen Installer auch Paketvarianten wie ZIP oder 7zip an. Für absolute Anfänger ist aber der normale Installer fast immer die bessere Wahl.

## 14. Direktlinks

### Bleepling

- Projektseite: [https://github.com/Bleepling/bleepling](https://github.com/Bleepling/bleepling)
- Direkt als ZIP: [https://github.com/Bleepling/bleepling/archive/refs/heads/main.zip](https://github.com/Bleepling/bleepling/archive/refs/heads/main.zip)
- Releases: [https://github.com/Bleepling/bleepling/releases](https://github.com/Bleepling/bleepling/releases)

### Python

- Windows-Downloads: [https://www.python.org/downloads/windows/](https://www.python.org/downloads/windows/)

### FFmpeg

- Offizielle Download-Seite: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
- Windows-Builds von gyan.dev: [https://www.gyan.dev/ffmpeg/builds/](https://www.gyan.dev/ffmpeg/builds/)

### VLC

- Offizielle Windows-Downloads: [https://images.videolan.org/vlc/download-windows.html](https://images.videolan.org/vlc/download-windows.html)

## Abschlusssatz

Wenn du bis hier gekommen bist und Bleepling startet, hast du den schwersten Teil geschafft.

Ab dann ist der wichtigste Satz:

**Zum normalen Start doppelklicke ich auf `start_bleepling.bat`.**
