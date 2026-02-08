#!/usr/bin/env python3
"""
Generate a formatted .tex file from manuscript content and style rules.

Usage:
    python generate_latex.py <content.json> <style_rules.json> <output.tex>

The content.json should follow the same structure as for format_docx.py.
The style rules JSON can come from analyze_docx.py or be manually crafted.

This script produces a compilable .tex file with appropriate preamble,
document class, packages, and formatting commands.
"""

import sys
import json
import re
from pathlib import Path


# Map common citation styles to BibLaTeX/natbib settings
CITATION_PACKAGES = {
    "numeric": {
        "package": "\\usepackage[numbers,sort&compress]{natbib}",
        "bibstyle": "unsrtnat",
    },
    "author-year": {
        "package": "\\usepackage[authoryear,round]{natbib}",
        "bibstyle": "plainnat",
    },
    "apa": {
        "package": "\\usepackage[style=apa,backend=biber]{biblatex}",
        "bibstyle": None,
    },
    "ieee": {
        "package": "\\usepackage[numbers]{natbib}",
        "bibstyle": "IEEEtranN",
    },
    "gb7714-numeric": {
        "package": "\\usepackage[style=gb7714-2015,backend=biber]{biblatex}",
        "bibstyle": None,
    },
    "gb7714-authoryear": {
        "package": "\\usepackage[style=gb7714-2015ay,backend=biber]{biblatex}",
        "bibstyle": None,
    },
    "vancouver": {
        "package": "\\usepackage[numbers,sort&compress]{natbib}",
        "bibstyle": "vancouver",
    },
}


def detect_chinese(text):
    """Check if text contains Chinese characters."""
    if not text:
        return False
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def has_chinese_content(content):
    """Check if the manuscript content contains Chinese."""
    texts = [
        content.get("title", ""),
        content.get("abstract", ""),
        " ".join(content.get("keywords", [])),
    ]
    for section in content.get("sections", []):
        texts.append(section.get("heading", ""))
        texts.extend(section.get("content", []))
    return any(detect_chinese(t) for t in texts)


def pt_to_latex_size(pt):
    """Convert point size to nearest standard LaTeX size command."""
    if pt is None:
        return None
    pt = float(pt)
    size_map = [
        (5, "\\tiny"),
        (7, "\\scriptsize"),
        (8, "\\footnotesize"),
        (9, "\\small"),
        (10, "\\normalsize"),
        (11, "\\normalsize"),
        (12, "\\large"),
        (14, "\\Large"),
        (17, "\\LARGE"),
        (20, "\\huge"),
        (25, "\\Huge"),
    ]
    closest = min(size_map, key=lambda x: abs(x[0] - pt))
    return closest[1]


def cm_to_latex(cm):
    """Format cm value for LaTeX."""
    if cm is None:
        return None
    return f"{cm}cm"


def escape_latex(text):
    """Escape special LaTeX characters."""
    if not text:
        return ""
    special = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    # Don't escape backslashes that are already LaTeX commands
    for char, replacement in special.items():
        text = text.replace(char, replacement)
    return text


def build_document_class(style_rules, is_chinese):
    """Determine document class and options."""
    layout = style_rules.get("page_layout", [{}])
    sec = layout[0] if isinstance(layout, list) and layout else layout

    # Base font size from body text
    para_fmt = style_rules.get("paragraph_formatting", {})
    body = para_fmt.get("body", {})
    sizes = body.get("font_sizes_pt", [12])
    base_size = int(sizes[0]) if sizes else 12
    # LaTeX only supports 10, 11, 12 as base
    if base_size <= 10:
        base_size = 10
    elif base_size <= 11:
        base_size = 11
    else:
        base_size = 12

    # Paper size
    paper = sec.get("paper_size", "A4").lower()
    paper_opt = "a4paper" if "a4" in paper else "letterpaper"

    # Two-column detection (from style rules if available)
    columns = sec.get("columns", 1)
    col_opt = "twocolumn" if columns == 2 else ""

    opts = [f"{base_size}pt", paper_opt]
    if col_opt:
        opts.append(col_opt)

    if is_chinese:
        return f"\\documentclass[{', '.join(opts)}]{{ctexart}}"
    else:
        return f"\\documentclass[{', '.join(opts)}]{{article}}"


