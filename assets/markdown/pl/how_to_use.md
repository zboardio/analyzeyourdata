# Jak korzystać z Analyze Your Data

## Szybki przegląd

**Analyze Your Data** umożliwia przesyłanie danych, eksplorację w interaktywnej tabeli i tworzenie do 3 niezależnych wykresów — wszystko w przeglądarce. Żadne dane nie są przechowywane na serwerze; wszystko pozostaje w Twojej sesji.

---

## Krok 1: Wczytaj dane

Wybierz jedno z obsługiwanych źródeł danych:

### Bezpośrednie przesyłanie pliku
- Kliknij obszar przesyłania lub przeciągnij i upuść plik
- **Obsługiwane formaty:** Excel (`.xlsx`, `.xls`), CSV (`.csv`, `.txt`, `.log`), JSON, Parquet, HDF5, SQLite (`.db`, `.sqlite`, `.sqlite3`)
- W przypadku plików CSV/TXT/LOG potwierdź lub zmień separator (przecinek, średnik, tabulator, pionowa kreska lub spacja)
- Maksymalny rozmiar pliku: **{{VALUE_MAX_FILE_SIZE_MB}} MB**

### Baza danych SQLite
- Prześlij plik `.db`, `.sqlite` lub `.sqlite3`
- Przeglądaj dostępne tabele z liczbą wierszy i kolumn
- Wybierz tabelę do analizy i kliknij **Load Selected Table**

### Microsoft SharePoint / OneDrive
- Wklej adres URL udostępniania z **anonimowym dostępem** ("Każdy z linkiem może wyświetlać")
- Obsługiwane formaty adresów URL:
  - `https://1drv.ms/x/s!...` (krótkie linki OneDrive)
  - `https://onedrive.live.com/...` (pełne linki OneDrive)
  - `https://[company].sharepoint.com/...` (linki SharePoint)
  - `https://[company]-my.sharepoint.com/...` (SharePoint osobisty)
- Jeśli plik zawiera wiele arkuszy, wybierz odpowiedni arkusz z listy rozwijanej

**Jak uzyskać adres URL udostępniania:** W SharePoint/OneDrive kliknij prawym przyciskiem myszy na plik → Udostępnij → ustaw na "Każdy z linkiem może wyświetlać" → skopiuj link.

**Testowy URL** — wypróbuj, aby zweryfikować konfigurację:
```
{{URL_TEST_DATASET_SHAREPOINT}}
```

> **Uwaga:** Korporacyjne dzierżawy Microsoft 365 mogą blokować anonimowe linki udostępniania ze względu na polityki bezpieczeństwa organizacji. Jest to ograniczenie po stronie SharePoint/OneDrive, nie aplikacji. Osobiste linki OneDrive zazwyczaj działają bez ograniczeń.

### Google Sheets
- Wklej publiczny adres URL Google Sheets (`https://docs.google.com/spreadsheets/d/[ID]/edit...`)
- Opcjonalnie wprowadź **GID** (identyfikator zakładki arkusza), aby wczytać konkretny arkusz
- Dokument musi być udostępniony jako "Każdy z linkiem może wyświetlać"

**Jak uzyskać adres URL udostępniania:** W Google Sheets kliknij Udostępnij → ustaw na "Każdy z linkiem" → Przeglądający → skopiuj link. Aby wczytać konkretną zakładkę arkusza, skopiuj adres URL z paska przeglądarki i użyj numeru `#gid=123456789` w polu GID.

**Testowy URL** — wypróbuj, aby zweryfikować konfigurację:
```
{{URL_TEST_DATASET_GOOGLE}}
```

### Airtable

Połączenie z Airtable wymaga **Personal Access Token** i **Base ID**.

#### Jak utworzyć Personal Access Token

1. Przejdź do [airtable.com/create/tokens]({{URL_DOCUMENTATION_AIRTABLE_TOKENS}}) (lub przejdź do swojego Konta → Developer Hub → Personal Access Tokens)
2. Kliknij **Create new token**
3. Nadaj mu nazwę (np. "Analyze Your Data")
4. W sekcji **Scopes** dodaj co najmniej:
   - `data.records:read` — do odczytu rekordów tabel
   - `schema.bases:read` — do wyświetlania listy tabel w bazie
