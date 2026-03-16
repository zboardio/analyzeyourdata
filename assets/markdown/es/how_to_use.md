# Cómo usar Analyze Your Data

## Descripción General

**Analyze Your Data** le permite cargar datos, explorarlos en una tabla interactiva y crear hasta 3 gráficos independientes — todo en su navegador. Ningún dato se almacena en el servidor; todo permanece en su sesión.

---

## Paso 1: Cargue Sus Datos

Elija una de las fuentes de datos compatibles:

### Carga Directa de Archivos
- Haga clic en el área de carga o arrastre y suelte su archivo
- **Formatos compatibles:** Excel (`.xlsx`, `.xls`), CSV (`.csv`, `.txt`, `.log`), JSON, Parquet, HDF5, SQLite (`.db`, `.sqlite`, `.sqlite3`)
- Para archivos CSV/TXT/LOG, confirme o cambie el delimitador (coma, punto y coma, tabulación, pipe o espacio)
- Tamaño máximo de archivo: **{{VALUE_MAX_FILE_SIZE_MB}} MB**

### Base de Datos SQLite
- Cargue un archivo `.db`, `.sqlite` o `.sqlite3`
- Navegue por las tablas disponibles con conteos de filas y columnas
- Seleccione la tabla que desea analizar y haga clic en **Load Selected Table**

### Microsoft SharePoint / OneDrive — Descontinuado

**Microsoft ha desactivado el acceso no autenticado a la API de uso compartido de OneDrive.** El endpoint de la API que anteriormente permitía cargar archivos desde enlaces públicos de SharePoint/OneDrive ahora devuelve errores de autenticación. Este es un cambio realizado por Microsoft — no por esta aplicación.

La solución de reemplazo de Microsoft requiere autenticación Azure AD OAuth 2.0, que añade una fricción significativa (inicio de sesión con cuenta Microsoft, aprobación del administrador de la organización) con garantías limitadas de estabilidad a largo plazo.

> **Alternativa recomendada:** Descargue su archivo de SharePoint/OneDrive a su computadora y luego use la **Carga directa de archivos** de arriba. Es más rápido, más fiable y sus datos permanecen completamente bajo su control.

### Google Sheets
- Copie la URL de la barra del navegador mientras visualiza la pestaña de hoja deseada y péguela
- La pestaña de hoja (GID) se detecta automáticamente desde la URL
- El documento debe estar compartido como "Cualquiera con el enlace puede ver"

**Cómo obtener la URL:** En Google Sheets, haga clic en Compartir → establezca en "Cualquiera con el enlace" → Lector. Luego navegue a la pestaña de hoja que desea cargar y copie la URL de la barra de direcciones de su navegador (contiene el ID de hoja automáticamente).

**URL de prueba** — pruebe esto para verificar su configuración:
```
{{URL_TEST_DATASET_GOOGLE}}
```

### Airtable

La conexión a Airtable requiere un **Personal Access Token** y un **Base ID**.

#### Cómo crear un Personal Access Token

1. Vaya a [airtable.com/create/tokens]({{URL_DOCUMENTATION_AIRTABLE_TOKENS}}) (o navegue a su Cuenta → Developer Hub → Personal Access Tokens)
2. Haga clic en **Create new token**
3. Asígnele un nombre (ej. "Analyze Your Data")
4. Bajo **Scopes**, agregue como mínimo:
   - `data.records:read` — para leer registros de tablas
   - `schema.bases:read` — para listar tablas en una base
5. Bajo **Access**, seleccione la(s) base(s) específica(s) a las que desea conectarse
6. Haga clic en **Create token** y cópielo inmediatamente — no podrá verlo nuevamente

> **Referencia:** [Creating Personal Access Tokens — Airtable Support]({{URL_DOCUMENTATION_AIRTABLE_PAT}})

#### Cómo encontrar su Base ID

