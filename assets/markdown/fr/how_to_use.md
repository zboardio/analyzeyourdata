# Comment utiliser Analyze Your Data

## Aperçu rapide

**Analyze Your Data** vous permet de télécharger des données, de les explorer dans une grille interactive et de créer jusqu'à 3 graphiques indépendants — le tout dans votre navigateur. Aucune donnée n'est stockée sur le serveur ; tout reste dans votre session.

---

## Étape 1 : Charger vos données

Choisissez l'une des sources de données prises en charge :

### Téléchargement direct de fichier
- Cliquez sur la zone de téléchargement ou faites glisser-déposer votre fichier
- **Formats pris en charge :** Excel (`.xlsx`, `.xls`), CSV (`.csv`, `.txt`, `.log`), JSON, Parquet, HDF5, SQLite (`.db`, `.sqlite`, `.sqlite3`)
- Pour les fichiers CSV/TXT/LOG, confirmez ou modifiez le délimiteur (virgule, point-virgule, tabulation, barre verticale ou espace)
- Taille maximale du fichier : **{{VALUE_MAX_FILE_SIZE_MB}} MB**

### Base de données SQLite
- Téléchargez un fichier `.db`, `.sqlite` ou `.sqlite3`
- Parcourez les tables disponibles avec leur nombre de lignes et de colonnes
- Sélectionnez la table que vous souhaitez analyser et cliquez sur **Load Selected Table**

### Microsoft SharePoint / OneDrive
- Collez une URL de partage avec **accès anonyme** ("Toute personne disposant du lien peut afficher")
- Formats d'URL pris en charge :
  - `https://1drv.ms/x/s!...` (liens courts OneDrive)
  - `https://onedrive.live.com/...` (liens complets OneDrive)
  - `https://[company].sharepoint.com/...` (liens SharePoint)
  - `https://[company]-my.sharepoint.com/...` (SharePoint personnel)
- Si le fichier contient plusieurs feuilles, sélectionnez la feuille souhaitée dans le menu déroulant

**Comment obtenir une URL de partage :** Dans SharePoint/OneDrive, faites un clic droit sur le fichier → Partager → définir sur "Toute personne disposant du lien peut afficher" → copier le lien.

**URL de test** — essayez ceci pour vérifier votre configuration :
```
{{URL_TEST_DATASET_SHAREPOINT}}
```

> **Remarque :** Les locataires Microsoft 365 d'entreprise peuvent bloquer les liens de partage anonymes en raison des politiques de sécurité de l'organisation. Il s'agit d'une limitation du côté SharePoint/OneDrive, pas de l'application. Les liens OneDrive personnels fonctionnent généralement sans restrictions.

