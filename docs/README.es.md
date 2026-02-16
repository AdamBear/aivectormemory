🌐 [简体中文](../README.md) | [繁體中文](README.zh-TW.md) | [English](README.en.md) | Español | [Deutsch](README.de.md) | [Français](README.fr.md) | [日本語](README.ja.md)

<p align="center">
  <h1 align="center">🧠 AIVectorMemory</h1>
  <p align="center">
    <strong>Dale memoria a tu asistente de IA — Servidor MCP de memoria persistente entre sesiones</strong>
  </p>
  <p align="center">
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/v/aivectormemory?color=blue&label=PyPI" alt="PyPI"></a>
    <a href="https://pypi.org/project/aivectormemory/"><img src="https://img.shields.io/pypi/pyversions/aivectormemory" alt="Python"></a>
    <a href="https://github.com/Edlineas/aivectormemory/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
    <a href="https://modelcontextprotocol.io"><img src="https://img.shields.io/badge/MCP-compatible-purple" alt="MCP"></a>
  </p>
</p>

---

> **Problema**: Los asistentes de IA "olvidan" todo con cada nueva sesión — repitiendo los mismos errores, olvidando convenciones del proyecto, perdiendo el progreso de desarrollo. Peor aún, para compensar esta amnesia, tienes que inyectar contexto masivo en cada conversación, desperdiciando tokens.
>
> **AIVectorMemory**: Proporciona un almacén de memoria vectorial local para IA a través del protocolo MCP, permitiéndole recordar todo — conocimiento del proyecto, errores encontrados, decisiones de desarrollo, progreso de trabajo — persistente entre sesiones. La recuperación semántica bajo demanda elimina la inyección masiva, reduciendo drásticamente el consumo de tokens.

## ✨ Características Principales

| Característica | Descripción |
|----------------|-------------|
| 🔍 **Búsqueda Semántica** | Basada en similitud vectorial — buscar "timeout de base de datos" encuentra "error en pool de conexiones MySQL" |
| 🏠 **Completamente Local** | Inferencia local con ONNX Runtime, sin API Key, los datos nunca salen de tu máquina |
| 🔄 **Deduplicación Inteligente** | Similitud coseno > 0.95 actualiza automáticamente, sin almacenamiento duplicado |
| 📊 **Panel Web** | Interfaz de gestión integrada con visualización 3D de red vectorial |
| 🔌 **Todos los IDEs** | OpenCode / Claude Code / Cursor / Kiro / Windsurf / VSCode / Trae y más |
| 📁 **Aislamiento por Proyecto** | Una sola BD compartida entre proyectos, aislada automáticamente por project_dir |
| 🏷️ **Sistema de Etiquetas** | Categorización de memorias, búsqueda, renombrado y fusión de etiquetas |
| 💰 **Ahorro de Tokens** | Recuperación semántica bajo demanda reemplaza la inyección masiva de contexto, reduciendo 50%+ de tokens redundantes |
| 📋 **Seguimiento de Problemas** | Rastreador de issues ligero, IA registra y archiva automáticamente |
| 🔐 **Autenticación Web** | El panel soporta autenticación por Token para prevenir acceso no autorizado |
| ⚡ **Caché de Embedding** | Sin cálculo vectorial redundante para contenido idéntico, escrituras más rápidas |
| 📤 **Exportar/Importar** | Exportación e importación de datos de memoria en JSON, soporta migración y respaldo |
| 🎯 **Retroalimentación** | Notificaciones Toast, guías de estado vacío, experiencia de interacción completa |
| ➕ **Agregar Proyectos** | Agregar proyectos directamente desde el panel con explorador de directorios |

## 🏗️ Arquitectura

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
│  │     SQLite + sqlite-vec (Índice Vectorial) │  │
│  │     ~/.aivectormemory/memory.db            │  │
│  └────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

## 🚀 Inicio Rápido

### Opción 1: Instalación con pip

```bash
pip install aivectormemory
cd /path/to/your/project
run install          # Selección interactiva de IDE, configuración con un clic
```

### Opción 2: uvx (sin instalación)

```bash
cd /path/to/your/project
uvx aivectormemory install
```

### Opción 3: Configuración manual

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
<summary>📍 Ubicación de archivos de configuración por IDE</summary>

| IDE | Ruta de configuración |
|-----|----------------------|
| Kiro | `.kiro/settings/mcp.json` |
| Cursor | `.cursor/mcp.json` |
| Claude Code | `.mcp.json` |
| Windsurf | `.windsurf/mcp.json` |
| VSCode | `.vscode/mcp.json` |
| Trae | `.trae/mcp.json` |
| OpenCode | `opencode.json` |
| Claude Desktop | `~/Library/Application Support/Claude/claude_desktop_config.json` |

