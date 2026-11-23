# APN Patrol & Event Report

An Ecoscope workflow for Argentina's national parks agency (Administración de Parques Nacionales, **APN**).

Give it one EarthRanger patrol and it produces:

- a **dashboard** with the patrol's headline numbers, its legs and a map, and
- a **Word report** (`.docx`) in APN's format, ready to print or share.

APN records patrol information on the patrol itself, as EarthRanger patrol **legs** (also called segments). The workflow reads the leaders, members, mandates and leg details from those legs, and the events linked to them.

**Contents:** [Using it](#using-it) · [What you get](#what-you-get) · [Where the data comes from](#where-the-data-comes-from) · [Troubleshooting](#troubleshooting) · [Development](#development) · [Releasing](#releasing)

---

## Using it

Fill in the config page from top to bottom:

| Section | What to set |
|---|---|
| **Workflow Details** | A name (and optional description) shown on the dashboard |
| **Data Source** | The EarthRanger connection, e.g. `apncentral` |
| **Time Range** | Any range that covers the patrol, and the timezone (Buenos Aires) |
| **ID de Patrulla** | The patrol's serial number in EarthRanger, e.g. `74`. Required. |
| Spatial Features / Local Spatial Features | Optional map layers, such as park boundaries |
| Patrol Style / Patrol Markers / Event Style | Map colors, legends and start/end markers |
| Download Attachments | Include event photos in the report, or skip them |
| Base Maps *(advanced)* | Map background tiles |
| Report Template *(advanced)* | The `.docx` template. Leave the default unless you're testing a new template. |

## What you get

### Dashboard

| Widget | Shows |
|---|---|
| **Distancia total** | Kilometres of GPS track, e.g. `4.05 km` |
| **Tiempo total** | Hours on patrol, summed over the legs, e.g. `0.44 h` |
| **Tramos** | Number of legs |
| **Eventos** | Number of events linked to the patrol (the closing report is not counted) |
| **Tramos de Patrulla** | One row per leg: #, type, start, end, leader, distance (km), time (h) |
| **Mapa de Patrulla y Eventos** | The track colored by leg type, the events, and any spatial features |

### Word report

| Section | Contents |
|---|---|
| Header | Patrol ID, mandates, start and end, and a stats row with the same four numbers as the dashboard |
| **Personal Participante** | One row per leader, with their members and any unlisted staff |
| **Tramos de Patrulla** | One row per leg: date and schedule, leader, distance, time, and the leg's form details |
| **Cierre de Patrulla** | The end-of-patrol form, when one was filed; otherwise *"Sin cierre de patrulla registrado"* |
| **Eventos** | A summary by category, then one table per category: ID, type, time, coordinates, details |
| **Mapa de Patrulla y Eventos** | The patrol map |
| **Notas** | Event notes. Left out entirely when there are none. |
| **Imágenes** | Event photos, unless downloads are skipped |

Dates and times are in the workflow timezone, and EarthRanger form codes are shown as their labels.

### The template

The report layout is [`resources/templates/apn_patrol_events_template.docx`](resources/templates/apn_patrol_events_template.docx), a Word file with [docxtpl](https://docxtpl.readthedocs.io) (Jinja) tags. The Report Template field defaults to that file's raw GitHub URL on `main`, so runs on the web and on desktop both download it.

To change the layout: edit the file, test it by pointing Report Template at your local copy, then merge it to `main`. Template-only changes need no recompile.

---

## Where the data comes from

| Report part | EarthRanger source |
|---|---|
| Patrol ID, start and end | The patrol's `serial_number` and its legs' time ranges |
| Leaders and members | Each leg's leader and members |
| Mandates and leg details | Leg form fields: `segment_details`, plus `type_details` for the leg type (vehicle, boat, horse, …) |
| Distance per leg | GPS track segments that start within the leg's time range |
| Events | Events linked to the patrol's legs, including ones whose event type has since been deactivated |
| Cierre de Patrulla | A linked `cierre_de_patrulla` event |

A patrol without a GPS track still gets a report, without distances or a map.

The tasks behind this live in the [`ecoscope-workflows-ext-apn`](https://github.com/wildlife-dynamics/APN) package: `get_patrol_segments_info`, `get_patrol_stats`, `get_patrol_legs_table`, `prepare_patrol_report_context` and `generate_patrol_report`.

---

## Troubleshooting

| You see | Why, and what to do |
|---|---|
| *No patrol matches the 'ID de Patrulla' in the selected time range* | The patrol isn't inside the time range, or the ID is wrong. Widen the range or check the serial number in EarthRanger. |
| *Invalid "root" object field configuration: uiSchema order list does not contain property …* (desktop) | A new config section isn't in the form order. Run `dev/check_rjsf_order.py` (see [Development](#development)) and fix `ui:order` in `spec.yaml`. |
| Distancia shows `0.00 km` | The patrol has little or no GPS track, e.g. a leg of a minute or two. |
| Eventos shows `0` but the report has a Cierre section | Expected: the closing report has its own section and isn't counted as an event. |
| A leg type, category or detail shows a raw code | The event type was deactivated in EarthRanger after the event was recorded, so its labels can't be looked up. |

---

## Development

You need [pixi](https://pixi.sh) and an EarthRanger connection for the site you test against.

### Files you edit

| File | What it holds |
|---|---|
| `spec.yaml` | Workflow steps, config page overrides (`rjsf-overrides`, including the section order) and dependency versions |
| `layout.json` | Dashboard layout |
| `resources/templates/` | The Word template |
| `param.yaml`, `test-cases.yaml` | Example parameters and test cases |

Everything in `ecoscope-workflows-patrol-event-workflow/` is generated. Don't edit it by hand.

### Compile

After changing `spec.yaml` or a dependency version:

```bash
./dev/recompile.sh --update
```

`--update` keeps the existing lockfile and bumps the workflow version. If you only changed form overrides, `./dev/regenerate_rjsf.sh` rebuilds just `rjsf.json`, much faster.

### Check the config page

ecoscope-desktop rejects a form whose section order is incomplete. Check it after every compile:

```bash
.pixi/envs/default/bin/python dev/check_rjsf_order.py ecoscope-workflows-patrol-event-workflow/ecoscope_workflows_patrol_event_workflow/rjsf.json
```

It prints `ui:order OK`, or each section that's missing or extra.

### Run against real data

```bash
cd ecoscope-workflows-patrol-event-workflow
ECOSCOPE_WORKFLOWS_RESULTS="file:///tmp/apn-patrol-event" \
  pixi run ecoscope-workflows-patrol-event-workflow run \
  --config-file ../param.yaml --execution-mode sequential --no-mock-io
```

The dashboard data is written to `result.json` and the report to `*_Patrol_Report_<ID>.docx` in the results folder. Useful test patrols on apn-central: **#74** (three legs, events in several categories) and **#76** (has a Cierre de Patrulla).

### Dependency versions

| Package | Pinned as | Why |
|---|---|---|
| `ecoscope-workflows-ext-apn` | exact | The APN tasks. Bump it after each ext-apn release. |
| `ecoscope-workflows-ext-custom` | exact | Shared tasks (attachments, template download) |
| `ecoscope-platform` | range | The solver picks the newest version that works with ext-custom |
| `wt-compiler` (in `pixi.toml`) | `>=0.8.2,<0.11` | wt-compiler 0.11 requires `wt-task >=0.3`, which ext-custom doesn't support yet. Lift the cap once it does. |

---

## Releasing

When a change needs new ext-apn code:

1. Merge the change in the [APN repo](https://github.com/wildlife-dynamics/APN), then tag `main` (e.g. `v0.0.33`). The tag publishes the package to prefix.dev.
2. Bump `ecoscope-workflows-ext-apn` in `spec.yaml` to the new version.
3. `./dev/recompile.sh --update`
4. Run the config page check.
5. Run #74 and #76 and look over the dashboard and report.
6. Open a PR here. After merging, load the workflow once in ecoscope-desktop to confirm the config page opens.
