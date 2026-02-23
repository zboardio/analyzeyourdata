# Como usar o Analyze Your Data

## Visão Geral Rápida

**Analyze Your Data** permite que você carregue dados, explore-os em uma grade interativa e crie até 3 gráficos independentes — tudo no seu navegador. Nenhum dado é armazenado no servidor; tudo permanece na sua sessão.

---

## Passo 1: Carregue Seus Dados

Escolha uma das fontes de dados suportadas:

### Carregamento Direto de Arquivo
- Clique na área de upload ou arraste e solte seu arquivo
- **Formatos suportados:** Excel (`.xlsx`, `.xls`), CSV (`.csv`, `.txt`, `.log`), JSON, Parquet, HDF5, SQLite (`.db`, `.sqlite`, `.sqlite3`)
- Para arquivos CSV/TXT/LOG, confirme ou altere o delimitador (vírgula, ponto e vírgula, tabulação, pipe ou espaço)
- Tamanho máximo do arquivo: **{{VALUE_MAX_FILE_SIZE_MB}} MB**

### Banco de Dados SQLite
- Carregue um arquivo `.db`, `.sqlite` ou `.sqlite3`
- Navegue pelas tabelas disponíveis com contagens de linhas e colunas
- Selecione a tabela que você deseja analisar e clique em **Load Selected Table**

### Microsoft SharePoint / OneDrive
- Cole uma URL de compartilhamento com **acesso anônimo** ("Qualquer pessoa com o link pode visualizar")
- Formatos de URL suportados:
  - `https://1drv.ms/x/s!...` (links curtos do OneDrive)
  - `https://onedrive.live.com/...` (links completos do OneDrive)
  - `https://[empresa].sharepoint.com/...` (links do SharePoint)
  - `https://[empresa]-my.sharepoint.com/...` (SharePoint pessoal)
- Se o arquivo tiver várias planilhas, selecione a planilha desejada no menu suspenso

**Como obter uma URL de compartilhamento:** No SharePoint/OneDrive, clique com o botão direito no arquivo → Compartilhar → defina como "Qualquer pessoa com o link pode visualizar" → copie o link.

**URL de teste** — experimente isto para verificar sua configuração:
```
{{URL_TEST_DATASET_SHAREPOINT}}
```

> **Observação:** Locatários corporativos/empresariais do Microsoft 365 podem bloquear links de compartilhamento anônimos devido a políticas de segurança da organização. Esta é uma limitação do lado do SharePoint/OneDrive, não da aplicação. Links do OneDrive pessoal normalmente funcionam sem restrições.

### Google Sheets
- Cole uma URL pública do Google Sheets (`https://docs.google.com/spreadsheets/d/[ID]/edit...`)
- Opcionalmente insira um **GID** (ID da aba da planilha) para carregar uma planilha específica
- O documento deve estar compartilhado como "Qualquer pessoa com o link pode visualizar"

**Como obter uma URL de compartilhamento:** No Google Sheets, clique em Compartilhar → defina como "Qualquer pessoa com o link" → Leitor → copie o link. Para carregar uma aba de planilha específica, copie a URL da barra do navegador e use o número `#gid=123456789` no campo GID.

**URL de teste** — experimente isto para verificar sua configuração:
```
{{URL_TEST_DATASET_GOOGLE}}
```

### Airtable

A conexão com Airtable requer um **Personal Access Token** e um **Base ID**.

#### Como criar um Personal Access Token

1. Vá para [airtable.com/create/tokens]({{URL_DOCUMENTATION_AIRTABLE_TOKENS}}) (ou navegue até sua Conta → Developer Hub → Personal Access Tokens)
2. Clique em **Create new token**
3. Dê um nome a ele (ex: "Analyze Your Data")
4. Em **Scopes**, adicione no mínimo:
   - `data.records:read` — para ler registros de tabelas
   - `schema.bases:read` — para listar tabelas em uma base
5. Em **Access**, selecione a(s) base(s) específica(s) que você deseja conectar
6. Clique em **Create token** e copie-o imediatamente — você não poderá vê-lo novamente

> **Referência:** [Creating Personal Access Tokens — Airtable Support]({{URL_DOCUMENTATION_AIRTABLE_PAT}})

#### Como encontrar seu Base ID

1. Abra sua base do Airtable no navegador
2. Observe a URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. O Base ID é a parte que começa com `app` (ex: `appXXXXXXXXXXXXXX`)

#### Carregando dados

1. Insira seu **Personal Access Token** no campo de token
2. Insira seu **Base ID**
3. Clique em **Connect to Airtable** — as tabelas disponíveis serão listadas
4. Selecione uma tabela e clique em **Load Selected Table**

> **Dica:** Seu token é mantido apenas na memória da sessão do navegador — ele nunca é armazenado no servidor. Fechar a aba do navegador o limpa.


> **Dica:** Para dados sensíveis ou privados, use o Carregamento Direto de Arquivo — seus dados nunca saem do navegador.

---

## Passo 2: Processamento de Data e Hora (Opcional)

O processamento de datetime está **desabilitado por padrão**. Quando desabilitado, seus dados são carregados diretamente na grade — nenhuma etapa extra é necessária.

Se seus dados contiverem uma coluna de datetime e você desejar análise baseada em tempo:

1. Alterne o processamento de datetime para **Enabled**
2. Selecione a **Coluna de Datetime** no menu suspenso
3. Escolha o **Formato de Datetime** correspondente (ou insira um formato personalizado Python `strftime()`)
4. Clique em **Load data to AgGrid Table**

As colunas geradas incluem: `tsYear`, `tsMonth`, `tsDay`, `tsHour`, `tsMinute`, `tsDayOfWeek`, `tsWeekNumber`, `tsDate` e mais.

---

## Passo 3: Explore Seus Dados na Grade

A tabela **AG Grid** fornece exploração poderosa de dados:

- **Ordenar** — clique em qualquer cabeçalho de coluna
- **Filtrar** — clique no ícone de filtro em qualquer cabeçalho de coluna para definir condições
- **Agrupar** — arraste cabeçalhos de coluna para o painel "Row Group" acima da tabela
- **Pivotear** — habilite o modo pivot no menu de coluna para tabulações cruzadas
- **Redimensionar** — arraste as bordas das colunas para ajustar as larguras
- **Agregar** — ao agrupar, a grade mostra subtotais e totais gerais

> **Importante:** Os gráficos abaixo leem dos **dados atualmente filtrados/agrupados** visíveis na grade. Cada ação de filtro, ordenação ou agrupamento atualiza todos os gráficos instantaneamente — **este é o poder central da ferramenta.** Use a grade como seu fatiador de dados interativo e veja os resultados refletidos em tempo real em todas as suas visualizações.


> **Exporte dados da grade:** Clique com o botão direito em qualquer lugar na tabela AG Grid para exportar os dados atualmente filtrados e estruturados diretamente para arquivo **CSV ou Excel**. A exportação reflete exatamente o que você vê na grade — incluindo quaisquer filtros, agrupamentos ou ordenações que você aplicou.

---

## Passo 4: Crie Gráficos

Você pode criar até **3 gráficos independentes**, cada um com sua própria configuração:

1. **Mostrar/Ocultar** — use o alternador para mostrar ou ocultar cada seção de gráfico
2. **Tipo de Gráfico** — escolha entre: Scatter, Scatter (multi y), Line, Bar (grouped), Bar (stacked), Histogram (grouped), Histogram (stacked), Pie, Bubble, Heatmap, Log, Sunburst, Icicle
3. **Coluna do Eixo X** — selecione a coluna para o eixo horizontal
4. **Coluna(s) do Eixo Y** — selecione uma ou mais colunas para o eixo vertical
5. **Coluna de Cor** (opcional) — colore os pontos de dados por uma coluna categórica
6. **Coluna do Eixo Z** (opcional) — para tipos de gráfico Bubble e Heatmap
7. **Títulos** — defina título personalizado do gráfico, título do eixo X e título do eixo Y

Os gráficos leem dos dados da grade atualmente filtrados/agrupados. **Cada ação de filtro, ordenação ou agrupamento na grade atualiza todos os gráficos instantaneamente.**

---

## Passo 5: Exportar

### Gráficos Individuais
- Clique em **Download Chart as HTML** abaixo de cada gráfico para salvá-lo como um arquivo HTML interativo independente

### Todos os gráficos (ZIP)
- Clique em **Download All Charts** no topo ou no final da seção de gráficos
- Cada gráfico ativo é exportado como um arquivo HTML independente, agrupados em um único download ZIP
- Apenas gráficos com dados são incluídos no ZIP

### Dados da Grade
- Clique com o botão direito na tabela AG Grid → **Export to CSV** ou **Export to Excel**
- Exporta exatamente os dados atualmente visíveis na grade (respeita filtros, agrupamentos, ordenação)

> **Dica:** Arquivos HTML exportados são totalmente interativos — você pode dar zoom, passar o mouse para dicas de ferramentas e mover — nenhum software necessário, apenas um navegador web.

---

## Dicas e Solução de Problemas

| Problema | Solução |
|---|---|
| Falha no carregamento do arquivo | Verifique se o arquivo tem menos de {{VALUE_MAX_FILE_SIZE_MB}} MB e está em um formato suportado |
| Link do SharePoint não funciona | Certifique-se de que o link permite acesso anônimo (sem necessidade de login). Locatários corporativos podem bloquear isso. |
| Google Sheet não carrega | Certifique-se de que o compartilhamento está definido como "Qualquer pessoa com o link pode visualizar" |
| Airtable não conecta | Verifique se seu Personal Access Token tem os escopos `data.records:read` e `schema.bases:read`, e se o Base ID começa com `app` |
| Erros de análise de datetime | Verifique se o formato selecionado corresponde aos seus dados. Tente um formato personalizado se necessário |
| Gráficos estão vazios | Certifique-se de que os dados estão carregados na grade e as colunas X/Y estão selecionadas |
| Grade não mostra dados após filtro | Limpe ou ajuste seus filtros de coluna |

---

## Privacidade de Dados

- Todos os dados carregados são processados **apenas em memória** (nunca gravados em disco ou banco de dados)
- Os dados são armazenados na **sessão do navegador** — fechar a aba limpa tudo
- Nenhum dado carregado é enviado para serviços externos
- Apenas envios voluntários de feedback e análises de uso anônimas são armazenados
- Consulte [PRIVACY.md]({{URL_DOCUMENTATION_AYD_PRIVACY}}) para detalhes completos
