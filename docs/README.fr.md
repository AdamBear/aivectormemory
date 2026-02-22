🌐 [简体中文](../README.md) | [繁體中文](README.zh-TW.md) | [English](README.en.md) | [Español](README.es.md) | [Deutsch](README.de.md) | Français | [日本語](README.ja.md)

<p align="center">
  <h1 align="center">🧠 AIVectorMemory</h1>
  <p align="center">
    <strong>Donnez une mémoire à votre assistant IA — Serveur MCP de mémoire persistante inter-sessions</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/v/aivectormemory?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/pyversions/aivectormemory" alt="Python"></a>
    <a href="https://github.com/Edlineas/aivectormemory/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
    <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple" alt="MCP"></a>
  </p>
</p>

---

> **Problème** : Les assistants IA « oublient » tout à chaque nouvelle session — répétant les mêmes erreurs, oubliant les conventions du projet, perdant la progression du développement. Pire encore, pour compenser cette amnésie, vous devez injecter un contexte massif dans chaque conversation, gaspillant des tokens.
>
> **AIVectorMemory** : Fournit un stockage de mémoire vectorielle local pour l'IA via le protocole MCP, lui permettant de se souvenir de tout — connaissances du projet, erreurs rencontrées, décisions de développement, progression du travail — persistant entre les sessions. La récupération sémantique à la demande élimine l'injection massive, réduisant considérablement la consommation de tokens.

## ✨ Fonctionnalités Principales

| Fonctionnalité | Description |
|----------------|-------------|
| 🔍 **Recherche Sémantique** | Basée sur la similarité vectorielle — chercher « timeout base de données » trouve « erreur pool de connexions MySQL » |
| 🏠 **Entièrement Local** | Inférence locale ONNX Runtime, pas de clé API nécessaire, les données ne quittent jamais votre machine |
| 🔄 **Déduplication Intelligente** | Similarité cosinus > 0.95 met à jour automatiquement, pas de stockage en double |
| 📊 **Tableau de Bord Web** | Interface de gestion intégrée avec visualisation 3D du réseau vectoriel |
| 🔌 **Tous les IDEs** | OpenCode / Claude Code / Cursor / Kiro / Windsurf / VSCode / Trae et plus |
| 📁 **Isolation par Projet** | Une seule BD partagée entre projets, isolée automatiquement par project_dir |
| 🏷️ **Système d'Étiquettes** | Catégorisation des mémoires, recherche, renommage et fusion d'étiquettes |
| 💰 **Économie de Tokens** | Récupération sémantique à la demande remplace l'injection massive de contexte, réduisant 50%+ de tokens redondants |
| 📋 **Suivi des Problèmes** | Traqueur d'issues léger, l'IA enregistre et archive automatiquement |
| 🔐 **Authentification Web** | Le tableau de bord supporte l'authentification par Token contre les accès non autorisés |
| ⚡ **Cache Embedding** | Pas de calcul vectoriel redondant pour un contenu identique, écritures plus rapides |
| 📤 **Export/Import** | Export et import des données mémoire en JSON, supporte la migration et la sauvegarde |
| 🎯 **Retour d'action** | Notifications Toast, guides d'état vide, expérience d'interaction complète |
| ➕ **Ajouter des projets** | Ajouter des projets directement depuis le tableau de bord avec navigateur de répertoires |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                   AI IDE                         │
│  OpenCode / Claude Code / Cursor / Kiro / ...   │
└──────────────────────┬──────────────────────────┘
                       │ MCP Protocol (stdio)
┌──────────────────────▼──────────────────────────┐
│              AIVectorMemory Server               │
│                                                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ remember │ │  recall   │ │   auto_save      │ │
│  │ forget   │ │  digest   │ │   status/track   │ │
│  └────┬─────┘ └────┬─────┘ └───────┬──────────┘ │
│       │            │               │             │
│  ┌────▼────────────▼───────────────▼──────────┐  │
│  │         Embedding Engine (ONNX)            │  │
│  │      intfloat/multilingual-e5-small        │  │
│  └────────────────────┬───────────────────────┘  │
│                       │                          │
│  ┌────────────────────▼───────────────────────┐  │
│  │     SQLite + sqlite-vec (Index Vectoriel)  │  │
│  │     ~/.aivectormemory/memory.db            │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 🚀 Démarrage Rapide

### Option 1 : Installation pip

```bash
pip install aivectormemory
pip install --upgrade aivectormemory  # Mettre à jour vers la dernière version
cd /path/to/your/project
run install          # Sélection interactive de l'IDE, configuration en un clic
```

