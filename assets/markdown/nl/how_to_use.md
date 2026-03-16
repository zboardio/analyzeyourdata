# Hoe Analyze Your Data te gebruiken

## Snel overzicht

**Analyze Your Data** stelt u in staat om gegevens te uploaden, ze in een interactief raster te verkennen en tot 3 onafhankelijke grafieken te maken — allemaal in uw browser. Er worden geen gegevens op de server opgeslagen; alles blijft in uw sessie.

---

## Stap 1: Laad uw gegevens

Kies een van de ondersteunde gegevensbronnen:

### Directe bestandsupload
- Klik op het uploadgebied of sleep uw bestand
- **Ondersteunde formaten:** Excel (`.xlsx`, `.xls`), CSV (`.csv`, `.txt`, `.log`), JSON, Parquet, HDF5, SQLite (`.db`, `.sqlite`, `.sqlite3`)
- Voor CSV/TXT/LOG-bestanden, bevestig of wijzig het scheidingsteken (komma, puntkomma, tab, pipe of spatie)
- Maximale bestandsgrootte: **{{VALUE_MAX_FILE_SIZE_MB}} MB**

### SQLite Database
- Upload een `.db`, `.sqlite` of `.sqlite3` bestand
- Blader door beschikbare tabellen met rij- en kolomaantallen
- Selecteer de tabel die u wilt analyseren en klik op **Load Selected Table**

### Microsoft SharePoint / OneDrive — Stopgezet

**Microsoft heeft niet-geauthenticeerde toegang tot de OneDrive delings-API uitgeschakeld.** Het API-eindpunt dat eerder het laden van bestanden via openbare SharePoint/OneDrive-links mogelijk maakte, geeft nu authenticatiefouten terug. Dit is een wijziging van Microsoft — niet van deze applicatie.

De vervangende oplossing van Microsoft vereist Azure AD OAuth 2.0-authenticatie, wat aanzienlijke wrijving toevoegt (inloggen met Microsoft-account, goedkeuring van organisatiebeheerder) met beperkte garanties voor langdurige stabiliteit.

> **Aanbevolen alternatief:** Download uw bestand van SharePoint/OneDrive naar uw computer en gebruik vervolgens de **Directe bestandsupload** hierboven. Dit is sneller, betrouwbaarder en uw gegevens blijven volledig onder uw controle.

### Google Sheets
- Kopieer de URL uit de adresbalk van de browser terwijl u het gewenste blad-tab bekijkt en plak deze
- Het blad-tab (GID) wordt automatisch gedetecteerd uit de URL
- Het document moet gedeeld zijn als "Iedereen met de link kan bekijken"

**Hoe krijgt u de URL:** In Google Sheets, klik op Delen → stel in op "Iedereen met de link" → Viewer. Navigeer vervolgens naar het blad-tab dat u wilt laden en kopieer de URL uit de adresbalk van uw browser (deze bevat het blad-ID automatisch).

**Test-URL** — probeer dit om uw configuratie te verifiëren:
```
{{URL_TEST_DATASET_GOOGLE}}
```

### Airtable

Airtable-verbinding vereist een **Personal Access Token** en een **Base ID**.

#### Hoe maakt u een Personal Access Token

1. Ga naar [airtable.com/create/tokens]({{URL_DOCUMENTATION_AIRTABLE_TOKENS}}) (of navigeer naar uw Account → Developer Hub → Personal Access Tokens)
2. Klik op **Create new token**
3. Geef het een naam (bijv. "Analyze Your Data")
4. Onder **Scopes**, voeg minimaal toe:
   - `data.records:read` — om tabelrecords te lezen
   - `schema.bases:read` — om tabellen in een base op te sommen
5. Onder **Access**, selecteer de specifieke base(s) waarmee u verbinding wilt maken
6. Klik op **Create token** en kopieer het onmiddellijk — u kunt het niet opnieuw zien

> **Referentie:** [Creating Personal Access Tokens — Airtable Support]({{URL_DOCUMENTATION_AIRTABLE_PAT}})

