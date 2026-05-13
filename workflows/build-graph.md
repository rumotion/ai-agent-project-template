# Build Graph Workflow

Use this workflow to build a queryable structural knowledge graph of the codebase using [Graphify](https://github.com/safishamsi/graphify). This gives agents a structural map instead of relying entirely on text grepping.

## Prerequisites

- Python 3.10+
- `uv` or `pipx` installed

## Steps

1. Install Graphify:
   ```bash
   uv tool install graphifyy
   ```
2. Run Graphify in the root directory:
   ```bash
   graphify .
   ```
3. Install the hook for your preferred agent (e.g., `graphify claude install`, `graphify codex install`, `graphify cursor install`, `graphify antigravity install`).

## Output

This will generate a `graphify-out/` folder containing:
- `graph.json` - queryable graph database
- `GRAPH_REPORT.md` - summary of key concepts and god-nodes
- `graph.html` - interactive web visualizer

## Cleanup

To remove from the project and uninstall the agent hook:
```bash
graphify uninstall --purge
```