5. W sekcji **Access** wybierz konkretną bazę/bazy, z którymi chcesz się połączyć
6. Kliknij **Create token** i natychmiast go skopiuj — później nie będziesz mógł go zobaczyć

> **Dokumentacja:** [Tworzenie Personal Access Tokenów — Airtable Support]({{URL_DOCUMENTATION_AIRTABLE_PAT}})

#### Jak znaleźć Base ID

1. Otwórz swoją bazę Airtable w przeglądarce
2. Sprawdź adres URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. Base ID to część zaczynająca się od `app` (np. `appXXXXXXXXXXXXXX`)

#### Wczytywanie danych

1. Wprowadź swój **Personal Access Token** w pole tokena
2. Wprowadź swoje **Base ID**
3. Kliknij **Connect to Airtable** — wyświetli się lista dostępnych tabel
4. Wybierz tabelę i kliknij **Load Selected Table**

> **Wskazówka:** Twój token jest przechowywany wyłącznie w pamięci sesji przeglądarki — nigdy nie jest zapisywany na serwerze. Zamknięcie karty przeglądarki go usuwa.

> **Wskazówka:** W przypadku wrażliwych lub prywatnych danych użyj bezpośredniego przesyłania pliku — Twoje dane nigdy nie opuszczają przeglądarki.

---

## Krok 2: Przetwarzanie daty i czasu (opcjonalne)

Przetwarzanie daty i czasu jest domyślnie **wyłączone**. Gdy jest wyłączone, dane ładują się bezpośrednio do tabeli — nie są potrzebne żadne dodatkowe kroki.

Jeśli Twoje dane zawierają kolumnę z datą i czasem i chcesz przeprowadzić analizę czasową:

1. Przełącz przetwarzanie daty i czasu na **Włączone**
2. Wybierz **kolumnę z datą i czasem** z listy rozwijanej
3. Wybierz odpowiedni **format daty i czasu** (lub wprowadź niestandardowy format Pythona `strftime()`)
4. Kliknij **Load data to AgGrid Table**

Wygenerowane kolumny obejmują: `tsYear`, `tsMonth`, `tsDay`, `tsHour`, `tsMinute`, `tsDayOfWeek`, `tsWeekNumber`, `tsDate` i inne.

---

## Krok 3: Eksploruj dane w tabeli

Tabela **AG Grid** zapewnia zaawansowaną eksplorację danych:

- **Sortowanie** — kliknij nagłówek dowolnej kolumny
- **Filtrowanie** — kliknij ikonę filtra w nagłówku dowolnej kolumny, aby ustawić warunki
- **Grupowanie** — przeciągnij nagłówki kolumn do panelu "Row Group" nad tabelą
- **Pivotowanie** — włącz tryb pivota z menu kolumny dla tabel krzyżowych
- **Zmiana rozmiaru** — przeciągnij krawędzie kolumn, aby dostosować szerokość
- **Agregacja** — podczas grupowania tabela pokazuje sumy częściowe i sumy końcowe

> **Kluczowe:** Wykresy poniżej odczytują dane z **aktualnie przefiltrowanych/zgrupowanych danych** widocznych w tabeli. Każde filtrowanie, sortowanie lub grupowanie natychmiast aktualizuje wszystkie wykresy — **to jest główna siła tego narzędzia.** Używaj tabeli jako interaktywnego narzędzia do wycinania danych i obserwuj wyniki odzwierciedlane w czasie rzeczywistym we wszystkich wizualizacjach.

> **Eksport danych z tabeli:** Kliknij prawym przyciskiem myszy gdziekolwiek w tabeli AG Grid, aby wyeksportować aktualnie przefiltrowane i ustrukturyzowane dane bezpośrednio do pliku **CSV lub Excel**. Eksport dokładnie odzwierciedla to, co widzisz w tabeli — łącznie ze wszystkimi zastosowanymi filtrami, grupowaniem i sortowaniem.

---

## Krok 4: Tworzenie wykresów