1. Abra su base de Airtable en el navegador
2. Mire la URL: `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. El Base ID es la parte que comienza con `app` (ej. `appXXXXXXXXXXXXXX`)

#### Cargando datos

1. Ingrese su **Personal Access Token** en el campo de token
2. Ingrese su **Base ID**
3. Haga clic en **Connect to Airtable** — las tablas disponibles se listarán
4. Seleccione una tabla y haga clic en **Load Selected Table**

> **Consejo:** Su token se mantiene únicamente en la memoria de la sesión del navegador — nunca se almacena en el servidor. Cerrar la pestaña del navegador lo borra.


> **Consejo:** Para datos sensibles o privados, use Carga Directa de Archivos — sus datos nunca salen del navegador.

---

## Paso 2: Procesamiento de Fecha y Hora (Opcional)

El procesamiento de fecha y hora está **deshabilitado por defecto**. Cuando está deshabilitado, sus datos se cargan directamente en la tabla — no se necesitan pasos adicionales.

Si sus datos contienen una columna de fecha y hora y desea análisis basado en tiempo:

1. Cambie el procesamiento de fecha y hora a **Habilitado**
2. Seleccione la **Columna de Fecha y Hora** del menú desplegable
3. Elija el **Formato de Fecha y Hora** correspondiente (o ingrese un formato personalizado Python `strftime()`)
4. Haga clic en **Load data to AgGrid Table**

Las columnas generadas incluyen: `tsYear`, `tsMonth`, `tsDay`, `tsHour`, `tsMinute`, `tsDayOfWeek`, `tsWeekNumber`, `tsDate`, y más.

---

## Paso 3: Explore Sus Datos en AG Grid

**AG Grid** proporciona una exploración de datos interactiva y poderosa con paneles laterales integrados:

- **Ordenar** — haga clic en cualquier encabezado de columna
- **Filtrar** — haga clic en el icono de filtro en cualquier encabezado de columna para establecer condiciones, o use el **Panel de filtros** en el lado derecho para gestionar todos los filtros de columna en un solo lugar
- **Agrupar** — arrastre encabezados de columna al panel "Row Group" sobre la tabla
- **Pivotar** — habilite el modo pivot desde el **Panel de columnas** en el lado derecho para tabulaciones cruzadas
- **Redimensionar** — arrastre los bordes de las columnas para ajustar anchos
- **Agregar** — al agrupar, AG Grid muestra subtotales y totales generales
- **Panel de columnas** — active o desactive la visibilidad de columnas, reordene columnas y configure ajustes de pivot/valores desde el panel lateral
- **Panel de filtros** — vea y gestione todos los filtros activos en todas las columnas desde un panel conveniente

> **Clave:** Los gráficos a continuación leen de los **datos actualmente filtrados/agrupados** visibles en AG Grid. Cada acción de filtrar, ordenar o agrupar actualiza todos los gráficos instantáneamente — **este es el poder principal de la herramienta.** Use AG Grid como su segmentador de datos interactivo y vea los resultados reflejados en tiempo real en todas sus visualizaciones.

### Exportar desde AG Grid

Use los botones **Export to Excel** y **Export to CSV** debajo de AG Grid para descargar los datos actualmente visibles:

- La exportación siempre refleja la **vista actual** de AG Grid — los filtros, agrupaciones y ordenamientos se respetan
- **Exportar a Excel** incluye el formato de tabla con filtros activos, para que pueda continuar filtrando directamente en Excel
- **Exportar a CSV** proporciona un archivo plano limpio de los datos filtrados
- Esto significa que puede aplicar diferentes criterios de filtro en AG Grid y exportar varias veces para crear **archivos separados para diferentes subconjuntos** de sus datos — un flujo de trabajo poderoso para el análisis de datos y la generación de informes

> **Consejo:** También puede hacer clic derecho en cualquier lugar de la tabla AG Grid para opciones de exportación adicionales a través del menú contextual.

---

## Paso 4: Cree Gráficos

Puede crear hasta **3 gráficos independientes**, cada uno con su propia configuración:

1. **Mostrar/Ocultar** — use el interruptor para mostrar u ocultar cada sección de gráfico
2. **Tipo de Gráfico** — elija entre: Scatter, Scatter (multi y), Line, Bar (grouped), Bar (stacked), Histogram (grouped), Histogram (stacked), Pie, Bubble, Heatmap, Log, Sunburst, Icicle
3. **Columna del Eje X** — seleccione la columna para el eje horizontal
4. **Columna(s) del Eje Y** — seleccione una o más columnas para el eje vertical
5. **Columna de Color** (opcional) — coloree puntos de datos por una columna categórica
6. **Columna del Eje Z** (opcional) — para tipos de gráficos Bubble y Heatmap
7. **Títulos** — establezca título personalizado del gráfico, título del eje X y título del eje Y

Los gráficos leen de los datos de AG Grid actualmente filtrados/agrupados. **Cada acción de filtrar, ordenar o agrupar en AG Grid actualiza todos los gráficos instantáneamente.**

---

## Paso 5: Exportar

### Gráficos Individuales
- Haga clic en **Download Chart as HTML** debajo de cada gráfico para guardarlo como un archivo HTML interactivo independiente

### Todos los gráficos (ZIP)
- Haz clic en **Download All Charts** en la parte superior o inferior de la sección de gráficos
- Cada gráfico activo se exporta como un archivo HTML independiente, agrupados en una descarga ZIP
- Solo se incluyen en el ZIP los gráficos con datos

### Datos de AG Grid
- Use los botones **Export to Excel** o **Export to CSV** debajo de AG Grid (ver Paso 3 arriba)
- Exporta exactamente los datos actualmente visibles en AG Grid (respeta filtros, agrupación, ordenamiento)

> **Consejo:** Los archivos HTML de gráficos exportados son completamente interactivos — puede hacer zoom, pasar el cursor para ver información y desplazarse — no se necesita software, solo un navegador web.

---

## Consejos y Solución de Problemas

| Problema | Solución |
|---|---|
| Falla la carga del archivo | Verifique que el archivo sea menor de {{VALUE_MAX_FILE_SIZE_MB}} MB y esté en un formato compatible |
| El enlace de SharePoint no funciona | Microsoft ha desactivado el acceso no autenticado a la API. Descargue el archivo y use la Carga directa de archivos en su lugar. |
| Google Sheet no se carga | Asegúrese de que el compartir esté establecido en "Cualquiera con el enlace puede ver" |
| Airtable no se conecta | Verifique que su Personal Access Token tenga los scopes `data.records:read` y `schema.bases:read`, y que el Base ID comience con `app` |
| Errores de análisis de fecha y hora | Verifique que el formato seleccionado coincida con sus datos. Pruebe un formato personalizado si es necesario |
| Los gráficos están vacíos | Asegúrese de que los datos estén cargados en AG Grid y que las columnas X/Y estén seleccionadas |
| AG Grid no muestra datos después de filtrar | Limpie o ajuste sus filtros de columna en el Panel de filtros |

---

## Privacidad de Datos

- Todos los datos cargados se procesan **solo en memoria** (nunca se escriben en disco o base de datos)
- Los datos se almacenan en su **sesión de navegador** — cerrar la pestaña lo borra todo
- Ningún dato cargado se envía a servicios externos
- Solo se almacenan envíos voluntarios de comentarios y análisis de uso anónimos
- Vea [PRIVACY.md]({{URL_DOCUMENTATION_AYD_PRIVACY}}) para detalles completos
