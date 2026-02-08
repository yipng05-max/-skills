# Paper Formatter — Claude Code Skill

一个用于学术论文排版的 [Claude Code](https://claude.ai/claude-code) Skill。提供范文（样本论文），自动提取排版规则并将你的稿件重新格式化为目标期刊样式。

A Claude Code skill that reformats academic manuscripts to match a target journal's style based on a sample paper.

## Features

- **Docx & LaTeX support**: Input/output both `.docx` and `.tex` formats
- **Chinese & English journals**: Full support for 中文期刊 (宋体/黑体/楷体, 字号, 2em缩进, GB/T 7714) and English journals
- **Automated style extraction**: Analyzes sample papers to extract page layout, fonts, spacing, heading styles, citation format, etc.
- **Comprehensive formatting**: Title, abstract, keywords, headings (4 levels), body text, figures, tables, references, footnotes, headers/footers

## File Structure

```
paper-formatter/
├── SKILL.md                              # Main skill definition (Claude Code reads this)
├── scripts/
│   ├── analyze_docx.py                   # Extract formatting rules from .docx sample
│   ├── format_docx.py                    # Generate formatted .docx from content + rules
│   └── generate_latex.py                 # Generate formatted .tex from content + rules
└── references/
    ├── formatting-elements.md            # Checklist of all formatting elements
    └── common-citation-styles.md         # APA, GB/T 7714, Vancouver, IEEE, Chicago, MLA
```

## Installation

Copy the `paper-formatter` directory to your Claude Code skills folder:

```bash
cp -r paper-formatter ~/.claude/skills/paper-formatter
```

### Dependencies

```bash
pip install python-docx
```

## Usage

In Claude Code, provide:
1. A sample paper (范文) from the target journal (`.docx` or `.pdf`)
2. Your manuscript (`.docx` or `.tex`)
3. Desired output format

Example prompt:
```
请参考这篇《社会学研究》的论文 sample.pdf，对我的稿件 manuscript.docx 进行排版，输出为 PDF。
```

Claude will:
1. Analyze the sample paper's formatting
2. Show you the extracted style rules for confirmation
3. Reformat your manuscript
4. Output the formatted file

## Scripts (Standalone Usage)

### analyze_docx.py

Extract formatting rules from a .docx file:
```bash
python scripts/analyze_docx.py sample.docx rules.json
```

### format_docx.py

Generate a formatted .docx:
```bash
python scripts/format_docx.py content.json rules.json output.docx
```

### generate_latex.py

Generate a formatted .tex:
```bash
python scripts/generate_latex.py content.json rules.json output.tex
```

## Supported Formatting Elements

| Category | Elements |
|----------|----------|
| Page Layout | Paper size, margins, orientation, columns, headers/footers |
| Title Block | Title, subtitle, authors, affiliations |
| Abstract | Label (摘要/Abstract), body, structured abstract |
| Keywords | Separator style, font |
| Headings | 4 levels, Chinese/Arabic/Roman numbering |
| Body Text | Font, size, line spacing, first-line indent, alignment |
| Figures & Tables | Caption format, three-line tables (三线表) |
| References | 7 citation styles (APA, GB/T 7714, Vancouver, IEEE, Chicago, MLA) |
| Chinese-specific | 字号 mapping, 中英文混排, 全角标点 |

## License

MIT
