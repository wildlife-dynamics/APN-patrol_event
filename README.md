# APN Patrol & Event Report

An Ecoscope workflow for Argentina's national parks agency (Administración de Parques Nacionales, **APN**). Pick one EarthRanger patrol, and the workflow builds:

- a **dashboard** with the patrol's headline numbers, its legs and a map, and
- a **Word report** (`.docx`) in APN's format, ready to print or share.

APN records patrol information on the patrol itself (EarthRanger patrol **legs**, also called segments), so the report reads the leaders, members, mandates and per-leg details from the patrol, and the events linked to it.

---

## Running it

The config page asks for, in order:

| Section | What to set |
|---|---|
| Workflow Details | Name and description shown on the dashboard |
| Data Source | The EarthRanger connection (e.g. `apncentral`) |
| Time Range | A range that covers the patrol, and the timezone (Buenos Aires) |
| **ID de Patrulla** | The patrol's serial number in EarthRanger, e.g. `74`. Required. |
| Spatial Features / Local Spatial Features | Optional map layers such as park boundaries |
| Patrol Style / Patrol Markers / Event Style | Map colors, legends and markers |
| Download Attachments | Include event photos in the report, or skip them |
| Base Maps *(advanced)* | Map background tiles |
| Report Template *(advanced)* | Path or URL of the `.docx` template. Defaults to the template in this repo, so leave it as is unless you are testing a new one. |

If no patrol with that ID falls inside the time range, the run stops with *"No patrol matches the 'ID de Patrulla' in the selected time range"*. Widen the time range or check the ID.

---

## Dashboard

| Widget | Shows |
|---|---|
| **Distancia total** | Kilometres of GPS track, e.g. `4.05 km` |
| **Tiempo total** | Hours on patrol, summed over the legs, e.g. `0.44 h` |
| **Tramos** | Number of legs |
| **Eventos** | Number of events linked to the patrol |
| **Tramos de Patrulla** | One row per leg: #, type, start, end, leader, distance (km), time (h) |
| **Mapa de Patrulla y Eventos** | The track colored by leg type, the events, and any spatial features |

The tiles use the same numbers as the report's stats row.

## Word report

| Page | Section |
|---|---|
| 1 | Header (patrol ID, mandates, start and end), stats row, **Personal Participante**: one row per leader, with members and unlisted staff |
| 2 | **Tramos de Patrulla**: one row per leg with date and schedule, leader, distance, time and the leg's form details. **Cierre de Patrulla**: the closing report, if one was filed |
| 3+ | **Eventos**: a summary by category, then one table per category (ID, type, time, coordinates, details) |
| … | **Mapa de Patrulla y Eventos**, **Notas** (only when there are notes) and **Imágenes** (event photos) |

Dates and times are shown in the workflow timezone. Choice codes from EarthRanger forms are shown as their labels.

### Changing the template

The template lives at [`resources/templates/apn_patrol_events_template.docx`](resources/templates/apn_patrol_events_template.docx), and the Report Template field defaults to its raw GitHub URL on `main`. To change the report layout, edit that file (it uses [docxtpl](https://docxtpl.readthedocs.io) Jinja tags), test it locally by pointing Report Template at your copy, then merge it to `main`. No recompile is needed for template-only changes.

---

## Where the data comes from

| Report part | EarthRanger source |
|---|---|
| Patrol ID, start and end | The patrol (`serial_number`) and its legs' time ranges |
| Leaders and members | Each leg's leader and members |
| Mandates and leg details | Leg form fields (`segment_details`, plus `type_details` for the leg type: vehicle, boat, horse, …) |
| Distance per leg | GPS track segments that start within the leg's time range |
| Events | Events linked to the patrol's legs, including ones whose event type is now inactive |
| Cierre de Patrulla | A linked `cierre_de_patrulla` event, if any |

A patrol without a GPS track still gets a report, without distances or a map.

The tasks behind this live in [`ecoscope-workflows-ext-apn`](https://github.com/wildlife-dynamics/APN) (`get_patrol_segments_info`, `get_patrol_stats`, `get_patrol_legs_table`, `prepare_patrol_report_context`, `generate_patrol_report`).

---

## Development

Requires [pixi](https://pixi.sh) and an EarthRanger connection for the data source you test against.

**Edit** `spec.yaml` (tasks, form overrides, dependency versions) and `layout.json` (dashboard layout). Don't edit the generated `ecoscope-workflows-patrol-event-workflow/` folder by hand.

**Compile** after changing the spec or a dependency version:

```bash
./dev/recompile.sh --update
```

`--update` keeps the existing lockfile and bumps the workflow version.

**Run** locally against real data (`param.yaml` holds example parameters):

```bash
cd ecoscope-workflows-patrol-event-workflow
ECOSCOPE_WORKFLOWS_RESULTS="file:///tmp/apn-patrol-event" \
  pixi run ecoscope-workflows-patrol-event-workflow run \
  --config-file ../param.yaml --execution-mode sequential --no-mock-io
```

The dashboard data goes to `result.json` and the report to `*_Patrol_Report_<ID>.docx` in the results folder.

### Dependency versions

| Package | Version | Why |
|---|---|---|
| `ecoscope-workflows-ext-apn` | pinned | APN tasks; bump it after each ext-apn release |
| `ecoscope-workflows-ext-custom` | pinned | Shared tasks (attachments, remote template download) |
| `ecoscope-platform` | range | The solver picks the newest version compatible with ext-custom |
| `wt-compiler` (in `pixi.toml`) | `>=0.8.2,<0.11` | wt-compiler 0.11 requires `wt-task >=0.3`, which ext-custom doesn't support yet. Lift the cap once it does. |
