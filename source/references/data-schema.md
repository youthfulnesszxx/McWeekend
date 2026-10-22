# plan.json 字段说明

传给 `scripts/build.py --data` 的输入。全部必填，除非标注「可选」。

完整样例：`references/example-plan-guangzhou.json`。

## 顶层

| 字段 | 类型 | 说明 |
|---|---|---|
| `generatedAt` | string | 抓取时间，形如 `2026-10-22 20:40`。会显示在券卡提示里 |
| `docTitle` | string | 浏览器标题，`周末不无聊计划 · <城市> \| 麦当劳城市漫游手册` |
| `hero` | object | 首屏 |
| `order` | string[] | 片区顺序，元素必须在 `cities` 里存在 |
| `cityIntro` | string | 01 章节副标题，概括这几个片区的差异 |
| `cities` | object | key → 片区对象，key 用 `gz_th` 这类拼音缩写 |
| `cmpHead` | string | 对比图标题，如 `片区作息对比 · 通宵店占比与最晚闭店时间` |
| `priceNote` | object | 可选。同款不同价的洞察，`{k, p}` |
| `activity` | object | 活动时间线 |
| `burger` | object | 菜单拆解章节的价格参数 |
| `combo` | object | 随心配参数 |
| `coupons` | object[] | **至少 3 张，顺序固定** |
| `couponFence` | string | PRINCIPLE 06 的实测证据，可含 HTML |
| `pricing` | object | 券池计算的 6 个单价 |
| `planSub` | string | 方案表副标题 |
| `plans` | object[] | 方案表行，建议 6 行 |
| `planConclusion` | string | 方案表下方结论，可含 HTML |
| `source` | object | 页脚数据来源 |
| `sigLeft` / `sigRight` | string | 页脚签名左右两段 |

## hero

```json
{
  "kicker": "广州 · 天河 / 从化 · 10 家门店 · 10-22 抓取",
  "title": "周末不知道干嘛？<br>先跟着<em>麦麦</em>把这座城市走一遍。",
  "lede": "一份给大学生的周末行动手册：……",
  "stats": [{ "v": "10", "u": "家", "label": "2 个片区实测门店" }]
}
```

- `title` 可含 HTML，`<em>` 会被渲染成红色高亮 + 黄色下划线。
- `stats` 固定 4 个：门店数 / 随心配组合数 / 可领券数 / 地板价。

## cities.\<key\>

| 字段 | 类型 | 说明 |
|---|---|---|
| `name` | string | `广州 · 天河`，显示在选择 chip 和章节头 |
| `sub` | string | 一段话概括这个片区。会用在「想出门」方案里 |
| `stores` | object[] | 至少 5 家 |
| `insights` | object[] | 3 条洞察卡 |
| `route` | object | 想出门路线 `{t, steps}` |
| `escape` | object | 可选。想逃离方案，缺省时回落到 `route` |
| `note` | string | 路线下方的一句提醒，可为空字符串 |

### stores[]

```json
{
  "n": "麦当劳广州天源路餐厅",
  "a": "天源路 5 号",
  "tags": [["24 小时", "time"], ["华南植物园口", "hot"], ["华工 / 华农辐射区", ""]],
  "d": "134 m",
  "c": "1400359",
  "end": "24:00",
  "closed": false
}
```

- `tags` 每项是 `[文案, 样式]`，样式只能是 `time`（绿）/ `hot`（红）/ `off`（灰）/ `""`（默认）。
- `end` 必须是 `HH:MM` 或 `24:00`。**通宵店写 `24:00`** —— chip 上的「N 家通宵」和对比图的占比都由它算出来。
- `closed: true` 时该店不计入通宵统计和最晚闭店时间。

### insights[]

```json
{ "k": "24 小时店占比", "big": "4 / 5", "p": "五家里四家通宵。天河的夜晚有<b>地铁末班车</b>撑着……" }
```

- `big` 可选，给了就渲染成大号数字。
- `p` 可含 HTML。

### route

```json
{
  "t": "天河高校带 · 一天走完",
  "steps": [
    ["09:00", "华南植物园", "学生半价，园子大到能走三小时。"],
    ["12:30", "天源路店 · 1400359", "出园步行即到。点随心配 14.9。"]
  ]
}
```

`steps` 是四元组数组 `[时间, 地点, 一句话]`，**四个**。

### escape

```json
{
  "kick": "想逃离 · 从天河出城",
  "h": "往北 60 公里，去从化",
  "d": "一句话说明为什么这条线值得走",
  "steps": [{ "t": "08:00", "h": "远达广场店 1400692", "s": "七点开门，先吃完早餐再出发。" }],
  "money": "¥40–50<small>含往返车费，比待在天河多花 15 块</small>",
  "cta": { "href": "#city", "label": "切到从化，看 5 家店" },
  "switchCity": "gz_ch"
}
```

- `steps` 是对象数组（不是四元组），字段 `t` / `h` / `s`。
- `money` 的第一段会放大显示，`<small>` 里是补充说明。
- `switchCity` 可选，点了 CTA 会同时切换城市。**目标 key 必须存在于 `cities`**，否则自动忽略。

## activity

```json
{
  "sub": "10 月 22 日至 11 月 3 日，官方活动日历里能直接参与的",
  "items": [
    { "date": "10 / 22 今天", "today": true, "title": "……", "desc": "……", "price": "+¥39.9" }
  ],
  "term": { "b": "¥49 / 150 天", "s": "学生专属麦金学期卡：……" }
}
```

- 第一项设 `today: true` 会高亮。
- `term` 可选，是活动下方的绿色卡片。

## burger / combo / pricing

```json
"burger": { "price": 25.5, "craftCost": 20, "storeLabel": "无折扣 · 天河天源路店 1400359" },
"combo":  { "price": 14.9, "total": 96 },
"pricing": {
  "couponBurger": 11.9, "chicken2": 19.9, "set3": 33.5,
  "soloBurger": 22.5, "soloChicken": 15, "soloFries": 13.5
}
```

- `burger.price` 必须来自 `query-meals` 里巨无霸的实付价。
- `combo.price` 是随心配 1+1 的固定价，`total` 是组合数（8×12=96，除非菜单结构变了）。
- `pricing` 全部来自菜单：`couponBurger` 是堡券价，`chicken2` 是双人炸鸡券价，`set3` 是三件套价，后三个是单点价。

## coupons

```json
{ "amt": "11.9 元", "name": "麦辣鸡腿堡", "note": "单点约 ¥22.5，一张省 ¥10.6",
  "short": "11.9 麦辣鸡腿堡", "state": "可领取" }
```

顺序固定：`[0]` 堡券 → `[1]` 炸鸡/双人券 → `[2]` 免费小食券。券池计算和复制文案都按这个下标取。

## plans

```json
{ "name": "极简党", "tag": "最便宜的完整一餐",
  "combo": "随心配 1+1（双层吉士汉堡 + 可乐麦炫酷）+ 圆筒冰淇淋",
  "kcal": "669 kcal", "price": "¥19.9" }
```

## source

```json
{
  "body": "本页所有门店、菜单、价格、券、活动数据，均通过麦当劳 MCP 接口实时拉取：……",
  "codes": "门店编码 —— 天河：1400359 / ……。价格为抓取时刻的到店自取价。"
}
```

两段都允许 HTML（`<code>` 会被样式化）。