def build_geometry(style_rules):
    """Build geometry package configuration."""
    layout = style_rules.get("page_layout", [{}])
    sec = layout[0] if isinstance(layout, list) and layout else layout
    margins = sec.get("margins", {})

    parts = []
    if margins.get("top_cm"):
        parts.append(f"top={margins['top_cm']}cm")
    if margins.get("bottom_cm"):
        parts.append(f"bottom={margins['bottom_cm']}cm")
    if margins.get("left_cm"):
        parts.append(f"left={margins['left_cm']}cm")
    if margins.get("right_cm"):
        parts.append(f"right={margins['right_cm']}cm")

    if not parts:
        parts = ["top=2.54cm", "bottom=2.54cm", "left=2.54cm", "right=2.54cm"]

    return f"\\usepackage[{', '.join(parts)}]{{geometry}}"


def build_font_config(style_rules, is_chinese):
    """Build font configuration."""
    lines = []
    lines.append("\\usepackage{fontspec}")

    para_fmt = style_rules.get("paragraph_formatting", {})
    body = para_fmt.get("body", {})
    font_names = body.get("font_names", [])

    # Main font
    main_font = None
    for fn in font_names:
        if not any("\u4e00" <= c <= "\u9fff" for c in fn):
            main_font = fn
            break
    if main_font:
        lines.append(f"\\setmainfont{{{main_font}}}")
    else:
        lines.append("\\setmainfont{Times New Roman}")

    if is_chinese:
        lines.append("\\usepackage{xeCJK}")
        # Find Chinese font
        cn_font = None
        for fn in font_names:
            if any("\u4e00" <= c <= "\u9fff" for c in fn):
                cn_font = fn
                break
        if cn_font:
            lines.append(f"\\setCJKmainfont{{{cn_font}}}")
        else:
            lines.append("% \\setCJKmainfont{SimSun}  % Uncomment and set appropriate Chinese font")

        # Heading fonts
        heading = para_fmt.get("heading_1", {})
        h_fonts = heading.get("font_names", [])
        cn_h_font = None
        for fn in h_fonts:
            if any("\u4e00" <= c <= "\u9fff" for c in fn):
                cn_h_font = fn
                break
        if cn_h_font:
            lines.append(f"\\setCJKsansfont{{{cn_h_font}}}")

    return "\n".join(lines)


def build_spacing_config(style_rules):
    """Build line spacing configuration."""
    lines = ["\\usepackage{setspace}"]

    para_fmt = style_rules.get("paragraph_formatting", {})
    body = para_fmt.get("body", {})
    spacing = body.get("line_spacing")

    if spacing:
        if isinstance(spacing, str) and spacing.endswith("pt"):
            pt_val = float(spacing.replace("pt", ""))
            # Convert exact pt spacing to baselineskip
            lines.append(f"\\setstretch{{1.0}}")
            lines.append(f"\\setlength{{\\baselineskip}}{{{pt_val}pt}}")
        else:
            try:
                val = float(spacing)
                if val <= 1.1:
                    lines.append("\\singlespacing")
                elif val <= 1.6:
                    lines.append("\\onehalfspacing")
                elif val <= 2.1:
                    lines.append("\\doublespacing")
                else:
                    lines.append(f"\\setstretch{{{val}}}")
            except (ValueError, TypeError):
                lines.append("\\onehalfspacing")

    return "\n".join(lines)


