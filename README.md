# Patrol & Event Report

Per-patrol report for Argentina's national parks agency (Administración de Parques Nacionales — APN). It pulls patrol and event data from EarthRanger over a time range, scopes it to one EarthRanger patrol (by its serial number), and produces both a dashboard summary and a downloadable Word (.docx) report for that patrol.

## Dashboard widgets

| Widget | Description |
|--------|-------------|
| Nro. de Patrullajes realizadas | Count of distinct patrols in scope (1 when a patrol is selected) |
| Nro. de Kilómetros recorridos | Total distance travelled along the patrol track, in km |
| Resumen de Patrullas | Per-patrol table: Patrol ID, transport type, start/end time, total distance (km), total duration (hr) |
| Mapa de Patrulla y Eventos | Map of the patrol track and its linked events, plus any configured spatial-feature layers (e.g. park boundaries), colored by the selected groupby attribute for each |

This workflow has no groupers — the dashboard shows a single view scoped to the selected patrol and time range.

## Word report

Beyond the dashboard, this workflow generates a `.docx` report (via `generate_patrol_report`) combining the patrol map (as a static PNG), trajectory statistics, event details, event notes, and event attachments, using a Jinja/docxtpl template supplied via the "Template Path" parameter (`get_template_path`). The template path is a local file path (or `file://` URL) resolved on the machine running the workflow — it is not stored in this repository.

## Scoping to a patrol

The "ID de Patrulla" parameter (`patrol_id`) is the EarthRanger patrol serial number. The patrols fetched for the time range are filtered to that one patrol; its track, its linked events (through the patrol's legs) and everything downstream (map, stats, report) are scoped to it.

## Patrol header (legs)

APN records patrol information on the patrol itself, using EarthRanger's patrol segments configuration, instead of on an "Información inicial de patrulla" event. `get_patrol_segments_info` (ext-apn) builds the report header from the patrol: one entry per leg with transport type, start/end time (in the workflow timezone), leader, member names, and the leg's form fields — `segment_details` (mandate, project, protection activity, armed) and `type_details` (per patrol type: vehicle plate and starting km, boat and engine hours, horse) — with choice codes resolved to labels. If the patrol has a linked `cierre_de_patrulla` event, its end-of-patrol fields are added too. A patrol with no linked events still produces the map, stats and report.

## Requirements

[pixi](https://pixi.sh) is required for environment and dependency management. You will also need an EarthRanger connection configured for the `apn` data source.
