# AGENTS.md

## Repository Structure

- `frontEnd/` - Vue 2 frontend (webpack 3, element-ui)
- `yail/` - Python backend using custom `yeab` framework (aiohttp-based)

## Backend (yail/)

### Run
```bash
python app.py  # Entry point at yail/app.py
```

### Key Paths
- `PIC_DIR` (raw image path): `frontEnd/static/car` - uploaded car images stored here
- `PIC_URL`: `static/car`

### Frameworks
- Custom `yeab` framework in `lib/yeab/`
- `yom` async ORM in `lib/yom.py` (aiomysql-based)
- Auto-reload via `pymonitor.py` (watchdog-based)

### Migrations
```bash
python tools/migrate/rake_migrate.py
```

## Frontend (frontEnd/)

```bash
npm run dev     # dev server
npm run build   # production build
npm run unit    # jest unit tests
```

## Notes

- Backend CORS uses middleware; Vue axios must set `withCredentials: true`
- `yeab` uses annotation-based routing similar to Spring MVC with auto-scanning
