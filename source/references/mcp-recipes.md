# MCP 调用配方

到店自取场景（beType=1）下，除 `query-nearby-stores` 外**都不传 beCode**。以下所有调用都基于这个前提。

## 1. now-time-info

无参数。返回服务器当前时间，用来确定「今天」是哪天、活动日历里哪一项该标 `today`。

## 2. query-nearby-stores

```json
{ "beType": 1, "searchType": 2, "city": "广州市", "keyword": "天河" }
```

- `searchType=1` 查收藏店，通常为空 —— **必须用 2**。
- `city` 带「市」更稳：`广州市`、`北京市`、`成都市`。
- `keyword` 用商圈 / 地标 / 大学 / 地铁站名。用行政区名会召回无关门店。
- 每个片区取前 5 家，按返回顺序（通常按距离）。

返回里要注意的字段：

| 字段 | 用途 |
|---|---|
| `storeCode` | 后续所有调用的门店编码 |
| `storeName` / `storeAddress` | 写进 `stores[].n` / `.a` |
| `businessStatus` | `false` → `closed: true`，tags 标「当前暂停营业」 |
| 营业时间字段 | 取结束时间写进 `stores[].end`，`24:00` 表示通宵 |
| 距离 | 写进 `stores[].d`，形如 `134 m` / `1.7 km` |
| `reservation` / `reservationTimeOptions` | 有宵夜时段时可以写进 insight（如「22:14–22:46 是这条街最后的营业窗口」） |

## 3. query-meals

```json
{ "storeCode": "1400359", "orderType": 1, "beType": 1 }
```

拿真实菜单价。需要从返回里挑出这几个商品的价格：

- 巨无霸（写 `burger.price`）
- 麦辣鸡腿堡三件套（写 `pricing.set3`）
- 麦辣鸡腿堡单点（写 `pricing.soloBurger`）
- 脆汁鸡 / 炸鸡单点（写 `pricing.soloChicken`）
- 中薯条（写 `pricing.soloFries`）
- 随心配 1+1（写 `combo.price`）
- 顺手记下几个做方案表的商品价：圆筒、麦香鸡、麦咖啡、麦旋风、香芋派

**同一个商品在不同门店价格可能不同**，两个片区各查一次，把差异写进 `priceNote`。注意找双向例子（有贵的也有便宜的），否则结论会失真。

## 4. query-meal-detail

```json
{ "storeCode": "1400359", "orderType": 1, "beType": 1, "code": "1100" }
```

三个固定 code：

| code | 商品 | 用来做什么 |
|---|---|---|
| `1100` | 巨无霸 | 取 `modification` 里的可特调项，写「接口返回的可特调项只有五个」 |
| `521952` | 龙焰鸡腿堡 | 同上，写「只有辣酱和切块生菜」 |
| `9900013304` | 随心配 1+1 | 取蓝区 / 粉区商品数，算组合总数 |

组合总数 = 蓝区数 × 粉区数。当前是 8 × 12 = 96，写进 `combo.total`。

## 5. available-coupons

无参数。返回可领券列表。

**这是 `coupons[]` 的唯一来源**，按顺序取前三张：

- `coupons[0]` 堡券（如 11.9 麦辣鸡腿堡）→ `pricing.couponBurger`
- `coupons[1]` 双人 / 炸鸡券（如 19.9 王牌炸鸡任选 2）→ `pricing.chicken2`
- `coupons[2]` 免费小食券（如 免费脆薯饼）

券面金额从返回里读，不要照抄示例里的 11.9 / 19.9 —— 会变。

## 6. query-my-coupons

无参数。返回**卡包里已有**的券。

和 `available-coupons` 是两回事：前者是「可领」，后者是「已有」。卡包为空是常态，如实写。

## 7. query-store-coupons

```json
{ "storeCode": "1400359", "orderType": 1, "beType": 1 }
```

查该店真正可用的券。返回空是常见情况，**这本身就是最好的素材** —— 写进 `couponFence`：

> 实测：可领 3 张券，但 `query-store-coupons` 在天源路店返回空 —— 卡包里没有可用资产

## 8. campaign-calendar

无参数。返回当月活动，含订阅状态。取日期 / 标题 / 描述 / 价格写进 `activity.items`。

## 9. calculate-price

```json
{
  "storeCode": "1400359", "orderType": 1, "beType": 1,
  "items": [{ "productCode": "521952", "quantity": 1 }]
}
```

用来验证：

- 单点 3 件的原价与实付差（写 PRINCIPLE 01 的「系统自己给你减了 ¥X」）
- 三件套实付价（`pricing.set3`）
- 券池拼单的实际总价

**返回价格单位是分**，展示前除以 100。

## 10. list-nutrition-foods

无参数。返回餐品营养成分。巨无霸的 513 kcal / 钠 961 mg 等数字来自这里。不调用时模板里已有默认值，不影响构建。

---

## 常见坑

**收藏店为空**：`searchType=1` 在没收藏过的账号上必然返回空，别在这上面浪费一轮。

**门店少于 5 家**：换更宽的商圈词，或把 `city` 改成上一级市名重试。

**同一家店在两个片区的结果里重复**：正常，商圈交界处会重叠。按 `storeCode` 去重。

**券的金额和示例不一样**：券是动态的，以 `available-coupons` 返回为准。示例 json 里的 11.9 / 19.9 只是广州 2026-10-22 那次快照。

**`end` 字段**：接口可能返回 `00:00` 表示通宵，也可能是 `23:59`。统一成 `24:00` 才会被算作通宵店 —— `h24()` 只认 `24:00`。