def build_heading_config(style_rules):
    """Build section heading formatting with titlesec."""
    lines = ["\\usepackage{titlesec}"]

    para_fmt = style_rules.get("paragraph_formatting", {})

    for level, cmd in [(1, "section"), (2, "subsection"), (3, "subsubsection")]:
        role = f"heading_{level}"
        fmt = para_fmt.get(role, {})

        sizes = fmt.get("font_sizes_pt", [])
        size_cmd = pt_to_latex_size(sizes[0]) if sizes else None
        bold = fmt.get("bold", True)
        align = fmt.get("alignment", "left")

        shape = "hang"
        if align == "center":
            shape = "block"

        font_spec = "\\bfseries" if bold else "\\normalfont"
        if fmt.get("italic"):
            font_spec += "\\itshape"
        if size_cmd:
            font_spec = f"{size_cmd}{font_spec}"

        before = fmt.get("space_before_pt", 12)
        after = fmt.get("space_after_pt", 6)

        align_cmd = ""
        if align == "center":
            align_cmd = "\\filcenter"

        lines.append(
            f"\\titleformat{{\\{cmd}}}"
            f"{{\\{font_spec.lstrip(chr(92))}}}"
            f"{{\\the{cmd}}}"
            f"{{1em}}"
            f"{{{align_cmd}}}"
        )
        lines.append(
            f"\\titlespacing*{{\\{cmd}}}{{0pt}}{{{before}pt}}{{{after}pt}}"
        )

    return "\n".join(lines)


def build_indent_config(style_rules, is_chinese):
    """Build paragraph indentation config."""
    lines = []
    para_fmt = style_rules.get("paragraph_formatting", {})
    body = para_fmt.get("body", {})
    indent = body.get("first_line_indent_cm")

    if indent and indent > 0:
        lines.append(f"\\setlength{{\\parindent}}{{{indent}cm}}")
    elif is_chinese:
        lines.append("\\setlength{\\parindent}{2em}")
    else:
        lines.append("\\setlength{\\parindent}{0.5in}")

    para_skip = body.get("space_after_pt")
    if para_skip and para_skip > 0:
        lines.append(f"\\setlength{{\\parskip}}{{{para_skip}pt}}")

    return "\n".join(lines)


def build_header_footer(style_rules):
    """Build header/footer configuration with fancyhdr."""
    lines = [
        "\\usepackage{fancyhdr}",
        "\\pagestyle{fancy}",
        "\\fancyhf{}",
    ]

    layout = style_rules.get("page_layout", [{}])
    sec = layout[0] if isinstance(layout, list) and layout else layout

    header_text = sec.get("header_text", "")
    footer_text = sec.get("footer_text", "")

    if header_text:
        lines.append(f"\\fancyhead[C]{{{escape_latex(header_text)}}}")
    if footer_text:
        lines.append(f"\\fancyfoot[C]{{{escape_latex(footer_text)}}}")
    else:
        lines.append("\\fancyfoot[C]{\\thepage}")

    lines.append("\\renewcommand{\\headrulewidth}{0.4pt}")

    return "\n".join(lines)


def render_section(section, level=1, number_prefix=""):
    """Render a section and its subsections to LaTeX."""
    lines = []
    heading = escape_latex(section.get("heading", ""))

    cmd_map = {1: "section", 2: "subsection", 3: "subsubsection", 4: "paragraph"}
    cmd = cmd_map.get(level, "paragraph")

    lines.append(f"\\{cmd}{{{heading}}}")
    lines.append("")

    for para in section.get("content", []):
        if para.strip():
            lines.append(escape_latex(para))
            lines.append("")

    for subsec in section.get("subsections", []):
        lines.extend(render_section(subsec, level + 1))

    return lines


