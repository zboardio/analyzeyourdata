# Ako používať Analyze Your Data

## Rýchly prehľad

**Analyze Your Data** vám umožňuje nahrať dáta, preskúmať ich v interaktívnej tabuľke a vytvoriť až 3 nezávislé grafy — všetko vo vašom prehliadači. Žiadne dáta nie sú uložené na serveri; všetko zostáva vo vašej relácii.

---

## Krok 1: Načítajte svoje dáta

Vyberte jeden z podporovaných zdrojov dát:

### Priamy upload súboru
- Kliknite na oblasť nahrávania alebo pretiahnite súbor
- **Podporované formáty:** Excel (`.xlsx`, `.xls`), CSV (`.csv`, `.txt`, `.log`), JSON, Parquet, HDF5, SQLite (`.db`, `.sqlite`, `.sqlite3`)
- Pre CSV/TXT/LOG súbory potvrďte alebo zmeňte oddeľovač (čiarka, bodkočiarka, tabulátor, zvislá čiara alebo medzera)
- Maximálna veľkosť súboru: **{{VALUE_MAX_FILE_SIZE_MB}} MB**

### SQLite databáza
- Nahrajte `.db`, `.sqlite`, alebo `.sqlite3` súbor
- Prezrite dostupné tabuľky s počtom riadkov a stĺpcov
- Vyberte tabuľku, ktorú chcete analyzovať a kliknite na **Load Selected Table**

### Microsoft SharePoint / OneDrive — Ukončené

**Microsoft zablokoval neautentifikovaný prístup k API na zdieľanie OneDrive.** Koncový bod API, ktorý predtým umožňoval načítavanie súborov z verejných odkazov SharePoint/OneDrive, teraz vracia chyby autentifikácie. Toto je zmena vykonaná spoločnosťou Microsoft — nie touto aplikáciou.

Náhradné riešenie od Microsoftu vyžaduje autentifikáciu Azure AD OAuth 2.0, ktorá pridáva značné prekážky (prihlásenie účtom Microsoft, schválenie administrátorom organizácie) s obmedzenými zárukami dlhodobej stability.

> **Odporúčaná alternatíva:** Stiahnite si súbor zo SharePoint/OneDrive do počítača a potom použite **Priame nahranie súboru** vyššie. Je to rýchlejšie, spoľahlivejšie a vaše dáta zostávajú plne pod vašou kontrolou.

### Google Sheets
- Vložte verejnú Google Sheets URL (`https://docs.google.com/spreadsheets/d/[ID]/edit...`)
- Voliteľne zadajte **GID** (ID hárku) pre načítanie konkrétneho hárku
- Dokument musí byť zdieľaný ako "Ktokoľvek s odkazom môže zobraziť"

**Ako získať zdieľaciu URL:** V Google Sheets kliknite na Zdieľať → nastavte na "Ktokoľvek s odkazom" → Čitateľ → skopírujte odkaz. Pre načítanie konkrétneho hárku skopírujte URL z panela prehliadača a použite číslo `#gid=123456789` v poli GID.

**Testovacia URL** — vyskúšajte ju pre overenie vášho nastavenia:
```
{{URL_TEST_DATASET_GOOGLE}}
```

### Airtable

Pripojenie k Airtable vyžaduje **Personal Access Token** a **Base ID**.

#### Ako vytvoriť Personal Access Token

1. Prejdite na [airtable.com/create/tokens]({{URL_DOCUMENTATION_AIRTABLE_TOKENS}}) (alebo navigujte na váš účet → Developer Hub → Personal Access Tokens)
2. Kliknite na **Create new token**
3. Pomenujte ho (napr. "Analyze Your Data")
4. Pod **Scopes** pridajte minimálne:
   - `data.records:read` — na čítanie záznamov tabuľky
   - `schema.bases:read` — na výpis tabuliek v databáze
5. Pod **Access** vyberte konkrétne databázy, ku ktorým sa chcete pripojiť
6. Kliknite na **Create token** a okamžite ho skopírujte — už sa k nemu nedostanete

> **Referencia:** [Creating Personal Access Tokens — Airtable Support]({{URL_DOCUMENTATION_AIRTABLE_PAT}})

#### Ako nájsť váš Base ID

1. Otvorte svoju Airtable databázu v prehliadači
2. Pozrite sa na URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. Base ID je časť začínajúca `app` (napr. `appXXXXXXXXXXXXXX`)

#### Načítanie dát

1. Zadajte váš **Personal Access Token** do poľa tokenu
2. Zadajte váš **Base ID**
3. Kliknite na **Connect to Airtable** — dostupné tabuľky sa zobrazia
4. Vyberte tabuľku a kliknite na **Load Selected Table**

> **Tip:** Váš token je uložený len v pamäti prehliadača — nikdy nie je uložený na serveri. Zatvorenie záložky prehliadača ho vymaže.


> **Tip:** Pre citlivé alebo súkromné dáta použite priamy upload súboru — vaše dáta nikdy neopustia prehliadač.

---

## Krok 2: Spracovanie dátumu a času (voliteľné)

Spracovanie dátumu a času je **predvolene vypnuté**. Keď je vypnuté, vaše dáta sa načítajú priamo do tabuľky — nie sú potrebné žiadne ďalšie kroky.

Ak vaše dáta obsahujú stĺpec s dátumom a časom a chcete časovú analýzu:

1. Prepnite spracovanie dátumu a času na **Zapnuté**
2. Vyberte **Datetime Column** z rozbaľovacieho zoznamu
3. Vyberte zodpovedajúci **Datetime Format** (alebo zadajte vlastný Python `strftime()` formát)
4. Kliknite na **Load data to AgGrid Table**

