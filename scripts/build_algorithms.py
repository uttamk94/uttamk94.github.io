#!/usr/bin/env python3
"""Build the Algorithms learning hub (generator + test harness).

Authoring lives in ``algo_content.py``. For each topic this script:

1. Compiles the C and C++ implementations (gcc / g++) and runs them,
2. Runs the Python implementation,
3. Normalizes + compares all three outputs -- they MUST be identical,
   otherwise the build fails (guarantees cross-language correctness),
4. Captures the real test output and embeds it in the page,
5. Records the simulation trace from the topic's ``sim()`` and embeds it,
6. Writes ``pages/algorithms/<slug>.html`` and ``data/algorithms/algos.json``.

Every generated page is fully static so GitHub Pages needs no build step.
The generated HTML is still committed to the repository.

Usage:  python3 scripts/build_algorithms.py
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
sys.path.insert(0, str(REPO / "scripts"))
import algo_content as ac  # noqa: E402

TMP = Path(tempfile.mkdtemp(prefix="algo_build_"))
OUT_PAGES = REPO / "pages" / "algorithms"
OUT_DATA = REPO / "data" / "algorithms"

C_COMPILER = shutil.which("gcc") or "gcc"
CPP_COMPILER = shutil.which("g++") or "g++"
PYTHON = sys.executable


# ---------------------------------------------------------------------------
# Running implementations
# ---------------------------------------------------------------------------

def run_cmd(args, cwd=None):
    proc = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=60)
    return proc


def normalize_output(text):
    """Normalize stdout for cross-language comparison: ignore trailing space,
    blank lines, and surrounding whitespace on each line."""
    lines = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.strip() == "":
            continue
        lines.append(line)
    return lines


def run_c(c_source, name):
    src = TMP / (name + ".c")
    exe = TMP / name
    src.write_text(c_source, encoding="utf-8")
    p = run_cmd([C_COMPILER, "-std=c11", "-O2", "-Wall", "-Wextra", "-o", str(exe), str(src)])
    if p.returncode != 0:
        raise RuntimeError(f"[C:{name}] compile failed:\n{p.stderr}")
    r = run_cmd([str(exe)])
    if r.returncode != 0:
        raise RuntimeError(f"[C:{name}] runtime failed:\n{r.stderr}")
    return r.stdout


def run_cpp(cpp_source, name):
    src = TMP / (name + ".cpp")
    exe = TMP / (name + "_cpp")
    src.write_text(cpp_source, encoding="utf-8")
    p = run_cmd([CPP_COMPILER, "-std=c++17", "-O2", "-Wall", "-Wextra", "-o", str(exe), str(src)])
    if p.returncode != 0:
        raise RuntimeError(f"[C++:{name}] compile failed:\n{p.stderr}")
    r = run_cmd([str(exe)])
    if r.returncode != 0:
        raise RuntimeError(f"[C++:{name}] runtime failed:\n{r.stderr}")
    return r.stdout


def run_py(py_source, name):
    src = TMP / (name + ".py")
    src.write_text(py_source, encoding="utf-8")
    p = run_cmd([PYTHON, str(src)])
    if p.returncode != 0:
        raise RuntimeError(f"[Python:{name}] failed:\n{p.stderr}")
    return p.stdout


# ---------------------------------------------------------------------------
# Syntax highlighting (server-side, lightweight)
# ---------------------------------------------------------------------------

def highlight(code, lang):
    """Render C/C++/Python source with simple span-based highlighting."""
    if lang in ("c", "cpp"):
        keywords = set("""auto break case char const continue default do double else enum extern
        float for goto if inline int long register return short signed sizeof static struct
        switch typedef union unsigned void volatile while bool class constexpr namespace new
        operator private protected public template this using virtual malloc free""".split())
        comment = re.compile(r"//[^\n]*|/\*.*?\*/", re.S)
        string = re.compile(r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'')
        directive = re.compile(r"#[^\n]*")
    else:  # python
        keywords = set("""and as assert async await break class continue def del elif else
        except finally for from global if import in is lambda nonlocal not or pass raise
        return try while with yield True False None""".split())
        comment = re.compile(r"#[^\n]*")
        string = re.compile(
            r'"""(?:\\.|[^"\\])*?"""|\'\'\'(?:\\.|[^\'\\])*?\'\'\''
            r'|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\''
        )
        directive = None

    number = re.compile(r"\b0x[0-9A-Fa-f]+\b|\b\d+(?:\.\d+)?\b")
    ident = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")

    tokens = []
    pos = 0
    while pos < len(code):
        best = None
        if directive:
            m = directive.match(code, pos)
            if m:
                best = ("pre", m)
        if best is None:
            m = comment.match(code, pos)
            if m:
                best = ("cmt", m)
        if best is None:
            m = string.match(code, pos)
            if m:
                best = ("str", m)
        if best is None:
            m = number.match(code, pos)
            if m:
                best = ("num", m)
        if best is None:
            m = ident.match(code, pos)
            if m:
                best = ("kw", m) if m.group(0) in keywords else ("id", m)
        if best is None:
            tokens.append(("pln", code[pos]))
            pos += 1
            continue
        kind, m = best
        text = m.group(0)
        if kind == "pln":
            tokens.append(("pln", text))
        else:
            tokens.append((kind, text))
        pos = m.end()

    out = []
    for kind, text in tokens:
        if kind == "pln":
            out.append(html.escape(text, quote=False))
        else:
            out.append(f'<span class="tok-{kind}">{html.escape(text, quote=False)}</span>')
    return "".join(out)


def esc(text):
    return html.escape(text, quote=False)


# ---------------------------------------------------------------------------
# Topic verification
# ---------------------------------------------------------------------------

def verify_topic(topic):
    """Compile/run all three languages, assert identical results, and record
    the trace. Returns a dict of outputs + trace steps."""
    slug = topic["slug"]
    out_c = run_c(topic["impl_c"], slug)
    out_cpp = run_cpp(topic["impl_cpp"], slug)
    out_py = run_py(topic["impl_py"], slug)

    norm_c = normalize_output(out_c)
    norm_cpp = normalize_output(out_cpp)
    norm_py = normalize_output(out_py)

    if not (norm_c == norm_cpp == norm_py):
        raise RuntimeError(
            f"[{slug}] outputs differ across languages!\n"
            f"  C      : {norm_c}\n"
            f"  C++    : {norm_cpp}\n"
            f"  Python : {norm_py}\n"
        )

    steps = topic["sim"]()
    return {
        "output_c": out_c.rstrip(),
        "output_cpp": out_cpp.rstrip(),
        "output_py": out_py.rstrip(),
        "steps": steps,
        "norm": norm_c,
    }


# ---------------------------------------------------------------------------
# Rendering helpers (HTML snippets)
# ---------------------------------------------------------------------------

def bullets(items, cls="algo-list"):
    lis = "".join(f"<li>{esc(it)}</li>" for it in items)
    return f'<ul class="{cls}">{lis}</ul>'


def nav_html(active, base_prefix):
    """Build the shared site navigation. ``base_prefix`` is the relative path
    prefix from the current file to the ``pages/`` directory; for files inside
    ``pages/algorithms/`` that is ``../``, for files in ``pages/`` it is ````.
    ``active`` selects the highlighted nav item."""
    items = [
        ("index.html", "Home"),
        ("publications.html", "Publications"),
        ("courses.html", "Courses"),
        ("projects.html", "Projects"),
        ("about.html", "About"),
        ("algorithm.html", "Algorithms"),
        ("gre_vocab.html", "GRE Vocab"),
        ("gre_verbal_test.html", "Verbal Test"),
    ]
    links = []
    home = base_prefix + "index.html"
    links.append(f'<li><a href="{home}">Home</a></li>')
    for page, label in items[1:]:
        href = base_prefix + page
        cls = ' class="active"' if label == active else ""
        links.append(f'<li><a href="{href}"{cls}>{label}</a></li>')
    return "\n".join(links)


def complexity_table(topic):
    c = topic["complexity"]
    rows = [
        ("Best case", c["best"]),
        ("Average case", c["average"]),
        ("Worst case", c["worst"]),
        ("Space", c["space"]),
        ("Stable", c["stable"]),
        ("In-place", c["in_place"]),
    ]
    body = "".join(
        f"<tr><td>{esc(label)}</td><td>{esc(value)}</td></tr>" for label, value in rows
    )
    return f'<table class="algo-cx-table"><tbody>{body}</tbody></table>'


def applications_html(topic):
    cards = []
    for app in topic["applications"]:
        cards.append(
            f'<div class="card algo-app"><h4 class="algo-app-title">📌 {esc(app["title"])}</h4>'
            f'<p class="card-content" style="margin:0;">{esc(app["detail"])}</p></div>'
        )
    return "".join(cards)


def references_html(topic):
    refs = []
    for ref in topic["references"]:
        refs.append(
            f'<li><a href="{esc(ref["url"])}" target="_blank" rel="noopener">'
            f'{esc(ref["title"])} ↗</a></li>'
        )
    return "<ul class=\"algo-refs\">" + "".join(refs) + "</ul>"
def embed_json(obj):
    """JSON safe to inline inside <script> without breaking the tag."""
    return json.dumps(obj).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def render_topic_page(topic, ctx):
    """Render one full topic page (all 7 required sections)."""
    pri_color = ac.priority_color(topic["priority"])
    pri_label = ac.priority_label(topic["priority"])
    steps_json = embed_json(ctx["steps"])

    # --- prev / next navigation ---
    if ctx.get("prev"):
        p = ctx["prev"]
        prev_html = f'<a class="algo-prevnext" href="{p["slug"]}.html">← {esc(p["name"])}</a>'
    else:
        prev_html = '<span class="algo-prevnext disabled">← First</span>'
    if ctx.get("next"):
        n = ctx["next"]
        next_html = f'<a class="algo-prevnext" href="{n["slug"]}.html">{esc(n["name"])} →</a>'
    else:
        next_html = '<span class="algo-prevnext disabled">Last →</span>'

    breadcrumb = (
        '<div class="algo-breadcrumb">'
        '<a href="../algorithm.html">← All Algorithms</a>'
        '<span class="algo-pn">'
        f'{prev_html}<span class="algo-pn-sep"> · </span>{next_html}'
        '</span></div>'
    )

    hero = (
        '<section class="hero"><div class="container">'
        f'<div class="algo-hero-icon">{topic["icon"]}</div>'
        f'<h1>{esc(topic["name"])}</h1>'
        '<p class="subtitle">'
        f'{esc(topic["type_icon"])} {esc(topic["type_label"])} · '
        f'<span style="color:{pri_color};font-weight:600;">{esc(pri_label)}</span> · {esc(topic["difficulty"])}'
        '</p><div class="hero-stats" style="margin-top:0.5rem;">'
        f'<span class="stat-badge">Worst case {esc(topic["complexity"]["worst"])}</span>'
        f'<span class="stat-badge">Priority {topic["priority"]}/5</span>'
        '</div></div></section>'
    )

    section2_cards = (
        '<div class="grid grid-2" style="align-items:start;">'
        f'<div class="card"><h4 class="algo-sec-title">Why we need it</h4><p class="card-content">{esc(topic["why"])}</p></div>'
        f'<div class="card"><h4 class="algo-sec-title">When it is needed</h4>{bullets(topic["when_needed"])}</div>'
        f'<div class="card"><h4 class="algo-sec-title">How to select it</h4>{bullets(topic["how_to_select"])}</div>'
        f'<div class="card"><h4 class="algo-sec-title" style="color:#dc2626;">When NOT to use it</h4>{bullets(topic["when_not"])}</div>'
        '</div>'
    )

    sim_section = (
        '<p style="max-width:760px;">Watch this algorithm run. Use <strong>Step</strong> to advance one '
        'operation, <strong>▶ Play</strong> to animate, <strong>↺ Reset</strong> to restart, and the '
        'slider to change speed.</p>'
        '<div class="algo-sim" id="simApp">'
        '<div class="algo-sim-legend" id="simLegend" style="display:none;"></div>'
        '<div class="algo-sim-stage" id="simStage"></div>'
        '<div class="algo-sim-caption" id="simCaption">Press ▶ Play or click Step to begin.</div>'
        '<div class="algo-sim-controls">'
        '<button type="button" id="simPrev">⏮</button>'
        '<button type="button" id="simStep" class="btn">Step ▸</button>'
        '<button type="button" id="simPlay" class="btn btn-secondary">▶ Play</button>'
        '<button type="button" id="simReset" class="btn btn-secondary">↺ Reset</button>'
        '<span class="sim-counter">Step <span id="simCounter">0/0</span></span>'
        '<label class="sim-speed">Speed <input type="range" id="simSpeed" min="1" max="10" value="4"></label>'
        '</div></div>'
    )

    code_tabs = (
        '<div class="algo-tabs" id="implTabs">'
        '<button type="button" class="algo-tab active" data-lang="c">C</button>'
        '<button type="button" class="algo-tab" data-lang="cpp">C++</button>'
        '<button type="button" class="algo-tab" data-lang="py">Python</button>'
        '</div>'
        f'<div class="algo-code" id="codeC"><pre><code>{highlight(topic["impl_c"], "c")}</code></pre></div>'
        f'<div class="algo-code hidden" id="codeCpp"><pre><code>{highlight(topic["impl_cpp"], "cpp")}</code></pre></div>'
        f'<div class="algo-code hidden" id="codePy"><pre><code>{highlight(topic["impl_py"], "python")}</code></pre></div>'
    )

    output_c = esc(ctx["output_c"])
    output_cpp = esc(ctx["output_cpp"])
    output_py = esc(ctx["output_py"])
    test_result = (
        '<div class="algo-verdict">✓ <strong>Verified:</strong> the C, C++ and Python implementations above '
        'were compiled and run by the build pipeline, and all three produced identical output.</div>'
        '<div class="grid grid-3" style="align-items:start;">'
        f'<div><h4 class="algo-sec-title">C output (gcc)</h4><pre class="algo-out">{output_c}</pre></div>'
        f'<div><h4 class="algo-sec-title">C++ output (g++)</h4><pre class="algo-out">{output_cpp}</pre></div>'
        f'<div><h4 class="algo-sec-title">Python output</h4><pre class="algo-out">{output_py}</pre></div>'
        '</div>'
    )

    return breadcrumb, hero, section2_cards, sim_section, code_tabs, test_result
def assemble_topic_page(topic, ctx):
    """Assemble the full HTML document for a topic page."""
    breadcrumb, hero, section2, sim_section, code_tabs, test_result = render_topic_page(topic, ctx)
    first_sentence = topic["what"].split(".")[0]
    sections = (
        '<section class="section"><h2 class="section-title">1 · What is it?</h2>'
        f'<p class="algo-lead">{esc(topic["what"])}</p></section>'
        '<section class="section"><h2 class="section-title">2 · Why, When &amp; How to select</h2>'
        f'{section2}</section>'
        '<section class="section"><h2 class="section-title">3 · Complexity</h2>'
        f'{complexity_table(topic)}</section>'
        '<section class="section"><h2 class="section-title">4 · Simulation</h2>'
        f'{sim_section}</section>'
        '<section class="section"><h2 class="section-title">5 · Implementation (C / C++ / Python)</h2>'
        f'{code_tabs}</section>'
        '<section class="section"><h2 class="section-title">6 · Test Result</h2>'
        f'{test_result}</section>'
        '<section class="section"><h2 class="section-title">7 · Real-world applications</h2>'
        f'<div class="grid grid-2">{applications_html(topic)}</div></section>'
        '<section class="section"><h2 class="section-title">Further reading</h2>'
        '<p class="algo-note">References are plain citations for deeper study; all text and code on this '
        'page are original to this project.</p>'
        f'{references_html(topic)}</section>'
    )
    steps_json = embed_json(ctx["steps"])
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        '  <meta charset="UTF-8" />\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
        f'  <meta name="description" content="{esc(first_sentence)}" />\n'
        f'  <title>{esc(topic["name"])} | Algorithms &amp; Data Structures</title>\n'
        '  <link rel="stylesheet" href="../../style.css?v=2">\n'
        '  <link rel="stylesheet" href="../../assets/css/algorithm_topic.css?v=1">\n'
        "</head>\n<body>\n"
        '  <!-- Navigation -->\n  <nav class="nav">\n    <div class="container">\n'
        '      <a href="../../index.html" class="nav-brand">UKM</a>\n'
        '      <button class="menu-toggle" onclick="toggleMenu()">☰</button>\n'
        '      <ul class="nav-links" id="navLinks">\n'
        f'{nav_html("Algorithms", "../")}\n'
        "      </ul>\n    </div>\n  </nav>\n\n"
        "  <main>\n"
        f"    {hero}\n"
        '    <div class="container">\n'
        f"      {breadcrumb}\n"
        f"      {sections}\n"
        "    </div>\n  </main>\n\n"
        '  <footer>\n    <div class="container">\n'
        '      <p style="margin: 0;">© 2024 Uttam Kumar Mondol. All rights reserved.</p>\n'
        '      <p style="margin: 0.5rem 0 0; font-size: 0.875rem;">\n'
        '        <a href="https://github.com/uttamk94" style="color: var(--text-light);">GitHub</a> · \n'
        '        <a href="https://linkedin.com/in/uttamk94" style="color: var(--text-light);">LinkedIn</a> · \n'
        '        <a href="mailto:uttam.cuet@gmail.com" style="color: var(--text-light);">Email</a>\n'
        "      </p>\n    </div>\n  </footer>\n\n"
        f'  <script id="simData" type="application/json">{steps_json}</script>\n'
        '  <script src="../../assets/js/algo_sim.js"></script>\n'
        "  <script>\n"
        "    function toggleMenu() {\n"
        "      const navLinks = document.getElementById('navLinks');\n"
        "      navLinks.classList.toggle('active');\n"
        "    }\n"
        "    document.addEventListener('DOMContentLoaded', function () {\n"
        "      const tabs = document.getElementById('implTabs');\n"
        "      if (tabs) tabs.addEventListener('click', function (e) {\n"
        "        const btn = e.target.closest('.algo-tab');\n"
        "        if (!btn) return;\n"
        "        tabs.querySelectorAll('.algo-tab').forEach(function(b){ b.classList.remove('active'); });\n"
        "        btn.classList.add('active');\n"
        "        ['c','cpp','py'].forEach(function(l){\n"
        "          var id = l === 'py' ? 'codePy' : (l === 'c' ? 'codeC' : 'codeCpp');\n"
        "          var el = document.getElementById(id);\n"
        "          if (el) el.classList.toggle('hidden', l !== btn.dataset.lang);\n"
        "        });\n"
        "      });\n"
        "      if (window.AlgoSim) window.AlgoSim.init();\n"
        "    });\n"
        "    document.addEventListener('click', function(event) {\n"
        "      const nav = document.querySelector('.nav');\n"
        "      const navLinks = document.getElementById('navLinks');\n"
        "      if (!nav.contains(event.target) && navLinks.classList.contains('active')) {\n"
        "        navLinks.classList.remove('active');\n"
        "      }\n"
        "    });\n"
        "  </script>\n"
        "</body>\n</html>\n"
    )
# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------

def build_manifest(results):
    """Build the manifest consumed by the landing page's JS."""
    from datetime import datetime, timezone
    topics = []
    for topic in ac.TOPICS:
        ttype = ac.TYPES[topic["type"]]
        topics.append({
            "id": topic["id"],
            "name": topic["name"],
            "slug": topic["slug"],
            "type": topic["type"],
            "type_label": topic["type_label"],
            "type_icon": topic["type_icon"],
            "priority": topic["priority"],
            "priority_label": ac.priority_label(topic["priority"]),
            "difficulty": topic["difficulty"],
            "icon": topic["icon"],
            "worst_complexity": topic["complexity"]["worst"],
            "kind": topic["kind"],
            "outline": topic["outline"],
            "link": f"algorithms/{topic['slug']}.html",
        })
    types_out = {}
    for key, cfg in ac.TYPES.items():
        types_out[key] = {"label": cfg["label"], "icon": cfg["icon"], "blurb": cfg["blurb"]}
    return {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_topics": len(topics),
        "types": types_out,
        "topics": topics,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    OUT_PAGES.mkdir(parents=True, exist_ok=True)
    OUT_DATA.mkdir(parents=True, exist_ok=True)

    results = {}
    total = len(ac.TOPICS)
    failures = []

    print("=" * 64)
    print("Algorithms build — verify & generate")
    print("=" * 64)
    print(f"gcc      : {C_COMPILER}")
    print(f"g++      : {CPP_COMPILER}")
    print(f"python   : {PYTHON}")
    print(f"topics   : {total}")
    print("-" * 64)

    for idx, topic in enumerate(ac.TOPICS, 1):
        slug = topic["slug"]
        print(f"[{idx}/{total}] {topic['name']} ... ", end="", flush=True)
        try:
            result = verify_topic(topic)
            results[slug] = result
            print(f"OK ({len(result['norm'])} test lines, {len(result['steps'])} sim steps)")
        except Exception as exc:  # noqa: BLE001
            failures.append(str(exc))
            print("FAILED")
            print("   ", exc)

    if failures:
        print("-" * 64)
        print("BUILD FAILED — the following topics broke:")
        for f in failures:
            print("   ✗", f)
        sys.exit(1)

    # Generate topic pages + manifest
    manifest = build_manifest(results)
    n = len(ac.TOPICS)
    for i, topic in enumerate(ac.TOPICS):
        ctx = {
            "steps": results[topic["slug"]]["steps"],
            "output_c": results[topic["slug"]]["output_c"],
            "output_cpp": results[topic["slug"]]["output_cpp"],
            "output_py": results[topic["slug"]]["output_py"],
            "prev": ac.TOPICS[i - 1] if i > 0 else None,
            "next": ac.TOPICS[i + 1] if i < n - 1 else None,
        }
        html = assemble_topic_page(topic, ctx)
        (OUT_PAGES / f"{topic['slug']}.html").write_text(html, encoding="utf-8")

    manifest_path = OUT_DATA / "algos.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("-" * 64)
    print("Generated pages:")
    for t in ac.TOPICS:
        print(f"   pages/algorithms/{t['slug']}.html")
    print(f"   data/algorithms/algos.json")
    print(f"   {len(results)} topics verified and generated.")


if __name__ == "__main__":
    main()