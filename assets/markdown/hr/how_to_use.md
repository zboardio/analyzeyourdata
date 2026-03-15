# Kako koristiti Analyze Your Data

## Brzi pregled

**Analyze Your Data** vam omogućuje učitavanje podataka, istraživanje u interaktivnoj tablici i stvaranje do 3 neovisna grafikona — sve u vašem pregledniku. Nikakvi podaci se ne pohranjuju na poslužitelju; sve ostaje u vašoj sesiji.

---

## Korak 1: Učitajte svoje podatke

Odaberite jedan od podržanih izvora podataka:

### Izravno učitavanje datoteke
- Kliknite na područje za učitavanje ili povucite i ispustite datoteku
- **Podržani formati:** Excel (`.xlsx`, `.xls`), CSV (`.csv`, `.txt`, `.log`), JSON, Parquet, HDF5, SQLite (`.db`, `.sqlite`, `.sqlite3`)
- Za CSV/TXT/LOG datoteke, potvrdite ili promijenite rastavni znak (zarez, točka-zarez, tabulator, okomita crta ili razmak)
- Maksimalna veličina datoteke: **{{VALUE_MAX_FILE_SIZE_MB}} MB**

### SQLite baza podataka
- Učitajte `.db`, `.sqlite` ili `.sqlite3` datoteku
- Pregledajte dostupne tablice s brojem redaka i stupaca
- Odaberite tablicu koju želite analizirati i kliknite **Load Selected Table**

### Microsoft SharePoint / OneDrive — Ukinuto

**Microsoft je onemogućio neautenticirani pristup OneDrive API-ju za dijeljenje.** API krajnja točka koja je ranije omogućavala učitavanje datoteka s javnih SharePoint/OneDrive poveznica sada vraća pogreške autentikacije. Ovo je promjena koju je napravio Microsoft — ne ova aplikacija.

Microsoftova zamjena zahtijeva Azure AD OAuth 2.0 autentikaciju, koja dodaje značajne prepreke (prijava Microsoft računom, odobrenje administratora organizacije) s ograničenim jamstvima dugoročne stabilnosti.

> **Preporučena alternativa:** Preuzmite svoju datoteku sa SharePoint/OneDrive na računalo, a zatim koristite **Izravno učitavanje datoteke** iznad. To je brže, pouzdanije i vaši podaci ostaju u potpunosti pod vašom kontrolom.

### Google Sheets
- Zalijepite javni Google Sheets URL (`https://docs.google.com/spreadsheets/d/[ID]/edit...`)
- Opcionalno unesite **GID** (ID kartice lista) za učitavanje određenog lista
- Dokument mora biti podijeljen kao "Svatko s vezom može vidjeti"

**Kako dobiti URL za dijeljenje:** U Google Sheets, kliknite Dijeli → postavite na "Svatko s vezom" → Pregledavatelj → kopirajte vezu. Za učitavanje određene kartice lista, kopirajte URL iz adresne trake preglednika i upotrijebite broj `#gid=123456789` u GID polju.

**Testni URL** — pokušajte ovo za provjeru postavke:
```
{{URL_TEST_DATASET_GOOGLE}}
```

### Airtable

Airtable veza zahtijeva **Personal Access Token** i **Base ID**.

#### Kako stvoriti Personal Access Token

1. Idite na [airtable.com/create/tokens]({{URL_DOCUMENTATION_AIRTABLE_TOKENS}}) (ili navigirajte na vaš račun → Developer Hub → Personal Access Tokens)
2. Kliknite **Create new token**
3. Dodijelite mu ime (npr. "Analyze Your Data")
4. Pod **Scopes**, dodajte barem:
   - `data.records:read` — za čitanje zapisa tablice
   - `schema.bases:read` — za popis tablica u bazi
5. Pod **Access**, odaberite određene baze s kojima se želite povezati
6. Kliknite **Create token** i odmah ga kopirajte — nećete ga moći ponovno vidjeti

> **Referenca:** [Creating Personal Access Tokens — Airtable Support]({{URL_DOCUMENTATION_AIRTABLE_PAT}})

#### Kako pronaći svoj Base ID

1. Otvorite svoju Airtable bazu u pregledniku
2. Pogledajte URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. Base ID je dio koji počinje s `app` (npr. `appXXXXXXXXXXXXXX`)

#### Učitavanje podataka

1. Unesite svoj **Personal Access Token** u polje za token
2. Unesite svoj **Base ID**
3. Kliknite **Connect to Airtable** — dostupne tablice će biti navedene
4. Odaberite tablicu i kliknite **Load Selected Table**

> **Savjet:** Vaš token se čuva samo u memoriji sesije preglednika — nikada se ne pohranjuje na poslužitelju. Zatvaranje kartice preglednika ga briše.


> **Savjet:** Za osjetljive ili privatne podatke, koristite izravno učitavanje datoteke — vaši podaci nikada ne napuštaju preglednik.

---

## Korak 2: Obrada datuma i vremena (opcionalno)

Obrada datuma i vremena je **onemogućena prema zadanim postavkama**. Kada je onemogućena, vaši se podaci učitavaju izravno u tablicu — nisu potrebni dodatni koraci.

Ako vaši podaci sadrže stupac s datumom i vremenom i želite analizu temeljenu na vremenu:

1. Prebacite obradu datuma i vremena na **Enabled**
2. Odaberite **Datetime Column** iz padajućeg izbornika
3. Odaberite odgovarajući **Datetime Format** (ili unesite prilagođeni Python `strftime()` format)
4. Kliknite **Load data to AgGrid Table**