### Option 2 : uvx (sans installation)

```bash
cd /path/to/your/project
uvx aivectormemory install
```

### Option 3 : Configuration manuelle

```json
{
  "mcpServers": {
    "aivectormemory": {
      "command": "run",
      "args": ["--project-dir", "/path/to/your/project"]
    }
  }
}
```

<details>
<summary>📍 Emplacements des fichiers de configuration par IDE</summary>

| IDE | Chemin de configuration |
|-----|------------------------|
| Kiro | `.kiro/settings/mcp.json` |
| Cursor | `.cursor/mcp.json` |
| Claude Code | `.mcp.json` |
| Windsurf | `.windsurf/mcp.json` |
| VSCode | `.vscode/mcp.json` |
| Trae | `.trae/mcp.json` |
| OpenCode | `opencode.json` |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` |

</details>

## 🛠️ 7 Outils MCP

### `remember` — Stocker une mémoire

```
content (string, requis)   Contenu au format Markdown
tags    (string[], requis)  Étiquettes, ex. ["erreur", "python"]
scope   (string)            "project" (par défaut) / "user" (inter-projets)
```

Similarité > 0.95 met à jour automatiquement la mémoire existante, sans doublons.

### `recall` — Recherche sémantique

```
query   (string)     Mots-clés de recherche sémantique
tags    (string[])   Filtre exact par étiquettes
scope   (string)     "project" / "user" / "all"
top_k   (integer)    Nombre de résultats, par défaut 5
```

Correspondance par similarité vectorielle — trouve des mémoires liées même avec des mots différents.

### `forget` — Supprimer des mémoires

```
memory_id  (string)     ID unique
memory_ids (string[])   IDs en lot
```

### `status` — État de session

```
state (object, optionnel)   Omettre pour lire, passer pour mettre à jour
  is_blocked, block_reason, current_task,
  next_step, progress[], recent_changes[], pending[]
```

Maintient la progression du travail entre les sessions, restaure automatiquement le contexte.

### `track` — Suivi des problèmes

```
action   (string)   "create" / "update" / "archive" / "list"
title    (string)   Titre du problème
issue_id (integer)  ID du problème
status   (string)   "pending" / "in_progress" / "completed"
content  (string)   Contenu d'investigation
```

### `digest` — Résumé des mémoires

```
scope          (string)    Portée
since_sessions (integer)   N dernières sessions
tags           (string[])  Filtre par étiquettes
```

### `auto_save` — Sauvegarde automatique

```
decisions[]      Décisions clés
modifications[]  Résumés des modifications de fichiers
pitfalls[]       Registres d'erreurs rencontrées
todos[]          Éléments en attente
```

Catégorise, étiquette et déduplique automatiquement à la fin de chaque conversation.

## 📊 Tableau de Bord Web

```bash
run web --port 9080
run web --port 9080 --quiet          # Supprimer les logs de requêtes
run web --port 9080 --quiet --daemon  # Exécuter en arrière-plan (macOS/Linux)
```

Visitez `http://localhost:9080` dans votre navigateur.

- Basculement entre projets, parcourir/rechercher/modifier/supprimer/exporter/importer les mémoires
- Recherche sémantique (correspondance par similarité vectorielle)
- Suppression des données de projet en un clic
- État de session, suivi des problèmes
- Gestion des étiquettes (renommer, fusionner, suppression par lots)
- Protection par authentification Token
- Visualisation 3D du réseau vectoriel de mémoires
- 🌐 Support multilingue (简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語)

<p align="center">
  <img src="dashboard-projects.png" alt="Sélection de Projet" width="100%">
  <br>
  <em>Sélection de Projet</em>
</p>

<p align="center">
  <img src="dashboard-overview.png" alt="Aperçu & Visualisation du Réseau Vectoriel" width="100%">
  <br>
  <em>Aperçu & Visualisation du Réseau Vectoriel</em>
</p>

## ⚡ Combinaison avec les Règles Steering

AIVectorMemory est la couche de stockage. Utilisez les règles Steering pour indiquer à l'IA **quand et comment** appeler ces outils.

L'exécution de `run install` génère automatiquement les règles Steering et la configuration des Hooks — aucune configuration manuelle nécessaire.