### Google Sheets
- Collez une URL publique Google Sheets (`https://docs.google.com/spreadsheets/d/[ID]/edit...`)
- Entrez éventuellement un **GID** (ID de l'onglet de feuille) pour charger une feuille spécifique
- Le document doit être partagé en tant que "Toute personne disposant du lien peut afficher"

**Comment obtenir une URL de partage :** Dans Google Sheets, cliquez sur Partager → définir sur "Toute personne disposant du lien" → Lecteur → copier le lien. Pour charger un onglet de feuille spécifique, copiez l'URL depuis la barre du navigateur et utilisez le numéro `#gid=123456789` dans le champ GID.

**URL de test** — essayez ceci pour vérifier votre configuration :
```
{{URL_TEST_DATASET_GOOGLE}}
```

### Airtable

La connexion Airtable nécessite un **Personal Access Token** et un **Base ID**.

#### Comment créer un Personal Access Token

1. Accédez à [airtable.com/create/tokens]({{URL_DOCUMENTATION_AIRTABLE_TOKENS}}) (ou naviguez vers votre Compte → Developer Hub → Personal Access Tokens)
2. Cliquez sur **Create new token**
3. Donnez-lui un nom (par exemple "Analyze Your Data")
4. Sous **Scopes**, ajoutez au minimum :
   - `data.records:read` — pour lire les enregistrements de table
   - `schema.bases:read` — pour lister les tables dans une base
5. Sous **Access**, sélectionnez la ou les bases spécifiques auxquelles vous souhaitez vous connecter
6. Cliquez sur **Create token** et copiez-le immédiatement — vous ne pourrez plus le voir par la suite

> **Référence :** [Creating Personal Access Tokens — Airtable Support]({{URL_DOCUMENTATION_AIRTABLE_PAT}})

#### Comment trouver votre Base ID

1. Ouvrez votre base Airtable dans le navigateur
2. Regardez l'URL : `https://airtable.com/appXXXXXXXXXXXXXX/...`
3. Le Base ID est la partie commençant par `app` (par exemple `appXXXXXXXXXXXXXX`)

#### Chargement des données

1. Entrez votre **Personal Access Token** dans le champ token
2. Entrez votre **Base ID**
3. Cliquez sur **Connect to Airtable** — les tables disponibles seront listées
4. Sélectionnez une table et cliquez sur **Load Selected Table**

> **Astuce :** Votre token est conservé uniquement dans la mémoire de session du navigateur — il n'est jamais stocké sur le serveur. Fermer l'onglet du navigateur l'efface.


> **Astuce :** Pour des données sensibles ou privées, utilisez le téléchargement direct de fichier — vos données ne quittent jamais le navigateur.

---

## Étape 2 : Traitement des dates/heures (Optionnel)

Le traitement des dates/heures est **désactivé par défaut**. Lorsqu'il est désactivé, vos données se chargent directement dans la grille — aucune étape supplémentaire n'est nécessaire.

Si vos données contiennent une colonne datetime et que vous souhaitez une analyse temporelle :

1. Activez le traitement datetime sur **Enabled**
2. Sélectionnez la **Datetime Column** dans le menu déroulant
3. Choisissez le **Datetime Format** correspondant (ou entrez un format Python `strftime()` personnalisé)
4. Cliquez sur **Load data to AgGrid Table**

Les colonnes générées incluent : `tsYear`, `tsMonth`, `tsDay`, `tsHour`, `tsMinute`, `tsDayOfWeek`, `tsWeekNumber`, `tsDate`, et plus encore.

---

## Étape 3 : Explorer vos données dans la grille

La table **AG Grid** offre une exploration de données puissante :

- **Trier** — cliquez sur n'importe quel en-tête de colonne
- **Filtrer** — cliquez sur l'icône de filtre sur n'importe quel en-tête de colonne pour définir des conditions
- **Regrouper** — faites glisser les en-têtes de colonne dans le panneau "Row Group" au-dessus de la table
- **Pivoter** — activez le mode pivot depuis le menu de colonne pour les tableaux croisés
- **Redimensionner** — faites glisser les bordures de colonne pour ajuster les largeurs
- **Agréger** — lors du regroupement, la grille affiche les sous-totaux et les totaux généraux

> **Important :** Les graphiques ci-dessous lisent les **données actuellement filtrées/regroupées** visibles dans la grille. Chaque action de filtre, tri ou regroupement met à jour tous les graphiques instantanément — **c'est la puissance fondamentale de l'outil.** Utilisez la grille comme votre sélecteur de données interactif et voyez les résultats reflétés en temps réel dans toutes vos visualisations.


> **Exportez les données depuis la grille :** Faites un clic droit n'importe où dans la table AG Grid pour exporter les données actuellement filtrées et structurées directement vers un fichier **CSV ou Excel**. L'export reflète exactement ce que vous voyez dans la grille — y compris tous les filtres, regroupements ou tris que vous avez appliqués.

---

## Étape 4 : Créer des graphiques

Vous pouvez créer jusqu'à **3 graphiques indépendants**, chacun avec sa propre configuration :

1. **Afficher/Masquer** — utilisez le bouton pour afficher ou masquer chaque section de graphique
2. **Type de graphique** — choisissez parmi : Scatter, Scatter (multi y), Line, Bar (grouped), Bar (stacked), Histogram (grouped), Histogram (stacked), Pie, Bubble, Heatmap, Log, Sunburst, Icicle
3. **Colonne de l'axe X** — sélectionnez la colonne pour l'axe horizontal
4. **Colonne(s) de l'axe Y** — sélectionnez une ou plusieurs colonnes pour l'axe vertical
5. **Colonne de couleur** (optionnel) — colorez les points de données par une colonne catégorielle
6. **Colonne de l'axe Z** (optionnel) — pour les types de graphiques Bubble et Heatmap
7. **Titres** — définissez un titre de graphique personnalisé, un titre d'axe X et un titre d'axe Y

Les graphiques lisent les données actuellement filtrées/regroupées de la grille. **Chaque action de filtre, tri ou regroupement dans la grille met à jour tous les graphiques instantanément.**

---

## Étape 5 : Exporter

### Graphiques individuels
- Cliquez sur **Download Chart as HTML** sous chaque graphique pour l'enregistrer en tant que fichier HTML interactif autonome

### Tous les graphiques (ZIP)
- Clique sur **Download All Charts** en haut ou en bas de la section des graphiques
- Chaque graphique actif est exporté sous forme de fichier HTML autonome, regroupés dans un téléchargement ZIP
- Seuls les graphiques contenant des données sont inclus dans le ZIP

### Données de la grille
- Faites un clic droit dans la table AG Grid → **Export to CSV** ou **Export to Excel**
- Exporte exactement les données actuellement visibles dans la grille (respecte les filtres, regroupements, tris)

> **Astuce :** Les fichiers HTML exportés sont entièrement interactifs — vous pouvez zoomer, survoler pour les info-bulles et faire un panoramique — aucun logiciel nécessaire, juste un navigateur web.

---

## Conseils et dépannage

| Problème | Solution |
|---|---|
| Le téléchargement du fichier échoue | Vérifiez que le fichier fait moins de {{VALUE_MAX_FILE_SIZE_MB}} MB et qu'il est dans un format pris en charge |
| Le lien SharePoint ne fonctionne pas | Assurez-vous que le lien permet l'accès anonyme (aucune connexion requise). Les locataires d'entreprise peuvent bloquer cela. |
| Google Sheet ne se charge pas | Assurez-vous que le partage est défini sur "Toute personne disposant du lien peut afficher" |
| Airtable ne se connecte pas | Vérifiez que votre Personal Access Token dispose des scopes `data.records:read` et `schema.bases:read`, et que le Base ID commence par `app` |
| Erreurs d'analyse datetime | Vérifiez que le format sélectionné correspond à vos données. Essayez un format personnalisé si nécessaire |
| Les graphiques sont vides | Assurez-vous que les données sont chargées dans la grille et que les colonnes X/Y sont sélectionnées |
| La grille n'affiche aucune donnée après le filtre | Effacez ou ajustez vos filtres de colonne |

---

## Confidentialité des données

- Toutes les données téléchargées sont traitées **en mémoire uniquement** (jamais écrites sur disque ou dans une base de données)
- Les données sont stockées dans votre **session de navigateur** — fermer l'onglet efface tout
- Aucune donnée téléchargée n'est envoyée à des services externes
- Seuls les soumissions de commentaires volontaires et les analyses d'utilisation anonymes sont stockés
- Consultez [PRIVACY.md]({{URL_DOCUMENTATION_AYD_PRIVACY}}) pour tous les détails
