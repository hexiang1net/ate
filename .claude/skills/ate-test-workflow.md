---
name: ate-test-workflow
description: 访问 Google 并保存结果为 markdown 文件
type: skill
---

# ATE 测试工作流技能

## 用途

访问 https://www.google.com/ 并将页面内容保存为 markdown 文件。

## 操作流程

1. 使用 `WebFetch` 工具访问 `https://www.google.com/`
2. 将返回的内容写入一个 markdown 文件（如 `google-result.md`）