| IDE | Emplacement Steering | Hooks |
|-----|---------------------|-------|
| Kiro | `.kiro/steering/aivectormemory.md` | `.kiro/hooks/*.hook` |
| Cursor | `.cursor/rules/aivectormemory.md` | `.cursor/hooks.json` |
| Claude Code | `CLAUDE.md` (ajouté) | `.claude/settings.json` |
| Windsurf | `.windsurf/rules/aivectormemory.md` | `.windsurf/hooks.json` |
| VSCode | `.github/copilot-instructions.md` (ajouté) | — |
| Trae | `.trae/rules/aivectormemory.md` | — |
| OpenCode | `AGENTS.md` (ajouté) | `.opencode/plugins/*.js` |

<details>
<summary>📋 Exemple de Règles Steering (généré automatiquement)</summary>

```markdown
# AIVectorMemory - Mémoire Persistante Inter-Sessions

## Vérification au Démarrage

Au début de chaque nouvelle session, exécuter dans l'ordre :

1. Appeler `status` (sans paramètres) pour lire l'état de la session, vérifier `is_blocked` et `block_reason`
2. Appeler `recall` (tags: ["connaissance-projet"], scope: "project") pour charger les connaissances du projet
3. Appeler `recall` (tags: ["preference"], scope: "user") pour charger les préférences utilisateur

## Quand Appeler

- Nouvelle session : appeler `status` pour lire l'état de travail précédent
- Erreur trouvée : appeler `remember` pour enregistrer, ajouter le tag "erreur"
- Besoin d'expérience historique : appeler `recall` pour recherche sémantique
- Bug ou tâche trouvé : appeler `track` (action: create)
- Changement de progression : appeler `status` (passer le paramètre state) pour mettre à jour
- Avant la fin de la conversation : appeler `auto_save` pour sauvegarder cette session

## Gestion de l'État de Session

Champs status : is_blocked, block_reason, current_task, next_step,
progress[], recent_changes[], pending[]

⚠️ **Protection de blocage** : Lors de la proposition d'un plan en attente de confirmation ou de la finalisation d'un correctif en attente de vérification, appelez toujours `status` pour définir `is_blocked: true` simultanément. Cela empêche une nouvelle session de supposer à tort « confirmé » et d'exécuter de manière autonome après le transfert de contexte.

## Suivi des Problèmes

1. `track create` → Enregistrer le problème
2. `track update` → Mettre à jour le contenu d'investigation
3. `track archive` → Archiver les problèmes résolus
```

</details>

<details>
<summary>🔗 Exemple de Configuration Hooks (Kiro uniquement, généré automatiquement)</summary>

Sauvegarde automatique en fin de session supprimée. Vérification du workflow de développement (`.kiro/hooks/dev-workflow-check.kiro.hook`) :

```json
{
  "enabled": true,
  "name": "Vérification du Workflow de Développement",
  "version": "1",
  "when": { "type": "promptSubmit" },
  "then": {
    "type": "askAgent",
    "prompt": "Principes : vérifier avant d'agir, pas de tests à l'aveugle, ne marquer comme terminé qu'après réussite des tests"
  }
}
```

</details>

## 🇨🇳 Utilisateurs en Chine

Le modèle d'Embedding (~200Mo) est téléchargé automatiquement au premier lancement. Si c'est lent :

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

Ou ajouter env dans la configuration MCP :

```json
{
  "env": { "HF_ENDPOINT": "https://hf-mirror.com" }
}
```

## 📦 Stack Technique

| Composant | Technologie |
|-----------|-----------|
| Runtime | Python >= 3.10 |
| BD Vectorielle | SQLite + sqlite-vec |
| Embedding | ONNX Runtime + intfloat/multilingual-e5-small |
| Tokenizer | HuggingFace Tokenizers |
| Protocole | Model Context Protocol (MCP) |
| Web | HTTPServer natif + Vanilla JS |

## 📋 Journal des Modifications

### v0.2.4

- 🔇 Prompt du hook Stop changé en instruction directe, éliminant les réponses dupliquées de Claude Code
- 🛡️ Règles Steering auto_save avec protection court-circuit, ignore les autres règles en fin de session
- 🐛 Correction d'idempotence de `_copy_check_track_script` (retourner l'état de changement pour éviter les faux "synchronisé")
- 🐛 Correction d'incompatibilité `row.get()` dans issue_repo delete avec `sqlite3.Row` (utiliser `row.keys()`)
- 🐛 Correction du défilement de la page de sélection de projets du tableau de bord Web (impossible de défiler avec beaucoup de projets)
- 🐛 Correction de pollution CSS du tableau de bord Web (strReplace remplacement global a corrompu 6 sélecteurs de style)
- 🔄 Tous les dialogues confirm() du tableau de bord Web remplacés par modal showConfirm personnalisé (supprimer mémoire/issue/tag/projet)
- 🔄 Opérations de suppression du tableau de bord Web avec gestion des réponses d'erreur API (toast au lieu d'alert)
- 🧹 `.gitignore` ajoute la règle d'ignorance du répertoire legacy `.devmemory/`
- 🧪 Nettoyage automatique des résidus de projets temporaires pytest en DB (conftest.py session fixture)