</details>

## 🛠️ 7 Herramientas MCP

### `remember` — Almacenar memoria

```
content (string, requerido)   Contenido en formato Markdown
tags    (string[], requerido)  Etiquetas, ej. ["error", "python"]
scope   (string)               "project" (por defecto) / "user" (entre proyectos)
```

Similitud > 0.95 actualiza automáticamente la memoria existente, sin duplicados.

### `recall` — Búsqueda semántica

```
query   (string)     Palabras clave de búsqueda semántica
tags    (string[])   Filtro exacto por etiquetas
scope   (string)     "project" / "user" / "all"
top_k   (integer)    Número de resultados, por defecto 5
```

Coincidencia por similitud vectorial — encuentra memorias relacionadas incluso con palabras diferentes.

### `forget` — Eliminar memorias

```
memory_id  (string)     ID individual
memory_ids (string[])   IDs en lote
```

### `status` — Estado de sesión

```
state (object, opcional)   Omitir para leer, pasar para actualizar
  is_blocked, block_reason, current_task,
  next_step, progress[], recent_changes[], pending[]
```

Mantiene el progreso de trabajo entre sesiones, restaura contexto automáticamente.

### `track` — Seguimiento de problemas

```
action   (string)   "create" / "update" / "archive" / "list"
title    (string)   Título del problema
issue_id (integer)  ID del problema
status   (string)   "pending" / "in_progress" / "completed"
content  (string)   Contenido de investigación
```

### `digest` — Resumen de memorias

```
scope          (string)    Alcance
since_sessions (integer)   Últimas N sesiones
tags           (string[])  Filtro por etiquetas
```

### `auto_save` — Guardado automático

```
decisions[]      Decisiones clave
modifications[]  Resúmenes de modificaciones de archivos
pitfalls[]       Registros de errores encontrados
todos[]          Elementos pendientes
```

Categoriza, etiqueta y deduplica automáticamente al final de cada conversación.

## 📊 Panel Web

```bash
run web --port 9080
```

Visita `http://localhost:9080` en tu navegador.

- Cambio entre múltiples proyectos, explorar/buscar/editar/eliminar/exportar/importar memorias
- Búsqueda semántica (coincidencia por similitud vectorial)
- Eliminación de datos de proyecto con un clic
- Estado de sesión, seguimiento de problemas
- Gestión de etiquetas (renombrar, fusionar, eliminación por lotes)
- Protección por autenticación Token
- Visualización 3D de red vectorial de memorias
- 🌐 Soporte multilingüe (简体中文 / 繁體中文 / English / Español / Deutsch / Français / 日本語)

<p align="center">
  <img src="dashboard-projects.png" alt="Selección de Proyecto" width="100%">
  <br>
  <em>Selección de Proyecto</em>
</p>

<p align="center">
  <img src="dashboard-overview.png" alt="Resumen y Visualización de Red Vectorial" width="100%">
  <br>
  <em>Resumen y Visualización de Red Vectorial</em>
</p>

## ⚡ Combinación con Reglas Steering

AIVectorMemory es la capa de almacenamiento. Usa reglas Steering para indicar a la IA **cuándo y cómo** llamar estas herramientas.

Ejecutar `run install` genera automáticamente las reglas Steering y la configuración de Hooks, sin necesidad de escribirlas manualmente.

| IDE | Ubicación de Steering | Hooks |
|-----|----------------------|-------|
| Kiro | `.kiro/steering/aivectormemory.md` | `.kiro/hooks/*.hook` |
| Cursor | `.cursor/rules/aivectormemory.md` | `.cursor/hooks.json` |
| Claude Code | `CLAUDE.md` (añadido) | `.claude/settings.json` |
| Windsurf | `.windsurf/rules/aivectormemory.md` | `.windsurf/hooks.json` |
| VSCode | `.github/copilot-instructions.md` (añadido) | — |
| Trae | `.trae/rules/aivectormemory.md` | — |
| OpenCode | `AGENTS.md` (añadido) | `.opencode/plugins/*.js` |

<details>
<summary>📋 Ejemplo de Reglas Steering (generado automáticamente)</summary>

