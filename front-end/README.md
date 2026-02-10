## Setup

```bash
cd front-end         # Navigate to front-end directory
make install_deps    # Install dependencies
make dev             # Start dev server (port 4200)
make build           # Build for production. Output: `dist/hn-hiring-frontend/browser/`
```

See `front-end/Makefile` for all commands.


## Local Development

1. **Navigate to front-end directory**
   ```bash
   cd front-end
   ```

2. **Install dependencies**
   ```bash
   make install_deps
   ```

3. **Start dev server**
   ```bash
   make dev
   ```
   Opens at `http://localhost:4200` with hot reload

4. **View locally**
   - Navigate to `http://localhost:4200`
   - App loads sample data from `public/jobs.json`
   - Make changes in `src/` - auto-reloads

5. **Debug**
   - Open browser DevTools (F12)
   - Source maps enabled for debugging TypeScript
   - Angular DevTools extension recommended