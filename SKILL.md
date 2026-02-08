---
name: literature-review-writer
description: >
  顶刊论文文献综述（Literature Review）写作工具。根据用户提供的研究选题/研究问题，
  自动检索真实学术文献，核实文献真实性，并以顶级期刊（如AMJ, ASQ, SMJ, MISQ, OS, JCR, JMR等）
  的写作标准撰写文献综述部分。采用漏斗型结构，强调文献间的脉络关系、演进趋势和研究空白。
  当用户提到需要写文献综述/literature review、提供研究选题/研究方向/research topic，
  或要求以顶刊风格撰写综述时触发此skill。
  注意：本skill用于写作文献综述，不同于paper-analyzer（用于拆解已有论文）。
---

# 顶刊文献综述写作工具

## 核心定位

为用户提供的研究选题撰写符合顶级期刊标准的文献综述（Literature Review）部分。
区别于博士论文文献综述的百科全书式覆盖，顶刊文献综述以精炼、论证驱动、战略性选文为核心特征。

## 工作流程

撰写文献综述涉及以下步骤：

1. 解析研究选题，拆解核心构念与变量关系
2. 检索真实文献（WebSearch）
3. 核实文献真实性（参照 references/verification-guide.md）
4. 确定综述结构（参照 references/structure-patterns.md）
5. 撰写综述正文（参照 references/writing-techniques.md）
6. 输出完整文献综述及参考文献列表（对话输出 + 生成 Word 文档）

### 步骤1：解析研究选题

从用户提供的研究选题中识别：
- **核心自变量（IV）**和**因变量（DV）**
- **可能的中介变量（Mediator）**和**调节变量（Moderator）**
- **研究所在的学科领域与子领域**
- **可能适用的理论框架**

将选题拆解为3-5个需要综述的主题模块。

### 步骤2：检索真实文献

用 WebSearch 系统性搜索每个主题模块的文献。搜索策略：

**必须执行的搜索**：
- 每个核心构念：`"[构念]" site:scholar.google.com` 或 `"[构念]" review meta-analysis`
- 核心变量关系：`"[IV]" "[DV]" empirical study`
- 理论基础：`"[理论名]" "[研究领域]"`
- 顶刊定向搜索：`"[核心概念]" site:journals.sagepub.com OR site:onlinelibrary.wiley.com OR site:sciencedirect.com`

**文献筛选优先级**：
1. 近5年顶刊实证研究（最重要）
2. 领域奠基性文献（seminal works，不论年份）
3. 近期meta-analysis或系统综述
4. 高引用经典理论文献

**文献数量目标**：为每个主题模块找到5-10条高质量文献，总量控制在25-50条。

### 步骤3：核实文献真实性

**这是强制步骤，不可跳过。必须在撰写综述正文之前完成。**

**调用 `literature-verifier` skill**，将步骤2中检索到的所有拟引用文献提交核查。该 skill 能够：
- 交叉校验作者、标题、期刊、年份等元数据
- 检测AI幻觉生成的虚假文献
- 覆盖中英文数据库（Google Scholar、CNKI、万方、维普等）
- 验证DOI有效性

核查规则：
- **所有拟引用文献必须经过 `literature-verifier` 核查通过后方可使用**
- 核查未通过的文献立即移除，绝不引用
- 若移除后某主题模块文献不足，返回步骤2补充检索并再次核查

### 步骤4：确定综述结构

阅读 references/structure-patterns.md 选择合适的结构。

**默认使用漏斗型结构**（除非研究选题明确适合其他结构）：

```
第一层：宏观领域定位（1段）
第二层：核心构念的文献脉络（2-4段，按主题组织）
第三层：变量间关系的研究现状（1-3段）
第四层：研究空白与本文定位（1段）
```

### 步骤5：撰写综述正文

阅读 references/writing-techniques.md 获取写作技法指导。

**写作铁律**：
1. **主题式综合，非逐篇罗列**：每段围绕一个论点，综合多项研究支撑
2. **每段必须有明确的论证功能**：不写无目的的段落
3. **段落间用逻辑衔接句串联**：体现递进、转折或聚焦关系
4. **批判性评价嵌入论证**：指出方法、理论或实证覆盖上的局限
5. **文献脉络清晰可见**：呈现研究的演进趋势（开创→发展→前沿→空白）
6. **以研究空白收束**：明确指出gap，自然引出本文研究的必要性

**引用格式**：默认使用APA第7版。若用户指定其他格式，从之。

**语言**：
- 若用户用中文提供选题，用英文撰写综述（顶刊标准），除非用户明确要求中文
- 行文学术、精炼，避免口语化表达

### 步骤6：输出格式

#### 6a：对话输出

在对话中直接输出以下内容：

```
## Literature Review

[完整的文献综述正文，含嵌入式引用]

## References

[按APA 7th或用户指定格式列出所有引用文献的完整信息]
```

每条参考文献格式：
`Author, A. A., & Author, B. B. (Year). Title of article. Journal Name, Volume(Issue), Pages. https://doi.org/xxx`

#### 6b：生成 Word 文档

对话输出完成后，**必须**同时生成 Word 文档：

1. 将综述正文和参考文献列表写入一个临时 markdown 文件
2. 调用 `scripts/generate_docx.py` 生成 .docx 文件

**操作步骤**：

```bash
# 1. 将综述内容写入临时 md 文件
cat > /tmp/lit_review_temp.md << 'EOF'
[此处粘贴完整的综述 markdown 内容，包含 ## Literature Review 和 ## References]
EOF

# 2. 生成 Word 文档（输出到用户桌面）
python3 [skill_base_dir]/scripts/generate_docx.py \
  --input /tmp/lit_review_temp.md \
  --output ~/Desktop/Literature_Review.docx \
  --title "[论文标题]"
```

**Word 文档格式规范**：
- 正文：Times New Roman 12pt，双倍行距，首行缩进0.75cm
- 中文字体回退：宋体（正文）、黑体（标题）
- 参考文献：悬挂缩进1.27cm
- 页边距：上下左右各1英寸

**文件命名**：默认保存到 `~/Desktop/Literature_Review.docx`。若用户指定了路径，从之。

**脚本说明**：`scripts/generate_docx.py` 接受以下参数：
- `--input`：输入 markdown 文件路径（必需）
- `--output`：输出 .docx 文件路径（必需）
- `--title`：文档标题，居中加粗显示在文档顶部（可选）

## 质量检查清单

完成写作后，对照以下清单自检：
- [ ] 是否采用主题式组织而非逐篇罗列？
- [ ] 每段是否有明确的主题句？
- [ ] 段落之间是否有逻辑衔接？
- [ ] 是否呈现了文献的演进脉络？
- [ ] 是否综合了共识与分歧？
- [ ] 是否包含批判性评价？
- [ ] 是否明确识别了研究空白？
- [ ] 空白是否自然指向本文的研究必要性？
- [ ] 所有引用文献是否已核实真实性？
- [ ] 引文密度是否合理（每段5-12条）？
- [ ] 参考文献列表是否完整、格式一致？
- [ ] 是否已生成 Word 文档并告知用户文件路径？
