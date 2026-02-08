---
name: paper-formatter
description: Format academic manuscripts to match a target journal's style. Use when users provide a sample paper (范文) from a journal and want their manuscript reformatted to match. Supports Word (.docx) and LaTeX (.tex) input/output. Covers Chinese and English journals. Handles title/abstract formatting, heading styles, body text font/size/spacing, figure/table captions, reference/bibliography style, page layout (margins, columns, headers/footers), footnotes, and section numbering.
---

# Paper Formatter Skill

Reformat an academic manuscript to match the style of a target journal, based on a sample paper (范文).

## Workflow

### Step 1: Receive Inputs

Ask the user for:
1. **Sample paper (范文)**: A paper from the target journal that exemplifies its formatting. Can be `.docx` or `.tex`.
2. **User manuscript**: The manuscript to reformat. Can be `.docx`, `.tex`, or plain text.
3. **Desired output format**: `.docx` or `.tex` (default: same as manuscript format).

### Step 2: Analyze Sample Paper Style

**If sample is `.docx`:**

Run the analysis script:
```bash
pip install python-docx 2>/dev/null
python ~/.claude/skills/paper-formatter/scripts/analyze_docx.py "<sample.docx>" "<output_rules.json>"
```

This extracts:
- Page layout (margins, paper size, orientation, columns)
- Paragraph styles per role (title, headings, body, abstract, captions, references)
- Font families, sizes, bold/italic
- Line spacing, indentation, paragraph spacing
- Table styles
- Citation style detection (numeric, author-year, etc.)

**If sample is `.tex`:**

Read the `.tex` file and extract style information from the preamble:
- `\documentclass` options (font size, paper, columns)
- `\usepackage{geometry}` margins
- Font packages and settings (`fontspec`, `xeCJK`, `ctex`)
- `\usepackage{setspace}` line spacing
- `\titleformat` / `\titlesec` heading styles
- Citation package (`natbib`, `biblatex`) and style
- `\fancyhdr` header/footer settings
- Custom commands for title, abstract, keywords formatting

Produce a JSON style-rules object with the same structure as the docx analyzer output.

### Step 3: Present Extracted Style Rules

Show the user a summary of extracted formatting rules organized by the checklist in `references/formatting-elements.md`:

- **Page**: paper size, margins, orientation
- **Title**: font, size, bold, alignment
- **Authors/Affiliations**: format
- **Abstract**: font, size, indentation
- **Keywords**: separator, font
- **Headings**: each level's font, size, bold, numbering scheme
- **Body**: font, size, line spacing, first-line indent, alignment
- **Captions**: position, font, size
- **References**: citation style, bibliography format
- **Header/Footer**: content

Ask the user to **confirm or adjust** any rules before proceeding.

### Step 4: Parse User Manuscript

Read the user's manuscript and extract structured content:

```json
{
    "title": "...",
    "authors": ["..."],
    "affiliations": ["..."],
    "abstract": "...",
    "keywords": ["..."],
    "sections": [
        {
            "heading": "Introduction",
            "level": 1,
            "content": ["paragraph1...", "paragraph2..."],
            "subsections": [...]
        }
    ],
    "references": ["[1] ...", "[2] ..."],
    "acknowledgments": "...",
    "footnotes": ["..."]
}
```

**For `.docx` manuscripts**: use `python-docx` to read paragraphs, classify by style (similar to analyze_docx.py logic).

**For `.tex` manuscripts**: parse section commands (`\section`, `\subsection`), extract text between them, identify `\begin{abstract}`, `\bibliography`, etc.

**For plain text**: ask the user to identify sections or use heuristic detection (numbered headings, "Abstract:", "References" headers).

### Step 5: Apply Formatting

**If output is `.docx`:**

Save the structured content to a temporary JSON file, then run:
```bash
python ~/.claude/skills/paper-formatter/scripts/format_docx.py "<content.json>" "<style_rules.json>" "<output.docx>"
```

**If output is `.tex`:**

```bash
python ~/.claude/skills/paper-formatter/scripts/generate_latex.py "<content.json>" "<style_rules.json>" "<output.tex>"
```

### Step 6: Review & Iterate

After generating the output:
1. Tell the user the output file path
2. Ask them to review and identify any formatting issues
3. Adjust style rules or content structure as needed
4. Re-run the formatting script with updated inputs

## Important Notes

### Chinese Journal Support (中文期刊支持)

- Chinese font size names (字号) are mapped: 五号=10.5pt, 小四=12pt, etc.
- Common Chinese fonts: 宋体 (body), 黑体 (headings), 楷体 (abstract), 仿宋
- First-line indent: typically 2em (2 characters)
- Use `ctexart` document class for LaTeX output
- GB/T 7714-2015 citation format with document type identifiers [J], [M], [C], etc.
- Full-width punctuation handling

### Citation Styles

Refer to `references/common-citation-styles.md` for detailed formatting rules for:
- APA 7th, GB/T 7714-2015, Vancouver, IEEE, Chicago, MLA

### Formatting Checklist

Refer to `references/formatting-elements.md` for the complete list of formatting elements to check and apply.

### Dependencies

- `python-docx`: Required for .docx analysis and generation. Install with `pip install python-docx`.
- For LaTeX output: the generated .tex file requires XeLaTeX compilation (for font support).
- Chinese LaTeX documents require: `ctex`, `xeCJK` packages and appropriate Chinese fonts installed.
