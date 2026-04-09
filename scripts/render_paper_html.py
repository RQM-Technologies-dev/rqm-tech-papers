#!/usr/bin/env python3
"""Render paper HTML pages from the authoritative LaTeX source.

This renderer is intentionally lightweight and only supports the subset of
LaTeX used by the papers in this repository. It turns `main.tex` into the
published `paper.html` page so the browsable HTML stays synchronized with the
source-of-truth paper text.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


THEOREM_ENVS = {"definition", "proposition", "lemma", "corollary", "remark", "example"}
BLOCK_ENVS = THEOREM_ENVS | {"proof", "enumerate", "itemize", "center", "equation", "figure", "table"}

ENV_LABELS = {
    "definition": "Definition",
    "proposition": "Proposition",
    "lemma": "Lemma",
    "corollary": "Corollary",
    "remark": "Remark",
    "example": "Example",
}

ENV_CLASSES = {
    "definition": "definition",
    "proposition": "proposition",
    "lemma": "proposition",
    "corollary": "proposition",
    "remark": "remark",
    "example": "definition",
}


def strip_comments(text: str) -> str:
    lines = []
    for line in text.splitlines():
        escaped = False
        pieces = []
        for ch in line:
            if ch == "%" and not escaped:
                break
            pieces.append(ch)
            escaped = ch == "\\"
            if ch != "\\":
                escaped = False
        lines.append("".join(pieces))
    return "\n".join(lines)


def parse_balanced_braces(text: str, open_index: int) -> tuple[str, int]:
    if open_index >= len(text) or text[open_index] != "{":
        raise ValueError(f"Expected '{{' at index {open_index}")
    depth = 0
    start = open_index + 1
    for index in range(open_index, len(text)):
        char = text[index]
        if char == "{" and (index == 0 or text[index - 1] != "\\"):
            depth += 1
        elif char == "}" and (index == 0 or text[index - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return text[start:index], index + 1
    raise ValueError("Unbalanced braces")


def extract_command_body(text: str, command: str) -> str:
    marker = f"\\{command}"
    start = text.find(marker)
    if start == -1:
        return ""
    brace_index = text.find("{", start)
    if brace_index == -1:
        return ""
    content, _ = parse_balanced_braces(text, brace_index)
    return content.strip()


def extract_first_environment(text: str, env_name: str) -> tuple[str, tuple[int, int]] | tuple[None, None]:
    start_marker = f"\\begin{{{env_name}}}"
    end_marker = f"\\end{{{env_name}}}"
    start = text.find(start_marker)
    if start == -1:
        return None, None
    end = text.find(end_marker, start)
    if end == -1:
        return None, None
    inner = text[start + len(start_marker) : end]
    return inner.strip(), (start, end + len(end_marker))


def normalize_ws(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def read_metadata(paper_dir: Path) -> dict:
    return json.loads((paper_dir / "metadata.json").read_text(encoding="utf-8"))


def extract_existing_blocks(paper_dir: Path) -> tuple[list[str], str]:
    paper_html = paper_dir / "paper.html"
    if not paper_html.exists():
        return [], ""
    text = paper_html.read_text(encoding="utf-8")
    figures = re.findall(r"<figure>.*?</figure>", text, flags=re.DOTALL)
    refs_match = re.search(r"<ol class=\"refs\">.*?</ol>", text, flags=re.DOTALL)
    return figures, refs_match.group(0) if refs_match else ""


def extract_macros(preamble: str) -> dict[str, object]:
    macros: dict[str, object] = {}
    for raw_line in preamble.splitlines():
        line = raw_line.strip()
        if not line.startswith("\\newcommand"):
            continue
        match = re.match(r"\\newcommand\{\\([A-Za-z]+)\}(?:\[(\d+)\])?\{(.*)\}\s*$", line)
        if not match:
            continue
        name, argc, definition = match.groups()
        if argc:
            macros[name] = [definition, int(argc)]
        else:
            macros[name] = definition
    return macros


def citation_index_map(metadata: dict) -> dict[str, int]:
    return {key: index + 1 for index, key in enumerate(metadata.get("citations", []))}


def render_citation(keys: str, ref_numbers: dict[str, int]) -> str:
    rendered = []
    for key in [item.strip() for item in keys.split(",") if item.strip()]:
        label = ref_numbers.get(key)
        if label is None:
            rendered.append(html.escape(key))
        else:
            rendered.append(f'<a href="#ref-{html.escape(key)}">[{label}]</a>')
    return ", ".join(rendered)


def transform_non_math(text: str, ref_numbers: dict[str, int]) -> str:
    text = text.replace("~", " ")

    def repl_cite(match: re.Match[str]) -> str:
        return render_citation(match.group(1), ref_numbers)

    text = re.sub(r"\\cite[t|p]?\{([^}]+)\}", repl_cite, text)
    text = re.sub(r"\\eqref\{([^}]+)\}", lambda m: f'(<a href="#{html.escape(m.group(1))}">{html.escape(m.group(1))}</a>)', text)
    text = re.sub(r"\\ref\{([^}]+)\}", lambda m: f'<a href="#{html.escape(m.group(1))}">{html.escape(m.group(1))}</a>', text)
    text = text.replace("\\noindent", "")

    output: list[str] = []
    index = 0
    while index < len(text):
        for command, open_tag, close_tag in (
            ("texttt", "<code>", "</code>"),
            ("textbf", "<strong>", "</strong>"),
            ("emph", "<em>", "</em>"),
        ):
            marker = f"\\{command}{{"
            if text.startswith(marker, index):
                content, next_index = parse_balanced_braces(text, index + len(command) + 1)
                output.append(open_tag + transform_non_math(content, ref_numbers) + close_tag)
                index = next_index
                break
        else:
            if text.startswith("\\\\", index):
                output.append("<br />")
                index += 2
            elif text.startswith("\\%", index):
                output.append("%")
                index += 2
            elif text.startswith("\\&", index):
                output.append("&amp;")
                index += 2
            elif text.startswith("\\_", index):
                output.append("_")
                index += 2
            elif text[index] in "{}":
                index += 1
            else:
                output.append(html.escape(text[index]))
                index += 1
    return "".join(output)


def render_inline_text(text: str, ref_numbers: dict[str, int]) -> str:
    text = expand_texorpdfstring(text.replace("~", " "))
    text = text.replace("\\noindent", "")

    def render_segment(segment: str) -> str:
        output: list[str] = []
        index = 0
        while index < len(segment):
            if segment.startswith("\\cite", index):
                brace_index = segment.find("{", index)
                if brace_index != -1:
                    cite_content, next_index = parse_balanced_braces(segment, brace_index)
                    output.append(render_citation(cite_content, ref_numbers))
                    index = next_index
                    continue
            if segment.startswith("\\eqref{", index):
                label, next_index = parse_balanced_braces(segment, index + len("\\eqref"))
                output.append(f'(<a href="#{html.escape(label)}">{html.escape(label)}</a>)')
                index = next_index
                continue
            if segment.startswith("\\ref{", index):
                label, next_index = parse_balanced_braces(segment, index + len("\\ref"))
                output.append(f'<a href="#{html.escape(label)}">{html.escape(label)}</a>')
                index = next_index
                continue
            for command, open_tag, close_tag in (
                ("texttt", "<code>", "</code>"),
                ("textbf", "<strong>", "</strong>"),
                ("emph", "<em>", "</em>"),
            ):
                marker = f"\\{command}{{"
                if segment.startswith(marker, index):
                    content, next_index = parse_balanced_braces(segment, index + len(marker) - 1)
                    output.append(open_tag + render_segment(content) + close_tag)
                    index = next_index
                    break
            else:
                if segment.startswith("\\\\", index):
                    output.append("<br />")
                    index += 2
                elif segment.startswith("\\%", index):
                    output.append("%")
                    index += 2
                elif segment.startswith("\\&", index):
                    output.append("&amp;")
                    index += 2
                elif segment.startswith("\\_", index):
                    output.append("_")
                    index += 2
                elif segment[index] == "$" and (index == 0 or segment[index - 1] != "\\"):
                    end = index + 1
                    while end < len(segment):
                        if segment[end] == "$" and segment[end - 1] != "\\":
                            break
                        end += 1
                    math_content = segment[index + 1 : end]
                    output.append(r"\(" + math_content.strip() + r"\)")
                    index = end + 1
                elif segment[index] in "{}":
                    index += 1
                else:
                    output.append(html.escape(segment[index]))
                    index += 1
        return "".join(output)

    return render_segment(text).strip()


def latex_title_to_html(title: str, ref_numbers: dict[str, int]) -> str:
    return render_inline_text(title, ref_numbers)


def author_first_line(author: str) -> str:
    first = author.split("\\\\", 1)[0]
    first = re.sub(r"\\[A-Za-z]+\{([^}]*)\}", r"\1", first)
    return normalize_ws(first)


def format_date(date_text: str) -> str:
    return normalize_ws(date_text.replace("Date", ""))


def strip_braces(value: str) -> str:
    cleaned = re.sub(r"\\[A-Za-z]+\{([^}]*)\}", r"\1", value)
    cleaned = cleaned.replace("\\\\", " ")
    cleaned = re.sub(r"\$([^$]+)\$", r"\1", cleaned)
    return normalize_ws(cleaned)


def expand_texorpdfstring(text: str) -> str:
    marker = "\\texorpdfstring"
    while marker in text:
        start = text.find(marker)
        first_open = text.find("{", start)
        if first_open == -1:
            break
        first_arg, after_first = parse_balanced_braces(text, first_open)
        if after_first >= len(text) or text[after_first] != "{":
            break
        _, after_second = parse_balanced_braces(text, after_first)
        text = text[:start] + first_arg + text[after_second:]
    return text


def list_type_from_options(options: str) -> str | None:
    if "\\roman*" in options:
        return "i"
    if "\\alph*" in options:
        return "a"
    if "\\arabic*" in options:
        return "1"
    return None


def extract_env_name(line: str) -> tuple[str, str]:
    match = re.match(r"\\begin\{([A-Za-z*]+)\}(?:\[(.*)\])?", line.strip())
    if not match:
        raise ValueError(f"Unsupported environment line: {line}")
    return match.group(1), match.group(2) or ""


def consume_environment(lines: list[str], start_index: int, env_name: str) -> tuple[list[str], int]:
    content: list[str] = []
    depth = 0
    index = start_index
    start_marker = f"\\begin{{{env_name}}}"
    end_marker = f"\\end{{{env_name}}}"
    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped.startswith(start_marker):
            depth += 1
            if depth > 1:
                content.append(line)
        elif stripped == end_marker:
            depth -= 1
            if depth == 0:
                return content, index + 1
            content.append(line)
        else:
            content.append(line)
        index += 1
    raise ValueError(f"Environment {env_name} was not closed")


def split_top_level_items(lines: list[str]) -> list[list[str]]:
    items: list[list[str]] = []
    current: list[str] = []
    depth = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("\\begin{") and not stripped.startswith("\\begin{itemize}") and not stripped.startswith("\\begin{enumerate}"):
            depth += 1
        elif stripped.startswith("\\end{") and not stripped.startswith("\\end{itemize}") and not stripped.startswith("\\end{enumerate}"):
            depth = max(0, depth - 1)
        if stripped.startswith("\\item") and depth == 0:
            if current:
                items.append(current)
            current = [stripped[5:].strip()]
        else:
            current.append(line)
    if current:
        items.append(current)
    return [item for item in items if any(part.strip() for part in item)]


def parse_tabular(lines: list[str], ref_numbers: dict[str, int]) -> str:
    rows: list[list[str]] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line in {"\\toprule", "\\midrule", "\\bottomrule"}:
            continue
        if line.endswith("\\\\"):
            line = line[:-2].strip()
        cells = [render_inline_text(cell.strip(), ref_numbers) for cell in line.split("&")]
        rows.append(cells)
    if not rows:
        return ""
    head, *body = rows
    output = ["<table>", "<thead><tr>"]
    output.extend(f"<th>{cell}</th>" for cell in head)
    output.append("</tr></thead>")
    if body:
        output.append("<tbody>")
        for row in body:
            output.append("<tr>")
            output.extend(f"<td>{cell}</td>" for cell in row)
            output.append("</tr>")
        output.append("</tbody>")
    output.append("</table>")
    return "".join(output)


@dataclass
class RenderState:
    ref_numbers: dict[str, int]
    figure_blocks: list[str]
    appendix_mode: bool = False
    section_number: int = 0
    appendix_number: int = -1
    subsection_number: int = 0
    theorem_counter: int = 0

    @property
    def section_label(self) -> str:
        if self.appendix_mode:
            return chr(ord("A") + self.appendix_number)
        return str(self.section_number)

    def next_section_heading(self, title: str) -> str:
        self.theorem_counter = 0
        self.subsection_number = 0
        if self.appendix_mode:
            self.appendix_number += 1
            return f"Appendix {self.section_label}. {title}"
        self.section_number += 1
        return f"{self.section_label}. {title}"

    def next_subsection_heading(self, title: str) -> str:
        self.subsection_number += 1
        return f"{self.section_label}.{self.subsection_number} {title}"

    def next_theorem_label(self, env_name: str, optional_title: str) -> str:
        self.theorem_counter += 1
        label = f"{ENV_LABELS[env_name]} {self.section_label}.{self.theorem_counter}."
        if optional_title:
            return f"{label} {optional_title}."
        return label


class LatexPaperRenderer:
    def __init__(self, state: RenderState) -> None:
        self.state = state

    def render_blocks(self, lines: list[str]) -> str:
        output: list[str] = []
        paragraph: list[str] = []
        index = 0

        def flush_paragraph() -> None:
            nonlocal paragraph
            if not paragraph:
                return
            text = normalize_ws(" ".join(line.strip() for line in paragraph if line.strip()))
            if text:
                output.append(f"<p>{render_inline_text(text, self.state.ref_numbers)}</p>")
            paragraph = []

        while index < len(lines):
            line = lines[index]
            stripped = line.strip()
            if not stripped:
                flush_paragraph()
                index += 1
                continue

            if stripped == "\\appendix":
                flush_paragraph()
                self.state.appendix_mode = True
                index += 1
                continue

            if stripped == "\\clearpage":
                flush_paragraph()
                index += 1
                continue

            section_match = re.match(r"\\section\{(.*)\}", stripped)
            if section_match:
                flush_paragraph()
                heading = self.state.next_section_heading(expand_texorpdfstring(section_match.group(1)))
                output.append(f"<h2>{render_inline_text(heading, self.state.ref_numbers)}</h2>")
                index += 1
                continue

            subsection_match = re.match(r"\\subsection\{(.*)\}", stripped)
            if subsection_match:
                flush_paragraph()
                output.append(
                    f"<h3>{render_inline_text(self.state.next_subsection_heading(expand_texorpdfstring(subsection_match.group(1))), self.state.ref_numbers)}</h3>"
                )
                index += 1
                continue

            if stripped == "\\[":
                flush_paragraph()
                math_lines = []
                index += 1
                while index < len(lines) and lines[index].strip() != "\\]":
                    math_lines.append(lines[index].rstrip())
                    index += 1
                output.append(self.render_display_math("\n".join(math_lines).strip()))
                index += 1
                continue

            if stripped.startswith("\\begin{"):
                flush_paragraph()
                env_name, env_options = extract_env_name(stripped)
                if env_name not in BLOCK_ENVS and env_name != "tabular":
                    paragraph.append(line)
                    index += 1
                    continue
                if env_name == "tabular":
                    env_lines, index = consume_environment(lines, index, env_name)
                    output.append(parse_tabular(env_lines, self.state.ref_numbers))
                    continue
                env_lines, index = consume_environment(lines, index, env_name)
                output.append(self.render_environment(env_name, env_options, env_lines))
                continue

            paragraph.append(line)
            index += 1

        flush_paragraph()
        return "\n".join(fragment for fragment in output if fragment)

    def render_display_math(self, expression: str, label: str = "") -> str:
        block = rf"\[{expression}\]"
        identifier = f' id="{html.escape(label)}"' if label else ""
        return f'<div class="display"{identifier}>{block}</div>'

    def render_environment(self, env_name: str, env_options: str, env_lines: list[str]) -> str:
        if env_name in THEOREM_ENVS:
            label = self.state.next_theorem_label(env_name, env_options)
            inner = self.render_blocks(env_lines)
            return f'<div class="env {ENV_CLASSES[env_name]}"><strong>{render_inline_text(label, self.state.ref_numbers)}</strong>{inner}</div>'

        if env_name == "proof":
            inner = self.render_blocks(env_lines)
            return f'<div class="proof">{inner}</div>'

        if env_name in {"enumerate", "itemize"}:
            return self.render_list(env_name, env_options, env_lines)

        if env_name == "center":
            return self.render_blocks(env_lines)

        if env_name == "equation":
            label = ""
            math_lines = []
            for raw_line in env_lines:
                stripped = raw_line.strip()
                label_match = re.match(r"\\label\{([^}]+)\}", stripped)
                if label_match:
                    label = label_match.group(1)
                elif stripped:
                    math_lines.append(raw_line.rstrip())
            return self.render_display_math("\n".join(math_lines).strip(), label=label)

        if env_name == "figure":
            return self.render_figure(env_lines)

        if env_name == "table":
            return self.render_table(env_lines)

        return ""

    def render_list(self, env_name: str, env_options: str, env_lines: list[str]) -> str:
        items = split_top_level_items(env_lines)
        tag = "ul" if env_name == "itemize" else "ol"
        type_attr = ""
        if tag == "ol":
            list_type = list_type_from_options(env_options)
            if list_type:
                type_attr = f' type="{list_type}"'
        rendered_items = []
        for item in items:
            rendered_items.append(f"<li>{self.render_blocks(item)}</li>")
        return f"<{tag}{type_attr}>" + "".join(rendered_items) + f"</{tag}>"

    def render_figure(self, env_lines: list[str]) -> str:
        if self.state.figure_blocks:
            return self.state.figure_blocks.pop(0)
        caption = ""
        for raw_line in env_lines:
            stripped = raw_line.strip()
            if stripped.startswith("\\caption{"):
                caption = strip_braces(extract_command_body(stripped, "caption"))
                break
        if not caption:
            return ""
        safe_caption = render_inline_text(caption, self.state.ref_numbers)
        return f"<figure><figcaption>{safe_caption}</figcaption></figure>"

    def render_table(self, env_lines: list[str]) -> str:
        caption = ""
        label = ""
        tabular_html = ""
        index = 0
        while index < len(env_lines):
            stripped = env_lines[index].strip()
            if not stripped or stripped == r"\centering":
                index += 1
                continue
            if stripped.startswith(r"\caption{"):
                command_text = "\n".join(env_lines[index:])
                command_start = command_text.find(r"\caption")
                brace_index = command_text.find("{", command_start)
                if brace_index != -1:
                    caption_body, consumed = parse_balanced_braces(command_text, brace_index)
                    caption = strip_braces(caption_body)
                    command_consumed = command_text[:consumed].count("\n") + 1
                    index += command_consumed
                    continue
                index += 1
                continue
            label_match = re.match(r"\\label\{([^}]+)\}", stripped)
            if label_match:
                label = label_match.group(1)
                index += 1
                continue
            if stripped.startswith(r"\begin{tabular}"):
                tabular_lines, index = consume_environment(env_lines, index, "tabular")
                tabular_html = parse_tabular(tabular_lines, self.state.ref_numbers)
                continue
            index += 1

        if not tabular_html:
            return ""

        identifier = f' id="{html.escape(label)}"' if label else ""
        caption_html = f"<figcaption>{render_inline_text(caption, self.state.ref_numbers)}</figcaption>" if caption else ""
        return f"<figure{identifier}>{tabular_html}{caption_html}</figure>"


def extract_body(tex_source: str) -> str:
    start_marker = "\\begin{document}"
    end_marker = "\\end{document}"
    start = tex_source.find(start_marker)
    end = tex_source.rfind(end_marker)
    if start == -1 or end == -1:
        raise ValueError("Could not locate document body")
    return tex_source[start + len(start_marker) : end]


def remove_front_matter(body: str) -> tuple[str, str, str]:
    abstract, abstract_span = extract_first_environment(body, "abstract")
    if abstract_span:
        body = body[: abstract_span[0]] + body[abstract_span[1] :]

    keywords = ""
    keywords_match = re.search(r"\\noindent\\textbf\{Keywords:\}\s*(.+)", body)
    if keywords_match:
        keywords = keywords_match.group(1).strip()
        start, end = keywords_match.span()
        body = body[:start] + body[end:]

    body = body.replace("\\maketitle", "")
    return body, abstract or "", keywords


def trim_back_matter(body: str) -> str:
    cutoff_markers = ["\\bibliographystyle", "\\bibliography"]
    cutoffs = [body.find(marker) for marker in cutoff_markers if body.find(marker) != -1]
    if not cutoffs:
        return body
    return body[: min(cutoffs)]


def build_mathjax_config(macros: dict[str, object]) -> str:
    config = {
        "tex": {
            "inlineMath": [["\\(", "\\)"]],
            "displayMath": [["\\[", "\\]"]],
            "macros": macros,
            "processEscapes": True,
        },
        "options": {"skipHtmlTags": ["script", "noscript", "style", "textarea", "pre", "code"]},
    }
    return (
        "<script>\n"
        f"window.MathJax = {json.dumps(config, indent=2)};\n"
        "</script>\n"
        '<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>'
    )


def companion_links(paper_id: str) -> str:
    base = f"/papers/{paper_id}"
    return (
        f'<a href="{base}/">package index</a>, '
        f'<a href="{base}/main.tex">main.tex</a>, '
        f'<a href="{base}/paper.pdf">paper.pdf</a>, '
        f'<a href="{base}/metadata.json">metadata.json</a>, '
        f'<a href="{base}/paper.jats.xml">paper.jats.xml</a>, '
        f'<a href="{base}/claims.json">claims.json</a>, '
        f'<a href="{base}/notation.json">notation.json</a>, '
        f'<a href="{base}/glossary.json">glossary.json</a>, '
        f'<a href="{base}/references.bib">references.bib</a>, '
        f'<a href="{base}/CITATION.cff">CITATION.cff</a>'
    )


def render_depends_on(depends_on: Iterable[str]) -> str:
    links = [f'<a href="/papers/{paper_id}/">{paper_id}</a>' for paper_id in depends_on]
    return ", ".join(links)


def references_html(existing_refs: str) -> str:
    if existing_refs:
        return existing_refs
    return '<ol class="refs"><li>References are available in <a href="references.bib">references.bib</a>.</li></ol>'


def render_fragment_blocks(text: str, ref_numbers: dict[str, int]) -> str:
    state = RenderState(ref_numbers=ref_numbers, figure_blocks=[])
    renderer = LatexPaperRenderer(state)
    return renderer.render_blocks(text.splitlines())


def render_paper_html(paper_dir: Path) -> str:
    metadata = read_metadata(paper_dir)
    raw_tex = strip_comments((paper_dir / "main.tex").read_text(encoding="utf-8"))
    preamble = raw_tex.split("\\begin{document}", 1)[0]
    title_tex = extract_command_body(preamble, "title")
    author_tex = extract_command_body(preamble, "author")
    date_tex = extract_command_body(preamble, "date")
    mathjax = build_mathjax_config(extract_macros(preamble))

    body = extract_body(raw_tex)
    body, abstract_tex, keywords_tex = remove_front_matter(body)
    body = trim_back_matter(body)

    figure_blocks, existing_refs = extract_existing_blocks(paper_dir)
    state = RenderState(
        ref_numbers=citation_index_map(metadata),
        figure_blocks=figure_blocks,
    )
    renderer = LatexPaperRenderer(state)
    main_html = renderer.render_blocks(body.splitlines())

    paper_id = metadata["paper_id"]
    visible_title = latex_title_to_html(title_tex or metadata["title"], state.ref_numbers)
    meta_title = metadata["title"]
    meta_author = author_first_line(author_tex) or "John G. Van Geem"
    abstract_html = render_fragment_blocks(abstract_tex or metadata.get("abstract", ""), state.ref_numbers)
    author_html = render_inline_text(author_tex, state.ref_numbers)
    keywords = metadata.get("keywords") or [strip_braces(keywords_tex)]
    keywords_text = "; ".join(keywords)
    depends_html = ""
    if metadata.get("depends_on"):
        depends_html = f'<div><strong>Depends on:</strong> {render_depends_on(metadata["depends_on"])}</div>'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(meta_title)}</title>
  <meta name="description" content="{html.escape(metadata.get("abstract", ""))}" />
  <meta name="author" content="{html.escape(meta_author)}" />
  <meta name="keywords" content="{html.escape(", ".join(keywords))}" />
  <meta name="citation_title" content="{html.escape(meta_title)}" />
  <meta name="citation_author" content="{html.escape(meta_author)}" />
  <meta name="citation_pdf_url" content="paper.pdf" />
  <link rel="alternate" type="application/json" href="metadata.json" title="Paper metadata" />
  <link rel="alternate" type="application/xml" href="paper.jats.xml" title="JATS XML" />
  <link rel="stylesheet" href="../../styles/site.css" />
  {mathjax}
</head>
<body class="paper-page">
  <div class="page-shell">
    <header class="paper-shell">
      <nav class="breadcrumb" aria-label="Breadcrumb">
        <a href="../../index.html">Home</a>
        <span>/</span>
        <a href="/papers/{html.escape(paper_id)}/">{html.escape(paper_id)}</a>
        <span>/</span>
        <span aria-current="page">paper.html</span>
      </nav>
      <div class="badge">{html.escape(metadata.get("series", "RQM Technologies Technical Papers"))} · Paper {metadata.get("series_number", "?")}</div>
      <h1>{visible_title}</h1>
      <p class="byline">{author_html}</p>

      <div class="abstract">
        <strong>Abstract</strong>
        {abstract_html}
      </div>

      <div class="meta">
        <div><strong>Paper ID:</strong> {html.escape(paper_id)} · <strong>Version:</strong> {html.escape(metadata.get("version", ""))} · <strong>Status:</strong> {html.escape(metadata.get("status", ""))} · <strong>Last updated:</strong> {html.escape(metadata.get("last_updated", format_date(date_tex)))}</div>
        {depends_html}
        <div><strong>Keywords:</strong> {html.escape(keywords_text)}</div>
        <div><strong>Companion files:</strong> {companion_links(paper_id)}</div>
      </div>
    </header>

    <main class="paper-shell">
      {main_html}

      <h2>References</h2>
      {references_html(existing_refs)}
    </main>

    <footer class="paper-shell">
      <p>{html.escape(paper_id)} · version {html.escape(metadata.get("version", ""))} · {html.escape(metadata.get("status", ""))} · license: <a href="https://creativecommons.org/licenses/by/4.0/">CC BY 4.0</a></p>
      <p><a href="/papers/{html.escape(paper_id)}/">Package page</a> · <a href="/papers/{html.escape(paper_id)}/main.tex">LaTeX source</a> · <a href="/papers/{html.escape(paper_id)}/paper.pdf">PDF</a> · <a href="/papers/{html.escape(paper_id)}/metadata.json">metadata</a> · <a href="/papers/{html.escape(paper_id)}/paper.jats.xml">JATS XML</a></p>
    </footer>
  </div>
</body>
</html>
"""


