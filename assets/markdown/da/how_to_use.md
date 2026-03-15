# Sådan bruger du Analyze Your Data

## Hurtig oversigt

**Analyze Your Data** lader dig uploade data, udforske dem i et interaktivt gitter og oprette op til 3 uafhængige diagrammer — alt sammen i din browser. Ingen data gemmes på serveren; alt forbliver i din session.

---

## Trin 1: Indlæs dine data

Vælg en af de understøttede datakilder:

### Direkte filupload
- Klik på uploadområdet eller træk og slip din fil
- **Understøttede formater:** Excel (`.xlsx`, `.xls`), CSV (`.csv`, `.txt`, `.log`), JSON, Parquet, HDF5, SQLite (`.db`, `.sqlite`, `.sqlite3`)
- For CSV/TXT/LOG-filer skal du bekræfte eller ændre separatoren (komma, semikolon, tabulator, lodret streg eller mellemrum)
- Maksimal filstørrelse: **{{VALUE_MAX_FILE_SIZE_MB}} MB**

### SQLite-database
- Upload en `.db`, `.sqlite` eller `.sqlite3`-fil
- Gennemse tilgængelige tabeller med række- og kolonneantal
- Vælg den tabel du vil analysere og klik **Load Selected Table**

### Microsoft SharePoint / OneDrive — Udgået

> **Microsoft har deaktiveret uautentificeret adgang til OneDrive delings-API'et.** Det API-endpoint, der tidligere tillod indlæsning af filer fra offentlige SharePoint/OneDrive-links, returnerer nu autentificeringsfejl. Dette er en ændring foretaget af Microsoft — ikke af denne applikation.
>
> Microsofts erstatning kræver Azure AD OAuth 2.0-godkendelse, som tilføjer betydelig friktion (Microsoft-kontologin, organisationsadministratorgodkendelse) med begrænsede garantier for langsigtet stabilitet.
>
> **Anbefalet alternativ:** Download din fil fra SharePoint/OneDrive til din computer, og brug derefter **Direkte filupload** ovenfor. Det er hurtigere, mere pålideligt, og dine data forbliver fuldt under din kontrol.

### Google Sheets
- Indsæt en offentlig Google Sheets-URL (`https://docs.google.com/spreadsheets/d/[ID]/edit...`)
- Indtast eventuelt et **GID** (ark-fane-ID) for at indlæse et specifikt ark
- Dokumentet skal deles som "Enhver med linket kan se"

**Sådan får du en deling-URL:** I Google Sheets, klik Del → indstil til "Enhver med linket" → Seer → kopiér linket. For at indlæse en specifik ark-fane, kopiér URL'en fra browserlinjen og brug `#gid=123456789`-nummeret i GID-feltet.

**Test-URL** — prøv dette for at verificere din opsætning:
```
{{URL_TEST_DATASET_GOOGLE}}
```

### Airtable

Airtable-forbindelse kræver et **Personal Access Token** og et **Base ID**.

#### Sådan opretter du et Personal Access Token

1. Gå til [airtable.com/create/tokens]({{URL_DOCUMENTATION_AIRTABLE_TOKENS}}) (eller naviger til din konto → Developer Hub → Personal Access Tokens)
2. Klik **Create new token**
3. Giv det et navn (f.eks. "Analyze Your Data")
4. Under **Scopes**, tilføj minimum:
   - `data.records:read` — for at læse tabelposter
   - `schema.bases:read` — for at liste tabeller i en base
5. Under **Access**, vælg de specifikke base(r) du vil forbinde til
6. Klik **Create token** og kopiér det med det samme — du kan ikke se det igen

> **Reference:** [Creating Personal Access Tokens — Airtable Support]({{URL_DOCUMENTATION_AIRTABLE_PAT}})

#### Sådan finder du dit Base ID

1. Åbn din Airtable-base i browseren
2. Se på URL'en: `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. Base ID'et er delen der starter med `app` (f.eks. `appXXXXXXXXXXXXXX`)

#### Indlæsning af data

1. Indtast dit **Personal Access Token** i token-feltet
2. Indtast dit **Base ID**
3. Klik **Connect to Airtable** — tilgængelige tabeller vises
4. Vælg en tabel og klik **Load Selected Table**

> **Tip:** Dit token opbevares kun i browsersessionens hukommelse — det gemmes aldrig på serveren. Lukning af browserfanen sletter det.


> **Tip:** For følsomme eller private data, brug Direkte filupload — dine data forlader aldrig browseren.

---

## Trin 2: Datetime-behandling (valgfrit)

Datetime-behandling er **deaktiveret som standard**. Når den er deaktiveret, indlæses dine data direkte i gitteret — ingen ekstra trin nødvendige.

Hvis dine data indeholder en datetime-kolonne, og du ønsker tidsbaseret analyse:

1. Skift datetime-behandling til **Enabled**
2. Vælg **Datetime Column** fra rullemenuen
3. Vælg det matchende **Datetime Format** (eller indtast et brugerdefineret Python `strftime()`-format)
4. Klik **Load data to AgGrid Table**