def generate_latex(content, style_rules, output_path):
    """Generate a complete .tex file."""
    is_chinese = has_chinese_content(content)

    lines = []

    # Document class
    lines.append(build_document_class(style_rules, is_chinese))
    lines.append("")

    # Encoding and basic packages
    lines.append("% === Packages ===")
    lines.append(build_geometry(style_rules))
    lines.append(build_font_config(style_rules, is_chinese))
    lines.append(build_spacing_config(style_rules))
    lines.append("")
    lines.append("\\usepackage{graphicx}")
    lines.append("\\usepackage{booktabs}  % For three-line tables")
    lines.append("\\usepackage{amsmath,amssymb}")
    lines.append("\\usepackage{hyperref}")
    lines.append("\\usepackage{caption}")
    lines.append("")

    # Heading formatting
    lines.append("% === Heading Formatting ===")
    lines.append(build_heading_config(style_rules))
    lines.append("")

    # Header/footer
    lines.append("% === Header/Footer ===")
    lines.append(build_header_footer(style_rules))
    lines.append("")

    # Indentation
    lines.append("% === Paragraph Formatting ===")
    lines.append(build_indent_config(style_rules, is_chinese))
    lines.append("")

    # Citation package
    citation = style_rules.get("citation_style", {})
    detected = citation.get("detected_style", "")
    cit_key = None
    if "GB/T 7714" in detected or "gb7714" in detected.lower():
        if "author-year" in detected.lower():
            cit_key = "gb7714-authoryear"
        else:
            cit_key = "gb7714-numeric"
    elif "ieee" in detected.lower():
        cit_key = "ieee"
    elif "apa" in detected.lower():
        cit_key = "apa"
    elif "vancouver" in detected.lower():
        cit_key = "vancouver"
    elif "author-year" in detected.lower():
        cit_key = "author-year"
    elif "numeric" in detected.lower():
        cit_key = "numeric"

    if cit_key and cit_key in CITATION_PACKAGES:
        lines.append(f"% === Citation Style: {detected} ===")
        lines.append(CITATION_PACKAGES[cit_key]["package"])
    else:
        lines.append("% === Citation (default numeric) ===")
        lines.append("\\usepackage[numbers,sort&compress]{natbib}")
    lines.append("")

    # Begin document
    lines.append("\\begin{document}")
    lines.append("")

    # Title
    if content.get("title"):
        lines.append(f"\\title{{{escape_latex(content['title'])}}}")

    # Authors
    if content.get("authors"):
        authors_str = " \\and ".join(escape_latex(a) for a in content["authors"])
        lines.append(f"\\author{{{authors_str}}}")

    if content.get("title") or content.get("authors"):
        lines.append("\\maketitle")
        lines.append("")

    # Abstract
    if content.get("abstract"):
        lines.append("\\begin{abstract}")
        lines.append(escape_latex(content["abstract"]))
        lines.append("\\end{abstract}")
        lines.append("")

    # Keywords
    if content.get("keywords"):
        kw_label = "关键词" if is_chinese else "Keywords"
        kw_sep = "；" if is_chinese else "; "
        kw_text = kw_sep.join(escape_latex(k) for k in content["keywords"])
        lines.append(f"\\noindent\\textbf{{{kw_label}:}} {kw_text}")
        lines.append("")

    # Sections
    for section in content.get("sections", []):
        section_lines = render_section(section)
        lines.extend(section_lines)

    # Acknowledgments
    if content.get("acknowledgments"):
        ack_heading = "致谢" if is_chinese else "Acknowledgments"
        lines.append(f"\\section*{{{ack_heading}}}")
        lines.append(escape_latex(content["acknowledgments"]))
        lines.append("")

    # References
    if content.get("references"):
        ref_heading = "参考文献" if is_chinese else "References"
        lines.append(f"\\section*{{{ref_heading}}}")
        lines.append("\\begin{enumerate}")
        for ref in content["references"]:
            # Strip leading [N] if present
            ref_text = re.sub(r"^\[?\d+\]?\s*", "", ref)
            lines.append(f"  \\item {escape_latex(ref_text)}")
        lines.append("\\end{enumerate}")
        lines.append("")

    lines.append("\\end{document}")

    output_path = Path(output_path)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"LaTeX file saved to: {output_path}")


def main():
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <content.json> <style_rules.json> <output.tex>")
        sys.exit(1)

    content_path = Path(sys.argv[1])
    rules_path = Path(sys.argv[2])
    output_path = Path(sys.argv[3])

    with open(content_path, "r", encoding="utf-8") as f:
        content = json.load(f)

    with open(rules_path, "r", encoding="utf-8") as f:
        style_rules = json.load(f)

    generate_latex(content, style_rules, output_path)


if __name__ == "__main__":
    main()
