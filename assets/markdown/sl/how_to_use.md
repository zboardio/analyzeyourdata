# Kako uporabljati Analyze Your Data

## Hiter pregled

**Analyze Your Data** vam omogoča nalaganje podatkov, raziskovanje v interaktivni tabeli in ustvarjanje do 3 neodvisnih grafov — vse v vašem brskalniku. Nobeni podatki se ne shranjujejo na strežniku; vse ostane v vaši seji.

---

## Korak 1: Naložite svoje podatke

Izberite enega od podprtih virov podatkov:

### Neposredna naložitev datoteke
- Kliknite na območje za nalaganje ali povlecite datoteko
- **Podprte oblike:** Excel (`.xlsx`, `.xls`), CSV (`.csv`, `.txt`, `.log`), JSON, Parquet, HDF5, SQLite (`.db`, `.sqlite`, `.sqlite3`)
- Za CSV/TXT/LOG datoteke potrdite ali spremenite ločilo (vejica, podpičje, tabulator, navpična črta ali presledek)
- Največja velikost datoteke: **{{VALUE_MAX_FILE_SIZE_MB}} MB**

### SQLite Database
- Naložite `.db`, `.sqlite` ali `.sqlite3` datoteko
- Preglejte razpoložljive tabele s številom vrstic in stolpcev
- Izberite tabelo, ki jo želite analizirati, in kliknite **Load Selected Table**

### Microsoft SharePoint / OneDrive — Ukinjeno

> **Microsoft je onemogočil neavtenticiran dostop do API-ja za skupno rabo OneDrive.** Končna točka API-ja, ki je prej omogočala nalaganje datotek prek javnih povezav SharePoint/OneDrive, zdaj vrača napake pri avtentikaciji. To je sprememba, ki jo je izvedel Microsoft — ne ta aplikacija.
>
> Microsoftova nadomestna rešitev zahteva avtentikacijo Azure AD OAuth 2.0, ki dodaja znatne ovire (prijava z Microsoftovim računom, odobritev skrbnika organizacije) z omejenimi jamstvi dolgoročne stabilnosti.
>
> **Priporočena alternativa:** Prenesite svojo datoteko iz SharePoint/OneDrive na računalnik in nato uporabite **Neposreden prenos datoteke** zgoraj. To je hitrejše, zanesljivejše in vaši podatki ostanejo v celoti pod vašim nadzorom.

### Google Sheets
- Prilepite javni Google Sheets URL (`https://docs.google.com/spreadsheets/d/[ID]/edit...`)
- Po želji vnesite **GID** (ID zavihka lista) za nalaganje določenega lista
- Dokument mora biti deljen kot "Kdorkoli s povezavo lahko pogleda"

**Kako dobiti URL za deljenje:** V Google Sheets kliknite Deli → nastavite na "Kdorkoli s povezavo" → Gledalec → kopirajte povezavo. Za nalaganje določenega zavihka lista kopirajte URL iz vrstice brskalnika in uporabite številko `#gid=123456789` v polju GID.

**Testni URL** — poskusite to za preverjanje vaše nastavitve:
```
{{URL_TEST_DATASET_GOOGLE}}
```

### Airtable

Povezava Airtable zahteva **Personal Access Token** in **Base ID**.

#### Kako ustvariti Personal Access Token

1. Pojdite na [airtable.com/create/tokens]({{URL_DOCUMENTATION_AIRTABLE_TOKENS}}) (ali pojdite na vaš račun → Developer Hub → Personal Access Tokens)
2. Kliknite **Create new token**
3. Dodelite mu ime (npr. "Analyze Your Data")
4. Pod **Scopes** dodajte vsaj:
   - `data.records:read` — za branje zapisov tabele
   - `schema.bases:read` — za seznam tabel v bazi
5. Pod **Access** izberite specifične baze, s katerimi se želite povezati
6. Kliknite **Create token** in ga takoj kopirajte — ne boste ga več mogli videti

> **Referenca:** [Creating Personal Access Tokens — Airtable Support]({{URL_DOCUMENTATION_AIRTABLE_PAT}})

#### Kako najti vaš Base ID

1. Odprite vašo Airtable bazo v brskalniku
2. Poglejte URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. Base ID je del, ki se začne z `app` (npr. `appXXXXXXXXXXXXXX`)

#### Nalaganje podatkov

1. Vnesite vaš **Personal Access Token** v polje za žeton
2. Vnesite vaš **Base ID**
3. Kliknite **Connect to Airtable** — prikazale se bodo razpoložljive tabele
4. Izberite tabelo in kliknite **Load Selected Table**

> **Nasvet:** Vaš žeton je shranjen samo v pomnilniku seje brskalnika — nikoli se ne shrani na strežnik. Zapiranje zavihka brskalnika ga izbriše.


> **Nasvet:** Za občutljive ali zasebne podatke uporabite neposredno nalaganje datotek — vaši podatki nikoli ne zapustijo brskalnika.

---

## Korak 2: Obdelava datetime (neobvezno)

Obdelava datetime je **privzeto onemogočena**. Ko je onemogočena, se vaši podatki naložijo neposredno v tabelo — brez dodatnih korakov.

Če vaši podatki vsebujejo stolpec datetime in želite analizo na osnovi časa:

1. Preklopite obdelavo datetime na **Enabled**
2. Izberite **Datetime Column** iz spustnega menija
3. Izberite ujemajoči se **Datetime Format** (ali vnesite obliko po meri Python `strftime()`)
4. Kliknite **Load data to AgGrid Table**

