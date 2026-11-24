# omp — Claude desktop themes

Dark and light [oh-my-pi](https://github.com/can1357/oh-my-pi) themes that follow the Claude desktop
app (claude.ai's chat UI): warm off-black or ivory surfaces, ivory/ink text, clay accents, blue
links, red-tinted inline code, and One Dark / One Light code.

| Dark | Light |
|---|---|
| ![Dark preview](docs/preview-dark.png) | ![Light preview](docs/preview-light.png) |

## Install

```sh
./install.sh          # copy both themes into ~/.omp/agent/themes
./install.sh --use    # copy, then set them as omp's dark and light themes
```

Or pick **claude-desktop-dark** / **claude-desktop-light** in omp's `/settings` → Appearance.
omp picks the dark or light one from the terminal's background. `./install.sh --uninstall`
removes the files; `PI_CODING_AGENT_DIR` targets another agent dir.

### Closest to the desktop app

omp's colorful Markdown (on by default) paints headings, bold and inline code from the terminal's
ANSI colors. Claude's chat keeps headings and bold in the text color and inline code red. To get
that:

```sh
omp config set tui.colorfulMarkdown false
```

The themes' `terminal` section is the terminal they were made for (`#262624` / `#faf9f5`
background). The same palette ships for the Herdr app in
[herdr-claude-theme](https://github.com/Tim-van-Oudheusden/herdr-claude-theme).

## Where the colors come from

| omp tokens | Claude desktop source |
|---|---|
| terminal background, `userMessageBg`, `toolPendingBg`, `statusLineBg` | `--bg-100`, `--bg-300` (user bubble), `--bg-000` (cards), `--bg-200` (sidebar) |
| `text`, `toolOutput`, `muted`, `dim` | `--text-100`, `--text-200`, `--text-400`, `--text-500` |
| `accent`, `borderAccent`, `statusLineModel`, `mdExtensionLink` | `--accent-brand` clay `#d97757` (light: `--brand-000` `#c6613f`) |
| `mdLink`, `thinkingLow`, `statusLineContext` | `--accent-000` blue |
| `mdCode` | `--danger-000`, the color of claude.ai's inline code |
| `success`, `error`, `warning`, diffs | `--success-*`, `--danger-*`, `--warning-*` |
| `customMessageLabel`, `thinkingMedium`, `subagent6` | `--accent-pro-*` violet |
| `syntax*`, `mdCodeBlock` | One Dark (dark); One Light (light, since omp can't paint the code block's background) |
| `subagent1`–`5` | Anthropic's plum, mineral, peach and cactus, plus blue/amber/green in light |

Tool result tints mix the success/danger colors 6–9% into the background. The spinner uses
the Claude spark glyphs.

## Previews

`scripts/preview.py` regenerates `docs/preview-*.png` from `omp gallery` in a throwaway agent dir,
so it reads none of your settings. It needs `omp` and Chromium (on `PATH` or the
`org.chromium.Chromium` flatpak).
