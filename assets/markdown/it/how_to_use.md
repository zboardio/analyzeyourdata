# Come utilizzare Analyze Your Data

## Panoramica Rapida

**Analyze Your Data** ti permette di caricare dati, esplorarli in una griglia interattiva e creare fino a 3 grafici indipendenti — tutto nel tuo browser. Nessun dato viene memorizzato sul server; tutto rimane nella tua sessione.

---

## Passo 1: Carica i Tuoi Dati

Scegli una delle sorgenti dati supportate:

### Caricamento Diretto di File
- Clicca sull'area di caricamento o trascina e rilascia il tuo file
- **Formati supportati:** Excel (`.xlsx`, `.xls`), CSV (`.csv`, `.txt`, `.log`), JSON, Parquet, HDF5, SQLite (`.db`, `.sqlite`, `.sqlite3`)
- Per file CSV/TXT/LOG, conferma o cambia il delimitatore (virgola, punto e virgola, tabulazione, pipe o spazio)
- Dimensione massima del file: **{{VALUE_MAX_FILE_SIZE_MB}} MB**

### Database SQLite
- Carica un file `.db`, `.sqlite` o `.sqlite3`
- Sfoglia le tabelle disponibili con conteggi di righe e colonne
- Seleziona la tabella che vuoi analizzare e clicca **Load Selected Table**

### Microsoft SharePoint / OneDrive — Interrotto

**Microsoft ha disabilitato l'accesso non autenticato all'API di condivisione di OneDrive.** L'endpoint API che in precedenza consentiva il caricamento di file da link pubblici SharePoint/OneDrive ora restituisce errori di autenticazione. Questa è una modifica apportata da Microsoft — non da questa applicazione.

La soluzione sostitutiva di Microsoft richiede l'autenticazione Azure AD OAuth 2.0, che aggiunge notevole complessità (accesso con account Microsoft, approvazione dell'amministratore dell'organizzazione) con garanzie limitate di stabilità a lungo termine.

> **Alternativa consigliata:** Scarica il tuo file da SharePoint/OneDrive sul computer, quindi usa il **Caricamento diretto file** sopra. È più veloce, più affidabile e i tuoi dati restano completamente sotto il tuo controllo.

### Google Sheets
- Copia l'URL dalla barra del browser mentre visualizzi la scheda foglio desiderata e incollalo
- La scheda foglio (GID) viene rilevata automaticamente dall'URL
- Il documento deve essere condiviso come "Chiunque con il link può visualizzare"

