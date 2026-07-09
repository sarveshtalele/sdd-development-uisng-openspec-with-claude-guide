#!/usr/bin/env python3
"""Builds a static HTML site from every Markdown file in the repository.

Walks the repo, converts each .md file to a styled HTML page (Apple-glass
aesthetic, shared sidebar navigation), rewrites internal .md links to .html,
and generates a browsable index.html for every directory. Output goes to
_site/, ready to be uploaded as a GitHub Pages artifact.
"""

import os
import re
import sys
from pathlib import Path

import markdown

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "_site"

EXCLUDE_DIR_NAMES = {
    ".git", ".github", "_site", "node_modules", ".venv", "venv",
    "__pycache__", ".pytest_cache",
}
EXCLUDE_DIR_SUFFIXES = (".egg-info",)

# Directories whose contents are still built as pages, but left out of the
# shared sidebar to keep it focused on the documents a reader actually
# starts from.
SIDEBAR_EXCLUDE_COMPONENTS = {"archive", "changes", ".claude", "openspec", "specs"}

SITE_TITLE = "Spec-Driven Development with OpenSpec and Claude Code"

GROUP_TITLES = {
    "": "Home",
    "openspec-guide": "OpenSpec Guide",
    "claude-guide": "Claude Code Guide",
    "travel-itinerary-agent": "Example Project",
}

MD_EXTENSIONS = ["extra", "toc", "sane_lists"]


def is_excluded_dir(name: str) -> bool:
    return name in EXCLUDE_DIR_NAMES or any(name.endswith(s) for s in EXCLUDE_DIR_SUFFIXES)


def find_markdown_files() -> list[Path]:
    found = []
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if not is_excluded_dir(d)]
        for name in filenames:
            if name.lower().endswith(".md"):
                found.append(Path(dirpath) / name)
    return sorted(found)


def rel(path: Path) -> Path:
    return path.relative_to(REPO_ROOT)


def out_path_for(md_path: Path) -> Path:
    return OUTPUT_DIR / rel(md_path).with_suffix(".html")


LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
FENCE_RE = re.compile(r"^(\s*)(`{3,}|~{3,})")


def _rewrite_link(match: re.Match) -> str:
    target = match.group(1)
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return match.group(0)
    path_part, sep, frag = target.partition("#")
    if path_part.lower().endswith(".md"):
        new_path = path_part[:-3] + ".html"
        new_target = new_path + (sep + frag if sep else "")
        return f"]({new_target})"
    return match.group(0)


def rewrite_markdown_links(text: str) -> str:
    """Rewrites .md links to .html, skipping anything inside a fenced code
    block so that literal markdown-link syntax shown as an example is left
    untouched."""
    out_lines = []
    fence_char = None
    fence_len = 0
    for line in text.split("\n"):
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(2)
            char, length = marker[0], len(marker)
            if fence_char is None:
                fence_char, fence_len = char, length
            elif char == fence_char and length >= fence_len:
                fence_char, fence_len = None, 0
            out_lines.append(line)
            continue
        if fence_char is not None:
            out_lines.append(line)
            continue
        out_lines.append(LINK_RE.sub(_rewrite_link, line))
    return "\n".join(out_lines)


