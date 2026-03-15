# Hur du använder Analyze Your Data

## Snabb översikt

**Analyze Your Data** låter dig ladda upp data, utforska den i en interaktiv tabell och skapa upp till 3 oberoende diagram — allt i din webbläsare. Ingen data lagras på servern; allt stannar i din session.

---

## Steg 1: Ladda din data

Välj en av de datakällor som stöds:

### Direkt filuppladdning
- Klicka på uppladdningsområdet eller dra & släpp din fil
- **Format som stöds:** Excel (`.xlsx`, `.xls`), CSV (`.csv`, `.txt`, `.log`), JSON, Parquet, HDF5, SQLite (`.db`, `.sqlite`, `.sqlite3`)
- För CSV/TXT/LOG-filer, bekräfta eller ändra avgränsaren (komma, semikolon, tab, pipe eller mellanslag)
- Maximal filstorlek: **{{VALUE_MAX_FILE_SIZE_MB}} MB**

### SQLite-databas
- Ladda upp en `.db`-, `.sqlite`- eller `.sqlite3`-fil
- Bläddra bland tillgängliga tabeller med rad- och kolumnantal
- Välj den tabell du vill analysera och klicka **Load Selected Table**

### Microsoft SharePoint / OneDrive — Avvecklat

**Microsoft har inaktiverat oautentiserad åtkomst till OneDrive delnings-API:et.** API-ändpunkten som tidigare tillät laddning av filer från offentliga SharePoint/OneDrive-länkar returnerar nu autentiseringsfel. Detta är en ändring gjord av Microsoft — inte av denna applikation.

Microsofts ersättning kräver Azure AD OAuth 2.0-autentisering, vilket lägger till betydande friktion (inloggning med Microsoft-konto, godkännande av organisationsadministratör) med begränsade garantier för långsiktig stabilitet.

> **Rekommenderat alternativ:** Ladda ner din fil från SharePoint/OneDrive till din dator och använd sedan **Direkt filuppladdning** ovan. Det är snabbare, mer tillförlitligt och dina data förblir helt under din kontroll.

### Google Sheets
- Klistra in en offentlig Google Sheets-URL (`https://docs.google.com/spreadsheets/d/[ID]/edit...`)
- Ange eventuellt ett **GID** (arkflik-ID) för att ladda ett specifikt ark
- Dokumentet måste delas som "Anyone with the link can view"

**Hur du får en delnings-URL:** I Google Sheets, klicka på Dela → ställ in på "Anyone with the link" → Viewer → kopiera länken. För att ladda en specifik arkflik, kopiera URL:en från webbläsarens adressfält och använd `#gid=123456789`-numret i GID-fältet.

**Test-URL** — prova detta för att verifiera din konfiguration:
```
{{URL_TEST_DATASET_GOOGLE}}
```

### Airtable

Airtable-anslutning kräver en **Personal Access Token** och ett **Base ID**.

#### Hur du skapar en Personal Access Token

1. Gå till [airtable.com/create/tokens]({{URL_DOCUMENTATION_AIRTABLE_TOKENS}}) (eller navigera till ditt konto → Developer Hub → Personal Access Tokens)
2. Klicka **Create new token**
3. Ge den ett namn (t.ex. "Analyze Your Data")
4. Under **Scopes**, lägg till minst:
   - `data.records:read` — för att läsa tabellposter
   - `schema.bases:read` — för att lista tabeller i en bas
5. Under **Access**, välj de specifika baser du vill ansluta till
6. Klicka **Create token** och kopiera den omedelbart — du kommer inte kunna se den igen

> **Referens:** [Creating Personal Access Tokens — Airtable Support]({{URL_DOCUMENTATION_AIRTABLE_PAT}})

#### Hur du hittar ditt Base ID