### v0.2.3

- 🛡️ Hook PreToolUse : vérification obligatoire du track issue avant Edit/Write, rejet si aucun issue actif (Claude Code / Kiro / OpenCode)
- 🔌 Plugin OpenCode mis à niveau au format SDK `@opencode-ai/plugin` (hook tool.execute.before)
- 🔧 `run install` déploie automatiquement check_track.sh avec injection dynamique du chemin
- 🐛 Correction de l'incompatibilité `row.get()` avec `sqlite3.Row` dans issue_repo archive/delete
- 🐛 Correction de la condition de concurrence session_id : lecture de la dernière valeur depuis la DB avant incrémentation
- 🐛 Validation du format date de track (YYYY-MM-DD) + validation du type issue_id
- 🐛 Renforcement de l'analyse des requêtes Web API (validation Content-Length + limite 10MB + gestion des erreurs JSON)
- 🐛 Correction de la logique scope du filtre de tags (`filter_dir is not None` au lieu de vérification falsy)
- 🐛 Validation de la longueur des octets struct.unpack pour l'export des données vectorielles
- 🐛 Migration versionnée du schéma (table schema_version + migration incrémentielle v1/v2/v3)
- 🐛 Correction de la synchronisation du numéro de version `__init__.py`

### v0.2.2

- 🔇 Tableau de bord Web : paramètre `--quiet` pour supprimer les logs de requêtes
- 🔄 Tableau de bord Web : paramètre `--daemon` pour exécution en arrière-plan (macOS/Linux)
- 🔧 Correction de la génération de configuration MCP dans `run install` (sys.executable + champs complets)
- 📋 Suivi des problèmes CRUD et archivage (Tableau de bord Web ajout/édition/archivage/suppression + association mémoires)
- 👆 Clic n'importe où sur la ligne pour ouvrir le modal d'édition (mémoires/problèmes/tags)
- 🔒 Règles de blocage appliquées lors des continuations de session/transferts de contexte (reconfirmation requise)

### v0.2.1

- ➕ Ajouter des projets depuis le tableau de bord Web (navigateur de répertoires + saisie manuelle)
- 🏷️ Correction de la contamination des tags entre projets (opérations limitées au projet actuel + mémoires globales)
- 📐 Troncature par points de suspension dans la pagination des modales + largeur 80%
- 🔌 OpenCode install génère automatiquement le plugin auto_save (événement session.idle)
- 🔗 Claude Code / Cursor / Windsurf install génère automatiquement la configuration Hooks (sauvegarde automatique en fin de session)
- 🎯 Améliorations UX du tableau de bord Web (retour Toast, guides d'état vide, barre d'export/import)
- 🔧 Clic sur les cartes de statistiques (clic sur les compteurs mémoire/problèmes pour voir les détails)
- 🏷️ Page de gestion des tags distingue les sources projet/global (marqueurs 📁/🌐)
- 🏷️ Le nombre de tags des cartes projet inclut désormais les tags des mémoires globales

### v0.2.0

- 🔐 Authentification par Token du tableau de bord Web
- ⚡ Cache de vecteurs Embedding, pas de calcul redondant pour un contenu identique
- 🔍 recall supporte la recherche combinée query + tags
- 🗑️ forget supporte la suppression par lots (paramètre memory_ids)
- 📤 Export/import de mémoires (format JSON)
- 🔎 Recherche sémantique dans le tableau de bord Web
- 🗂️ Bouton de suppression de projet dans le tableau de bord Web
- 📊 Optimisation des performances du tableau de bord Web (élimination des analyses complètes de table)
- 🧠 Compression intelligente de digest
- 💾 Persistance de session_id
- 📏 Protection de limite de longueur de content
- 🏷️ Référence dynamique de version (plus codée en dur)

### v0.1.x

- Version initiale : 7 outils MCP, tableau de bord Web, visualisation 3D vectorielle, support multilingue

## License

MIT