#### Hoe vindt u uw Base ID

1. Open uw Airtable-base in de browser
2. Bekijk de URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. De Base ID is het deel dat begint met `app` (bijv. `appXXXXXXXXXXXXXX`)

#### Gegevens laden

1. Voer uw **Personal Access Token** in het token-veld in
2. Voer uw **Base ID** in
3. Klik op **Connect to Airtable** — beschikbare tabellen worden weergegeven
4. Selecteer een tabel en klik op **Load Selected Table**

> **Tip:** Uw token wordt alleen in het browsergeheugen van de sessie bewaard — het wordt nooit op de server opgeslagen. Het sluiten van het browsertabblad wist het.


> **Tip:** Voor gevoelige of privégegevens, gebruik Directe bestandsupload — uw gegevens verlaten de browser nooit.

---

## Stap 2: Datetime-verwerking (optioneel)

Datetime-verwerking is **standaard uitgeschakeld**. Wanneer uitgeschakeld, worden uw gegevens direct in het raster geladen — geen extra stappen nodig.

Als uw gegevens een datetime-kolom bevatten en u tijdgebaseerde analyse wilt:

1. Schakel datetime-verwerking in op **Enabled**
2. Selecteer de **Datetime Column** uit de dropdown
3. Kies het overeenkomstige **Datetime Format** (of voer een aangepast Python `strftime()` formaat in)
4. Klik op **Load data to AgGrid Table**

Gegenereerde kolommen omvatten: `tsYear`, `tsMonth`, `tsDay`, `tsHour`, `tsMinute`, `tsDayOfWeek`, `tsWeekNumber`, `tsDate`, en meer.

---

## Stap 3: Verken uw gegevens in AG Grid

**AG Grid** biedt krachtige interactieve gegevensverkenning met ingebouwde zijpanelen:

- **Sorteren** — klik op elke kolomkop
- **Filteren** — klik op het filterpictogram op elke kolomkop om voorwaarden in te stellen, of gebruik het **Filterpaneel** aan de rechterkant om alle kolomfilters op één plek te beheren
- **Groeperen** — sleep kolomkoppen naar het "Row Group"-paneel boven de tabel
- **Draaien** — schakel draaimodus in vanuit het **Kolommenpaneel** aan de rechterkant voor kruistabellen
- **Grootte wijzigen** — sleep kolomranden om breedtes aan te passen
- **Aggregeren** — bij groepering toont AG Grid subtotalen en eindtotalen
- **Kolommenpaneel** — schakel kolomzichtbaarheid, herorden kolommen en configureer pivot/waarde-instellingen vanuit het zijpaneel
- **Filterpaneel** — bekijk en beheer alle actieve filters over alle kolommen vanuit één handig paneel

> **Belangrijk:** De onderstaande grafieken lezen van de **momenteel gefilterde/gegroepeerde gegevens** die zichtbaar zijn in AG Grid. Elke filter-, sorteer- of groepeeringsactie werkt alle grafieken direct bij — **dit is de kernkracht van de tool.** Gebruik AG Grid als uw interactieve gegevensslicer en zie de resultaten in realtime weerspiegeld in al uw visualisaties.

### AG Grid Export

Gebruik de knoppen **Export to Excel** en **Export to CSV** onder AG Grid om de momenteel zichtbare gegevens te downloaden:

- De export weerspiegelt altijd de **huidige weergave** van AG Grid — filters, groeperingen en sorteringen worden gerespecteerd
- **Excel-export** bevat tabelopmaak met actieve filters, zodat u direct in Excel kunt doorfilteren
- **CSV-export** biedt een schoon plat bestand van de gefilterde gegevens
- Dit betekent dat u verschillende filtercriteria kunt toepassen in AG Grid en meerdere keren kunt exporteren om **afzonderlijke bestanden voor verschillende subsets** van uw gegevens te maken — een krachtige workflow voor gegevensanalyse en rapportage

