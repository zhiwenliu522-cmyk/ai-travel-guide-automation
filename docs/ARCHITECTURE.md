# 系统架构

## 组件

### Agent 入口

`.agents/travel-guide-planner.md` 负责把旅游攻略任务路由到核心 Skill，并声明隐私和交付边界。

### 核心 Skill

`skills/customize-travel-guide/SKILL.md` 定义工作模式、优先级、制作流程、Word 输出和验证要求。

### 规则层

- `guide-standards.md`：客户成品、路线、交通、餐饮、图片和交付标准
- `restaurant-research.md`：本地评论证据、广告识别、地图核验和路线匹配
- `case-library.md`：历史成品选择与案例规律
- `template-profile.md`：版式和图文节奏
- `block-reuse-contract.md`：同城内容块复用合同

### 验证层

`reference_fidelity_audit.py` 对最终 Word 与同城参考文档进行段落、原句、图片和复用合同审计，防止只复制图片或样式而重写全部正文。

## 数据流

```text
客户需求
  → 工作模式与同城案例检查
  → 动态信息和餐厅证据研究
  → 路线与用餐窗口编排
  → 图文 Word 生成
  → 内容复用审计与逐页渲染
  → 客户成品
```

研究证据、来源链接和评论摘要属于内部制作记录；客户文档只保留经过提炼的可执行结论。

