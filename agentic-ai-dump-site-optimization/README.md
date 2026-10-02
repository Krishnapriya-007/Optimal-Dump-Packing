# Agentic AI-Based Dump Site Optimization

> **Intelligent mining decision support for dump-site allocation and fleet routing.**
> Final Year Engineering Project · Department of Computer Science · 2026

[![Status](https://img.shields.io/badge/status-prototype-6D28D9)]()
[![Stack](https://img.shields.io/badge/stack-single--file%20HTML-3DB5F7)]()
[![Coverage](https://img.shields.io/badge/coverage-62%25%20→%2075%25-00D26A)]()
[![Hardware](https://img.shields.io/badge/new%20hardware-ZERO-00D26A)]()

## Open the Dashboard

[Open the live dashboard](https://krishnapriya-007.github.io/Optimal-Dump-Packing/) in any browser.

The [dashboard source](https://github.com/Krishnapriya-007/Optimal-Dump-Packing/tree/main/agentic-ai-dump-site-optimization/site) contains the browser UI. The accompanying Python pipeline and agents are in [`required_project_files`](../required_project_files).

A planning and monitoring workflow for mining trucks across irregular site polygons, including zone decomposition, route planning, fleet coordination, and operational analytics.

The site is a single self-contained HTML file. The trained Q-table, the training history,
the polygon math, the token broker, and the greedy circle-packer are all embedded inline as
JavaScript. The only network call is to `fonts.googleapis.com` for the typeface (with system
font fallbacks if that fails).

Older standalone builds are kept in the `older versions/` folder for reference. The live
site entry point is `site/index.html`.

## Documentation

- [CHANGELOG.md](docs/CHANGELOG.md) — summary of the repo reorganization and feature updates.
- [TESTING.md](docs/TESTING.md) — testing log with errors, fixes, and verification results.

## What's inside

| Page | What it shows |
|---|---|
| **Problem Statement** | KPIs · the 62 % baseline · three-layer architecture |
| **Zone Decomposition** | Animated sweep-line algorithm · O(n log n) |
| **Live RL Simulation** | Trained Q-agent placing dumps in real time |
| **ML Training Results** | Hand-drawn SVG charts of reward + coverage curves |
| **Before vs After** | Side-by-side rigid grid vs RL policy |
| **Token Protocol** | 4 live Coffman-1971 scenarios |
| **Custom Field** | Judge draws their own polygon · pipeline rebuilds live |
| **Architecture** | Pipeline SVG · in-browser modules · deployment notes |

## Architecture (3 layers)

1. **Zone Decomposition** — Sweep-line in O(n log n). Sliver-merge + MultiPolygon handling.
2. **Q-Learning Agent** — Tabular ε-greedy, 60 states × 3 actions, trained 1500 episodes.
3. **Token Broker** — FIFO + heartbeat watchdog + physical-clearance flag.
   Provably deadlock-free against all four Coffman-1971 conditions.

## Measured results

| Metric | Baseline | Planning policy | Theoretical ceiling |
|---|---|---|---|
| Coverage | 62.18 % | 74.84 % | 99.41 % |
| Dumps placed | 10 | 72 | 27 |
| Decision time | manual | < 1 ms / step | — |
| Deadlock-free | no | **yes** (Coffman proof + 4 live scenarios) | — |
| New hardware | — | **ZERO** | — |

## Local development

You don't actually need a web server — `site/index.html` opens directly in any browser.
But during development a local server helps with cache busting:

```bash
cd site/
python3 -m http.server 8000
# open http://localhost:8000/
```

## Backend source code

The Python workflow, agents, models, sample scenes, and validation documents are included in [`required_project_files`](../required_project_files).

## Citation

```bibtex
@misc{agenticmining2026,
  title  = {Agentic AI-Based Dump Site Optimization},
  author = {Department of Computer Science},
  year   = {2026},
  note   = {Final Year Engineering Project}
}
```

## License

Final Year Engineering Project · Department of Computer Science · 2026.