**Come ottenere l'URL:** In Google Sheets, clicca Condividi → imposta su "Chiunque con il link" → Visualizzatore. Poi naviga alla scheda foglio che desideri caricare e copia l'URL dalla barra degli indirizzi del browser (contiene l'ID del foglio automaticamente).

**URL di Test** — prova questo per verificare la tua configurazione:
```
{{URL_TEST_DATASET_GOOGLE}}
```

### Airtable

La connessione Airtable richiede un **Personal Access Token** e un **Base ID**.

#### Come creare un Personal Access Token

1. Vai su [airtable.com/create/tokens]({{URL_DOCUMENTATION_AIRTABLE_TOKENS}}) (o naviga su Account → Developer Hub → Personal Access Tokens)
2. Clicca **Create new token**
3. Assegnagli un nome (es. "Analyze Your Data")
4. Sotto **Scopes**, aggiungi come minimo:
   - `data.records:read` — per leggere i record della tabella
   - `schema.bases:read` — per elencare le tabelle in una base
5. Sotto **Access**, seleziona le basi specifiche a cui vuoi connetterti
6. Clicca **Create token** e copialo immediatamente — non potrai vederlo di nuovo

> **Riferimento:** [Creating Personal Access Tokens — Airtable Support]({{URL_DOCUMENTATION_AIRTABLE_PAT}})

#### Come trovare il tuo Base ID

1. Apri la tua base Airtable nel browser
2. Guarda l'URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. Il Base ID è la parte che inizia con `app` (es. `appXXXXXXXXXXXXXX`)

#### Caricamento dati

1. Inserisci il tuo **Personal Access Token** nel campo token
2. Inserisci il tuo **Base ID**
3. Clicca **Connect to Airtable** — verranno elencate le tabelle disponibili
4. Seleziona una tabella e clicca **Load Selected Table**

> **Suggerimento:** Il tuo token viene mantenuto solo nella memoria della sessione del browser — non viene mai memorizzato sul server. Chiudendo la scheda del browser viene cancellato.


> **Suggerimento:** Per dati sensibili o privati, usa il Caricamento Diretto di File — i tuoi dati non lasciano mai il browser.

---

## Passo 2: Elaborazione Datetime (Opzionale)

L'elaborazione datetime è **disabilitata per impostazione predefinita**. Quando è disabilitata, i tuoi dati vengono caricati direttamente nella griglia — nessun passaggio aggiuntivo necessario.

Se i tuoi dati contengono una colonna datetime e desideri un'analisi basata sul tempo:

1. Attiva l'elaborazione datetime su **Abilitata**
2. Seleziona la **Colonna Datetime** dal menu a discesa
3. Scegli il **Formato Datetime** corrispondente (o inserisci un formato Python `strftime()` personalizzato)
4. Clicca **Load data to AgGrid Table**

Le colonne generate includono: `tsYear`, `tsMonth`, `tsDay`, `tsHour`, `tsMinute`, `tsDayOfWeek`, `tsWeekNumber`, `tsDate` e altro.

---

## Passo 3: Esplora i Tuoi Dati in AG Grid

**AG Grid** fornisce una potente esplorazione interattiva dei dati con pannelli laterali integrati:

- **Ordina** — clicca su qualsiasi intestazione di colonna
- **Filtra** — clicca sull'icona del filtro su qualsiasi intestazione di colonna per impostare condizioni, oppure usa il **Pannello filtri** sul lato destro per gestire tutti i filtri delle colonne in un unico posto
- **Raggruppa** — trascina le intestazioni di colonna nel pannello "Row Group" sopra la tabella
- **Pivot** — abilita la modalità pivot dal **Pannello colonne** sul lato destro per tabulazioni incrociate
- **Ridimensiona** — trascina i bordi delle colonne per regolare le larghezze
- **Aggrega** — durante il raggruppamento, AG Grid mostra subtotali e totali generali
- **Pannello colonne** — attiva/disattiva la visibilità delle colonne, riordina le colonne e configura le impostazioni di pivot/valori dal pannello laterale
- **Pannello filtri** — visualizza e gestisci tutti i filtri attivi su tutte le colonne da un unico pannello comodo

> **Chiave:** I grafici sottostanti leggono dai **dati attualmente filtrati/raggruppati** visibili in AG Grid. Ogni azione di filtro, ordinamento o raggruppamento aggiorna istantaneamente tutti i grafici — **questo è il potere centrale dello strumento.** Usa AG Grid come il tuo slicer di dati interattivo e vedi i risultati riflessi in tempo reale in tutte le tue visualizzazioni.

### Esportazione da AG Grid

Usa i pulsanti **Export to Excel** e **Export to CSV** sotto AG Grid per scaricare i dati attualmente visibili:

- L'esportazione riflette sempre la **vista corrente** di AG Grid — filtri, raggruppamenti e ordinamenti sono rispettati
- **L'esportazione Excel** include la formattazione della tabella con i filtri attivi, così puoi continuare a filtrare direttamente in Excel
- **L'esportazione CSV** fornisce un file piatto pulito dei dati filtrati
- Questo significa che puoi applicare diversi criteri di filtro in AG Grid ed esportare più volte per creare **file separati per diversi sottoinsiemi** dei tuoi dati — un flusso di lavoro potente per l'analisi dei dati e il reporting

> **Suggerimento:** Puoi anche fare clic destro ovunque nella tabella AG Grid per opzioni di esportazione aggiuntive tramite il menu contestuale.

---

## Passo 4: Crea Grafici

Puoi creare fino a **3 grafici indipendenti**, ciascuno con la propria configurazione:

1. **Mostra/Nascondi** — usa l'interruttore per mostrare o nascondere ogni sezione grafico
2. **Tipo di Grafico** — scegli tra: Scatter, Scatter (multi y), Line, Bar (grouped), Bar (stacked), Histogram (grouped), Histogram (stacked), Pie, Bubble, Heatmap, Log, Sunburst, Icicle
3. **Colonna Asse X** — seleziona la colonna per l'asse orizzontale
4. **Colonna(e) Asse Y** — seleziona una o più colonne per l'asse verticale
5. **Colonna Colore** (opzionale) — colora i punti dati per una colonna categorica
6. **Colonna Asse Z** (opzionale) — per i tipi di grafici Bubble e Heatmap
7. **Titoli** — imposta titolo grafico personalizzato, titolo asse X e titolo asse Y

I grafici leggono dai dati di AG Grid attualmente filtrati/raggruppati. **Ogni azione di filtro, ordinamento o raggruppamento in AG Grid aggiorna istantaneamente tutti i grafici.**

---

## Passo 5: Esporta

### Grafici Individuali
- Clicca **Download Chart as HTML** sotto ogni grafico per salvarlo come file HTML interattivo autonomo

### Tutti i grafici (ZIP)
- Clicca su **Download All Charts** nella parte superiore o inferiore della sezione grafici
- Ogni grafico attivo viene esportato come file HTML autonomo, raggruppati in un unico download ZIP
- Nel file ZIP sono inclusi solo i grafici con dati

### Dati AG Grid
- Usa i pulsanti **Export to Excel** o **Export to CSV** sotto AG Grid (vedi Passo 3 sopra)
- Esporta esattamente i dati attualmente visibili in AG Grid (rispetta filtri, raggruppamenti, ordinamenti)

> **Suggerimento:** I file HTML dei grafici esportati sono completamente interattivi — puoi ingrandire, passare il mouse per i tooltip e fare pan — nessun software necessario, solo un browser web.

---

## Suggerimenti e Risoluzione Problemi

| Problema | Soluzione |
|---|---|
| Caricamento file fallisce | Verifica che il file sia sotto i {{VALUE_MAX_FILE_SIZE_MB}} MB e in un formato supportato |
| Il link SharePoint non funziona | Microsoft ha disabilitato l'accesso non autenticato all'API. Scarica il file e usa il Caricamento diretto file. |
| Google Sheet non si carica | Assicurati che la condivisione sia impostata su "Chiunque con il link può visualizzare" |
| Airtable non si connette | Verifica che il tuo Personal Access Token abbia gli scope `data.records:read` e `schema.bases:read`, e che il Base ID inizi con `app` |
| Errori di parsing datetime | Verifica che il formato selezionato corrisponda ai tuoi dati. Prova un formato personalizzato se necessario |
| I grafici sono vuoti | Assicurati che i dati siano caricati in AG Grid e che le colonne X/Y siano selezionate |
| AG Grid non mostra dati dopo il filtro | Cancella o regola i filtri delle colonne nel Pannello filtri |

---

## Privacy dei Dati

- Tutti i dati caricati vengono elaborati **solo in memoria** (mai scritti su disco o database)
- I dati vengono memorizzati nella **sessione del browser** — chiudendo la scheda si cancella tutto
- Nessun dato caricato viene inviato a servizi esterni
- Vengono memorizzate solo le sottomissioni di feedback volontarie e analisi di utilizzo anonime
- Vedi [PRIVACY.md]({{URL_DOCUMENTATION_AYD_PRIVACY}}) per i dettagli completi