Genererede kolonner inkluderer: `tsYear`, `tsMonth`, `tsDay`, `tsHour`, `tsMinute`, `tsDayOfWeek`, `tsWeekNumber`, `tsDate` og flere.

---

## Trin 3: Udforsk dine data i gitteret

**AG Grid**-tabellen giver kraftfuld dataudforskning:

- **Sortér** — klik på en hvilken som helst kolonneoverskrift
- **Filtrér** — klik på filterikonet på en hvilken som helst kolonneoverskrift for at indstille betingelser
- **Gruppér** — træk kolonneoverskrifter ind i "Row Group"-panelet over tabellen
- **Pivot** — aktiver pivot-tilstand fra kolonnemenuen for krydstabuleringer
- **Tilpas størrelse** — træk kolonnekanter for at justere bredder
- **Aggregér** — ved gruppering viser gitteret subtotaler og hovedtotaler

> **Nøgle:** Diagrammerne nedenfor læser fra de **aktuelt filtrerede/grupperede data** synlige i gitteret. Hver filtrering, sortering eller grupperingshandling opdaterer alle diagrammer øjeblikkeligt — **dette er værktøjets kerneværdi.** Brug gitteret som din interaktive data-slicer og se resultaterne afspejlet i realtid på tværs af alle dine visualiseringer.


> **Eksportér data fra gitteret:** Højreklik hvor som helst i AG Grid-tabellen for at eksportere de aktuelt filtrerede og strukturerede data direkte til **CSV eller Excel**-fil. Eksporten afspejler præcis hvad du ser i gitteret — inklusive eventuelle filtre, grupperinger eller sorteringer du har anvendt.

---

## Trin 4: Opret diagrammer

Du kan oprette op til **3 uafhængige diagrammer**, hver med sin egen konfiguration:

1. **Vis/Skjul** — brug skifteren til at vise eller skjule hver diagramsektion
2. **Diagramtype** — vælg mellem: Scatter, Scatter (multi y), Line, Bar (grouped), Bar (stacked), Histogram (grouped), Histogram (stacked), Pie, Bubble, Heatmap, Log, Sunburst, Icicle
3. **X-aksens kolonne** — vælg kolonnen til den horisontale akse
4. **Y-aksens kolonne(r)** — vælg en eller flere kolonner til den vertikale akse
5. **Farvekolonne** (valgfrit) — farvekod datapunkter efter en kategorisk kolonne
6. **Z-aksens kolonne** (valgfrit) — for Bubble- og Heatmap-diagramtyper
7. **Titler** — indstil brugerdefineret diagramtitel, X-aksetitel og Y-aksetitel

Diagrammer læser fra de aktuelt filtrerede/grupperede gitterdata. **Hver filtrering, sortering eller grupperingshandling i gitteret opdaterer alle diagrammer øjeblikkeligt.**

---

## Trin 5: Eksport

### Individuelle diagrammer
- Klik **Download Chart as HTML** under hvert diagram for at gemme det som en selvstændig interaktiv HTML-fil

### Alle diagrammer (ZIP)
- Klik på **Download All Charts** øverst eller nederst i diagramsektionen
- Hvert aktivt diagram eksporteres som en separat selvstændig HTML-fil, samlet i én ZIP-download
- Kun diagrammer med data inkluderes i ZIP-filen

### Gitterdata
- Højreklik i AG Grid-tabellen → **Export to CSV** eller **Export to Excel**
- Eksporterer præcis de data der aktuelt er synlige i gitteret (respekterer filtre, gruppering, sortering)

> **Tip:** Eksporterede HTML-filer er fuldt interaktive — du kan zoome, holde markøren over for værktøjstips og panorere — ingen software nødvendig, kun en webbrowser.

---

## Tips og fejlfinding

| Problem | Løsning |
|---|---|
| Filupload mislykkes | Kontrollér at filen er under {{VALUE_MAX_FILE_SIZE_MB}} MB og i et understøttet format |
| SharePoint-link virker ikke | Microsoft har deaktiveret uautentificeret API-adgang. Download filen og brug Direkte filupload i stedet. |
| Google Sheet indlæses ikke | Sørg for at deling er indstillet til "Enhver med linket kan se" |
| Airtable vil ikke forbinde | Verificér at dit Personal Access Token har `data.records:read` og `schema.bases:read` scopes, og at Base ID'et starter med `app` |
| Datetime-parsing-fejl | Verificér at det valgte format matcher dine data. Prøv et brugerdefineret format hvis nødvendigt |
| Diagrammer er tomme | Sørg for at data er indlæst i gitteret, og at X/Y-kolonner er valgt |
| Gitteret viser ingen data efter filtrering | Ryd eller juster dine kolonnefiltre |

---

## Databeskyttelse

- Alle uploadede data behandles **kun i hukommelsen** (skrives aldrig til disk eller database)
- Data gemmes i din **browsersession** — lukning af fanen rydder alt
- Ingen uploadede data sendes til eksterne tjenester
- Kun frivillige feedback-indsendelser og anonyme brugsanalyser gemmes
- Se [PRIVACY.md]({{URL_DOCUMENTATION_AYD_PRIVACY}}) for fulde detaljer