1. Öppna din Airtable-bas i webbläsaren
2. Titta på URL:en: `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. Base ID är delen som börjar med `app` (t.ex. `appXXXXXXXXXXXXXX`)

#### Ladda data

1. Ange din **Personal Access Token** i tokenfältet
2. Ange ditt **Base ID**
3. Klicka **Connect to Airtable** — tillgängliga tabeller kommer att listas
4. Välj en tabell och klicka **Load Selected Table**

> **Tips:** Din token hålls endast i webbläsarens sessionsminne — den lagras aldrig på servern. Att stänga webbläsarfliken rensar den.


> **Tips:** För känslig eller privat data, använd direkt filuppladdning — din data lämnar aldrig webbläsaren.

---

## Steg 2: Datetime-bearbetning (valfritt)

Datetime-bearbetning är **inaktiverad som standard**. När inaktiverad laddas din data direkt in i tabellen — inga extra steg behövs.

Om din data innehåller en datetime-kolumn och du vill ha tidbaserad analys:

1. Växla datetime-bearbetning till **Enabled**
2. Välj **Datetime Column** från rullgardinsmenyn
3. Välj matchande **Datetime Format** (eller ange ett anpassat Python `strftime()`-format)
4. Klicka **Load data to AgGrid Table**

Genererade kolumner inkluderar: `tsYear`, `tsMonth`, `tsDay`, `tsHour`, `tsMinute`, `tsDayOfWeek`, `tsWeekNumber`, `tsDate`, med mera.

---

## Steg 3: Utforska din data i tabellen

**AG Grid**-tabellen erbjuder kraftfull datautforskning:

- **Sortera** — klicka på valfri kolumnrubrik
- **Filtrera** — klicka på filterikonen på valfri kolumnrubrik för att ställa in villkor
- **Gruppera** — dra kolumnrubriker till "Row Group"-panelen ovanför tabellen
- **Pivotera** — aktivera pivotläge från kolumnmenyn för korsklassificering
- **Ändra storlek** — dra kolumnkanter för att justera bredder
- **Aggregera** — vid gruppering visar tabellen delsummor och totalsummor

> **Viktigt:** Diagrammen nedan läser från den **aktuellt filtrerade/grupperade datan** som är synlig i tabellen. Varje filter-, sorterings- eller grupperingsåtgärd uppdaterar alla diagram omedelbart — **detta är verktygets kärnkraft.** Använd tabellen som din interaktiva data-slicer och se resultaten återspeglas i realtid över alla dina visualiseringar.


> **Exportera data från tabellen:** Högerklicka var som helst i AG Grid-tabellen för att exportera den aktuellt filtrerade och strukturerade datan direkt till **CSV eller Excel**-fil. Exporten återspeglar exakt vad du ser i tabellen — inklusive eventuella filter, grupperingar eller sorteringar du har tillämpat.

---

## Steg 4: Skapa diagram

Du kan skapa upp till **3 oberoende diagram**, vart och ett med sin egen konfiguration:

1. **Visa/Dölj** — använd växlaren för att visa eller dölja varje diagramsektion
2. **Diagramtyp** — välj bland: Scatter, Scatter (multi y), Line, Bar (grouped), Bar (stacked), Histogram (grouped), Histogram (stacked), Pie, Bubble, Heatmap, Log, Sunburst, Icicle
3. **X-axelkolumn** — välj kolumnen för den horisontella axeln
4. **Y-axelkolumn(er)** — välj en eller flera kolumner för den vertikala axeln
5. **Färgkolumn** (valfritt) — färglägg datapunkter efter en kategorisk kolumn
6. **Z-axelkolumn** (valfritt) — för Bubble- och Heatmap-diagramtyper
7. **Titlar** — ställ in anpassad diagramtitel, X-axeltitel och Y-axeltitel

Diagram läser från den aktuellt filtrerade/grupperade tabelldatan. **Varje filter-, sorterings- eller grupperingsåtgärd i tabellen uppdaterar alla diagram omedelbart.**

---

## Steg 5: Exportera

### Enskilda diagram
- Klicka **Download Chart as HTML** under varje diagram för att spara det som en fristående interaktiv HTML-fil

### Alla diagram (ZIP)
- Klicka på **Download All Charts** högst upp eller längst ner i diagramsektionen
- Varje aktivt diagram exporteras som en separat fristående HTML-fil, samlade i en ZIP-nedladdning
- Endast diagram med data inkluderas i ZIP-filen

### Tabelldata
- Högerklicka i AG Grid-tabellen → **Export to CSV** eller **Export to Excel**
- Exporterar exakt den data som för närvarande är synlig i tabellen (respekterar filter, gruppering, sortering)

> **Tips:** Exporterade HTML-filer är helt interaktiva — du kan zooma, hovra för verktygstips och panorera — ingen programvara behövs, bara en webbläsare.

---

## Tips & felsökning

| Problem | Lösning |
|---|---|
| Filuppladdning misslyckas | Kontrollera att filen är under {{VALUE_MAX_FILE_SIZE_MB}} MB och i ett format som stöds |
| SharePoint-länk fungerar inte | Microsoft har inaktiverat oautentiserad API-åtkomst. Ladda ner filen och använd Direkt filuppladdning istället. |
| Google Sheet laddar inte | Se till att delning är inställd på "Anyone with the link can view" |
| Airtable ansluter inte | Verifiera att din Personal Access Token har `data.records:read`- och `schema.bases:read`-behörigheter, och att Base ID börjar med `app` |
| Datetime-tolkningsfel | Verifiera att det valda formatet matchar din data. Prova ett anpassat format om det behövs |
| Diagram är tomma | Se till att data är laddad i tabellen och att X/Y-kolumner är valda |
| Tabellen visar ingen data efter filtrering | Rensa eller justera dina kolumnfilter |

---

## Datasekretess

- All uppladdad data bearbetas **endast i minnet** (skrivs aldrig till disk eller databas)
- Data lagras i din **webbläsarsession** — att stänga fliken rensar allt
- Ingen uppladdad data skickas till externa tjänster
- Endast frivilliga feedbackinlämningar och anonym användningsanalys lagras
- Se [PRIVACY.md]({{URL_DOCUMENTATION_AYD_PRIVACY}}) för fullständiga detaljer
