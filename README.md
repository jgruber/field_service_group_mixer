# Field Service Group Mixer

A single-page web application for visualizing and reorganizing congregation field service groups. Upload a congregation SQLite database, view a live breakdown of each group's families and members, and drag families between groups to experiment with different arrangements.

## Database Source

The `congregation.db` SQLite database used by this application can be exported from the [congregation-directory](https://github.com/jgruber/congregation-directory) application. Use that application to manage your congregation's data, then export the database and upload it here.

## Features

- **Auto-load** — place `congregation.db` in the `data/` directory and it loads automatically on startup
- **Upload any congregation database** — accepts any SQLite `.db` file matching the congregation schema
- **Per-group statistics** — each group card displays counts for:
  - Families, Total Persons
  - Elders, Ministerial Servants
  - Special Pioneers, Regular Pioneers
  - Active, Inactive, Associated
- **Congregation-wide summary bar** — totals across all groups update in real time
- **Local groups** — create a field service group that does not exist in the source database yet (with its own overseer and assistant), so an arrangement can be planned before it is made official
- **Delete any group** — in this copy of the database only; a re-import restores anything that came from the source
- **Drag & drop** — move families between field service groups; all stats update instantly, and the group is written to both the family and its members
- **Editable assistant** — assign any elder or ministerial servant in the group as the assistant; automatically cleared if the assistant's family is moved out
- **Family member tooltip** — hover any family card to see each member with their role and status indicators
- **Moved members excluded** — only persons and families with `moved = false` are included

## Authentication

The Flask server requires HTTP Basic Authentication on all routes.

| Default username | Default password |
|---|---|
| `admin` | `changeme` |

**Change the default password immediately after first login** using the **Users** button in the app header.

User credentials are stored in plain text in `data/users.json` (excluded from version control). The file is created automatically with the default `admin` account on first startup if it does not already exist.

> **Note:** HTTP Basic Authentication transmits credentials with every request. Run behind a TLS-terminating reverse proxy (nginx, Caddy, etc.) in any non-local deployment.

## Getting Started

### Option 1 — Flask dev server (recommended)

```bash
pip install flask
python3 server.py
```

Then open [http://localhost:3000](http://localhost:3000).

Place your exported `congregation.db` in the `data/` directory to have it load automatically on startup.

### Option 2 — Docker

```bash
docker build -t field-service-mixer .
docker run -p 3000:3000 -v /path/to/your/data:/app/data field-service-mixer
```

Then open [http://localhost:3000](http://localhost:3000).

Mount your `data/` directory as a volume so `congregation.db` persists across container restarts.

### Option 3 — Static file server

```bash
python3 -m http.server 3000
```

Then open [http://localhost:3000](http://localhost:3000).

> **Note:** Auto-load and delete features require the Flask server. With a static server, upload the database manually via the browser.

## Usage

1. On startup, if `congregation.db` is present on the server it loads automatically.
2. Otherwise, click **Upload Database** or drag a `.db` file onto the landing zone.
3. The congregation's field service groups load as cards in a responsive grid.
4. Each card shows the group name, overseer, assistant (editable), statistics, and assigned families.
5. **Drag a family card** from one group and **drop it** onto another group to reassign it — stats update immediately.
6. **Hover a family card** to see a tooltip listing each member with their role and status badges.
7. Click the ✏️ pencil next to the assistant name to reassign from eligible elders and ministerial servants.
8. Click **New Group** in the header to create a *local* group — see [Local Groups](#local-groups) below.
9. To delete the server-side database or upload a new one, click **Populate Database** in the header.

## Local Groups

A local group is a field service group created inside the mixer that the source
database does not know about yet. It lets the secretary plan a new group —
assigning families and choosing an overseer and assistant — before the group is
added to the system that feeds the exported database.

- Click **New Group** in the header, then give the group a name, plus an optional
  overseer, assistant, and phone number. A new group has no families yet, so the
  overseer and assistant are chosen from every elder and ministerial servant in
  the congregation rather than from the group's own members.
- Choosing an overseer fills the phone number in with that person's mobile,
  matching how the source data sets a group's phone. Typing your own number
  instead keeps it — a later change of overseer will not overwrite it.
- Local group cards are **green** and carry a **Local** badge so they are easy to
  tell apart from groups that came out of the source database. Their headers have
  ✏️ edit and 🗑 delete buttons; imported groups have 🗑 only and cannot be renamed.
- Printed reports label the group *"Local group — not yet in the source database."*

Local groups are stored in the working copy of the database (with negative ids,
so they never collide with ids assigned by the source), which means they survive
a download / re-upload of that file.

### Deleting a group

Any group can be deleted, imported ones included, and either way it is a change
to **this copy of the database only** — the source system is never written to.
Everyone who was in the group is left **unassigned**: both the `families` and
the `persons` rows have their `field_service_group_id` and
`field_service_group_name` cleared, and that is done by group id rather than
family by family, so records the display leaves out — people who moved away, and
families with no active members — are unassigned too rather than left pointing at
a group that no longer exists. Deleting an imported group is a planning move
rather than a loss: populating the database from the source again brings it back.

### The imported database wins

Populating the database — by file, by drag and drop, or from a URL — replaces
this copy outright and is authoritative. Local groups do not survive it, family
moves and assistant changes made here do not survive it, and nothing is merged.
When an import replaces local groups, the app says so in a banner naming them.

So once an arrangement is settled, add the group to the source system to make it
permanent; anything left only in this copy is provisional by design.

## Database Schema

The application expects a SQLite database exported from [congregation-directory](https://github.com/jgruber/congregation-directory) with the following tables:

| Table | Key Columns |
|---|---|
| `congregations` | `id`, `name` |
| `field_service_groups` | `id`, `congregation_id`, `name`, `overseer`, `overseer_id`, `assistant`, `assistant_id`, `phone` |
| `families` | `id`, `name`, `field_service_group_id`, `field_service_group_name`, `family_head`, `city`, `moved` |
| `persons` | `id`, `family_id`, `display_name`, `mobile`, `category`, `elder`, `ministerial_servant`, `special_pioneer`, `pioneer`, `inactive`, `moved`, `removed`, `field_service_group_id`, `field_service_group_name` |

Only records where `moved = 0` are included in the display and statistics.

Group membership is stored in four places — the id and the name on both
`families` and `persons` — so moving a family, renaming a local group, or
deleting a group writes all of them. Otherwise the exported database
contradicts itself, with a family reading as moved while its members still
name the group they came from.

## Tech Stack

- [Tailwind CSS](https://tailwindcss.com/) — utility-first styling (CDN)
- [sql.js](https://sql.js.org/) — SQLite compiled to WebAssembly (CDN)
- [Flask](https://flask.palletsprojects.com/) — lightweight Python server for auto-load and file management
- [python:3.12-alpine](https://hub.docker.com/_/python) — Docker container base image
- Vanilla JavaScript, HTML5 Drag and Drop API — no framework dependencies