def first_heading(text: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
    return fallback


def group_title_for(top_component: str) -> str:
    return GROUP_TITLES.get(top_component, top_component.replace("-", " ").title())


def is_sidebar_eligible(rel_path: Path) -> bool:
    return not any(part in SIDEBAR_EXCLUDE_COMPONENTS for part in rel_path.parts[:-1])


def build_sidebar_model(pages: list[dict]) -> "OrderedDictType":
    from collections import OrderedDict

    groups: "OrderedDictType" = OrderedDict()
    root_pages = [p for p in pages if is_sidebar_eligible(p["rel"]) and len(p["rel"].parts) == 1]
    groups[""] = root_pages

    top_dirs = sorted({p["rel"].parts[0] for p in pages if len(p["rel"].parts) > 1})
    for top in top_dirs:
        children = [
            p for p in pages
            if is_sidebar_eligible(p["rel"])
            and p["rel"].parts[0] == top
            and len(p["rel"].parts) == 2
        ]
        if children:
            children.sort(key=lambda p: (p["rel"].name != "README.md", p["rel"].name.lower()))
            groups[top] = children
    return groups


def relhref(from_file_out: Path, to_file_out: Path) -> str:
    return os.path.relpath(to_file_out, start=from_file_out.parent).replace(os.sep, "/")


def render_sidebar(current_out: Path, groups: dict) -> str:
    parts = ['<nav class="sidebar-nav">']
    for top, children in groups.items():
        title = group_title_for(top)
        parts.append(f'<div class="nav-group"><div class="nav-group-title">{title}</div><ul>')
        for page in children:
            href = relhref(current_out, page["out"])
            active = " active" if page["out"] == current_out else ""
            parts.append(f'<li><a class="nav-link{active}" href="{href}">{page["title"]}</a></li>')
        parts.append("</ul></div>")
    parts.append("</nav>")
    return "\n".join(parts)


def render_breadcrumbs(current_out: Path, rel_path: Path) -> str:
    crumbs = ['<a href="{}">Home</a>'.format(relhref(current_out, OUTPUT_DIR / "index.html"))]
    accumulated = OUTPUT_DIR
    parts = rel_path.parts[:-1]
    for part in parts:
        accumulated = accumulated / part
        index_html = accumulated / "index.html"
        crumbs.append(f'<a href="{relhref(current_out, index_html)}">{part}</a>')
    crumbs.append(f'<span>{rel_path.name}</span>')
    return '<div class="breadcrumbs">' + '<span class="crumb-sep">/</span>'.join(crumbs) + "</div>"


PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{page_title} · {site_title}</title>
<link rel="stylesheet" href="{css_href}">
<link rel="preconnect" href="https://cdnjs.cloudflare.com">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-light.min.css">
</head>
<body>
<div class="bg-blob blob-1"></div>
<div class="bg-blob blob-2"></div>
<div class="bg-blob blob-3"></div>

<button class="nav-toggle" id="navToggle" aria-label="Toggle navigation">Menu</button>

<div class="layout">
  <aside class="sidebar glass" id="sidebar">
    <a class="brand" href="{home_href}">{site_title}</a>
    {sidebar_html}
  </aside>
  <main class="content-wrap">
    <div class="content glass">
      {breadcrumbs_html}
      {body_html}
    </div>
  </main>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="{js_href}"></script>
</body>
</html>
"""


def render_page(md_path: Path, page_title: str, sidebar_html: str, breadcrumbs_html: str,
                 css_href: str, js_href: str, home_href: str) -> str:
    raw = md_path.read_text(encoding="utf-8")
    raw = rewrite_markdown_links(raw)
    body_html = markdown.markdown(raw, extensions=MD_EXTENSIONS)
    return PAGE_TEMPLATE.format(
        page_title=page_title,
        site_title=SITE_TITLE,
        css_href=css_href,
        js_href=js_href,
        home_href=home_href,
        sidebar_html=sidebar_html,
        breadcrumbs_html=breadcrumbs_html,
        body_html=body_html,
    )


def render_dir_listing(dir_out: Path, dir_rel: Path, entries: list[dict], subdirs: list[str],
                        sidebar_html: str, css_href: str, js_href: str, home_href: str) -> str:
    title = dir_rel.name if dir_rel.parts else "Home"
    items = []
    for name in sorted(subdirs):
        target = dir_out / name / "index.html"
        items.append(f'<li><a href="{relhref(dir_out / "index.html", target)}">{name}/</a></li>')
    for page in sorted(entries, key=lambda p: p["rel"].name.lower()):
        items.append(
            f'<li><a href="{relhref(dir_out / "index.html", page["out"])}">{page["title"]}</a></li>'
        )
    body_html = f"<h1>{title}</h1><ul class='dir-listing'>" + "\n".join(items) + "</ul>"
    breadcrumbs_html = render_breadcrumbs(dir_out / "index.html", dir_rel) if dir_rel.parts else ""
    return PAGE_TEMPLATE.format(
        page_title=title,
        site_title=SITE_TITLE,
        css_href=css_href,
        js_href=js_href,
        home_href=home_href,
        sidebar_html=sidebar_html,
        breadcrumbs_html=breadcrumbs_html,
        body_html=body_html,
    )


def main() -> None:
    if OUTPUT_DIR.exists():
        import shutil
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True)

    md_files = find_markdown_files()
    pages = []
    for md_path in md_files:
        rel_path = rel(md_path)
        out = out_path_for(md_path)
        text = md_path.read_text(encoding="utf-8")
        title = first_heading(text, rel_path.stem)
        pages.append({"md": md_path, "rel": rel_path, "out": out, "title": title})

    sidebar_groups = build_sidebar_model(pages)

    assets_dir = OUTPUT_DIR / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    (assets_dir / "style.css").write_text(CSS, encoding="utf-8")
    (assets_dir / "app.js").write_text(JS, encoding="utf-8")
    (OUTPUT_DIR / ".nojekyll").write_text("", encoding="utf-8")

    for page in pages:
        out = page["out"]
        out.parent.mkdir(parents=True, exist_ok=True)
        css_href = relhref(out, assets_dir / "style.css")
        js_href = relhref(out, assets_dir / "app.js")
        home_href = relhref(out, OUTPUT_DIR / "index.html")
        sidebar_html = render_sidebar(out, sidebar_groups)
        breadcrumbs_html = render_breadcrumbs(out, page["rel"])
        html = render_page(page["md"], page["title"], sidebar_html, breadcrumbs_html,
                            css_href, js_href, home_href)
        out.write_text(html, encoding="utf-8")

        if page["rel"].name == "README.md":
            index_out = out.parent / "index.html"
            index_out.write_text(html, encoding="utf-8")

    all_dirs = {OUTPUT_DIR}
    for page in pages:
        d = page["out"].parent
        while True:
            all_dirs.add(d)
            if d == OUTPUT_DIR:
                break
            d = d.parent

    for d in sorted(all_dirs, key=lambda p: len(p.parts)):
        index_file = d / "index.html"
        if index_file.exists():
            continue
        dir_rel = d.relative_to(OUTPUT_DIR)
        entries = [p for p in pages if p["out"].parent == d]
        subdirs = sorted({
            sub.relative_to(d).parts[0]
            for sub in all_dirs
            if sub != d and d in sub.parents and len(sub.relative_to(d).parts) == 1
        })
        css_href = relhref(index_file, assets_dir / "style.css")
        js_href = relhref(index_file, assets_dir / "app.js")
        home_href = relhref(index_file, OUTPUT_DIR / "index.html")
        sidebar_html = render_sidebar(index_file, sidebar_groups)
        html = render_dir_listing(d, dir_rel, entries, subdirs, sidebar_html, css_href, js_href, home_href)
        index_file.write_text(html, encoding="utf-8")

    print(f"Built {len(pages)} pages into {OUTPUT_DIR}")


CSS = """
:root {
  --blue-deep: #0a5fb4;
  --blue-accent: #2f8fe0;
  --blue-soft: #cfe6fb;
  --cream: #fbf4e8;
  --cream-soft: #fdf9f0;
  --white: #ffffff;
  --ink: #1c2733;
  --ink-soft: #51606f;
  --glass-bg: rgba(255, 255, 255, 0.52);
  --glass-border: rgba(255, 255, 255, 0.65);
  --glass-shadow: 0 8px 40px rgba(24, 66, 115, 0.14);
  --radius-lg: 22px;
  --radius-md: 14px;
}

* { box-sizing: border-box; }

html, body {
  margin: 0;
  padding: 0;
  min-height: 100%;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
    "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: var(--ink);
  background: linear-gradient(160deg, #eaf3fc 0%, #f7f2e7 45%, #fdf7ec 100%);
  min-height: 100vh;
  position: relative;
  overflow-x: hidden;
  line-height: 1.65;
}

.bg-blob {
  position: fixed;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.55;
  z-index: 0;
  pointer-events: none;
}
.blob-1 { width: 520px; height: 520px; top: -160px; left: -120px; background: radial-gradient(circle, #bcdcfb, transparent 70%); }
.blob-2 { width: 460px; height: 460px; bottom: -140px; right: -100px; background: radial-gradient(circle, #f7e6c4, transparent 70%); }
.blob-3 { width: 360px; height: 360px; top: 40%; right: 10%; background: radial-gradient(circle, #d9c9fb, transparent 70%); opacity: 0.35; }

.glass {
  background: var(--glass-bg);
  backdrop-filter: blur(22px) saturate(180%);
  -webkit-backdrop-filter: blur(22px) saturate(180%);
  border: 1px solid var(--glass-border);
  box-shadow: var(--glass-shadow);
  border-radius: var(--radius-lg);
}

.layout {
  position: relative;
  z-index: 1;
  display: flex;
  max-width: 1280px;
  margin: 0 auto;
  padding: 32px 24px 80px;
  gap: 28px;
  align-items: flex-start;
}

.sidebar {
  flex: 0 0 264px;
  position: sticky;
  top: 24px;
  max-height: calc(100vh - 48px);
  overflow-y: auto;
  padding: 22px 18px;
}

.brand {
  display: block;
  font-weight: 700;
  font-size: 15px;
  letter-spacing: -0.01em;
  color: var(--blue-deep);
  text-decoration: none;
  margin-bottom: 18px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(10, 95, 180, 0.14);
}

.nav-group { margin-bottom: 14px; }
.nav-group-title {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--ink-soft);
  margin: 10px 0 6px 6px;
}
.sidebar-nav ul { list-style: none; margin: 0; padding: 0; }
.nav-link {
  display: block;
  padding: 7px 10px;
  border-radius: 10px;
  color: var(--ink);
  text-decoration: none;
  font-size: 13.5px;
  transition: background 0.15s ease, color 0.15s ease, transform 0.15s ease;
}
.nav-link:hover {
  background: rgba(47, 143, 224, 0.12);
  color: var(--blue-deep);
  transform: translateX(2px);
}
.nav-link.active {
  background: linear-gradient(135deg, var(--blue-accent), var(--blue-deep));
  color: var(--white);
  font-weight: 600;
}

.content-wrap { flex: 1 1 auto; min-width: 0; }
.content { padding: 44px 52px; }

.breadcrumbs {
  font-size: 12.5px;
  color: var(--ink-soft);
  margin-bottom: 22px;
}
.breadcrumbs a { color: var(--blue-accent); text-decoration: none; }
.breadcrumbs a:hover { text-decoration: underline; }
.crumb-sep { margin: 0 8px; opacity: 0.5; }

.content h1, .content h2, .content h3, .content h4 {
  color: var(--ink);
  letter-spacing: -0.015em;
  font-weight: 700;
}
.content h1 {
  font-size: 32px;
  margin: 0 0 18px;
  background: linear-gradient(120deg, var(--blue-deep), var(--blue-accent) 60%, #6ab6ee);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.content h2 { font-size: 23px; margin: 40px 0 14px; padding-top: 6px; border-top: 1px solid rgba(10, 95, 180, 0.1); }
.content h2:first-of-type { border-top: none; padding-top: 0; }
.content h3 { font-size: 18px; margin: 28px 0 10px; color: var(--blue-deep); }
.content h4 { font-size: 15px; margin: 20px 0 8px; }

.content p, .content li { color: var(--ink); font-size: 15px; }
.content ul, .content ol { padding-left: 22px; }
.content li { margin: 4px 0; }

.content a { color: var(--blue-deep); text-decoration: none; border-bottom: 1px solid rgba(10, 95, 180, 0.28); }
.content a:hover { color: var(--blue-accent); border-bottom-color: var(--blue-accent); }

.content code {
  font-family: "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
  background: rgba(10, 95, 180, 0.08);
  color: #0a4d90;
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 13px;
}

.content pre {
  background: rgba(24, 32, 44, 0.92);
  backdrop-filter: blur(10px);
  color: #eef3f8;
  border-radius: var(--radius-md);
  padding: 18px 20px;
  overflow-x: auto;
  box-shadow: 0 6px 24px rgba(20, 30, 45, 0.25);
  margin: 18px 0;
}
.content pre code {
  background: transparent;
  color: inherit;
  padding: 0;
  font-size: 13px;
}

.content table {
  width: 100%;
  border-collapse: collapse;
  margin: 18px 0;
  border-radius: var(--radius-md);
  overflow: hidden;
  box-shadow: 0 4px 18px rgba(24, 66, 115, 0.08);
}
.content th, .content td {
  padding: 10px 14px;
  border-bottom: 1px solid rgba(10, 95, 180, 0.1);
  text-align: left;
  font-size: 13.5px;
  vertical-align: top;
}
.content th {
  background: rgba(47, 143, 224, 0.14);
  color: var(--blue-deep);
  font-weight: 700;
  font-size: 12.5px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.content tr:nth-child(even) td { background: rgba(255, 255, 255, 0.4); }

.content blockquote {
  margin: 18px 0;
  padding: 12px 18px;
  border-left: 3px solid var(--blue-accent);
  background: rgba(47, 143, 224, 0.08);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  color: var(--ink-soft);
}

.content hr { border: none; border-top: 1px solid rgba(10, 95, 180, 0.14); margin: 32px 0; }

.dir-listing { list-style: none; padding: 0; }
.dir-listing li { margin: 6px 0; }
.dir-listing a {
  display: inline-block;
  padding: 8px 14px;
  border-radius: var(--radius-md);
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid var(--glass-border);
  color: var(--blue-deep);
  text-decoration: none;
  font-size: 14px;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.dir-listing a:hover { transform: translateY(-2px); box-shadow: 0 6px 18px rgba(24, 66, 115, 0.14); }

.nav-toggle {
  display: none;
  position: fixed;
  top: 18px;
  left: 18px;
  z-index: 10;
  padding: 10px 16px;
  border-radius: 999px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg);
  backdrop-filter: blur(16px);
  color: var(--blue-deep);
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
}

@media (max-width: 860px) {
  .layout { flex-direction: column; padding: 84px 16px 60px; }
  .sidebar {
    position: fixed;
    left: 16px;
    right: 16px;
    top: 68px;
    z-index: 9;
    max-height: 70vh;
    display: none;
  }
  .sidebar.open { display: block; }
  .nav-toggle { display: block; }
  .content { padding: 28px 22px; }
  .content h1 { font-size: 26px; }
}
"""

JS = """
document.addEventListener('DOMContentLoaded', function () {
  if (window.hljs) {
    document.querySelectorAll('pre code').forEach(function (block) {
      hljs.highlightElement(block);
    });
  }
  var toggle = document.getElementById('navToggle');
  var sidebar = document.getElementById('sidebar');
  if (toggle && sidebar) {
    toggle.addEventListener('click', function () {
      sidebar.classList.toggle('open');
    });
  }
});
"""


if __name__ == "__main__":
    sys.exit(main())