Generirani stolpci vključujejo: `tsYear`, `tsMonth`, `tsDay`, `tsHour`, `tsMinute`, `tsDayOfWeek`, `tsWeekNumber`, `tsDate` in več.

---

## Korak 3: Raziščite svoje podatke v tabeli

Tabela **AG Grid** ponuja močno raziskovanje podatkov:

- **Razvrsti** — kliknite na katerikoli glavo stolpca
- **Filtriraj** — kliknite na ikono filtra na katerikoli glavi stolpca za nastavitev pogojev
- **Grupiraj** — povlecite glave stolpcev v ploščo "Row Group" nad tabelo
- **Obračaj** — omogočite pivot način iz menija stolpca za navzkrižne tabelacije
- **Spremeni velikost** — povlecite obrobe stolpcev za prilagoditev širin
- **Agregacija** — pri grupiranju tabela prikazuje vmesne seštevke in skupne seštevke

> **Ključno:** Grafi spodaj berejo iz **trenutno filtriranih/grupiranih podatkov**, vidnih v tabeli. Vsaka akcija filtriranja, razvrščanja ali grupiranja takoj posodobi vse grafe — **to je osnovna moč tega orodja.** Uporabite tabelo kot vaš interaktivni rezalnik podatkov in vidite rezultate, ki se odražajo v realnem času v vseh vaših vizualizacijah.


> **Izvozite podatke iz tabele:** Kliknite desno kjerkoli v AG Grid tabeli in izvozite trenutno filtrirane in strukturirane podatke neposredno v **CSV ali Excel** datoteko. Izvoz odraža točno tisto, kar vidite v tabeli — vključno z vsemi filtri, grupiranjem ali razvrščanjem, ki ste ga uporabili.

---

## Korak 4: Ustvarite grafe

Ustvarite lahko do **3 neodvisne grafe**, vsak s svojo konfiguracijo:

1. **Prikaži/Skrij** — uporabite stikalo za prikaz ali skrivanje vsakega odseka grafa
2. **Tip grafa** — izbirajte med: Scatter, Scatter (multi y), Line, Bar (grouped), Bar (stacked), Histogram (grouped), Histogram (stacked), Pie, Bubble, Heatmap, Log, Sunburst, Icicle
3. **Stolpec osi X** — izberite stolpec za vodoravno os
4. **Stolpec(ci) osi Y** — izberite enega ali več stolpcev za navpično os
5. **Stolpec barve** (neobvezno) — obarvajte podatkovne točke po kategoričnem stolpcu
6. **Stolpec osi Z** (neobvezno) — za tipe grafov Bubble in Heatmap
7. **Naslovi** — nastavite naslov grafa po meri, naslov osi X in naslov osi Y

Grafi berejo iz trenutno filtriranih/grupiranih podatkov tabele. **Vsaka akcija filtriranja, razvrščanja ali grupiranja v tabeli takoj posodobi vse grafe.**

---

## Korak 5: Izvoz

### Posamezni grafi
- Kliknite **Download Chart as HTML** pod vsakim grafom za shranjevanje kot samostojno interaktivno HTML datoteko

### Vsi grafikoni (ZIP)
- Kliknite na **Download All Charts** na vrhu ali dnu razdelka z grafikoni
- Vsak aktiven grafikon se izvozi kot ločena samostojna HTML datoteka, združena v en ZIP prenos
- V ZIP so vključeni samo grafikoni s podatki

### Podatki tabele
- Kliknite desno v AG Grid tabeli → **Export to CSV** ali **Export to Excel**
- Izvozi točno podatke, ki so trenutno vidni v tabeli (upošteva filtre, grupiranje, razvrščanje)

> **Nasvet:** Izvožene HTML datoteke so popolnoma interaktivne — lahko približate, premaknete miško za opise orodij in premikate — ne potrebujete programske opreme, samo spletni brskalnik.

---

## Nasveti in odpravljanje težav

| Težava | Rešitev |
|---|---|
| Nalaganje datoteke ne uspe | Preverite, da je datoteka pod {{VALUE_MAX_FILE_SIZE_MB}} MB in v podprti obliki |
| Povezava SharePoint ne deluje | Microsoft je onemogočil neavtenticiran dostop do API-ja. Prenesite datoteko in uporabite Neposreden prenos datoteke. |
| Google Sheet se ne naloži | Prepričajte se, da je deljenje nastavljeno na "Kdorkoli s povezavo lahko pogleda" |
| Airtable se ne poveže | Preverite, da ima vaš Personal Access Token obsege `data.records:read` in `schema.bases:read`, in da se Base ID začne z `app` |
| Napake pri razčlenjevanju datetime | Preverite, da se izbrana oblika ujema z vašimi podatki. Po potrebi poskusite obliko po meri |
| Grafi so prazni | Prepričajte se, da so podatki naloženi v tabeli in da so izbrani stolpci X/Y |
| Tabela ne prikazuje podatkov po filtriranju | Počistite ali prilagodite vaše filtre stolpcev |

---

## Zasebnost podatkov

- Vsi naloženi podatki se obdelujejo **samo v pomnilniku** (nikoli ne zapisujejo na disk ali v bazo podatkov)
- Podatki so shranjeni v vaši **seji brskalnika** — zapiranje zavihka počisti vse
- Nobeni naloženi podatki se ne pošiljajo zunanjim storitvam
- Shranjujejo se samo prostovoljne povratne informacije in anonimne analitike uporabe
- Oglejte si [PRIVACY.md]({{URL_DOCUMENTATION_AYD_PRIVACY}}) za popolne podrobnosti