Możesz utworzyć do **3 niezależnych wykresów**, każdy z własną konfiguracją:

1. **Pokaż/Ukryj** — użyj przełącznika, aby pokazać lub ukryć sekcję każdego wykresu
2. **Typ wykresu** — wybierz spośród: Scatter, Scatter (multi y), Line, Bar (grouped), Bar (stacked), Histogram (grouped), Histogram (stacked), Pie, Bubble, Heatmap, Log, Sunburst, Icicle
3. **Kolumna osi X** — wybierz kolumnę dla osi poziomej
4. **Kolumna(y) osi Y** — wybierz jedną lub więcej kolumn dla osi pionowej
5. **Kolumna koloru** (opcjonalnie) — koloruj punkty danych według kolumny kategorycznej
6. **Kolumna osi Z** (opcjonalnie) — dla typów wykresów Bubble i Heatmap
7. **Tytuły** — ustaw niestandardowy tytuł wykresu, tytuł osi X i tytuł osi Y

Wykresy odczytują dane z aktualnie przefiltrowanych/zgrupowanych danych w tabeli. **Każde filtrowanie, sortowanie lub grupowanie w tabeli natychmiast aktualizuje wszystkie wykresy.**

---

## Krok 5: Eksport

### Pojedyncze wykresy
- Kliknij **Download Chart as HTML** pod każdym wykresem, aby zapisać go jako samodzielny interaktywny plik HTML

### Wszystkie wykresy (ZIP)
- Kliknij **Download All Charts** na górze lub na dole sekcji wykresów
- Każdy aktywny wykres jest eksportowany jako osobny samodzielny plik HTML, spakowane razem w jednym pliku ZIP do pobrania
- Do pliku ZIP trafiają tylko wykresy zawierające dane

### Dane z tabeli
- Kliknij prawym przyciskiem myszy w tabeli AG Grid → **Export to CSV** lub **Export to Excel**
- Eksportuje dokładnie te dane, które są aktualnie widoczne w tabeli (uwzględnia filtry, grupowanie, sortowanie)

> **Wskazówka:** Wyeksportowane pliki HTML są w pełni interaktywne — można przybliżać, najeżdżać kursorem dla podpowiedzi i przesuwać — nie potrzeba żadnego oprogramowania, wystarczy przeglądarka internetowa.

---

## Porady i rozwiązywanie problemów

| Problem | Rozwiązanie |
|---|---|
| Przesyłanie pliku nie powiodło się | Sprawdź, czy plik ma mniej niż {{VALUE_MAX_FILE_SIZE_MB}} MB i jest w obsługiwanym formacie |
| Link SharePoint nie działa | Upewnij się, że link umożliwia anonimowy dostęp (bez konieczności logowania). Dzierżawy korporacyjne mogą to blokować. |
| Google Sheet się nie wczytuje | Upewnij się, że udostępnianie jest ustawione na "Każdy z linkiem może wyświetlać" |
| Airtable nie łączy się | Sprawdź, czy Twój Personal Access Token ma uprawnienia `data.records:read` i `schema.bases:read` oraz czy Base ID zaczyna się od `app` |
| Błędy parsowania daty i czasu | Sprawdź, czy wybrany format odpowiada Twoim danym. W razie potrzeby wypróbuj niestandardowy format |
| Wykresy są puste | Upewnij się, że dane są wczytane do tabeli i kolumny X/Y są wybrane |
| Tabela nie pokazuje danych po filtrowaniu | Wyczyść lub dostosuj filtry kolumn |

---

## Prywatność danych

- Wszystkie przesłane dane są przetwarzane **wyłącznie w pamięci** (nigdy nie są zapisywane na dysku ani w bazie danych)
- Dane są przechowywane w **sesji przeglądarki** — zamknięcie karty usuwa wszystko
- Żadne przesłane dane nie są wysyłane do usług zewnętrznych
- Przechowywane są jedynie dobrowolne zgłoszenia opinii i anonimowe statystyki użytkowania
- Szczegóły znajdziesz w [PRIVACY.md]({{URL_DOCUMENTATION_AYD_PRIVACY}})
