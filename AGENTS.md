# omp-claude-theme

oh-my-pi (omp) themes modeled on the Claude desktop app (claude.ai chat UI, not the Claude Code
CLI): `themes/claude-desktop-dark.json`, `themes/claude-desktop-light.json`. Sibling repo for the
Herdr app: `~/Git/herdr-claude-theme`; keep surface, text, clay and ANSI values identical across
both (README "Where the colors come from" names each source token).

`presets/claude-desktop.yml` (applied by `./install.sh --preset`) sets omp settings for the rest of
the desktop look. Keep it opt-in: nothing applies it implicitly. Re-check its keys and values
against the installed omp (`omp config list --json`) after an omp upgrade.

## You are probably running inside omp

The session editing this repo is usually omp itself, inside Herdr. Keep it intact:

- Leave `~/.omp/agent/config.yml` alone (`install.sh --use` writes it). Select a theme for a test
  process with `omp --config <overlay.yml>` or a throwaway `PI_CODING_AGENT_DIR`.
- Copying into `~/.omp/agent/themes/` is safe: omp watches only the active theme's file.
- Don't switch Herdr between light and dark to test the light theme: every running omp follows
  the terminal's appearance. `COLORFGBG=0;15` makes a non-TTY omp pick the light slot.

## Theme format: the non-obvious parts

The schema of the installed omp is the truth (`omp --version`; the GitHub `main` docs run ahead):
`packages/tui/src/theme/schema.ts` and `theme-schema.json` at tag `v<version>`.

- Color values: `#rrggbb`, a 0–255 index, a `vars` name, or `""` (terminal default).
- `vars` resolve in `colors`, `export` and `terminal.background/foreground/ansi`; this repo writes
  literal hex in `export` and `terminal`, which hosts such as Tern read directly.
- `terminal.ansi` also colors Markdown while `tui.colorfulMarkdown` is on (default): headings,
  bold and inline code then ignore `mdHeading` / `mdCode`.
- `assistantMessageText` (not `text`) colors assistant prose.
- A custom theme that fails to load makes omp fall back to the built-in `dark`; output in
  `dark`'s colors (e.g. `#febc38` headings) means the theme didn't load.

## Verify every change

1. Validate both files against the version's `theme-schema.json` (python `jsonschema`) and check
   every var reference resolves.
2. `scripts/preview.py`: regenerates `docs/preview-*.png`. Read the PNGs.
3. For real transcript surfaces (markdown, user bubbles, diffs), open a Herdr tab running
   `omp --config <overlay selecting the theme> --session-dir <tmp> --resume <copy of a session>`
   and `herdr-app shot`. Drive it with `hc keys` only: `hc send` arrives as an agent message and
   starts a model turn. `omp render` ignores the theme setting and resuming switches cwd (which
   drops project `.omp/config.yml`), hence `--config`.

## Commits

Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`), straight to `main`.