Generované stĺpce zahŕňajú: `tsYear`, `tsMonth`, `tsDay`, `tsHour`, `tsMinute`, `tsDayOfWeek`, `tsWeekNumber`, `tsDate` a ďalšie.

---

## Krok 3: Preskúmajte svoje dáta v tabuľke

Tabuľka **AG Grid** poskytuje výkonné skúmanie dát:

- **Zoradiť** — kliknite na hlavičku ľubovoľného stĺpca
- **Filtrovať** — kliknite na ikonu filtra v hlavičke ľubovoľného stĺpca pre nastavenie podmienok
- **Zoskupiť** — pretiahnite hlavičky stĺpcov do panela "Row Group" nad tabuľkou
- **Pivotovať** — aktivujte pivot režim z ponuky stĺpca pre krížové tabuľky
- **Zmeniť veľkosť** — pretiahnite okraje stĺpcov pre úpravu šírky
- **Agregovať** — pri zoskupovaní tabuľka zobrazuje medzisúčty a celkové súčty

> **Kľúčové:** Grafy nižšie čítajú z **aktuálne filtrovaných/zoskupených dát** viditeľných v tabuľke. Každá akcia filtra, zoradenia alebo zoskupenia okamžite aktualizuje všetky grafy — **to je hlavná sila tohto nástroja.** Použite tabuľku ako interaktívny nástroj na rezanie dát a pozorujte výsledky v reálnom čase vo všetkých vašich vizualizáciách.


> **Exportujte dáta z tabuľky:** Kliknite pravým tlačidlom kdekoľvek v AG Grid tabuľke na export aktuálne filtrovaných a štruktúrovaných dát priamo do **CSV alebo Excel** súboru. Export odráža presne to, čo vidíte v tabuľke — vrátane všetkých filtrov, zoskupení alebo zoradení, ktoré ste aplikovali.

---

## Krok 4: Vytvorte grafy

Môžete vytvoriť až **3 nezávislé grafy**, každý s vlastnou konfiguráciou:

1. **Zobraziť/Skryť** — použite prepínač pre zobrazenie alebo skrytie každej sekcie grafu
2. **Typ grafu** — vyberte z: Scatter, Scatter (multi y), Line, Bar (grouped), Bar (stacked), Histogram (grouped), Histogram (stacked), Pie, Bubble, Heatmap, Log, Sunburst, Icicle
3. **X-Axis Column** — vyberte stĺpec pre horizontálnu os
4. **Y-Axis Column(s)** — vyberte jeden alebo viac stĺpcov pre vertikálnu os
5. **Color Column** (voliteľné) — zafarbite dátové body podľa kategoriálneho stĺpca
6. **Z-Axis Column** (voliteľné) — pre typy grafov Bubble a Heatmap
7. **Titulky** — nastavte vlastný titulok grafu, titulok osi X a titulok osi Y

Grafy čítajú z aktuálne filtrovaných/zoskupených dát tabuľky. **Každá akcia filtra, zoradenia alebo zoskupenia v tabuľke okamžite aktualizuje všetky grafy.**

---

## Krok 5: Export

### Jednotlivé grafy
- Kliknite na **Download Chart as HTML** pod každým grafom pre uloženie ako samostatný interaktívny HTML súbor

### Všetky grafy (ZIP)
- Kliknite na **Download All Charts** v hornej alebo dolnej časti sekcie grafov
- Každý aktívny graf sa exportuje ako samostatný HTML súbor, zabalený do jedného ZIP súboru na stiahnutie
- Do ZIPu sú zahrnuté iba grafy s dátami

### Dáta tabuľky
- Kliknite pravým tlačidlom v AG Grid tabuľke → **Export to CSV** alebo **Export to Excel**
- Exportuje presne tie dáta, ktoré sú momentálne viditeľné v tabuľke (rešpektuje filtre, zoskupenie, zoradenie)

> **Tip:** Exportované HTML súbory sú plne interaktívne — môžete priblížiť, posúvať pre zobrazenie popiskov a posúvať — nie je potrebný žiadny softvér, iba webový prehliadač.

---

## Tipy a riešenie problémov

| Problém | Riešenie |
|---|---|
| Nahranie súboru zlyhá | Skontrolujte, že súbor má menej ako {{VALUE_MAX_FILE_SIZE_MB}} MB a je v podporovanom formáte |
| Odkaz na SharePoint nefunguje | Microsoft zablokoval neautentifikovaný prístup k API. Stiahnite súbor a použite Priame nahranie súboru. |
| Google Sheet sa nenačíta | Uistite sa, že zdieľanie je nastavené na "Ktokoľvek s odkazom môže zobraziť" |
| Airtable sa nepripojí | Overte, že váš Personal Access Token má oprávnenia `data.records:read` a `schema.bases:read` a Base ID začína na `app` |
| Chyby pri spracovaní dátumu a času | Overte, že vybraný formát zodpovedá vašim dátam. Ak je potrebné, vyskúšajte vlastný formát |
| Grafy sú prázdne | Uistite sa, že dáta sú načítané v tabuľke a stĺpce X/Y sú vybrané |
| Tabuľka nezobrazuje žiadne dáta po filtrovaní | Vymažte alebo upravte filtre stĺpcov |

---

## Ochrana osobných údajov

- Všetky nahrané dáta sú spracované **len v pamäti** (nikdy nie sú zapísané na disk alebo databázu)
- Dáta sú uložené vo vašej **relácii prehliadača** — zatvorenie záložky všetko vymaže
- Žiadne nahrané dáta nie sú odoslané na externé služby
- Ukladajú sa len dobrovoľné odoslania spätnej väzby a anonymná analytika používania
- Pozrite si [PRIVACY.md]({{URL_DOCUMENTATION_AYD_PRIVACY}}) pre kompletné detaily
