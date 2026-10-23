# 工具适配参考

> Phase 1 探查到笔记工具后，按需读取对应章节。Phase 5 生成 wiki-management skill 时，根据工具类型调整链接语法和集成方式。

---

## Obsidian

```yaml
wikilink: "[[path|name]]"
mcp: obsidian (全局 MCP)
vault_path: ~/Documents/Obsidian Vault/
schema_path: .claude/WIKI_SCHEMA.md
wiki_path: wiki/
link_syntax: double-bracket
graph_view: supported
```

**wiki-management 调整**：
- 页面间链接使用 `[[path|name]]` 双括号语法
- 提及 Obsidian Graph View 用于可视化知识关联
- 如果有 Obsidian MCP，说明如何通过 MCP 直接读写页面
- 索引页维护 Obsidian Dataview 兼容的 frontmatter

---

## Logseq

```yaml
wikilink: "[[page name]]"
mcp: none (文件操作)
vault_path: ~/Documents/Logseq/
schema_path: .claude/WIKI_SCHEMA.md
wiki_path: wiki/
link_syntax: double-bracket
naming: "page title.md" (not Page Title.md)
```

**wiki-management 调整**：
- 页面间链接使用 `[[page name]]` 双括号语法
- 遵循 Logseq 命名约定：文件名小写连字符，页面标题保留原格式
- 不支持 MCP，所有操作通过文件系统
- 说明 Logseq 的块引用 `((block-id))` 供参考

---

## 纯文件夹

```yaml
wikilink: "[text](relative/path.md)"
mcp: none
vault_path: 用户指定路径
schema_path: .claude/WIKI_SCHEMA.md
wiki_path: wiki/
link_syntax: standard-markdown
```

**wiki-management 调整**：
- 页面间链接使用 Markdown 标准 `[text](relative/path.md)` 语法
- 所有操作通过文件系统
- 说明：链接路径相对于 wiki/ 根目录

---

## Notion

```yaml
wikilink: "@page name" 或标准 markdown 链接
mcp: notion (如已配置)
vault_path: N/A (Notion workspace)
schema_path: .claude/WIKI_SCHEMA.md (存放于工作目录)
wiki_path: wiki/ (存放于工作目录)
link_syntax: 根据 MCP 能力
note: >
  Notion 用户需额外配置 notion MCP。
  Wiki 层文件存储在工作目录下，内容通过 MCP 与 Notion 双向同步。
```

**wiki-management 调整**：
- 说明当前 Notion 集成的局限性
- 链接语法取决于 MCP 能力（通常为 Markdown 链接或 `@mention` 格式）
- Wiki 文件系统层面使用标准 Markdown，Notion 同步通过 MCP 桥接
