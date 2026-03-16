# Jak používat Analyze Your Data

## Stručný přehled

**Analyze Your Data** vám umožňuje nahrát data, interaktivně je prozkoumat v tabulce a vytvořit až 3 nezávislé grafy — vše přímo v prohlížeči. Na serveru se neukládají žádná data; vše zůstává ve vaší relaci.

---

## Krok 1: Načtěte svá data

Vyberte si jeden z podporovaných zdrojů dat:

### Přímé nahrání souboru
- Klikněte na oblast pro nahrání nebo přetáhněte soubor myší
- **Podporované formáty:** Excel (`.xlsx`, `.xls`), CSV (`.csv`, `.txt`, `.log`), JSON, Parquet, HDF5, SQLite (`.db`, `.sqlite`, `.sqlite3`)
- U souborů CSV/TXT/LOG potvrďte nebo změňte oddělovač (čárka, středník, tabulátor, svislítko nebo mezera)
- Maximální velikost souboru: **{{VALUE_MAX_FILE_SIZE_MB}} MB**

### SQLite databáze
- Nahrajte soubor `.db`, `.sqlite` nebo `.sqlite3`
- Procházejte dostupné tabulky s počtem řádků a sloupců
- Vyberte tabulku, kterou chcete analyzovat, a klikněte na **Load Selected Table**

### Microsoft SharePoint / OneDrive — Ukončeno

**Microsoft zablokoval neautentizovaný přístup k API pro sdílení OneDrive.** Koncový bod API, který dříve umožňoval načítání souborů z veřejných odkazů SharePoint/OneDrive, nyní vrací chyby autentizace. Toto je změna provedená společností Microsoft — nikoli touto aplikací.

Náhradní řešení od Microsoftu vyžaduje autentizaci Azure AD OAuth 2.0, která přidává značné překážky (přihlášení účtem Microsoft, schválení administrátorem organizace) s omezenými zárukami dlouhodobé stability.

> **Doporučená alternativa:** Stáhněte si soubor ze SharePoint/OneDrive do počítače a poté použijte **Přímé nahrání souboru** výše. Je to rychlejší, spolehlivější a vaše data zůstávají plně pod vaší kontrolou.

### Google Sheets
- Zkopírujte URL z adresního řádku prohlížeče při zobrazení požadované záložky listu a vložte ji
- Záložka listu (GID) je automaticky rozpoznána z URL
- Dokument musí být sdílen jako "Kdokoli s odkazem může zobrazit"

**Jak získat URL:** V Google Sheets klikněte na Sdílet → nastavte "Kdokoli s odkazem" → Čtenář. Poté přejděte na záložku listu, kterou chcete načíst, a zkopírujte URL z adresního řádku prohlížeče (automaticky obsahuje ID listu).

**Testovací URL** — vyzkoušejte pro ověření funkčnosti:
```
{{URL_TEST_DATASET_GOOGLE}}
```

### Airtable

Připojení k Airtable vyžaduje **Personal Access Token** a **Base ID**.

#### Jak vytvořit Personal Access Token

1. Přejděte na [airtable.com/create/tokens]({{URL_DOCUMENTATION_AIRTABLE_TOKENS}}) (nebo navigujte do svého Účtu → Developer Hub → Personal Access Tokens)
2. Klikněte na **Create new token**
3. Pojmenujte ho (např. "Analyze Your Data")
4. V části **Scopes** přidejte minimálně:
   - `data.records:read` — pro čtení záznamů tabulek
   - `schema.bases:read` — pro výpis tabulek v bázi
5. V části **Access** vyberte konkrétní bázi/báze, ke kterým se chcete připojit
6. Klikněte na **Create token** a okamžitě ho zkopírujte — poté ho již neuvidíte

> **Odkaz:** [Vytváření Personal Access Tokenů — Airtable podpora]({{URL_DOCUMENTATION_AIRTABLE_PAT}})

#### Jak najít Base ID

