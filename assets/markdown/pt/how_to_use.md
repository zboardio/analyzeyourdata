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

### Microsoft SharePoint / OneDrive — Descontinuado

**A Microsoft desativou o acesso não autenticado à API de partilha do OneDrive.** O endpoint da API que anteriormente permitia carregar ficheiros a partir de links públicos do SharePoint/OneDrive agora retorna erros de autenticação. Esta é uma alteração feita pela Microsoft — não por esta aplicação.

A solução de substituição da Microsoft requer autenticação Azure AD OAuth 2.0, que adiciona fricção significativa (início de sessão com conta Microsoft, aprovação do administrador da organização) com garantias limitadas de estabilidade a longo prazo.

> **Alternativa recomendada:** Transfira o seu ficheiro do SharePoint/OneDrive para o computador e depois utilize o **Carregamento direto de ficheiro** acima. É mais rápido, mais fiável e os seus dados ficam totalmente sob o seu controlo.

### Google Sheets
- Copie a URL da barra do navegador enquanto visualiza a aba da planilha desejada e cole-a
- A aba da planilha (GID) é automaticamente detectada a partir da URL
- O documento deve estar compartilhado como "Qualquer pessoa com o link pode visualizar"

**Como obter a URL:** No Google Sheets, clique em Compartilhar → defina como "Qualquer pessoa com o link" → Leitor. Em seguida, navegue até a aba da planilha que deseja carregar e copie a URL da barra de endereços do navegador (ela contém o ID da planilha automaticamente).

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

## Passo 3: Explore Seus Dados no AG Grid

**AG Grid** fornece uma exploração interativa e poderosa de dados com painéis laterais integrados:

- **Ordenar** — clique em qualquer cabeçalho de coluna
- **Filtrar** — clique no ícone de filtro em qualquer cabeçalho de coluna para definir condições, ou use o **Painel de filtros** no lado direito para gerenciar todos os filtros de coluna em um só lugar
- **Agrupar** — arraste cabeçalhos de coluna para o painel "Row Group" acima da tabela
- **Pivotear** — habilite o modo pivot no **Painel de colunas** no lado direito para tabulações cruzadas
- **Redimensionar** — arraste as bordas das colunas para ajustar as larguras
- **Agregar** — ao agrupar, o AG Grid mostra subtotais e totais gerais
- **Painel de colunas** — alterne a visibilidade das colunas, reordene colunas e configure as definições de pivot/valores a partir do painel lateral
- **Painel de filtros** — visualize e gerencie todos os filtros ativos em todas as colunas a partir de um painel conveniente

> **Importante:** Os gráficos abaixo leem dos **dados atualmente filtrados/agrupados** visíveis no AG Grid. Cada ação de filtro, ordenação ou agrupamento atualiza todos os gráficos instantaneamente — **este é o poder central da ferramenta.** Use o AG Grid como seu fatiador de dados interativo e veja os resultados refletidos em tempo real em todas as suas visualizações.

### Exportação do AG Grid

Use os botões **Export to Excel** e **Export to CSV** abaixo do AG Grid para baixar os dados atualmente visíveis:

- A exportação sempre reflete a **visualização atual** do AG Grid — filtros, agrupamentos e ordenações são respeitados
- **Exportação para Excel** inclui formatação de tabela com filtros ativos, para que você possa continuar filtrando diretamente no Excel
- **Exportação para CSV** fornece um arquivo plano limpo dos dados filtrados
- Isso significa que você pode aplicar diferentes critérios de filtro no AG Grid e exportar várias vezes para criar **arquivos separados para diferentes subconjuntos** dos seus dados — um fluxo de trabalho poderoso para análise de dados e relatórios

> **Dica:** Você também pode clicar com o botão direito em qualquer lugar na tabela AG Grid para opções adicionais de exportação pelo menu de contexto.

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

Os gráficos leem dos dados do AG Grid atualmente filtrados/agrupados. **Cada ação de filtro, ordenação ou agrupamento no AG Grid atualiza todos os gráficos instantaneamente.**

---

## Passo 5: Exportar

### Gráficos Individuais
- Clique em **Download Chart as HTML** abaixo de cada gráfico para salvá-lo como um arquivo HTML interativo independente

### Todos os gráficos (ZIP)
- Clique em **Download All Charts** no topo ou no final da seção de gráficos
- Cada gráfico ativo é exportado como um arquivo HTML independente, agrupados em um único download ZIP
- Apenas gráficos com dados são incluídos no ZIP

### Dados do AG Grid
- Use os botões **Export to Excel** ou **Export to CSV** abaixo do AG Grid (veja Passo 3 acima)
- Exporta exatamente os dados atualmente visíveis no AG Grid (respeita filtros, agrupamentos, ordenação)

> **Dica:** Arquivos HTML de gráficos exportados são totalmente interativos — você pode dar zoom, passar o mouse para dicas de ferramentas e mover — nenhum software necessário, apenas um navegador web.

---

## Dicas e Solução de Problemas

| Problema | Solução |
|---|---|
| Falha no carregamento do arquivo | Verifique se o arquivo tem menos de {{VALUE_MAX_FILE_SIZE_MB}} MB e está em um formato suportado |
| O link do SharePoint não funciona | A Microsoft desativou o acesso não autenticado à API. Transfira o ficheiro e utilize o Carregamento direto de ficheiro. |
| Google Sheet não carrega | Certifique-se de que o compartilhamento está definido como "Qualquer pessoa com o link pode visualizar" |
| Airtable não conecta | Verifique se seu Personal Access Token tem os escopos `data.records:read` e `schema.bases:read`, e se o Base ID começa com `app` |
| Erros de análise de datetime | Verifique se o formato selecionado corresponde aos seus dados. Tente um formato personalizado se necessário |
| Gráficos estão vazios | Certifique-se de que os dados estão carregados no AG Grid e as colunas X/Y estão selecionadas |
| AG Grid não mostra dados após filtro | Limpe ou ajuste seus filtros de coluna no Painel de filtros |

---

## Privacidade de Dados

- Todos os dados carregados são processados **apenas em memória** (nunca gravados em disco ou banco de dados)
- Os dados são armazenados na **sessão do navegador** — fechar a aba limpa tudo
- Nenhum dado carregado é enviado para serviços externos
- Apenas envios voluntários de feedback e análises de uso anônimas são armazenados
- Consulte [PRIVACY.md]({{URL_DOCUMENTATION_AYD_PRIVACY}}) para detalhes completos