def render_index_links(index_html: str, paper_id: str) -> str:
    base = f"/papers/{paper_id}"
    replacements = {
        'href="./paper.html"': f'href="{base}/paper.html"',
        'href="./paper.pdf"': f'href="{base}/paper.pdf"',
        'href="./main.tex"': f'href="{base}/main.tex"',
        'href="./metadata.json"': f'href="{base}/metadata.json"',
        'href="./paper.jats.xml"': f'href="{base}/paper.jats.xml"',
        'href="./claims.json"': f'href="{base}/claims.json"',
        'href="./notation.json"': f'href="{base}/notation.json"',
        'href="./glossary.json"': f'href="{base}/glossary.json"',
        'href="./references.bib"': f'href="{base}/references.bib"',
        'href="./CITATION.cff"': f'href="{base}/CITATION.cff"',
        'href="./README.md"': f'href="{base}/README.md"',
        'href="./artifacts/figures/"': f'href="{base}/artifacts/figures/"',
        'href="./artifacts/notebooks/"': f'href="{base}/artifacts/notebooks/"',
        'href="./artifacts/code/"': f'href="{base}/artifacts/code/"',
    }
    for old, new in replacements.items():
        index_html = index_html.replace(old, new)
    return index_html


def render_template_index_links(template_index: str) -> str:
    replacements = {
        'href="paper.html"': 'href="/papers/SERIES-NNN-slug/paper.html"',
        'href="paper.pdf"': 'href="/papers/SERIES-NNN-slug/paper.pdf"',
        'href="main.tex"': 'href="/papers/SERIES-NNN-slug/main.tex"',
        'href="metadata.json"': 'href="/papers/SERIES-NNN-slug/metadata.json"',
        'href="paper.jats.xml"': 'href="/papers/SERIES-NNN-slug/paper.jats.xml"',
        'href="claims.json"': 'href="/papers/SERIES-NNN-slug/claims.json"',
        'href="notation.json"': 'href="/papers/SERIES-NNN-slug/notation.json"',
        'href="glossary.json"': 'href="/papers/SERIES-NNN-slug/glossary.json"',
        'href="references.bib"': 'href="/papers/SERIES-NNN-slug/references.bib"',
        'href="CITATION.cff"': 'href="/papers/SERIES-NNN-slug/CITATION.cff"',
        'href="README.md"': 'href="/papers/SERIES-NNN-slug/README.md"',
        'href="artifacts/figures/"': 'href="/papers/SERIES-NNN-slug/artifacts/figures/"',
        'href="artifacts/notebooks/"': 'href="/papers/SERIES-NNN-slug/artifacts/notebooks/"',
        'href="artifacts/code/"': 'href="/papers/SERIES-NNN-slug/artifacts/code/"',
    }
    for old, new in replacements.items():
        template_index = template_index.replace(old, new)
    return template_index