1. Otevřete svou Airtable bázi v prohlížeči
2. Podívejte se na URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. Base ID je část začínající na `app` (např. `appXXXXXXXXXXXXXX`)

#### Načtení dat

1. Zadejte svůj **Personal Access Token** do pole pro token
2. Zadejte své **Base ID**
3. Klikněte na **Connect to Airtable** — zobrazí se seznam dostupných tabulek
4. Vyberte tabulku a klikněte na **Load Selected Table**

> **Tip:** Váš token je uložen pouze v paměti relace prohlížeče — nikdy se neukládá na server. Zavření záložky prohlížeče ho smaže.

> **Tip:** Pro citlivá nebo soukromá data použijte přímé nahrání souboru — vaše data nikdy neopustí prohlížeč.

---

## Krok 2: Zpracování data a času (volitelné)

Zpracování data a času je ve výchozím nastavení **vypnuto**. Když je vypnuto, data se načtou přímo do tabulky — nejsou potřeba žádné další kroky.

Pokud vaše data obsahují sloupec s datem a časem a chcete provádět časovou analýzu:

1. Přepněte zpracování data a času na **Zapnuto**
2. Vyberte **sloupec s datem a časem** z rozbalovací nabídky
3. Zvolte odpovídající **formát data a času** (nebo zadejte vlastní Python `strftime()` formát)
4. Klikněte na **Load data to AgGrid Table**

Vygenerované sloupce zahrnují: `tsYear`, `tsMonth`, `tsDay`, `tsHour`, `tsMinute`, `tsDayOfWeek`, `tsWeekNumber`, `tsDate` a další.

---

## Krok 3: Prozkoumejte svá data v AG Grid

**AG Grid** poskytuje výkonné interaktivní nástroje pro práci s daty s vestavěnými bočními panely:

- **Řazení** — klikněte na záhlaví libovolného sloupce
- **Filtrování** — klikněte na ikonu filtru v záhlaví sloupce pro nastavení podmínek, nebo použijte **Panel filtrů** na pravé straně pro správu všech filtrů sloupců na jednom místě
- **Seskupování** — přetáhněte záhlaví sloupců do panelu "Row Group" nad tabulkou
- **Pivotování** — aktivujte režim pivot z **Panelu sloupců** na pravé straně pro křížové tabulky
- **Změna šířky** — přetáhněte okraje sloupců pro úpravu šířky
- **Agregace** — při seskupování AG Grid zobrazuje mezisoučty a celkové součty
- **Panel sloupců** — přepínejte viditelnost sloupců, měňte pořadí sloupců a konfigurujte nastavení pivotu/hodnot z bočního panelu
- **Panel filtrů** — zobrazujte a spravujte všechny aktivní filtry napříč sloupci z jednoho přehledného panelu

> **Klíčové:** Grafy níže čtou z **aktuálně filtrovaných/seskupených dat** viditelných v AG Grid. Každý filtr, řazení nebo seskupení okamžitě aktualizuje všechny grafy — **to je hlavní síla tohoto nástroje.** Používejte AG Grid jako interaktivní průřez daty a sledujte výsledky promítnuté v reálném čase do všech vašich vizualizací.

### Export z AG Grid

Použijte tlačítka **Export to Excel** a **Export to CSV** pod AG Grid pro stažení aktuálně viditelných dat:

- Export vždy odpovídá **aktuálnímu zobrazení** AG Grid — filtry, seskupování a řazení jsou respektovány
- **Export do Excelu** zahrnuje formátování tabulky s aktivními filtry, takže můžete pokračovat ve filtrování přímo v Excelu
- **Export do CSV** poskytuje čistý plochý soubor filtrovaných dat
- To znamená, že můžete aplikovat různá kritéria filtrů v AG Grid a exportovat vícekrát pro vytvoření **samostatných souborů pro různé podmnožiny** vašich dat — výkonný pracovní postup pro analýzu dat a reporting

