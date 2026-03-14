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
- **Drag & drop** — move families between field service groups; all stats update instantly
- **Editable assistant** — assign any elder or ministerial servant in the group as the assistant; automatically cleared if the assistant's family is moved out
- **Family member tooltip** — hover any family card to see each member with their role and status indicators
- **Moved members excluded** — only persons and families with `moved = false` are included

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
8. To delete the server-side database or upload a new one, click **Upload Database** in the header.

## Database Schema

The application expects a SQLite database exported from [congregation-directory](https://github.com/jgruber/congregation-directory) with the following tables:

| Table | Key Columns |
|---|---|
| `congregations` | `id`, `name` |
| `field_service_groups` | `id`, `congregation_id`, `name`, `overseer`, `overseer_id`, `assistant`, `assistant_id`, `phone` |
| `families` | `id`, `name`, `field_service_group_id`, `family_head`, `city`, `moved` |
| `persons` | `id`, `family_id`, `display_name`, `category`, `elder`, `ministerial_servant`, `special_pioneer`, `pioneer`, `inactive`, `moved`, `removed` |

Only records where `moved = 0` are included in the display and statistics.

## Tech Stack

- [Tailwind CSS](https://tailwindcss.com/) — utility-first styling (CDN)
- [sql.js](https://sql.js.org/) — SQLite compiled to WebAssembly (CDN)
- [Flask](https://flask.palletsprojects.com/) — lightweight Python server for auto-load and file management
- [python:3.12-alpine](https://hub.docker.com/_/python) — Docker container base image
- Vanilla JavaScript, HTML5 Drag and Drop API — no framework dependencies
