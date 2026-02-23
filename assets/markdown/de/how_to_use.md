# So verwenden Sie Analyze Your Data

## Kurzübersicht

**Analyze Your Data** ermöglicht es Ihnen, Daten hochzuladen, sie in einem interaktiven Grid zu erkunden und bis zu 3 unabhängige Diagramme zu erstellen — alles in Ihrem Browser. Es werden keine Daten auf dem Server gespeichert; alles verbleibt in Ihrer Sitzung.

---

## Schritt 1: Daten laden

Wählen Sie eine der unterstützten Datenquellen:

### Direkter Datei-Upload
- Klicken Sie auf den Upload-Bereich oder ziehen Sie Ihre Datei per Drag & Drop hinein
- **Unterstützte Formate:** Excel (`.xlsx`, `.xls`), CSV (`.csv`, `.txt`, `.log`), JSON, Parquet, HDF5, SQLite (`.db`, `.sqlite`, `.sqlite3`)
- Bei CSV/TXT/LOG-Dateien bestätigen oder ändern Sie das Trennzeichen (Komma, Semikolon, Tabulator, Pipe oder Leerzeichen)
- Maximale Dateigröße: **{{VALUE_MAX_FILE_SIZE_MB}} MB**

### SQLite Database
- Laden Sie eine `.db`-, `.sqlite`- oder `.sqlite3`-Datei hoch
- Durchsuchen Sie die verfügbaren Tabellen mit Zeilen- und Spaltenanzahl
- Wählen Sie die gewünschte Tabelle aus und klicken Sie auf **Load Selected Table**

### Microsoft SharePoint / OneDrive
- Fügen Sie eine Freigabe-URL mit **anonymem Zugriff** ein ("Jeder mit dem Link kann anzeigen")
- Unterstützte URL-Formate:
  - `https://1drv.ms/x/s!...` (OneDrive-Kurzlinks)
  - `https://onedrive.live.com/...` (OneDrive-Volllinks)
  - `https://[company].sharepoint.com/...` (SharePoint-Links)
  - `https://[company]-my.sharepoint.com/...` (SharePoint persönlich)
- Wenn die Datei mehrere Blätter enthält, wählen Sie das gewünschte Blatt aus dem Dropdown-Menü

**So erhalten Sie eine Freigabe-URL:** Klicken Sie in SharePoint/OneDrive mit der rechten Maustaste auf die Datei → Teilen → auf "Jeder mit dem Link kann anzeigen" setzen → Link kopieren.

**Test URL** — probieren Sie diese aus, um Ihre Einrichtung zu überprüfen:
```
{{URL_TEST_DATASET_SHAREPOINT}}
```

> **Hinweis:** Unternehmens-/Enterprise-Microsoft-365-Mandanten können anonyme Freigabelinks aufgrund von Sicherheitsrichtlinien der Organisation blockieren. Dies ist eine Einschränkung auf der SharePoint/OneDrive-Seite, nicht der Anwendung. Persönliche OneDrive-Links funktionieren in der Regel ohne Einschränkungen.

### Google Sheets
- Fügen Sie eine öffentliche Google Sheets URL ein (`https://docs.google.com/spreadsheets/d/[ID]/edit...`)
- Geben Sie optional eine **GID** (Blatt-Tab-ID) ein, um ein bestimmtes Blatt zu laden
- Das Dokument muss als "Jeder mit dem Link kann anzeigen" freigegeben sein

**So erhalten Sie eine Freigabe-URL:** Klicken Sie in Google Sheets auf Teilen → auf "Jeder mit dem Link" setzen → Betrachter → Link kopieren. Um ein bestimmtes Blatt zu laden, kopieren Sie die URL aus der Browserleiste und verwenden Sie die Nummer `#gid=123456789` im GID-Feld.

**Test URL** — probieren Sie diese aus, um Ihre Einrichtung zu überprüfen:
```
{{URL_TEST_DATASET_GOOGLE}}
```

### Airtable

Die Airtable-Verbindung erfordert einen **Personal Access Token** und eine **Base ID**.

#### So erstellen Sie einen Personal Access Token

