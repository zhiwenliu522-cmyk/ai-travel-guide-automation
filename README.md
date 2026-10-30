# AI旅行攻略自动化定制系统

面向中文旅游定制业务的 Codex Agent 项目。系统把客户需求、历史成品、实时旅行信息和路线研究整合为可直接交付的图文 Word 攻略，并通过餐厅证据筛选、同城内容块复用和交付前审计降低人工返工。

## 核心能力

- 根据目的地、日期、同行人、体力、预算、酒店和到离时间生成逐日路线
- 优先读取同城市历史成品，复用经过确认的段落、图片与版式节奏
- 从抖音、小红书等可访问内容的评论中发现餐厅候选，结合目的地对应 IP 属地、独立评论与广告风险进行筛选
- 使用地图或商户官方信息复核准确分店、营业状态、营业时间和前后景点距离
- 默认制作可直接交付的图文 Word，覆盖预约、天气、交通、景点、餐饮、酒店和每日时间链
- 通过内容块复用合同和审计脚本检查“只借模板、不复用成品内容”等问题

## 工作流程

1. 收集客户需求并识别完整新攻略或局部修改模式
2. 查找同城成品，选择最相近主案例并建立内容块复用合同
3. 核查天气、预约、交通、营业状态等动态信息
4. 按每日动线研究餐厅候选，排除广告并核验准确分店
5. 生成图文 Word 客户成品
6. 完成时间、路线、餐厅、章节编号、图片和隐私检查
7. 渲染 Word 全页后再交付

## 项目结构

```text
.
├─ .agents/                         # Agent 入口说明
├─ .github/workflows/               # GitHub Actions 校验
├─ docs/                            # 架构、隐私与发布说明
├─ examples/                        # 安全示例占位，不含客户文件
├─ scripts/                         # 安装和项目校验脚本
└─ skills/customize-travel-guide/   # Codex Skill 本体
   ├─ SKILL.md
   ├─ agents/openai.yaml
   ├─ references/
   └─ scripts/reference_fidelity_audit.py
```

## 快速安装

Windows PowerShell：

```powershell
git clone <repository-url>
Set-Location .\AI旅行攻略自动化定制系统
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

安装完成后重启 Codex，然后使用类似请求：

```text
使用 $customize-travel-guide，根据客户需求制作一份可直接交付的五日图文 Word 攻略
```

如果 Codex 目录不在默认位置：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1 -CodexRoot "D:\path\to\.codex"
```

## 本地校验

```powershell
python -X utf8 .\scripts\validate_project.py
python -X utf8 .\skills\customize-travel-guide\scripts\reference_fidelity_audit.py --help
```

## 餐厅研究原则

平台 IP 属地只能作为一项辅助证据，不能单独证明评论者身份。候选门店需要跨独立帖子或账号获得有实质内容的评论支持，并继续进行广告风险、准确分店、营业状态和路线距离核验。系统不会绕过登录、验证码或平台访问限制，也不会在客户文档中展示评论用户名、头像、IP 或截图。

完整规则见 [餐厅研究规则](skills/customize-travel-guide/references/restaurant-research.md)。

## 数据与隐私

仓库不包含客户 Word、订单、个人账号截图、评论用户信息、酒店订单或历史工作目录。提交真实案例前，请先完成匿名化并确认拥有发布权限。详见 [隐私与数据边界](docs/PRIVACY.md)。

## 许可

当前项目未附开源许可证，默认保留全部权利。若计划公开开源，请在发布前选择并添加合适的许可证。