Generirani stupci uključuju: `tsYear`, `tsMonth`, `tsDay`, `tsHour`, `tsMinute`, `tsDayOfWeek`, `tsWeekNumber`, `tsDate` i još mnogo toga.

---

## Korak 3: Istražite svoje podatke u tablici

**AG Grid** tablica pruža moćno istraživanje podataka:

- **Sortiraj** — kliknite na bilo koje zaglavlje stupca
- **Filtriraj** — kliknite ikonu filtera na bilo kojem zaglavlju stupca za postavljanje uvjeta
- **Grupiraj** — povucite zaglavlja stupaca u "Row Group" panel iznad tablice
- **Okreni** — omogućite pivot način iz izbornika stupca za unakrsne tabulacije
- **Promijeni veličinu** — povucite rubove stupaca za prilagodbu širine
- **Zbrajaj** — pri grupiranju, tablica prikazuje međuzbrojeve i ukupne zbrojeve

> **Ključno:** Grafikoni ispod čitaju iz **trenutno filtriranih/grupiranih podataka** vidljivih u tablici. Svaka akcija filtriranja, sortiranja ili grupiranja odmah ažurira sve grafikone — **to je osnovna snaga alata.** Koristite tablicu kao svoj interaktivni rezač podataka i vidite rezultate koji se trenutno odražavaju u svim vašim vizualizacijama.


> **Izvezite podatke iz tablice:** Kliknite desnom tipkom miša bilo gdje u AG Grid tablici za izvoz trenutno filtriranih i strukturiranih podataka izravno u **CSV ili Excel** datoteku. Izvoz odražava upravo ono što vidite u tablici — uključujući sve filtere, grupiranje ili sortiranje koje ste primijenili.

---

## Korak 4: Stvaranje grafikona

Možete stvoriti do **3 neovisna grafikona**, svaki sa svojom konfiguracijom:

1. **Prikaži/Sakrij** — upotrijebite prekidač za prikaz ili skrivanje svakog odjeljka grafikona
2. **Vrsta grafikona** — odaberite iz: Scatter, Scatter (multi y), Line, Bar (grouped), Bar (stacked), Histogram (grouped), Histogram (stacked), Pie, Bubble, Heatmap, Log, Sunburst, Icicle
3. **Stupac X-osi** — odaberite stupac za vodoravnu os
4. **Stupac(ci) Y-osi** — odaberite jedan ili više stupaca za okomitu os
5. **Stupac boje** (opcionalno) — obojite podatkovne točke prema kategoričkom stupcu
6. **Stupac Z-osi** (opcionalno) — za vrste grafikona Bubble i Heatmap
7. **Naslovi** — postavite prilagođeni naslov grafikona, naslov X-osi i naslov Y-osi

Grafikoni čitaju iz trenutno filtriranih/grupiranih podataka tablice. **Svaka akcija filtriranja, sortiranja ili grupiranja u tablici odmah ažurira sve grafikone.**

---

## Korak 5: Izvoz

### Pojedinačni grafikoni
- Kliknite **Download Chart as HTML** ispod svakog grafikona za spremanje kao samostalna interaktivna HTML datoteka

### Svi grafikoni (ZIP)
- Klikni na **Download All Charts** na vrhu ili dnu sekcije grafikona
- Svaki aktivni grafikon izvozi se kao zasebna samostalna HTML datoteka, objedinjeni u jednom ZIP preuzimanju
- U ZIP su uključeni samo grafikoni s podacima

### Podaci tablice
- Desni klik u AG Grid tablici → **Export to CSV** ili **Export to Excel**
- Izvozi upravo podatke trenutno vidljive u tablici (poštuje filtere, grupiranje, sortiranje)

> **Savjet:** Izvezene HTML datoteke su potpuno interaktivne — možete zumirati, prelaziti za opise alata i pomicati — nije potreban softver, samo web preglednik.

---

## Savjeti i rješavanje problema

| Problem | Rješenje |
|---|---|
| Učitavanje datoteke ne uspijeva | Provjerite je li datoteka manja od {{VALUE_MAX_FILE_SIZE_MB}} MB i u podržanom formatu |
| SharePoint poveznica ne radi | Microsoft je onemogućio neautenticirani pristup API-ju. Preuzmite datoteku i koristite Izravno učitavanje datoteke. |
| Google Sheet se ne učitava | Provjerite je li dijeljenje postavljeno na "Svatko s vezom može vidjeti" |
| Airtable se ne povezuje | Provjerite ima li vaš Personal Access Token `data.records:read` i `schema.bases:read` dozvole, i počinje li Base ID s `app` |
| Greške u parsiranju datuma i vremena | Provjerite odgovara li odabrani format vašim podacima. Pokušajte prilagođeni format ako je potrebno |
| Grafikoni su prazni | Provjerite su li podaci učitani u tablici i odabrani X/Y stupci |
| Tablica ne prikazuje podatke nakon filtra | Obrišite ili prilagodite svoje filtere stupaca |

---

## Privatnost podataka

- Svi učitani podaci se obrađuju **samo u memoriji** (nikada se ne zapisuju na disk ili bazu podataka)
- Podaci se pohranjuju u vašoj **sesiji preglednika** — zatvaranje kartice briše sve
- Nikakvi učitani podaci se ne šalju vanjskim servisima
- Pohranjuju se samo dobrovoljne povratne informacije i anonimna analitika korištenja
- Pogledajte [PRIVACY.md]({{URL_DOCUMENTATION_AYD_PRIVACY}}) za sve detalje
