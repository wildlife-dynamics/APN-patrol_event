# Patrol & Event Report

Per-outing patrol and event report for Argentina's national parks agency (Administración de Parques Nacionales — APN). It pulls patrol and event data from EarthRanger over a time range, filters it down to a single outing (identified by an "Outing ID" that matches the `numero_patrulla` field recorded on each event), and produces both a dashboard summary and a downloadable Word (.docx) report for that outing.

## Dashboard widgets

| Widget | Description |
|--------|-------------|
| Nro. de Patrullajes realizadas | Count of distinct patrols in the outing |
| Nro. de Kilómetros recorridos | Total distance travelled across all patrol tracks in the outing, in km |
| Resumen de Patrullas | Per-patrol table: Patrol ID, transport type, start/end time, total distance (km), total duration (hr) |
| Mapa de Patrulla y Eventos | Map of patrol tracks and events for the outing, plus any configured spatial-feature layers (e.g. park boundaries), colored by the selected groupby attribute for each |

This workflow has no groupers — the dashboard shows a single view scoped to the selected outing and time range.

## Word report

Beyond the dashboard, this workflow generates a `.docx` report (via `generate_patrol_report`) combining the patrol map (as a static PNG), trajectory statistics, event details, event notes, and event attachments, using a Jinja/docxtpl template supplied via the "Template Path" parameter (`get_template_path`). The template path is a local file path (or `file://` URL) resolved on the machine running the workflow — it is not stored in this repository.

## Scoping to an outing

The "Outing ID" parameter (`outing_id`) is a free-text value matched against the `numero_patrulla` field in each event's details. Only events (and, after exploding patrol segments, only patrols) belonging to that outing ID are kept — everything downstream (map, stats, report) is scoped to that one outing.

## Requirements

[pixi](https://pixi.sh) is required for environment and dependency management. You will also need an EarthRanger connection configured for the `apn` data source.