def update_package_indexes(root: Path) -> None:
    for paper_dir in sorted((root / "papers").iterdir()):
        if not paper_dir.is_dir():
            continue
        index_path = paper_dir / "index.html"
        metadata_path = paper_dir / "metadata.json"
        if not index_path.exists() or not metadata_path.exists():
            continue
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        updated = render_index_links(index_path.read_text(encoding="utf-8"), metadata["paper_id"])
        index_path.write_text(updated, encoding="utf-8")

    template_index = root / "templates" / "index.html"
    if template_index.exists():
        template_index.write_text(
            render_template_index_links(template_index.read_text(encoding="utf-8")),
            encoding="utf-8",
        )


def render_all(root: Path, selected: list[Path] | None = None) -> None:
    paper_dirs = selected or sorted(
        paper_dir
        for paper_dir in (root / "papers").iterdir()
        if paper_dir.is_dir() and (paper_dir / "main.tex").exists() and (paper_dir / "metadata.json").exists()
    )
    for paper_dir in paper_dirs:
        (paper_dir / "paper.html").write_text(render_paper_html(paper_dir), encoding="utf-8")
    update_package_indexes(root)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render HTML papers from main.tex.")
    parser.add_argument(
        "paper_dirs",
        nargs="*",
        type=Path,
        help="Optional paper directories to render. Defaults to all papers.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parent.parent
    selected = [path.resolve() if not path.is_absolute() else path for path in args.paper_dirs] or None
    render_all(root, selected)


if __name__ == "__main__":
    main()
