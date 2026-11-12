---
title: 'ZIP Upload: ganze Ordnerstrukturen in einem Schritt importieren'
description: 'Heute zeige ich Ihnen, wie Sie eine ZIP-Datei direkt in einen Space importieren: mit Vorschau des Inhalts, übernommener Ordnerstruktur und der Wahl, ob leere Ordner bleiben.'
date: 2026-11-12
author: 'SDX Team'
category: tutorial
level: beginner
feature: zip-upload
audience:
  - 'Alle, die Unterlagen von Partnern als ZIP bekommen'
  - 'Projektteams, die große Ordnerstrukturen nach SDX bringen'
  - 'Admins, die einen neuen Space befüllen'
outcomes:
  - 'Eine ZIP-Datei in einen Space oder Ordner importieren'
  - 'Den Inhalt vor dem Import prüfen'
  - 'Entscheiden, ob leere Ordner übernommen werden'
requirements:
  - 'Ein SDX-Konto mit Bearbeitungsrechten auf dem Ziel-Space oder -Ordner'
  - 'Eine ZIP-Datei auf Ihrem Rechner'
cover: '/media/community/zip-dialog-preview.webp'
coverAlt: 'Dialog „ZIP importieren“ mit Vorschau der Ordnerstruktur einer ZIP-Datei'
intro:
  - 'Ich schreibe heute über eine kleine Funktion, die viel Klickarbeit spart: den **ZIP Upload.** Sie bekommen von einem Partner ein ZIP mit hundert Dateien in zwanzig Ordnern? Statt alles zu entpacken und Ordner für Ordner hochzuladen, importieren Sie die ZIP-Datei direkt. SDX legt die Ordner an und lädt die Dateien hinein.'
  - 'Vier Schritte, danach ein paar Situationen, in denen das besonders hilft.'
steps:
  - title: 'Ziel öffnen und „ZIP importieren“ wählen'
    text: 'Öffnen Sie den Space oder Ordner, in den der Inhalt soll. In der Werkzeugleiste finden Sie das Symbol „ZIP importieren“, direkt neben „Ordner anlegen“.'
    image: '/media/community/zip-toolbar.webp'
    alt: 'Werkzeugleiste eines Spaces mit dem Tooltip „ZIP importieren“'
  - title: 'ZIP-Datei auswählen'
    text: 'Ziehen Sie die ZIP-Datei in das Feld oder klicken Sie auf „Durchsuchen …“. Rechts erklärt der Dialog, was als Nächstes passiert: Die Datei wird extrahiert, Sie entscheiden über leere Ordner, dann wird der Inhalt importiert.'
    image: '/media/community/zip-dialog-empty.webp'
    alt: 'Leerer Dialog „ZIP importieren“ mit Ablagefeld und Erklärung in drei Schritten'
  - title: 'Vorschau prüfen'
    text: 'Bevor etwas importiert wird, zeigt SDX den Inhalt der ZIP-Datei als Baum, mit der Zahl der Elemente, Ordner und Dateien. So sehen Sie sofort, ob es die richtige Datei ist und ob die Struktur passt.'
    image: '/media/community/zip-dialog-preview.webp'
    alt: 'Vorschau mit 11 Elementen, 5 Ordnern und 6 Dateien als aufklappbarer Baum'
    tip: 'Die Ordnerstruktur wird genau so übernommen, wie sie in der Vorschau steht. Benennen Sie Ordner also am besten vor dem Zippen so, wie sie in SDX heißen sollen.'
  - title: 'Leere Ordner wählen und importieren'
    text: 'Haken Sie „Leere Ordner beibehalten“ an, wenn auch leere Verzeichnisse aus der ZIP-Datei angelegt werden sollen, zum Beispiel als Vorlage für eine Projektstruktur. Mit „Importieren“ landet alles in Ihrem Space.'
    image: '/media/community/zip-dialog-empty-folders.webp'
    alt: 'Dialog mit aktivierter Option „Leere Ordner beibehalten“ und dem Button „Importieren“'
related:
  - intro-using-external-share
order: 2
---

## Wofür sich der ZIP Upload eignet

- **Unterlagen für eine Prüfung:** Berechnungen, Genehmigungen, Verträge und Gutachten als ein Paket in den Projektbereich.
- **Wartungsberichte mehrerer Standorte**, die regelmäßig als ZIP kommen.
- **Druckdaten**, die gebündelt an eine Druckerei gehen oder von ihr zurückkommen.
- **Projektvorlagen:** ein ZIP mit leeren Ordnern (Pläne, Berichte, Fotos, Verträge) gibt jedem neuen Projekt dieselbe Struktur.
- **Abschluss und Archiv:** die Dokumentation eines fertigen Projekts strukturiert an einem Ort.

## Gut zu wissen

- **Nur .zip.** Andere Archivformate werden nicht angenommen.
- **Gleiche Grenzen wie beim normalen Upload.** Große Archive mit vielen Dateien sind möglich.
- **Abgesichert:** SDX entpackt ZIP-Dateien mit einer sicheren Implementierung, die sogenannte ZIP-Bomben abwehrt.
- **Nachliefern:** Wenn Sie ein aktualisiertes ZIP in denselben Ordner importieren, werden Dateien mit gleichem Namen ersetzt, ihre Berechtigungen bleiben erhalten, neue Dateien kommen dazu und nichts wird gelöscht.

## Und dann?

Sobald die Unterlagen in SDX liegen, können Sie sie mit External Share an Externe weitergeben, ohne Mailanhang und mit Ablaufdatum. Wie das geht, zeigt der Artikel unten.
