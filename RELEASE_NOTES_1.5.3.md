# Release-Vorlage 1.5.3

Diese Datei dient als vorbereitete Arbeitsgrundlage für die manuelle Veröffentlichung von **Bleepling 1.5.3**.

## Tag

`v1.5.3`

## Titel

`Bleepling 1.5.3`

## Überblick

Version **1.5.3** baut das Anwenderhandbuch direkt in die Anwendung ein. Statt ausgelieferter PDF- oder DOCX-Dateien gibt es jetzt eine zentrale Markdown-Quelle im Projekt, einen integrierten Handbuch-Viewer mit Suche und Kapitelsprüngen sowie einen HTML-Export direkt aus der App.

## Wichtigste Änderungen

- integrierter Button **„Handbuch öffnen“** in der App-Kopfzeile
- neuer Handbuch-Viewer mit Suche, Kapitelsprüngen und HTML-Export
- viele Fragezeichen-Hilfen führen direkt in passende Kapitel des Anwenderhandbuchs
- `docs/Bleepling_Benutzerhandbuch.md` ist jetzt die zentrale Handbuchquelle
- Inhaltsverzeichnis und Sprungmarken des Handbuchs wurden vereinheitlicht
- offizielle PDF- und DOCX-Auslieferung des Anwenderhandbuchs entfällt

## Hinweise

- Das Benutzerhandbuch gehört jetzt direkt zur Anwendung und zum Repository.
- Wer eine separate Fassung benötigt, kann sie aus der App als HTML exportieren.
- Externe Komponenten wie FFmpeg, VLC/libVLC sowie optionale CUDA-/cuDNN-Bausteine bleiben weiterhin nicht Bestandteil des Repositorys.
- Eine menschliche Endkontrolle anonymisierter Medien bleibt weiterhin erforderlich.

## Release-Check

- Versionsstand im Code: `1.5.3`
- Tag für GitHub-Release: `v1.5.3`
- bevorzugter Release-Titel: `Bleepling 1.5.3`
- GitHub-Release erst nach Merge in `main` und finalem Tag `v1.5.3` erstellen
