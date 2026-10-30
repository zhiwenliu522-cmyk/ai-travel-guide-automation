# 同城成品内容块复用合同

只在“完整新攻略 + 存在同城成品参考”时使用。本合同是制作过程中的内部文件，不进入客户 Word，也不替代动态信息核验。

## 先建立行程槽位

在写正文和改 Word 前，按实际游玩顺序列出每天的槽位，例如：

`D1-景点一 → D1-午餐 → D1-景点二 → D1-晚餐 → D1-返程`

预约说明、天气、景点介绍也分别建立槽位。不要先写新文案再回头找参考。

## 选择主案例与内容块

1. 完整读取全部同城成品，按交通方式、天数、同行人、核心景点、酒店片区、天气/季节和游玩类型选一份最相似主案例；文件时间不参与优先排序。
2. 从主案例副本开始工作。主案例缺少某个槽位时，再从其他同城案例选择补充块。
3. 内容块从一个有导航意义的标题、预约项或时间段开始，包含其后的适用原文、内部路线、相关图片、紧邻餐厅推荐和必要 `Tips：`，到下一个独立槽位开始前结束。
4. 匹配内容块时，景点和路线方向优先，其次比较同行人、交通、天气/季节、当天前后顺序和作息。找到条件相近的原块后，整块复制，不只拿图片或零散句子。

## 允许与禁止的修改

允许修改的字段只有：

- `date`：日期；
- `time`：时间与停留时长；
- `hotel`：酒店、起点和终点；
- `transport`：本次交通方式、线路、方向、车程和缓冲；
- `weather`：本次天气、温度和携带建议；
- `reservation`：最新预约入口、场次、票价、开放规则和证件要求；
- `business_status`：餐厅或酒店的营业、位置和当前适配性；
- `user_requirement`：用户本次明确提出的差异。

除上述字段外，原句逐字保留。预约句、景点介绍、内部路线、餐厅推荐、菜品和 `Tips：`都适用同一规则。不为换一种说法、统一措辞或展示写作能力而改写；内容块之间只补最短过渡。

禁止清空主案例正文后重建所有段落，禁止只继承样式、主题或图片。所有同城案例都没有覆盖的槽位才允许原创，并记录原因。

## 内部 JSON

在任务工作目录保存 `reference-reuse-contract.json`：

```json
{
  "mode": "full_new_guide",
  "primary_reference": "C:/path/to/同城成品.docx",
  "selection": {
    "transport": "地铁为主",
    "days": 4,
    "travelers": "老人和儿童同行",
    "core_attractions": ["景点一", "景点二"],
    "hotel_area": "市中心",
    "weather_season": "夏季晴热",
    "reason": "交通、同行人与核心景点最接近"
  },
  "outline": ["D1-景点一", "D1-午餐", "D1-景点二"],
  "blocks": [
    {
      "slot": "D1-景点一",
      "source_doc": "C:/path/to/同城成品.docx",
      "source_locator": "8月1日 09:30 景点一 至下一时间标题前",
      "source_images": ["景点一正文图1"],
      "reuse": "adapted",
      "allowed_changes": ["date", "time", "transport"],
      "reason": "日期、酒店起点和交通不同"
    },
    {
      "slot": "D1-午餐",
      "source_doc": "C:/path/to/同城成品.docx",
      "source_locator": "景点一后的午餐推荐段",
      "source_images": [],
      "reuse": "verbatim",
      "allowed_changes": [],
      "reason": ""
    }
  ]
}
```

`reuse`只能是：

- `verbatim`：整块原样复用，不修改文字；
- `adapted`：仅修改白名单字段，必须写明原因；
- `new`：同城案例没有覆盖，`source_doc`和`source_locator`写 `null`，必须写明原创原因。

每个 `outline` 槽位必须在 `blocks` 中出现一次。多个同城来源可以并用，但全文视觉样式服从主案例。

## 交付前门槛

1. 逐槽位确认：匹配块保留了可识别原句、相关原图和紧邻餐饮/`Tips：`。
2. 对 `adapted` 块做文字对照，确认改动全部属于白名单；无必要修改的句子逐字相同。
3. 运行：

```bash
python <本 Skill 目录>/scripts/reference_fidelity_audit.py --reference 主案例.docx --reference 补充案例.docx --output 最终攻略.docx --contract reference-reuse-contract.json
```

如果审计提示“复用了同城图片但没有任何完整同城段落保持不变”，或合同中的复用槽位缺少足够的原段落/原句命中，必须返工，不能交付。