> **Tip:** U kunt ook met de rechtermuisknop ergens in de AG Grid-tabel klikken voor extra exportopties via het contextmenu.

---

## Stap 4: Maak grafieken

U kunt tot **3 onafhankelijke grafieken** maken, elk met zijn eigen configuratie:

1. **Tonen/verbergen** — gebruik de schakelaar om elke grafieksectie te tonen of te verbergen
2. **Grafiektype** — kies uit: Scatter, Scatter (multi y), Line, Bar (grouped), Bar (stacked), Histogram (grouped), Histogram (stacked), Pie, Bubble, Heatmap, Log, Sunburst, Icicle
3. **X-as kolom** — selecteer de kolom voor de horizontale as
4. **Y-as kolom(men)** — selecteer een of meer kolommen voor de verticale as
5. **Kleurkolom** (optioneel) — kleur datapunten volgens een categorische kolom
6. **Z-as kolom** (optioneel) — voor Bubble en Heatmap grafiektypen
7. **Titels** — stel aangepaste grafiektitel, X-as titel en Y-as titel in

Grafieken lezen van de momenteel gefilterde/gegroepeerde AG Grid gegevens. **Elke filter-, sorteer- of groepeeringsactie in AG Grid werkt alle grafieken direct bij.**

---

## Stap 5: Exporteren

### Individuele grafieken
- Klik op **Download Chart as HTML** onder elke grafiek om deze op te slaan als een zelfstandig interactief HTML-bestand

### Alle grafieken (ZIP)
- Klik op **Download All Charts** bovenaan of onderaan het grafiekgedeelte
- Elke actieve grafiek wordt geëxporteerd als een apart zelfstandig HTML-bestand, gebundeld in één ZIP-download
- Alleen grafieken met data worden opgenomen in het ZIP-bestand

### AG Grid Gegevens
- Gebruik de knoppen **Export to Excel** of **Export to CSV** onder AG Grid (zie Stap 3 hierboven)
- Exporteert precies de gegevens die momenteel zichtbaar zijn in AG Grid (respecteert filters, groeperingen, sorteringen)

> **Tip:** Geëxporteerde HTML-grafiekbestanden zijn volledig interactief — u kunt zoomen, zweven voor tooltips en pannen — geen software nodig, alleen een webbrowser.

---

## Tips & probleemoplossing

| Probleem | Oplossing |
|---|---|
| Bestandsupload mislukt | Controleer of het bestand kleiner is dan {{VALUE_MAX_FILE_SIZE_MB}} MB en in een ondersteund formaat |
| SharePoint-link werkt niet | Microsoft heeft niet-geauthenticeerde API-toegang uitgeschakeld. Download het bestand en gebruik in plaats daarvan Directe bestandsupload. |
| Google Sheet wordt niet geladen | Zorg ervoor dat delen is ingesteld op "Iedereen met de link kan bekijken" |
| Airtable maakt geen verbinding | Verifieer dat uw Personal Access Token `data.records:read` en `schema.bases:read` scopes heeft, en de Base ID begint met `app` |
| Datetime-parsefouten | Verifieer dat het geselecteerde formaat overeenkomt met uw gegevens. Probeer zo nodig een aangepast formaat |
| Grafieken zijn leeg | Zorg ervoor dat gegevens in AG Grid zijn geladen en X/Y-kolommen zijn geselecteerd |
| AG Grid toont geen gegevens na filter | Wis of pas uw kolomfilters aan in het Filterpaneel |

---

## Gegevensprivacy

- Alle geüploade gegevens worden **alleen in het geheugen** verwerkt (nooit naar schijf of database geschreven)
- Gegevens worden opgeslagen in uw **browsersessie** — het sluiten van het tabblad wist alles
- Er worden geen geüploade gegevens naar externe diensten verzonden
- Alleen vrijwillige feedbackinzendingen en anonieme gebruiksanalyses worden opgeslagen
- Zie [PRIVACY.md]({{URL_DOCUMENTATION_AYD_PRIVACY}}) voor volledige details
