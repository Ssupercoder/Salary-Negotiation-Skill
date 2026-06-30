# Salary Negotiation Skill · 谈薪助手

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Skill version](https://img.shields.io/badge/version-v1-blue.svg)](SKILL.md)

> 一个让 AI agent 化身"谈薪教练"的 OpenClaw / Claude Skills 指令文档。

针对**准备谈判、谈判中、拿到 offer 决策**这三种时刻,基于真实对话经验蒸馏出的可复用策略库 + 压力场景剧本 + 话术卡片输出模板。

---

## 特性

- 🎯 **5 阶段流程** —— 信息收集 → 策略制定 → 实战谈判 → 决策辅助 → 后续跟进
- 🧰 **4 个核心策略** —— 反问询价 / STAR 价值陈述 / 替代补偿 / Offer 锚定
- 🎭 **5 个压力场景剧本** —— 预算有限 / 锚定陷阱 / 压价试探 / 时间压力 / 职级压低
- 💬 **中文话术卡片输出** —— 一键复制,直接可用于真实对话
- 🛡️ **安全护栏** —— 不教唆虚构 offer / 恶意抬价 / 透露前雇主机密

---

## 快速开始

### 在 OpenClaw 中使用

将 `SKILL.md` 放到你的 workspace skills 目录:

```bash
mkdir -p ~/.openclaw/workspace/skills/salary-negotiation
cp SKILL.md ~/.openclaw/workspace/skills/salary-negotiation/
```

之后,在对话中提到"我要谈薪"、"HR 压我价"、"模拟一下面试"等关键词,agent 会自动加载本 skill。

### 在 Claude / 其他支持 Skills 协议的 agent 中使用

将 `SKILL.md` 放在 agent 能识别的 skills 路径下即可。具体路径参考你的 agent 文档。

### 直接阅读

`SKILL.md` 是纯 Markdown,可直接阅读。所有策略和场景都不依赖任何代码。

---

## 仓库结构

```
salary-negotiation-skill/
├── SKILL.md           # skill 主体(给 AI agent 消费的指令文档)
├── README.md          # 本文件(对外说明)
├── LICENSE            # MIT 许可证
├── examples/          # 实战案例库(社区贡献)
│   └── README.md
└── references/        # 原项目源码摘录(留作参考)
    └── original-strategies.py
```

---

## 核心机制预览

### 5 阶段状态机

| 阶段 | 干什么 | 进入条件 |
|---|---|---|
| P1 信息收集 | 收 4 个必要字段 | 用户开始谈薪咨询 |
| P2 策略制定 | 基于用户画像推荐策略组合 | P1 信息齐全 |
| P3 实战谈判 | 模拟 HR / 实战辅助话术 | 用户请求模拟或实战 |
| P4 决策辅助 | offer 横向对比 + 风险分析 | 用户拿到 offer |
| P5 后续跟进 | 接受/拒绝后续事项 | 用户做出决策 |

### 开场价算法

```
已知用户的期望上限 X
- 建议开场价: X × 1.12
- 底线:      X × 0.95
- 上限:      X × 1.20
```

详细策略和场景见 [`SKILL.md`](./SKILL.md)。

---

## 实战案例

社区贡献的真实案例,详见 [`examples/`](./examples/)。

---

## 知识来源 & 致谢

本 skill 的策略与场景知识蒸馏自 **[Ssupercoder/Salary-Negotiation-Skill](https://github.com/Ssupercoder/Salary-Negotiation-Skill)**。

原作者团队:
- **Lei Xin(辛磊)** — 快手科技
- **Zitong Wang(王梓同)** — 武汉大学
- **Hui Wang(王慧)**

原项目是一个基于 Qwen2.5-7B + vLLM 的独立 Python 服务,包含多模态输入、5 阶段状态机、RAG 知识库等完整工程实现。本仓库的 SKILL.md 把其中**对话策略 + 场景剧本**的知识蒸馏为通用 AI agent 指令形态,如果你需要完整的工程实现(包含 RAG / OCR / 语音 / FastAPI 服务),请直接参考原项目。

### 核心参考的源文件

- `strategies/negotiation_strategies.py` — 4 策略 + 5 场景(本仓库的 [`references/original-strategies.py`](./references/original-strategies.py) 是原文摘录)
- `models/state_machine.py` — 5 阶段流程定义
- `models/schema.py` — 用户元数据字段
- `config.py` — 系统配置参考

---

## 贡献

欢迎以 PR 形式补充:

- 📝 **实战案例** —— 在 `examples/` 下添加 `case-N-简短描述.md`,包含背景 / 策略 / 结果
- 🌐 **场景剧本** —— 在 `SKILL.md` 的"压力场景剧本"表格里追加新场景
- 🇨🇳 **话术本地化** —— 不同行业 / 不同地区的谈薪话术差异
- 🐛 **错误修正** —— 提 issue 或 PR

## License

MIT — 详见 [LICENSE](./LICENSE)。

---

> **免责声明**:本 skill 提供的是**通用策略与话术模板**,不构成法律 / 财务建议。实际 offer 决策请结合个人情况、市场行情、合同条款综合判断。