> **Tip:** Můžete také kliknout pravým tlačítkem kamkoli v tabulce AG Grid pro další možnosti exportu prostřednictvím kontextového menu.

---

## Krok 4: Vytvořte grafy

Můžete vytvořit až **3 nezávislé grafy**, každý s vlastním nastavením:

1. **Zobrazit/Skrýt** — pomocí přepínače zobrazte nebo skryjte sekci každého grafu
2. **Typ grafu** — vyberte z: Scatter, Scatter (multi y), Line, Bar (grouped), Bar (stacked), Histogram (grouped), Histogram (stacked), Pie, Bubble, Heatmap, Log, Sunburst, Icicle
3. **Sloupec osy X** — vyberte sloupec pro vodorovnou osu
4. **Sloupec/sloupce osy Y** — vyberte jeden nebo více sloupců pro svislou osu
5. **Sloupec barvy** (volitelné) — obarvěte datové body podle kategoriálního sloupce
6. **Sloupec osy Z** (volitelné) — pro typy grafů Bubble a Heatmap
7. **Názvy** — nastavte vlastní název grafu, název osy X a název osy Y

Grafy čtou z aktuálně filtrovaných/seskupených dat v AG Grid. **Každý filtr, řazení nebo seskupení v AG Grid okamžitě aktualizuje všechny grafy.**

---

## Krok 5: Export

### Jednotlivé grafy
- Klikněte na **Download Chart as HTML** pod každým grafem pro uložení jako samostatný interaktivní HTML soubor

### Všechny grafy (ZIP)
- Klikněte na **Download All Charts** v horní nebo dolní části sekce grafů
- Každý aktivní graf se exportuje jako samostatný HTML soubor, zabalený do jednoho ZIP souboru ke stažení
- Do ZIPu jsou zahrnuty pouze grafy s daty

### Data z AG Grid
- Použijte tlačítka **Export to Excel** nebo **Export to CSV** pod AG Grid (viz Krok 3 výše)
- Exportuje přesně ta data, která jsou aktuálně viditelná v AG Grid (respektuje filtry, seskupování, řazení)

> **Tip:** Exportované HTML soubory grafů jsou plně interaktivní — můžete přibližovat, najet myší pro zobrazení popisků a posouvat — není potřeba žádný software, stačí webový prohlížeč.

---

## Tipy a řešení problémů

| Problém | Řešení |
|---|---|
| Nahrání souboru selže | Zkontrolujte, že soubor má méně než {{VALUE_MAX_FILE_SIZE_MB}} MB a je v podporovaném formátu |
| Odkaz na SharePoint nefunguje | Microsoft zablokoval neautentizovaný přístup k API. Stáhněte soubor a použijte Přímé nahrání souboru. |
| Google Sheet se nenačte | Ujistěte se, že sdílení je nastaveno na "Kdokoli s odkazem může zobrazit" |
| Airtable se nepřipojí | Ověřte, že váš Personal Access Token má oprávnění `data.records:read` a `schema.bases:read` a že Base ID začíná na `app` |
| Chyby při zpracování data a času | Ověřte, že vybraný formát odpovídá vašim datům. V případě potřeby zkuste vlastní formát |
| Grafy jsou prázdné | Ujistěte se, že jsou data načtena v AG Grid a jsou vybrány sloupce X/Y |
| AG Grid nezobrazuje data po filtrování | Zrušte nebo upravte filtry sloupců v Panelu filtrů |

---

## Ochrana osobních údajů

- Všechna nahraná data jsou zpracovávána **pouze v paměti** (nikdy se nezapisují na disk ani do databáze)
- Data jsou uložena ve vaší **relaci prohlížeče** — zavření záložky vše smaže
- Žádná nahraná data nejsou odesílána externím službám
- Ukládají se pouze dobrovolně odeslané zpětné vazby a anonymní analytika využití
- Podrobnosti naleznete v [PRIVACY.md]({{URL_DOCUMENTATION_AYD_PRIVACY}})
