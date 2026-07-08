<!-- SSOT：小红书 headline（标题）硬规则。被 ADR-0015 D4 定义、ADR-0016 D1 收敛为共享契约。
     引用方：prompts/compose_publish_xiaohongshu.md（monolithic 首发稿）
           prompts/compose_publish_xiaohongshu_headline.md（body-aware headline-only 重生成）
     改规则只改这一处，两处 prompt 经各自的注入占位符引用本文件，不再各写一份。 -->

## headline 硬规则（共享契约）

除正文外，另产一句**小红书笔记标题**：一句**描述这部电影、并勾住今天这条新闻**的创作型短语。

- **调性**：可比正文更凝练、更有画面 / 悬念；但仍守底线——**不用推荐 / 煽动词**（不容错过 / 催泪 / 必看 / 快去看）、**不剧透结局**、**不排名 / 不吹捧**、**不裸露字面片名**（片名由归属行承载，标题里不要直接写出片名）。
- 一句话，别写成两三句或带换行。
- **硬约束：≤ 10 个中文字（不含标点）。**