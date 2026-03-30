# /crawl - 爬取数据

## 目的

从知识星球爬取博主的精华文章和问答。

## 支持的数据源

| 数据源 | 内容类型 | 状态 |
|--------|----------|------|
| 知识星球 (zsxq) | 精华文章、问答 | ✅ 已实现 |
| 微信公众号 | 历史文章 | 🚧 规划中 |
| RSS订阅 | 文章 | 🚧 规划中 |

## 执行步骤

### Step 1: 检查环境

```bash
# 检查爬虫脚本是否存在
CRAWLER_PATH="~/Documents/My_Code_Projects/练习-demo/zsxq-crawler"
if [ ! -d "$CRAWLER_PATH" ]; then
  echo "错误：爬虫目录不存在"
  echo "请确保 zsxq-crawler 已安装"
  exit 1
fi

# 检查浏览器认证状态
# 知识星球需要登录态，通过 Playwright 保存的 cookies 实现
```

### Step 2: 执行爬取

```bash
# 进入爬虫目录
cd $CRAWLER_PATH

# 运行爬虫（示例：爬取重远投资观）
bun run crawler-complete.js \
  --group-id 1524888414515152 \
  --output-dir ~/Documents/My_Code_Projects/练习-demo/mind-distillation/cases/zhongyuan/data
```

### Step 3: 数据后处理

爬取完成后自动执行：

1. **URL解码**：处理 `%E6%88%91%E5%AF%B9...` 格式的编码
2. **HTML清理**：移除 `<e type="web" href="..." />` 标签
3. **格式标准化**：统一Markdown格式，添加YAML frontmatter

### Step 4: 生成爬取报告

```markdown
# 爬取完成报告

## 数据统计

| 类型 | 数量 | 来源 |
|------|------|------|
| 精华文章 | 103篇 | 知识星球精华区 |
| 问答 | 109条 | 知识星球问答区 |
| **总计** | **212条** | 重远投资观 |

## 数据质量

- 最短文章：500字
- 最长文章：8000字
- 平均字数：2000字

## 存储路径

- 文章：`cases/zhongyuan/data/articles/`
- 问答：`cases/zhongyuan/data/qa/`
```

## 已知问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 精华区内容为空 | 内容类型是`talk`不是`article` | 修改过滤条件 |
| 内容被截断 | 长文章有"展开更多"按钮 | 滚动时自动点击 |
| URL编码未解码 | 知识星球API返回编码格式 | 后处理脚本解码 |
| HTML标签残留 | 富文本内容包含自定义标签 | 正则替换清理 |

## 命令参数

```bash
/mind-distillation crawl --source zsxq --user zhongyuan --type all
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| --source | 数据源（zsxq/wechat/rss） | 必填 |
| --user | 博主标识 | 必填 |
| --type | 内容类型（articles/qa/all） | all |
| --limit | 最大爬取数量 | 不限制 |

## 输出结构

```
cases/{user}/data/
├── articles/
│   ├── 2026-03-27_第一个数据异常信号出现.md
│   ├── 2026-03-26_楼市小阳春前瞻.md
│   └── ...
├── qa/
│   ├── qa-001.md
│   ├── qa-002.md
│   └── ...
└── crawl-report.md
```