1. Gehen Sie zu [airtable.com/create/tokens]({{URL_DOCUMENTATION_AIRTABLE_TOKENS}}) (oder navigieren Sie zu Ihrem Konto → Developer Hub → Personal Access Tokens)
2. Klicken Sie auf **Create new token**
3. Geben Sie ihm einen Namen (z.B. "Analyze Your Data")
4. Fügen Sie unter **Scopes** mindestens hinzu:
   - `data.records:read` — um Tabellendatensätze zu lesen
   - `schema.bases:read` — um Tabellen in einer Base aufzulisten
5. Wählen Sie unter **Access** die spezifische(n) Base(s) aus, mit der/denen Sie sich verbinden möchten
6. Klicken Sie auf **Create token** und kopieren Sie ihn sofort — Sie können ihn danach nicht mehr einsehen

> **Referenz:** [Personal Access Tokens erstellen — Airtable Support]({{URL_DOCUMENTATION_AIRTABLE_PAT}})

#### So finden Sie Ihre Base ID

1. Öffnen Sie Ihre Airtable Base im Browser
2. Schauen Sie sich die URL an: `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. Die Base ID ist der Teil, der mit `app` beginnt (z.B. `appXXXXXXXXXXXXXX`)

#### Daten laden

1. Geben Sie Ihren **Personal Access Token** in das Token-Feld ein
2. Geben Sie Ihre **Base ID** ein
3. Klicken Sie auf **Connect to Airtable** — die verfügbaren Tabellen werden aufgelistet
4. Wählen Sie eine Tabelle aus und klicken Sie auf **Load Selected Table**

> **Tipp:** Ihr Token wird nur im Sitzungsspeicher des Browsers gehalten — er wird niemals auf dem Server gespeichert. Das Schließen des Browser-Tabs löscht ihn.

> **Tipp:** Für sensible oder private Daten verwenden Sie den direkten Datei-Upload — Ihre Daten verlassen niemals den Browser.

---

## Schritt 2: Datetime-Verarbeitung (Optional)

Die Datetime-Verarbeitung ist **standardmäßig deaktiviert**. Wenn sie deaktiviert ist, werden Ihre Daten direkt in das Grid geladen — keine weiteren Schritte erforderlich.

Wenn Ihre Daten eine Datetime-Spalte enthalten und Sie eine zeitbasierte Analyse wünschen:

1. Schalten Sie die Datetime-Verarbeitung auf **Aktiviert**
2. Wählen Sie die **Datetime-Spalte** aus dem Dropdown-Menü
3. Wählen Sie das passende **Datetime-Format** (oder geben Sie ein benutzerdefiniertes Python `strftime()`-Format ein)
4. Klicken Sie auf **Load data to AgGrid Table**

Generierte Spalten umfassen: `tsYear`, `tsMonth`, `tsDay`, `tsHour`, `tsMinute`, `tsDayOfWeek`, `tsWeekNumber`, `tsDate` und weitere.

---

## Schritt 3: Daten im Grid erkunden

Die **AG Grid**-Tabelle bietet leistungsstarke Datenexploration:

- **Sortieren** — klicken Sie auf eine beliebige Spaltenüberschrift
- **Filtern** — klicken Sie auf das Filtersymbol in einer beliebigen Spaltenüberschrift, um Bedingungen festzulegen
- **Gruppieren** — ziehen Sie Spaltenüberschriften in den "Row Group"-Bereich oberhalb der Tabelle
- **Pivotieren** — aktivieren Sie den Pivot-Modus über das Spaltenmenü für Kreuztabellierungen
- **Größe ändern** — ziehen Sie an den Spaltenrändern, um die Breite anzupassen
- **Aggregieren** — bei Gruppierungen zeigt das Grid Zwischensummen und Gesamtsummen an

> **Wichtig:** Die untenstehenden Diagramme lesen die **aktuell gefilterten/gruppierten Daten**, die im Grid sichtbar sind. Jede Filter-, Sortier- oder Gruppierungsaktion aktualisiert alle Diagramme sofort — **das ist die zentrale Stärke des Tools.** Verwenden Sie das Grid als interaktiven Datenschneider und sehen Sie die Ergebnisse in Echtzeit in allen Ihren Visualisierungen.

> **Daten aus dem Grid exportieren:** Klicken Sie mit der rechten Maustaste irgendwo in die AG Grid-Tabelle, um die aktuell gefilterten und strukturierten Daten direkt als **CSV- oder Excel**-Datei zu exportieren. Der Export spiegelt genau das wider, was Sie im Grid sehen — einschließlich aller angewendeten Filter, Gruppierungen und Sortierungen.

---

## Schritt 4: Diagramme erstellen

Sie können bis zu **3 unabhängige Diagramme** erstellen, jedes mit eigener Konfiguration:

1. **Anzeigen/Ausblenden** — verwenden Sie den Schalter, um jeden Diagrammbereich ein- oder auszublenden
2. **Diagrammtyp** — wählen Sie aus: Scatter, Scatter (multi y), Line, Bar (grouped), Bar (stacked), Histogram (grouped), Histogram (stacked), Pie, Bubble, Heatmap, Log, Sunburst, Icicle
3. **X-Achsen-Spalte** — wählen Sie die Spalte für die horizontale Achse
4. **Y-Achsen-Spalte(n)** — wählen Sie eine oder mehrere Spalten für die vertikale Achse
5. **Farbspalte** (optional) — färben Sie Datenpunkte nach einer kategorialen Spalte ein
6. **Z-Achsen-Spalte** (optional) — für Bubble- und Heatmap-Diagrammtypen
7. **Titel** — legen Sie einen benutzerdefinierten Diagrammtitel, X-Achsen-Titel und Y-Achsen-Titel fest

Die Diagramme lesen die aktuell gefilterten/gruppierten Grid-Daten. **Jede Filter-, Sortier- oder Gruppierungsaktion im Grid aktualisiert alle Diagramme sofort.**

---

## Schritt 5: Export

### Einzelne Diagramme
- Klicken Sie unter jedem Diagramm auf **Download Chart as HTML**, um es als eigenständige interaktive HTML-Datei zu speichern

### Alle Diagramme (ZIP)
- Klicken Sie auf **Download All Charts** oben oder unten im Diagrammbereich
- Jedes aktive Diagramm wird als separate eigenständige HTML-Datei exportiert, gebündelt in einem ZIP-Download
- Nur Diagramme mit Daten werden in die ZIP-Datei aufgenommen

### Grid-Daten
- Klicken Sie mit der rechten Maustaste in die AG Grid-Tabelle → **Export to CSV** oder **Export to Excel**
- Exportiert genau die Daten, die aktuell im Grid sichtbar sind (berücksichtigt Filter, Gruppierungen, Sortierungen)

> **Tipp:** Exportierte HTML-Dateien sind vollständig interaktiv — Sie können zoomen, mit der Maus für Tooltips darüberfahren und schwenken — keine Software erforderlich, nur ein Webbrowser.

---

## Tipps & Fehlerbehebung

| Problem | Lösung |
|---|---|
| Datei-Upload schlägt fehl | Überprüfen Sie, ob die Datei unter {{VALUE_MAX_FILE_SIZE_MB}} MB groß ist und ein unterstütztes Format hat |
| SharePoint-Link funktioniert nicht | Stellen Sie sicher, dass der Link anonymen Zugriff erlaubt (keine Anmeldung erforderlich). Unternehmens-Mandanten können dies blockieren. |
| Google Sheet lässt sich nicht laden | Stellen Sie sicher, dass die Freigabe auf "Jeder mit dem Link kann anzeigen" eingestellt ist |
| Airtable lässt sich nicht verbinden | Überprüfen Sie, ob Ihr Personal Access Token die Berechtigungen `data.records:read` und `schema.bases:read` hat und die Base ID mit `app` beginnt |
| Datetime-Analysefehler | Überprüfen Sie, ob das ausgewählte Format mit Ihren Daten übereinstimmt. Probieren Sie bei Bedarf ein benutzerdefiniertes Format |
| Diagramme sind leer | Stellen Sie sicher, dass Daten im Grid geladen sind und X/Y-Spalten ausgewählt wurden |
| Grid zeigt nach dem Filtern keine Daten | Löschen oder passen Sie Ihre Spaltenfilter an |

---

## Datenschutz

- Alle hochgeladenen Daten werden **ausschließlich im Arbeitsspeicher** verarbeitet (niemals auf die Festplatte oder in eine Datenbank geschrieben)
- Daten werden in Ihrer **Browsersitzung** gespeichert — das Schließen des Tabs löscht alles
- Es werden keine hochgeladenen Daten an externe Dienste gesendet
- Nur freiwillige Feedback-Eingaben und anonyme Nutzungsanalysen werden gespeichert
- Vollständige Details finden Sie unter [PRIVACY.md]({{URL_DOCUMENTATION_AYD_PRIVACY}})