```markdown
# AIVectorMemory - Memoria Persistente entre Sesiones

## Verificación de Inicio

Al inicio de cada nueva sesión, ejecutar en orden:

1. Llamar `status` (sin parámetros) para leer el estado de la sesión, verificar `is_blocked` y `block_reason`
2. Llamar `recall` (tags: ["conocimiento-proyecto"], scope: "project") para cargar conocimiento del proyecto
3. Llamar `recall` (tags: ["preference"], scope: "user") para cargar preferencias del usuario

## Cuándo Llamar

- Nueva sesión: llamar `status` para leer el estado de trabajo anterior
- Encontrar un error: llamar `remember` para registrar, añadir etiqueta "error"
- Buscar experiencia histórica: llamar `recall` para búsqueda semántica
- Encontrar un bug o tarea pendiente: llamar `track` (action: create)
- Cambio en el progreso: llamar `status` (pasar parámetro state) para actualizar
- Antes de terminar la conversación: llamar `auto_save` para guardar esta sesión

## Gestión del Estado de Sesión

Campos de status: is_blocked, block_reason, current_task, next_step,
progress[], recent_changes[], pending[]

## Seguimiento de Problemas

1. `track create` → Registrar problema
2. `track update` → Actualizar contenido de investigación
3. `track archive` → Archivar problemas resueltos
```

</details>

<details>
<summary>🔗 Ejemplo de Configuración de Hooks (solo Kiro, generado automáticamente)</summary>

Guardado automático al finalizar sesión (`.kiro/hooks/auto-save-session.kiro.hook`):

```json
{
  "enabled": true,
  "name": "Guardado Automático de Sesión",
  "version": "1",
  "when": { "type": "agentStop" },
  "then": {
    "type": "askAgent",
    "prompt": "Llamar auto_save para categorizar y guardar decisiones, modificaciones, errores y tareas pendientes"
  }
}
```

Verificación del flujo de desarrollo (`.kiro/hooks/dev-workflow-check.kiro.hook`):

```json
{
  "enabled": true,
  "name": "Verificación del Flujo de Desarrollo",
  "version": "1",
  "when": { "type": "promptSubmit" },
  "then": {
    "type": "askAgent",
    "prompt": "Principios: verificar antes de actuar, no probar a ciegas, solo marcar como completado después de pasar las pruebas"
  }
}
```

</details>

## 🇨🇳 Usuarios en China

El modelo de Embedding (~200MB) se descarga automáticamente en la primera ejecución. Si es lento:

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

O agregar env en la configuración MCP:

```json
{
  "env": { "HF_ENDPOINT": "https://hf-mirror.com" }
}
```

## 📦 Stack Tecnológico

| Componente | Tecnología |
|------------|-----------|
| Runtime | Python >= 3.10 |
| BD Vectorial | SQLite + sqlite-vec |
| Embedding | ONNX Runtime + intfloat/multilingual-e5-small |
| Tokenizador | HuggingFace Tokenizers |
| Protocolo | Model Context Protocol (MCP) |
| Web | HTTPServer nativo + Vanilla JS |

## 📋 Registro de Cambios

### v0.2.1

- ➕ Agregar proyectos desde el panel Web (explorador de directorios + entrada manual)
- 🏷️ Corrección de contaminación de etiquetas entre proyectos (operaciones limitadas al proyecto actual + memorias globales)
- 📐 Truncamiento con puntos suspensivos en paginación de modales + ancho 80%
- 🔌 OpenCode install genera automáticamente plugin auto_save (evento session.idle)
- 🔗 Claude Code / Cursor / Windsurf install genera automáticamente configuración de Hooks (guardado automático al finalizar sesión)
- 🎯 Mejoras de UX del panel Web (retroalimentación Toast, guías de estado vacío, barra de exportar/importar)
- 🔧 Clic en tarjetas de estadísticas (clic en conteos de memoria/problemas para ver detalles)
- 🏷️ Página de gestión de etiquetas distingue origen proyecto/global (marcadores 📁/🌐)
- 🏷️ Conteo de etiquetas en tarjetas de proyecto incluye etiquetas de memorias globales

### v0.2.0

- 🔐 Autenticación por Token en el panel Web
- ⚡ Caché de vectores Embedding, sin cálculo redundante para contenido idéntico
- 🔍 recall soporta búsqueda combinada query + tags
- 🗑️ forget soporta eliminación por lotes (parámetro memory_ids)
- 📤 Exportación/importación de memorias (formato JSON)
- 🔎 Búsqueda semántica en el panel Web
- 🗂️ Botón de eliminación de proyecto en el panel Web
- 📊 Optimización de rendimiento del panel Web (eliminación de escaneos completos de tabla)
- 🧠 Compresión inteligente de digest
- 💾 Persistencia de session_id
- 📏 Protección de límite de longitud de content
- 🏷️ Referencia dinámica de version (ya no codificada)

### v0.1.x

- Versión inicial: 7 herramientas MCP, panel Web, visualización 3D vectorial, soporte multilingüe

## License

MIT
