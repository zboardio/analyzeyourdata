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

**Microsoft je onemogočil neavtenticiran dostop do API-ja za skupno rabo OneDrive.** Končna točka API-ja, ki je prej omogočala nalaganje datotek prek javnih povezav SharePoint/OneDrive, zdaj vrača napake pri avtentikaciji. To je sprememba, ki jo je izvedel Microsoft — ne ta aplikacija.

Microsoftova nadomestna rešitev zahteva avtentikacijo Azure AD OAuth 2.0, ki dodaja znatne ovire (prijava z Microsoftovim računom, odobritev skrbnika organizacije) z omejenimi jamstvi dolgoročne stabilnosti.

> **Priporočena alternativa:** Prenesite svojo datoteko iz SharePoint/OneDrive na računalnik in nato uporabite **Neposreden prenos datoteke** zgoraj. To je hitrejše, zanesljivejše in vaši podatki ostanejo v celoti pod vašim nadzorom.

### Google Sheets
- Kopirajte URL iz vrstice brskalnika med ogledom želenega zavihka lista in ga prilepite
- Zavihek lista (GID) se samodejno zazna iz URL-ja
- Dokument mora biti deljen kot "Kdorkoli s povezavo lahko pogleda"

**Kako dobiti URL:** V Google Sheets kliknite Deli → nastavite na "Kdorkoli s povezavo" → Gledalec. Nato se pomaknite na zavihek lista, ki ga želite naložiti, in kopirajte URL iz vrstice brskalnika (samodejno vsebuje ID lista).

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

## Korak 3: Raziščite svoje podatke v AG Grid

**AG Grid** ponuja močno interaktivno raziskovanje podatkov z vgrajenimi stranskimi ploščami:

- **Razvrsti** — kliknite na katerikoli glavo stolpca
- **Filtriraj** — kliknite na ikono filtra na katerikoli glavi stolpca za nastavitev pogojev, ali uporabite **Ploščo filtrov** na desni strani za upravljanje vseh filtrov stolpcev na enem mestu
- **Grupiraj** — povlecite glave stolpcev v ploščo "Row Group" nad tabelo
- **Obračaj** — omogočite pivot način iz **Plošče stolpcev** na desni strani za navzkrižne tabelacije
- **Spremeni velikost** — povlecite obrobe stolpcev za prilagoditev širin
- **Agregacija** — pri grupiranju AG Grid prikazuje vmesne seštevke in skupne seštevke
- **Plošča stolpcev** — preklapljajte vidnost stolpcev, prerazporejajte stolpce in konfigurirajte nastavitve pivota/vrednosti iz stranske plošče
- **Plošča filtrov** — oglejte si in upravljajte vse aktivne filtre v vseh stolpcih iz ene priročne plošče

> **Ključno:** Grafi spodaj berejo iz **trenutno filtriranih/grupiranih podatkov**, vidnih v AG Grid. Vsaka akcija filtriranja, razvrščanja ali grupiranja takoj posodobi vse grafe — **to je osnovna moč tega orodja.** Uporabite AG Grid kot vaš interaktivni rezalnik podatkov in vidite rezultate, ki se odražajo v realnem času v vseh vaših vizualizacijah.

### Izvoz iz AG Grid

Uporabite gumba **Export to Excel** in **Export to CSV** pod AG Grid za prenos trenutno vidnih podatkov:

- Izvoz vedno odraža **trenutni pogled** AG Grid — filtri, grupiranje in razvrščanje so upoštevani
- **Izvoz v Excel** vključuje oblikovanje tabele z aktivnimi filtri, tako da lahko nadaljujete filtriranje neposredno v Excelu
- **Izvoz v CSV** zagotavlja čisto ravno datoteko filtriranih podatkov
- To pomeni, da lahko uporabite različna merila filtrov v AG Grid in izvozite večkrat za ustvarjanje **ločenih datotek za različne podmnožice** vaših podatkov — zmogljiv delovni tok za analizo podatkov in poročanje

> **Nasvet:** Lahko tudi kliknete desno kjerkoli v AG Grid tabeli za dodatne možnosti izvoza prek kontekstnega menija.

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

Grafi berejo iz trenutno filtriranih/grupiranih podatkov AG Grid. **Vsaka akcija filtriranja, razvrščanja ali grupiranja v AG Grid takoj posodobi vse grafe.**

---

## Korak 5: Izvoz

### Posamezni grafi
- Kliknite **Download Chart as HTML** pod vsakim grafom za shranjevanje kot samostojno interaktivno HTML datoteko

### Vsi grafikoni (ZIP)
- Kliknite na **Download All Charts** na vrhu ali dnu razdelka z grafikoni
- Vsak aktiven grafikon se izvozi kot ločena samostojna HTML datoteka, združena v en ZIP prenos
- V ZIP so vključeni samo grafikoni s podatki

### Podatki AG Grid
- Uporabite gumba **Export to Excel** ali **Export to CSV** pod AG Grid (glejte Korak 3 zgoraj)
- Izvozi točno podatke, ki so trenutno vidni v AG Grid (upošteva filtre, grupiranje, razvrščanje)

> **Nasvet:** Izvožene HTML datoteke grafov so popolnoma interaktivne — lahko približate, premaknete miško za opise orodij in premikate — ne potrebujete programske opreme, samo spletni brskalnik.

---

## Nasveti in odpravljanje težav

| Težava | Rešitev |
|---|---|
| Nalaganje datoteke ne uspe | Preverite, da je datoteka pod {{VALUE_MAX_FILE_SIZE_MB}} MB in v podprti obliki |
| Povezava SharePoint ne deluje | Microsoft je onemogočil neavtenticiran dostop do API-ja. Prenesite datoteko in uporabite Neposreden prenos datoteke. |
| Google Sheet se ne naloži | Prepričajte se, da je deljenje nastavljeno na "Kdorkoli s povezavo lahko pogleda" |
| Airtable se ne poveže | Preverite, da ima vaš Personal Access Token obsege `data.records:read` in `schema.bases:read`, in da se Base ID začne z `app` |
| Napake pri razčlenjevanju datetime | Preverite, da se izbrana oblika ujema z vašimi podatki. Po potrebi poskusite obliko po meri |
| Grafi so prazni | Prepričajte se, da so podatki naloženi v AG Grid in da so izbrani stolpci X/Y |
| AG Grid ne prikazuje podatkov po filtriranju | Počistite ali prilagodite vaše filtre stolpcev v Plošči filtrov |

---

## Zasebnost podatkov

- Vsi naloženi podatki se obdelujejo **samo v pomnilniku** (nikoli ne zapisujejo na disk ali v bazo podatkov)
- Podatki so shranjeni v vaši **seji brskalnika** — zapiranje zavihka počisti vse
- Nobeni naloženi podatki se ne pošiljajo zunanjim storitvam
- Shranjujejo se samo prostovoljne povratne informacije in anonimne analitike uporabe
- Oglejte si [PRIVACY.md]({{URL_DOCUMENTATION_AYD_PRIVACY}}) za popolne podrobnosti
