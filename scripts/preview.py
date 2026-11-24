#!/usr/bin/env python3
"""Render omp's tool gallery in each theme to docs/preview-<variant>.png.

Runs `omp gallery` against a throwaway agent dir holding only this repo's themes,
so it reads no personal settings and needs no install. Converts the ANSI output
to HTML on the theme's own terminal colors, then screenshots it with headless
Chromium (a `chromium` on PATH, else the org.chromium.Chromium flatpak).

    scripts/preview.py            both themes
    scripts/preview.py dark       one variant
"""

import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COLS = 100
FONT_PX = 14
LINE_PX = 18
# (args, label): the surfaces worth looking at when judging a theme.
SECTIONS = [
    (["--composer", "claude"], "composer"),
    (["-t", "edit", "-s", "done", "-s", "failed"], "edit"),
    (["-t", "bash", "-s", "done"], "bash"),
    (["-t", "todo", "-s", "done"], "todo"),
    (["-t", "task", "-s", "done"], "task"),
]

SGR = re.compile(r"\x1b\[([0-9;:]*)m")
OTHER_ESC = re.compile(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)|\x1b\[[0-9;?]*[A-Za-ln-z]")


def ansi256(n: int) -> str:
    base = ["#000000", "#800000", "#008000", "#808000", "#000080", "#800080", "#008080", "#c0c0c0",
            "#808080", "#ff0000", "#00ff00", "#ffff00", "#0000ff", "#ff00ff", "#00ffff", "#ffffff"]
    if n < 16:
        return base[n]
    if n < 232:
        n -= 16
        steps = [0, 95, 135, 175, 215, 255]
        return "#%02x%02x%02x" % (steps[n // 36], steps[n // 6 % 6], steps[n % 6])
    v = 8 + (n - 232) * 10
    return "#%02x%02x%02x" % (v, v, v)


def to_html(ansi: str, fg: str, bg: str) -> str:
    """Convert SGR-colored text to HTML spans; other escapes are dropped."""
    ansi = OTHER_ESC.sub("", ansi)
    out, state = [], {}
    pos = 0

    def span(text: str) -> str:
        if not text:
            return ""
        css = []
        f, b = state.get("fg"), state.get("bg")
        if state.get("inverse"):
            f, b = (b or bg), (f or fg)
        if f:
            css.append(f"color:{f}")
        if b:
            css.append(f"background:{b}")
        if state.get("bold"):
            css.append("font-weight:700")
        if state.get("faint"):
            css.append("opacity:.6")
        if state.get("italic"):
            css.append("font-style:italic")
        deco = [d for d in ("underline", "line-through") if state.get(d)]
        if deco:
            css.append("text-decoration:" + " ".join(deco))
        body = html.escape(text)
        return f'<span style="{";".join(css)}">{body}</span>' if css else body

    for m in SGR.finditer(ansi):
        out.append(span(ansi[pos:m.start()]))
        pos = m.end()
        codes = [int(c) if c else 0 for c in re.split("[;:]", m.group(1) or "0")]
        i = 0
        while i < len(codes):
            c = codes[i]
            if c == 0:
                state.clear()
            elif c in (38, 48, 58) and i + 1 < len(codes):
                key = {38: "fg", 48: "bg", 58: None}[c]
                if codes[i + 1] == 2 and i + 4 < len(codes):
                    value = "#%02x%02x%02x" % tuple(codes[i + 2:i + 5])
                    i += 4
                elif codes[i + 1] == 5 and i + 2 < len(codes):
                    value = ansi256(codes[i + 2])
                    i += 2
                else:
                    value = None
                if key:
                    state[key] = value
            elif c == 39:
                state.pop("fg", None)
            elif c == 49:
                state.pop("bg", None)
            elif 30 <= c <= 37 or 90 <= c <= 97:
                state["fg"] = ansi256(c - 30 if c < 90 else c - 90 + 8)
            elif 40 <= c <= 47 or 100 <= c <= 107:
                state["bg"] = ansi256(c - 40 if c < 100 else c - 100 + 8)
            else:
                flag = {1: ("bold", True), 2: ("faint", True), 3: ("italic", True), 4: ("underline", True),
                        7: ("inverse", True), 9: ("line-through", True), 22: ("bold", False),
                        23: ("italic", False), 24: ("underline", False), 27: ("inverse", False),
                        29: ("line-through", False)}.get(c)
                if flag:
                    state[flag[0]] = flag[1]
                    if c == 22:
                        state["faint"] = False
            i += 1
    out.append(span(ansi[pos:]))
    return "".join(out)


def gallery(agent_dir: Path, light: bool) -> str:
    env = {**os.environ, "PI_CODING_AGENT_DIR": str(agent_dir), "COLORFGBG": "0;15" if light else "15;0"}
    chunks = []
    for args, label in SECTIONS:
        r = subprocess.run(["omp", "gallery", "-w", str(COLS), *args], env=env, capture_output=True,
                           text=True, check=True, cwd=agent_dir)
        if not r.stdout.strip():
            raise SystemExit(f"omp gallery printed nothing for {label}: {r.stderr.strip()}")
        chunks.append(r.stdout.strip("\n"))
    return "\n\n".join(chunks) + "\n"


def chromium() -> list[str]:
    for name in ("chromium", "chromium-browser", "google-chrome"):
        if shutil.which(name):
            return [name]
    if shutil.which("flatpak"):
        return ["flatpak", "run", "org.chromium.Chromium"]
    raise SystemExit("no Chromium found for the screenshot")


def render(variant: str) -> Path:
    theme_file = REPO / "themes" / f"claude-desktop-{variant}.json"
    theme = json.loads(theme_file.read_text())
    term = theme["terminal"]
    out_dir = REPO / "docs"
    out_dir.mkdir(exist_ok=True)
    # The flatpak browser can't see /tmp; keep its page under the repo.
    with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory(dir=REPO) as page_dir:
        agent = Path(tmp)
        (agent / "themes").mkdir()
        shutil.copy(theme_file, agent / "themes")
        (agent / "config.yml").write_text(f"theme:\n  dark: {theme['name']}\n  light: {theme['name']}\n")
        ansi = gallery(agent, variant == "light")
        lines = ansi.count("\n")
        page = Path(page_dir) / "preview.html"
        page.write_text(
            "<!doctype html><meta charset=utf-8><style>"
            f"html,body{{margin:0;background:{term['background']}}}"
            f"pre{{margin:0;padding:16px 20px;color:{term['foreground']};"
            f"font:{FONT_PX}px/{LINE_PX}px 'JetBrains Mono','Fira Code','Noto Sans Mono',monospace}}"
            f"</style><pre>{to_html(ansi, term['foreground'], term['background'])}</pre>"
        )
        png = out_dir / f"preview-{variant}.png"
        width = int(COLS * FONT_PX * 0.6) + 40
        height = lines * LINE_PX + 32
        subprocess.run([*chromium(), "--headless", "--disable-gpu", "--hide-scrollbars",
                        f"--window-size={width},{height}", f"--screenshot={png}", page.as_uri()],
                       check=True, capture_output=True)
    return png


def main() -> None:
    variants = sys.argv[1:] or ["dark", "light"]
    for v in variants:
        if v not in ("dark", "light"):
            raise SystemExit(f"unknown variant {v!r}: use dark or light")
        print(render(v))


if __name__ == "__main__":
    main()
